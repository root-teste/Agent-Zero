# Primeiro marco local — 01/11/2026

Branch: `work/base-local-segura`. Estado: implementação inicial, sem publicação remota.

## Implementado

- Lifespan FastAPI, validação da configuração, autenticação uniforme, health autenticado e notas ligadas.
- Contrato de tarefas corrigido; entradas CLI/Streamlit funcionais; cliente HTTP com timeout, origem restrita e redirects desativados.
- Reserva atómica por POST; teste com oito concorrentes; reports com estados terminais e repetição idempotente; worker repete report sem repetir script.
- Agenda impede sobreposição pending/running no processo único; arranque/paragem explícitos e defaults desativados.
- Schema de argumentos validado na criação, enfileiramento e reserva. Interpretadores incompatíveis não seguem para o executor legado.
- Busca de leitura no índice FTS existente do segundo cérebro, fonte/referência/trecho, limite de consulta, sem rede/modelo nem alteração das fontes.
- Interface com aba Memória local; telemetria desligada. API e web apenas em loopback pelo launcher.
- Configurador que cria segredo sem o imprimir e preserva .env existente; banco em diretório de dados do utilizador.
- Ambiente reprodutível fixado em requirements-lock.txt e scripts de arranque/paragem.

## Evidência

28 testes passaram em Python 3.12/Windows, no ambiente .venv instalado pelo lock. Incluem API, memória sintética, garantia de não chamada de rede no serviço de busca, Streamlit AppTest com pesquisa, concorrência, validação, retry do worker e proteção de configuração. `git diff --check` sem erros.

Verificação real local: API /health HTTP 200, web /_stcore/health HTTP 200, busca no índice já existente HTTP 200 e processing local_only. Nenhum script ou modelo foi executado. Serviços em loopback e sem instalação de arranque automático do Windows. Não se consultaram servidores remotos.

Há avisos de depreciação de datetime.utcnow e do transporte httpx no TestClient; os testes passaram. Não equivalem a auditoria de segurança nem validação em Linux.

## Pendente antes de execução/autonomia habitual

Identidade/RBAC por worker, lease/heartbeat e reconciliação, snapshot imutável de script, isolamento real e ferramentas tipadas, agenda distribuída, migrações e backup/restauro, autenticação da UI para acesso remoto, chat e inferência local verificada, política executável de delegação pública/broker de saída, conectores e avaliação de cibersegurança.

O mecanismo de saída para outros agentes não está implementado. Não há garantia global de contenção só por configuração. A busca entregue não usa LLM e os clientes de modelo estão desligados por padrão. Núcleo, agenda e executor continuam sujeitos às limitações detalhadas no README.

## Registo da revisão

Alterações preparadas no índice da branch local. O commit não foi criado: Git sem nome/email configurados. Nenhuma identidade foi presumida e nada foi enviado ao GitHub.

## Atualização: correções e conversa local

Implementados histórico persistente, fontes opcionais e adaptador configurável restrito a loopback. Geração testada com modelo simulado; pesos reais, streaming, cancelamento e voz pendentes. Novas tabelas são aditivas; create_all não substitui migrações. Gerador de contexto limitado a código rastreado e exclusões de publicação reforçadas. A preparação de publicação atual substitui o estado histórico de não publicação registado acima.
