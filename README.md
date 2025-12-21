# Agent-Zero

Agent-Zero: Um orquestrador pessoal de automação, notas e inteligência artificial privada.

Este é um sistema pessoal de automação, desenvolvido para gerenciar tarefas, projetos, scripts e agendamentos de forma eficiente. Ele utiliza FastAPI para a criação de APIs RESTful e SQLAlchemy para a manipulação do banco de dados.

## Funcionalidades

- **Gerenciamento de Áreas e Projetos**: Criação e listagem de áreas e projetos associados.
- **Gerenciamento de Tarefas**: Criação e listagem de tarefas com status e vinculação a projetos.
- **Execução de Scripts**: Criação, listagem e execução de scripts com suporte a diferentes interpretadores.
- **Agendamento de Tarefas**: Agendamento de tarefas periódicas com base em intervalos de tempo.

## Instalação

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_DIRETORIO>
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Executando o Servidor

Para rodar o servidor FastAPI, utilize o Uvicorn:

```bash
uvicorn core.main:app --reload
app.include_router(agent.router)

## Executando a CLI

Para executar a CLI, utilize o seguinte comando:

```bash
python core/cli.py
```

Certifique-se de que o ambiente virtual esteja ativado antes de executar os comandos acima.
