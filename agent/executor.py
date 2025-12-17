# core/executor.py
import subprocess
import sys
import os
import tempfile
import json
from datetime import datetime

def execute_script_logic(script_data: dict, args: dict = {}) -> dict:
    """
    Executa o script fornecido no dicionário script_data.
    script_data deve conter 'content' (o código do script).
    """
    
    script_content = script_data.get('content', '')
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
        temp_file.write(script_content)
        temp_file_path = temp_file.name

    start_time = datetime.utcnow()
    
    # Prepara os argumentos para o subprocesso
    # Ex: python script.py arg1 arg2
    cmd_args = [sys.executable, temp_file_path]

    for key, value in args.items():
        # Remove traços existentes na chave para evitar duplicação (----nome)
        clean_key = key.lstrip("-") 
        cmd_args.append(f"--{clean_key}")
        cmd_args.append(str(value))

    try:
        result = subprocess.run(
            cmd_args, # Passa a lista com argumentos
            capture_output=True,
            text=True,
            timeout=30
        )
        
        status = "success" if result.returncode == 0 else "failed"
        stdout = result.stdout
        stderr = result.stderr

    except subprocess.TimeoutExpired:
        status = "timeout"
        stdout = ""
        stderr = "Timeout de 30s excedido."
    except Exception as e:
        status = "failed"
        stdout = ""
        stderr = str(e)
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    finished_time = datetime.utcnow()

    return {
        "status": status,
        "started_at": start_time,
        "finished_at": finished_time,
        "stdout": stdout,
        "stderr": stderr,
        "run_args": args # Registra o que foi usado
    }
