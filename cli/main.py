# cli/main.py

import os
from dotenv import load_dotenv

load_dotenv()
import typer
import requests
import json
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from ai_clients import ollama_bridge

app = typer.Typer()
console = Console()

API_URL = os.getenv("API_URL")
HEADERS = {"x-api-key": os.getenv("SYSTEM_API_KEY")}

# --- Funções Auxiliares ---

def check_server():
    """Verifica se a API está online."""
    try:
        requests.get(API_URL)
    except requests.exceptions.ConnectionError:
        rprint("[bold red]Erro:[/bold red] O Core App não está rodando.")
        rprint(f"Certifique-se de rodar: [green]uvicorn core.main:app --reload[/green]")
        raise typer.Exit(code=1)

# --- Comandos de Tarefas ---

@app.command("tasks")
def list_tasks():
    """Lista todas as tarefas pendentes."""
    check_server()
    response = requests.get(f"{API_URL}/tasks/", headers=HEADERS)
    tasks = response.json()

    if not tasks:
        rprint("[yellow]Nenhuma tarefa encontrada.[/yellow]")
        return

    table = Table(title="Tarefas Atuais")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Título", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Script Vinculado", style="blue")

    for task in tasks:
        script_info = str(task['linked_script_id']) if task['linked_script_id'] else "-"
        table.add_row(str(task['id']), task['title'], task['status'], script_info)

    console.print(table)

