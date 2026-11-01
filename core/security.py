import secrets
from fastapi import Header, HTTPException
from .config import settings

def get_api_key(x_api_key: str | None = Header(default=None)):
    if not settings.API_KEY or not x_api_key or not secrets.compare_digest(x_api_key.encode("utf-8"), settings.API_KEY.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Credencial inválida ou ausente")

def require_script_execution():
    if not settings.EXECUTION_ENABLED:
        raise HTTPException(403, "Execução desativada: esta versão ainda não oferece isolamento do host.")
