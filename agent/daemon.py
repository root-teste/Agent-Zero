import requests
import time
from datetime import datetime
from agent.executor import execute_script_logic

API_URL = 'http://127.0.0.1:8000'

def run_worker():
    while True:
        try:
            response = requests.get(f"{API_URL}/agent/jobs/pending")
            
            if response.status_code in [204, 404]:
                time.sleep(2)
                continue
            
            if response.status_code == 200:
                job_data = response.json()
                script_content = job_data.get('script_content')
                run_args = job_data.get('run_args', {})
                job_id = job_data.get('id')
                
                print(f"Executando Job {job_id}...")
                
                script_data = {'content': script_content}
                result = execute_script_logic(script_data, run_args)
                
                report_data = {
                    "status": result["status"],
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                    "finished_at": datetime.utcnow().isoformat()
                }
                
                requests.post(f"{API_URL}/agent/jobs/{job_id}/report", json=report_data)
        
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_worker()
