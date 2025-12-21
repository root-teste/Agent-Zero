import requests
import time
from datetime import datetime
from agent.executor import execute_script_logic

import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")
HEADERS = {"x-api-key": os.getenv("SYSTEM_API_KEY")}

def run_worker():
    while True:
        try:
            response = requests.get(f"{API_URL}/agent/jobs/pending", headers=HEADERS)
            
            if response.status_code in [204, 404]:
                time.sleep(2)
                continue
            
            if response.status_code == 200:
                job_data = response.json()
                print(f"DEBUG: Dados recebidos: {job_data}")
                script_content = job_data.get('script_content')
                run_args = job_data.get('run_args', {})
                job_id = job_data.get('job_id') or job_data.get('id')
                
                print(f"Executando Job {job_id}...")
                
                script_data = {'content': script_content}
                result = execute_script_logic(script_data, run_args)
                
                report_data = {
                    "status": result["status"],
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                    "finished_at": datetime.utcnow().isoformat()
                }
                
                requests.post(f"{API_URL}/agent/jobs/{job_id}/report", json=report_data, headers=HEADERS)
        
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_worker()
