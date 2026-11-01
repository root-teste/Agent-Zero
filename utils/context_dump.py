"""Exporta código rastreado; rever antes de partilhar."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def generate_context():
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)
    print("Contexto de código rastreado — rever antes de partilhar.")
    for name in result.stdout.decode("utf-8").split("\0"):
        if not name:
            continue
        path = ROOT / name
        if path.suffix not in {".py", ".ps1"} or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            continue
        if path.is_file() and path.stat().st_size <= 100_000:
            print(f"\n--- {name} ---\n{path.read_text(encoding='utf-8-sig')}")


if __name__ == "__main__":
    generate_context()
