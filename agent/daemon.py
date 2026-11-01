"""Worker legado opt-in; não constitui isolamento de scripts."""
import logging
import time
from datetime import datetime

from agent.executor import execute_script_logic
from core import http_client as requests
from core.config import settings

logger = logging.getLogger(__name__)

def report_result(job_id, payload):
    # Repetir apenas o report, nunca o script, após erro de comunicação.
    for attempt in range(3):
        try:
            response = requests.post(f"{settings.API_URL}/agent/jobs/{job_id}/report", json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            if attempt < 2:
                time.sleep(2 ** attempt)
    logger.error("Report não confirmado para job %s; reconciliar manualmente", job_id)
    return False

def run_once():
    response = requests.post(f"{settings.API_URL}/agent/jobs/claim")
    if response.status_code == 404:
        return False
    response.raise_for_status()
    job = response.json()
    if not isinstance(job.get("job_id"), int) or not isinstance(job.get("script_content"), str):
        raise ValueError("Resposta de claim inválida")
    result = execute_script_logic({"content": job["script_content"]}, job.get("run_args", {}))
    report_result(job["job_id"], {
        "status": result["status"], "stdout": result["stdout"][:100_000],
        "stderr": result["stderr"][:100_000], "finished_at": datetime.utcnow().isoformat(),
    })
    return True

def run_worker():
    settings.validate()
    if not settings.EXECUTION_ENABLED:
        raise RuntimeError("Execução de scripts desativada. O worker legado exige opt-in explícito.")
    while True:
        try:
            if not run_once():
                time.sleep(2)
        except (requests.exceptions.RequestException, ValueError, KeyError):
            logger.error("Worker sem resposta válida; nova consulta após espera")
            time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_worker()
