"""Arranca apenas serviços deste projeto em loopback, sem instalação de autostart."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import requests

from .config import ROOT, settings


def wait_for(url, process, headers=None):
    for _ in range(40):
        if process.poll() is not None:
            raise RuntimeError("Serviço terminou durante o arranque; consulte os logs locais.")
        try:
            response = requests.get(url, headers=headers or {}, timeout=1, allow_redirects=False)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.25)
    raise RuntimeError("Serviço não ficou disponível no prazo de arranque.")


def main():
    settings.validate()
    if settings.API_URL != "http://127.0.0.1:8000":
        raise RuntimeError("Este launcher exige API_URL=http://127.0.0.1:8000")
    for port in (8000, 8501):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Porta {port} já ocupada; nenhuma instância adicional foi iniciada.")
    data = Path(os.getenv("LOCALAPPDATA", str(Path.home() / ".local/share"))) / "AgentZero"
    data.mkdir(parents=True, exist_ok=True)
    processes = []
    try:
        commands = [
            ("api", ["-m", "uvicorn", "core.main:app", "--host", "127.0.0.1", "--port", "8000", "--no-access-log"]),
            ("web", ["-m", "streamlit", "run", "web/app.py"]),
        ]
        for name, args in commands:
            with (data / f"{name}.log").open("ab") as log:
                process = subprocess.Popen([sys.executable, *args], cwd=ROOT, stdout=log, stderr=log,
                                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            processes.append(process)
            url = "http://127.0.0.1:8000/health" if name == "api" else "http://127.0.0.1:8501/_stcore/health"
            wait_for(url, process, {"x-api-key": settings.API_KEY} if name == "api" else None)
        (data / "run-state.json").write_text(json.dumps({"project": str(ROOT), "pids": [p.pid for p in processes]}), encoding="utf-8")
        print("Agente Zero disponível em http://127.0.0.1:8501 (apenas neste computador).")
    except Exception:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
        raise


if __name__ == "__main__":
    main()
