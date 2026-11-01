# Agente Zero — núcleo local

Primeiro marco de implementação: API, tarefas, notas e consulta privada ao segundo cérebro, com interface web local. O sistema ainda não é um agente autónomo de gestão/cibersegurança.

## Preparar (Python 3.12)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m core.setup --brain "CAMINHO-ABSOLUTO-DO-SEGUNDO-CEREBRO"
.\Iniciar.ps1
```

A configuração gera uma credencial aleatória em `.env` sem a mostrar e recusa substituir um arquivo existente. O banco fica no diretório de dados local do utilizador (Windows: `%LOCALAPPDATA%/AgentZero`), fora do repositório. O segundo cérebro precisa do índice existente `90-Config/memoria.sqlite`; não se cria, reindexa ou altera o índice nesta aplicação.

Abra http://127.0.0.1:8501 e use a aba **Memória local**. A busca é textual, preserva fontes e não chama modelos. Existe conversa com histórico persistente e fontes locais opcionais. Inferência real depende da validação do Ollama; delegação ainda não implementada. Notas/tarefas da API são independentes das notas canónicas do segundo cérebro; criar uma nota na UI não a sincroniza automaticamente.

O launcher inicia API e Streamlit em segundo plano, só em loopback, sem autostart do Windows. Logs em `%LOCALAPPDATA%/AgentZero`. Portas 8000/8501 já ocupadas impedem nova instância. Para parar os serviços iniciados pelo launcher: `.\Parar.ps1`; o script confere caminho do executável e comando antes de terminar cada processo. A UI é para o utilizador local e não tem login próprio: não expor por proxy/túnel/rede antes da fase de autenticação da UI.

Alternativa em dois terminais, a partir da raiz:

```powershell
.\.venv\Scripts\python.exe -m uvicorn core.main:app --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe -m streamlit run web/app.py
```

CLI: `.\.venv\Scripts\python.exe -m cli.main --help`.

## Privacidade e execução

- API exige chave; respostas usam `Cache-Control: no-store`; pesquisa é POST para evitar termos em URLs. Telemetria Streamlit desligada.
- Scripts, agenda e chamadas ao modelo estão desligados por padrão. Nenhuma integração de servidor ou modelo externo é criada por esta versão.
- O segundo cérebro é aberto em SQLite read-only. Trechos permanecem privados; nenhum resumo ou pseudonimização os torna públicos.
- Outros agentes só poderão receber subtarefas necessárias e públicas/sintéticas. A camada de delegação e o broker de saída ainda não estão implementados.
- A opção `AGENT_ZERO_ENABLE_LOCAL_MODEL=true` habilita o adaptador Ollama local configurável; só usar após confirmar inferência local e o destino efetivo. Não equivale a autorização para um gateway com fallback externo.
- `AGENT_ZERO_ENABLE_SCRIPT_EXECUTION=true` habilita execução legada com permissões do host. Não é isolamento e não deve ser usada com código não revisto. O worker também exige esse opt-in. Agenda exige `AGENT_ZERO_ENABLE_SCHEDULER=true`.
- Segredos e dados não vão para Git. Se a pasta do projeto estiver no OneDrive, o cliente de sincronização pode copiar o `.env`; isso é separado da política de saída do agente.

## Fila e operação

A reserva usa POST `/agent/jobs/claim`, atómico, marcando `running`. A rota GET antiga foi removida para impedir reserva via leitura. Atualizar API e worker juntos. Reports aceitam apenas `success`, `failed`, `timeout`; um report idêntico pode ser repetido. O worker repete report, nunca reexecuta o script após falha de comunicação.

Limites desta etapa: chave de API partilhada (sem RBAC por worker), sem lease/heartbeat de execução, sem recuperação automática de jobs `running`, sem snapshot imutável de script e sem isolamento. Um job interrompido exige reconciliação manual; não repor como pending sem verificar o efeito. Agenda é de um único processo: não iniciar vários workers Uvicorn/schedulers. Não há garantia de deduplicação distribuída de agenda.

Não se alterou o esquema das tabelas existentes; novas instalações são inicializadas no lifespan. `create_all` não é migração. A etapa de migrações versionadas e backup/restauro permanece pendente antes de alterações de esquema.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Testes usam banco e fontes sintéticas temporários. Cobrem autenticação, notas/tarefas, reserva com oito workers concorrentes, report idempotente, agenda, schemas, busca sem rede e interface via Streamlit AppTest. O lock guarda o ambiente validado com Python 3.12/Windows; outros sistemas precisam validar compatibilidade. O conjunto completo inclui dependências de desenvolvimento.

## Próximos marcos

Identidade e lease por worker; ferramentas tipadas isoladas; chat privado com inferência local verificada; política de classificação/saída e delegação pública; conectores de leitura para os serviços existentes; avaliação de cibersegurança em laboratório. Nenhum destes marcos é declarado concluído nesta versão.

## Publicação

Consulte [a política de publicação](docs/PUBLICACAO.md).
