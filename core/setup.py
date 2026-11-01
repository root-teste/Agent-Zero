"""Configuração local sem mostrar credenciais nem substituir configuração existente."""
import argparse
import os
from pathlib import Path
import secrets

from .config import ROOT


def main():
    parser = argparse.ArgumentParser(description="Preparar configuração privada local")
    parser.add_argument("--brain", type=Path)
    args = parser.parse_args()
    env = ROOT / ".env"
    if env.exists():
        parser.exit(1, ".env já existe; configuração preservada.\n")
    base = Path(os.getenv("LOCALAPPDATA", str(Path.home() / ".local/share"))) / "AgentZero"
    base.mkdir(parents=True, exist_ok=True)
    lines = [f"SYSTEM_API_KEY={secrets.token_urlsafe(48)}", "API_URL=http://127.0.0.1:8000",
             f"DATABASE_URL=sqlite:///{(base / 'system.db').as_posix()}",
             "AGENT_ZERO_ENABLE_SCRIPT_EXECUTION=false", "AGENT_ZERO_ENABLE_SCHEDULER=false",
             "AGENT_ZERO_ENABLE_LOCAL_MODEL=false"]
    if args.brain:
        root = args.brain.resolve()
        if not (root / "90-Config/memoria.sqlite").is_file():
            parser.exit(1, "Índice do segundo cérebro não encontrado; nada foi configurado.\n")
        lines.append(f'SECOND_BRAIN_ROOT="{root.as_posix()}"')
    with env.open("x", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    print("Configuração criada. Credencial guardada apenas no .env local; execução e modelos desligados.")


if __name__ == "__main__":
    main()
