import os

# Pastas e arquivos para ignorar
IGNORE_DIRS = {'venv', '__pycache__', '.git', '.idea', '.vscode', 'system.db'}
IGNORE_FILES = {'system.db', '.env', 'poetry.lock', 'package-lock.json'}
EXTENSIONS = {'.py', '.yaml', '.json', '.md', '.sql'}

def generate_context():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output = []
    
    output.append("=== ESTRUTURA DO PROJETO ===")
    for root, dirs, files in os.walk(project_root):
        # Filtra pastas ignoradas
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(project_root, '').count(os.sep)
        indent = ' ' * 4 * (level)
        output.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in IGNORE_FILES:
                output.append(f"{subindent}{f}")

    output.append("\n=== CONTEÚDO DOS ARQUIVOS ===")
    
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES:
                continue
            
            ext = os.path.splitext(file)[1]
            if ext not in EXTENSIONS:
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, project_root)
            
            output.append(f"\n--- ARQUIVO: {rel_path} ---")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    output.append(f.read())
            except Exception as e:
                output.append(f"[Erro ao ler arquivo: {e}]")
                
    print("\n".join(output))

if __name__ == "__main__":
    generate_context()
