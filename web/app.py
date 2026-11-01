import os
from dotenv import load_dotenv
import streamlit as st
from core import http_client as requests
from core.config import settings
import pandas as pd
from datetime import datetime

# Configuração da página DEVE ser a primeira chamada Streamlit
st.set_page_config(layout='wide', page_title="Agente Zero")

load_dotenv()
API_URL = settings.API_URL
HEADERS = {"x-api-key": settings.API_KEY}

def main():
    st.title("Agente Zero — núcleo local")
    with st.expander("Conversar com o Agente Zero", expanded=True):
        try:
            available = requests.get(f"{API_URL}/chat/conversations")
            available.raise_for_status()
            items = available.json()
            if st.button("Nova conversa"):
                created = requests.post(f"{API_URL}/chat/conversations", json={"title": "Nova conversa"})
                created.raise_for_status()
                st.session_state["conversation"] = created.json()["id"]
                st.rerun()
            if items:
                labels = {c["id"]: f"{c['title']} · {c['id']}" for c in items}
                current = st.session_state.get("conversation", items[0]["id"])
                selected = st.selectbox("Conversa", list(labels), format_func=labels.get,
                                        index=list(labels).index(current) if current in labels else 0)
                history = requests.get(f"{API_URL}/chat/conversations/{selected}")
                history.raise_for_status()
                for message in history.json():
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                        for source in message.get("sources") or []:
                            st.caption(f"Fonte: {source['path']} · {source['reference']}")
                with st.form("chat_message", clear_on_submit=True):
                    content = st.text_area("Mensagem", max_chars=6000)
                    use_memory = st.checkbox("Consultar o segundo cérebro")
                    submitted = st.form_submit_button("Enviar")
                if submitted and content.strip():
                    with st.spinner("A preparar a resposta local…"):
                        reply = requests.post(f"{API_URL}/chat/conversations/{selected}/messages",
                                              json={"content": content, "use_memory": use_memory}, timeout=190)
                    if reply.status_code == 200:
                        st.rerun()
                    else:
                        st.warning(reply.json().get("detail", "Resposta indisponível"))
            else:
                st.info("Crie uma conversa para começar.")
        except requests.exceptions.RequestException:
            st.info("A conversa estará disponível quando o núcleo local estiver ligado.")
    st.caption("Memória privada local. Execução de scripts desativada por padrão nesta etapa.")

    # Definição das 5 Abas
    tabs = st.tabs(["Monitoramento", "Controle (Scripts)", "Setup", "Agendamento", "🧠 Notas", "Memória local"])

    with tabs[5]:
        st.header("Consultar o segundo cérebro")
        st.caption("Busca local com fontes. Nenhum modelo ou agente externo recebe esta consulta.")
        with st.form("memory_search"):
            query = st.text_input("O que procura?", max_chars=300, key="memory_query")
            submitted = st.form_submit_button("Pesquisar", key="memory_submit")
        if submitted and query.strip():
            try:
                response = requests.post(f"{API_URL}/memory/search", json={"query": query, "limit": 5})
                if response.status_code == 200:
                    results = response.json()["results"]
                    if not results:
                        st.info("Não foram encontradas fontes para esta consulta.")
                    for result in results:
                        st.subheader(result["title"])
                        st.text(result["excerpt"])
                        st.caption(f"Fonte: {result['path']} · {result['reference']}")
                else:
                    st.warning("Busca indisponível. Verifique a configuração local e o índice.")
            except requests.exceptions.RequestException:
                st.error("Não foi possível consultar o núcleo local.")

    # --- ABA 1: MONITORAMENTO ---
    with tabs[0]:
        st.header("Histórico de Execuções")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Atualizar Lista"):
                st.rerun()
        
        try:
            # Busca histórico de jobs
            response = requests.get(f"{API_URL}/jobs", headers=HEADERS)
            if response.status_code == 200:
                jobs = response.json()
                if jobs:
                    df = pd.DataFrame(jobs)
                    # Conversão de datas e cálculo de duração
                    df['started_at'] = pd.to_datetime(df['started_at'])
                    df['finished_at'] = pd.to_datetime(df['finished_at'])
                    df['Duração'] = df['finished_at'] - df['started_at']
                    
                    # Exibição organizada
                    st.dataframe(
                        df[['id', 'script_id', 'status', 'started_at', 'Duração']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Nenhum histórico de execução encontrado.")
            else:
                st.error(f"Erro na API: {response.status_code}")
        except Exception as e:
            st.error(f"API Offline ou erro de conexão: {e}")

    # --- ABA 2: CONTROLE (SCRIPTS) ---
    with tabs[1]:
        st.header("Biblioteca de Scripts")
        try:
            response = requests.get(f"{API_URL}/scripts/", headers=HEADERS)
            if response.status_code == 200:
                scripts = response.json()
                for script in scripts:
                    with st.expander(f"📜 {script['name']} (ID: {script['id']})"):
                        st.write(script.get('description', 'Sem descrição'))
                        st.code(script['content'], language='python')
                        
                        # Botão com chave única para evitar erro de ID duplicado
                        if st.button("▶️ Executar Agora", key=f"btn_run_{script['id']}", disabled=not settings.EXECUTION_ENABLED):
                            run_res = requests.post(f"{API_URL}/run/{script['id']}", headers=HEADERS)
                            if run_res.status_code == 200:
                                st.success(f"Script {script['name']} enviado para fila!")
                            else:
                                st.error("Falha ao iniciar script.")
            else:
                st.warning("Não foi possível carregar os scripts.")
        except Exception as e:
            st.error(f"Erro ao carregar scripts: {e}")

    # --- ABA 3: SETUP ---
    with tabs[2]:
        st.header("Status do Sistema")
        try:
            r = requests.get(f"{API_URL}/health", headers=HEADERS)
            if r.status_code == 200:
                st.success("✅ API Core: ONLINE")
            else:
                st.warning(f"⚠️ API Core retornou: {r.status_code}")
        except:
            st.error("❌ API Core: OFFLINE")
            
        st.info("ℹ️ Para ver o Agente, verifique o terminal onde 'daemon.py' está rodando.")

    # --- ABA 4: AGENDAMENTO (NOVA) ---
    with tabs[3]:
        st.header("Automação e Agendamento")
        st.markdown("Configure quais scripts devem rodar automaticamente.")
        
        try:
            # Reutiliza a lista de scripts
            response = requests.get(f"{API_URL}/scripts/")
            if response.status_code == 200:
                scripts = response.json()
                
                # Cria um formulário para cada script
                for script in scripts:
                    with st.container():
                        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                        
                        # Coluna 1: Nome
                        c1.subheader(script['name'])
                        
                        # Coluna 2: Checkbox Ativo
                        is_scheduled = c2.checkbox(
                            "Agendado", 
                            value=script.get('is_scheduled', False),
                            key=f"check_sched_{script['id']}"
                        )
                        
                        # Coluna 3: Input Minutos
                        interval = c3.number_input(
                            "Minutos", 
                            min_value=1, 
                            value=script.get('schedule_interval', 60) or 60,
                            key=f"num_sched_{script['id']}"
                        )
                        
                        # Coluna 4: Botão Salvar
                        if c4.button("💾 Salvar", key=f"save_sched_{script['id']}"):
                            payload = {
                                "is_scheduled": is_scheduled,
                                "schedule_interval": interval
                            }
                            # Chama o endpoint PATCH
                            patch_res = requests.patch(f"{API_URL}/scripts/{script['id']}", json=payload, headers=HEADERS)
                            
                            if patch_res.status_code == 200:
                                st.toast(f"Agendamento de '{script['name']}' atualizado!", icon="✅")
                            else:
                                st.error("Erro ao salvar configuração.")
                        
                        st.divider()
        except Exception as e:
            st.error(f"Erro ao carregar dados de agendamento: {e}")

    # --- ABA 5: NOTAS ---
    with tabs[4]:
        st.header("Notas")
        try:
            response = requests.get(f"{API_URL}/notes/", headers=HEADERS)
            if response.status_code == 200:
                notes = response.json()
                for note in notes:
                    with st.expander(f"📝 {note['title']} (ID: {note['id']})"):
                        st.markdown(note['content'])
            else:
                st.warning("Não foi possível carregar as notas.")
        except Exception as e:
            st.error(f"Erro ao carregar notas: {e}")

        st.subheader("Criar Nova Nota")
        note_title = st.text_input("Título da Nota")
        note_content = st.text_area("Conteúdo da Nota (Markdown)")
        area_id = st.number_input("ID da Área", min_value=1, step=1)
        project_id = st.number_input("ID do Projeto (Opcional)", min_value=0, step=1)

        if st.button("Salvar Nota"):
            payload = {
                "title": note_title,
                "content": note_content,
                "area_id": area_id,
                "project_id": project_id if project_id > 0 else None
            }
            try:
                response = requests.post(f"{API_URL}/notes/", json=payload, headers=HEADERS)
                if response.status_code == 200:
                    st.success("Nota criada com sucesso!")
                else:
                    st.error("Erro ao criar nota.")
            except Exception as e:
                st.error(f"Erro ao criar nota: {e}")

if __name__ == "__main__":
    main()