@app.command("add-task")
def add_task(title: str, project_id: int = 0):
    """Adiciona uma nova tarefa."""
    check_server()
    payload = {"title": title}
    if project_id > 0:
        payload["project_id"] = project_id
    
    response = requests.post(f"{API_URL}/tasks/", json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        rprint(f"[bold green]Sucesso![/bold green] Tarefa criada: [bold]{data['title']}[/bold] (ID: {data['id']})")
    else:
        rprint("[bold red]Erro ao criar tarefa.[/bold red]")

# --- Comandos de Scripts e IA ---

@app.command("scripts")
def list_scripts():
    """Lista os scripts disponíveis."""
    check_server()
    response = requests.get(f"{API_URL}/scripts/", headers=HEADERS)
    scripts = response.json()

    table = Table(title="Biblioteca de Scripts")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Interpretador", style="yellow")

    for script in scripts:
        table.add_row(str(script['id']), script['name'], script['interpreter'])

    console.print(table)

@app.command("run")
def run_script(script_id: int, args: str = "{}"):
    """
    Executa script. Pode passar argumentos em JSON.
    Ex: run 1 --args '{"key": "val"}'
    """
    check_server()
    
    try:
        args_dict = json.loads(args)
    except:
        rprint("[red]Erro:[/red] Argumentos inválidos. Use formato JSON ex: '{\"key\": \"val\"}'")
        return

    # Confirmação de segurança
    rprint(f"[bold yellow]Atenção:[/bold yellow] Executando Script ID {script_id} com args: {args_dict}")
    if not typer.confirm("Deseja continuar?"):
        raise typer.Abort()

    rprint("[dim]Enviando comando para o Core App...[/dim]")
    
    response = requests.post(f"{API_URL}/run/{script_id}", json={"args": args_dict}, headers=HEADERS)
    
    if response.status_code == 200:
        job = response.json()
        panel_color = "green" if job['status'] == "success" else "red"
        rprint(f"\n[bold {panel_color}]Status: {job['status'].upper()}[/bold {panel_color}]")
        rprint(f"Início: {job['started_at']}")
        rprint(f"Fim:   {job['finished_at']}")
        
        rprint("\n[bold]--- SAÍDA (STDOUT) ---[/bold]")
        rprint(f"[white]{job['stdout']}[/white]")
        
        if job['stderr']:
            rprint("\n[bold red]--- ERROS (STDERR) ---[/bold red]")
            rprint(f"[red]{job['stderr']}[/red]")
    else:
        rprint(f"[bold red]Erro na requisição:[/bold red] {response.status_code}")

@app.command("ask")
def ask_ai(question: str):
    """Conversa rápida com a IA Local."""
    rprint(f"[bold yellow]Pergunta:[/bold yellow] {question}")
    rprint("[dim]Pensando...[/dim]")
    resposta = ollama_bridge.generate_response(question)
    rprint(f"\n[bold cyan]IA Local:[/bold cyan] {resposta}")

@app.command("create")
def create_ai_script(instruction: str):
    """Usa a IA para gerar um novo script."""
    check_server()
    rprint(f"[bold yellow]Solicitando ao Arquiteto Local:[/bold yellow] '{instruction}'")
    rprint("[dim]Gerando código...[/dim]")
    
    script_data = ollama_bridge.generate_automation_script(instruction)
    
    if not script_data:
        rprint("[bold red]Erro:[/bold red] A IA não retornou um formato válido.")
        return

    rprint("\n[bold cyan]Proposta Gerada:[/bold cyan]")
    rprint(f"Nome: [green]{script_data['name']}[/green]")
    rprint(f"Desc: {script_data['description']}")
    rprint("-" * 30)
    rprint(script_data['content'])
    rprint("-" * 30)
    
    if typer.confirm("Deseja salvar este script no sistema?"):
        payload = {
            "name": script_data['name'],
            "description": script_data['description'],
            "content": script_data['content'],
            "interpreter": "python3"
        }
        response = requests.post(f"{API_URL}/scripts/", json=payload, headers=HEADERS)
        if response.status_code == 200:
            new_script = response.json()
            rprint(f"[bold green]Sucesso![/bold green] Script salvo com ID: {new_script['id']}")
        else:
            rprint(f"[red]Erro na API:[/red] {response.text}")
    else:
        rprint("[yellow]Operação cancelada.[/yellow]")

@app.command("advisor")
def advisor(question: str = "O que devo priorizar hoje?"):
    """Analisa suas tarefas e dá conselhos."""
    check_server()
    rprint("[dim]Coletando dados do sistema...[/dim]")
    
    try:
        tasks = requests.get(f"{API_URL}/tasks/", headers=HEADERS).json()
        scripts = requests.get(f"{API_URL}/scripts/", headers=HEADERS).json()
        projects = requests.get(f"{API_URL}/projects/", headers=HEADERS).json()
    except Exception as e:
        rprint(f"[red]Erro ao buscar dados:[/red] {e}")
        return

    context_str = "PROJECTS:\n" + "\n".join([f"- {p['name']}" for p in projects])
    context_str += "\nTASKS:\n" + "\n".join([f"- {t['title']} ({t['status']})" for t in tasks])
    context_str += "\nSCRIPTS:\n" + "\n".join([f"- {s['name']}: {s['description']}" for s in scripts])

    rprint(f"[bold yellow]Pergunta:[/bold yellow] {question}")
    advice = ollama_bridge.analyze_context(context_str, question)
    rprint("\n[bold cyan]--- CONSELHO DO SISTEMA ---[/bold cyan]")
    rprint(advice)

@app.command("do")
def magic_do(instruction: str):
    """Comando inteligente: Tenta entender o que você quer executar."""
    check_server()
    scripts = requests.get(f"{API_URL}/scripts/").json()
    if not scripts:
        rprint("[red]Nenhum script disponível.[/red]")
        return

    rprint(f"[dim]Analisando instrução: '{instruction}'...[/dim]")
    decision = ollama_bridge.route_instruction(instruction, scripts)
    
    script_id = decision.get("script_id")
    if not script_id:
        rprint(f"[yellow]A IA não encontrou um script correspondente.[/yellow]")
        return

    script_name = next((s['name'] for s in scripts if s['id'] == script_id), "Desconhecido")
    args = decision.get("args", {})

    rprint(f"\n[bold cyan]Intenção Detectada:[/bold cyan] Executar [green]{script_name}[/green] (ID {script_id})")
    if args:
        rprint(f"Argumentos extraídos: {args}")
    
    if typer.confirm("Proceder?"):
        run_script(script_id, json.dumps(args))
    else:
        rprint("[yellow]Cancelado.[/yellow]")

@app.command("cat")
def cat_script(script_id: int):
    """
    Exibe o código fonte de um script salvo no banco.
    Ex: python cli/main.py cat 1
    """
    check_server()
    response = requests.get(f"{API_URL}/scripts/{script_id}", headers=HEADERS)
    
    if response.status_code == 200:
        script = response.json()
        rprint(f"\n[bold cyan]--- Script: {script['name']} (ID {script['id']}) ---[/bold cyan]")
        rprint(f"[dim]{script['description']}[/dim]\n")
        # Exibe o código com sintaxe colorida (se o terminal suportar)
        from rich.syntax import Syntax
        syntax = Syntax(script['content'], "python", theme="monokai", line_numbers=True)
        console.print(syntax)
        rprint("\n[bold cyan]------------------------------------------[/bold cyan]")
    else:
        rprint("[red]Script não encontrado.[/red]")

if __name__ == "__main__":
    app()
import requests

def schedule_script(script_id: int, interval_minutes: int):
    """
    Agenda um script para execução periódica.
    """
    url = f"http://127.0.0.1:8000/scripts/{script_id}"
    payload = {
        "is_scheduled": True,
        "schedule_interval": interval_minutes
    }
    response = requests.patch(url, json=payload)
    
    if response.status_code == 200:
        print(f"Script {script_id} agendado para rodar a cada {interval_minutes} minutos.")
    else:
        print(f"Erro ao agendar script {script_id}: {response.status_code} - {response.text}")

# Exemplo de uso
if __name__ == "__main__":
    # Substitua pelos valores desejados
    schedule_script(1, 30)
