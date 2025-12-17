import streamlit as st
import requests
import pandas as pd

API_URL = 'http://127.0.0.1:8000'

def main():
    st.title("Dashboard do Sistema C2")

    tabs = st.tabs(["Monitor de Jobs", "Biblioteca de Scripts", "Setup"])

    with tabs[0]:
        st.header("Monitor de Jobs")
        response = requests.get(f"{API_URL}/agent/jobs/pending")
        if response.status_code == 200:
            jobs = response.json()
            df = pd.DataFrame(jobs)
            df['Duration'] = pd.to_datetime(df['finished_at']) - pd.to_datetime(df['started_at'])
            st.dataframe(df[['id', 'script_name', 'status', 'started_at', 'Duration']])
        else:
            st.write("Nenhum job pendente encontrado.")

    with tabs[1]:
        st.header("Biblioteca de Scripts")
        response = requests.get(f"{API_URL}/scripts/")
        if response.status_code == 200:
            scripts = response.json()
            for script in scripts:
                st.subheader(script['name'])
                st.write(script['description'])
                if st.button(f"Executar Agora {script['id']}"):
                    run_response = requests.post(f"{API_URL}/run/{script['id']}")
                    if run_response.status_code == 200:
                        st.success(f"Script {script['id']} executado com sucesso!")
                    else:
                        st.error(f"Erro ao executar script {script['id']}.")

    with tabs[2]:
        st.header("Setup")
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                st.success("API Online")
            else:
                st.error("API Offline")
        except requests.exceptions.RequestException:
            st.error("API Offline")

if __name__ == "__main__":
    main()
