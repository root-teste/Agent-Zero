import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

class Settings:
    API_KEY = os.getenv("SYSTEM_API_KEY", "")
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(ROOT / 'system.db').as_posix()}")
    EXECUTION_ENABLED = os.getenv("AGENT_ZERO_ENABLE_SCRIPT_EXECUTION", "false").lower() == "true"
    SCHEDULER_ENABLED = os.getenv("AGENT_ZERO_ENABLE_SCHEDULER", "false").lower() == "true"
    SECOND_BRAIN_ROOT = os.getenv("SECOND_BRAIN_ROOT")
    LOCAL_MODEL_ENABLED = os.getenv("AGENT_ZERO_ENABLE_LOCAL_MODEL", "false").lower() == "true"
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")

    def validate(self):
        if len(self.API_KEY) < 32 or self.API_KEY.startswith(("sua_chave", "SUBSTITUA")):
            raise RuntimeError("Configure SYSTEM_API_KEY com pelo menos 32 caracteres aleatórios.")

settings = Settings()
