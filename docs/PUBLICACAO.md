# Política de publicação no GitHub

Revisão: 01/11/2026.

Publicar código, testes sintéticos, dependências, exemplos sem credenciais e documentação técnica genérica.

## Nunca incluir no envio

- Configuração real: .env e variantes, tokens, senhas, cookies, credenciais OAuth, chaves SSH/TLS e secrets do Streamlit.
- Bancos, dumps, filas, histórico de conversas, tarefas reais e estado de processos.
- Segundo cérebro, índices, notas pessoais, transcrições, áudio, biometria e documentos de clientes. Resumos e pseudonimizações continuam privados.
- Logs, capturas, anexos, uploads, exports e dumps de contexto com dados reais.
- IPs, nomes de hosts, caminhos pessoais, topologia privada, configurações de servidores e resultados reais de pentest.
- Backups, pesos de modelos, caches, ambientes Python e artefactos temporários.
- Dossiês locais analise-*, auditorias e documentos que conservem contexto privado. Redigir documentação pública própria, sem copiar fontes privadas.

## Verificação de cada publicação

Rever a lista preparada e o diff integral; procurar credenciais e dados privados; confirmar exclusões com git check-ignore; executar testes e git diff --check; confirmar o hash publicado no remoto.

.gitignore não remove ficheiros já rastreados nem apaga histórico. Se surgir um segredo, revogar primeiro e tratar o histórico separadamente. O gerador de contexto limita-se a código rastreado, mas o resultado ainda deve ser revisto antes de partilhar.
