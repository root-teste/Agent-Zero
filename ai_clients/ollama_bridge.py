# ai_clients/ollama_bridge.py
import requests
import json
import re
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b" 

def generate_response(prompt: str, model: str = DEFAULT_MODEL) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=300)
        return r.json().get("response", "")
    except Exception as e:
        return f"Erro de conexão: {e}"

def generate_automation_script(user_request: str, model: str = DEFAULT_MODEL) -> dict:
    # Prompt simplificado e direto para evitar confusão
    system_prompt = (
        "Write a Python 3 script for: " + user_request + "\n"
        "RULES:\n"
        "1. Output ONLY the code inside markdown blocks like ```python ... ```\n"
        "2. Do not add explanations before or after.\n"
        "3. Include a comment at the top with a suggested name: # Name: script_name"
    )
    
    print("\n[DEBUG] Enviando prompt para IA...")
    raw_response = generate_response(system_prompt, model)
    
    # Debug: Mostrar o que a IA realmente respondeu
    print(f"[DEBUG] Resposta Bruta da IA:\n{raw_response[:200]}...\n[Fim do Debug]\n")

    # --- TENTATIVA 1: Extrair bloco Markdown (```python ... ```) ---
    code_match = re.search(r'```python(.*?)```', raw_response, re.DOTALL)
    if not code_match:
        code_match = re.search(r'```(.*?)```', raw_response, re.DOTALL)
    
    content = ""
    if code_match:
        content = code_match.group(1).strip()
    else:
        # --- TENTATIVA 2: Se não tem markdown, assume que tudo é código ---
        # (Se tiver 'import' ou 'def', confiamos que é código)
        if "import " in raw_response or "def " in raw_response:
            content = raw_response.strip()
        else:
            print("Erro: Não encontrei código Python válido na resposta.")
            return None

    # Tenta extrair o nome do comentário, senão gera um aleatório
    name_match = re.search(r'# Name: (\w+)', content)
    script_name = name_match.group(1) if name_match else f"script_{int(time.time())}"
    
    return {
        "name": script_name,
        "description": f"Gerado via IA para: {user_request}",
        "content": content
    }

def analyze_context(context_data: str, user_question: str, model: str = DEFAULT_MODEL) -> str:
    """
    Analisa dados do sistema (tarefas, projetos) e responde uma pergunta estratégica.
    """
    system_prompt = (
        "You are a Personal System Advisor. "
        "I will provide you with a list of my current Projects, Tasks, and available Scripts. "
        "Your goal is to help me prioritize, organize, and suggest automations. "
        "Be concise, direct, and practical. "
        "If you see a task that sounds like it could be automated by Python, mention it explicitly."
    )
    
    final_prompt = (
        f"{system_prompt}\n\n"
        f"--- CURRENT SYSTEM DATA ---\n{context_data}\n"
        f"---------------------------\n\n"
        f"User Question: {user_question}"
    )
    
    return generate_response(final_prompt, model)

def route_instruction(user_instruction: str, available_scripts: list, model: str = DEFAULT_MODEL) -> dict:
    """
    Decide qual script executar com base na linguagem natural.
    """
    scripts_summary = "\n".join([f"- ID {s['id']}: {s['name']} (Desc: {s['description']})" for s in available_scripts])
    
    system_prompt = (
        "You are an Intent Router for a CLI Automation System. "
        "Match the User Instruction to one of the Available Scripts. "
        "Extract any arguments mentioned in the instruction. "
        "RETURN ONLY JSON format: "
        '{"script_id": <int or null>, "args": <dict>, "reason": "<string>"}'
        "\nIf no script matches, set script_id to null."
    )
    
    final_prompt = (
        f"{system_prompt}\n\n"
        f"--- AVAILABLE SCRIPTS ---\n{scripts_summary}\n"
        f"-------------------------\n"
        f"User Instruction: {user_instruction}"
    )
    
    # Reutiliza a lógica de limpeza de JSON que já fizemos antess
    # (Pode copiar a lógica de limpeza da função generate_automation_script se quiser refatorar, 
    # mas aqui vou chamar o generate_response e limpar manualmente para ser breve)
    raw = generate_response(final_prompt, model)
    
    # Limpeza básica de Markdown
    clean_json = raw.strip()
    if "```json" in clean_json:
        clean_json = clean_json.split("```json")[1].split("```")[0]
    elif "```" in clean_json:
        clean_json = clean_json.split("```")[1].split("```")[0]
        
    try:
        return json.loads(clean_json)
    except:
        return {"script_id": None, "reason": "Falha ao processar JSON da IA", "raw": raw}
