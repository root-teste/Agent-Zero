# core/scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime
from . import database, models, executor

# Instância global do scheduler
scheduler = BackgroundScheduler()

def run_pending_job(task_id: int):
    """
    Função que o Scheduler chama quando o relógio bate.
    """
    # Cria uma nova sessão de banco apenas para essa execução
    db = database.SessionLocal()
    try:
        task = db.query(models.PeriodicTask).filter(models.PeriodicTask.id == task_id).first()
        
        if not task or not task.is_active:
            return

        print(f"[SCHEDULER] Executando tarefa agendada: {task.name}")
        
        # 1. Cria o Job no histórico
        job = models.Job(script_id=task.script_id, status="running", run_args=task.run_args)
        db.add(job)
        db.commit()
        
        # 2. Executa
        script = db.query(models.Script).filter(models.Script.id == task.script_id).first()
        result = executor.execute_script_logic(script, task.run_args)
        
        # 3. Atualiza Job
        job.status = result["status"]
        job.started_at = result["started_at"]
        job.finished_at = result["finished_at"]
        job.stdout = result["stdout"]
        job.stderr = result["stderr"]
        
        # 4. Atualiza a Tarefa Periódica
        task.last_run = datetime.utcnow()
        
        db.commit()
        print(f"[SCHEDULER] Tarefa {task.name} finalizada com status: {job.status}")
        
    except Exception as e:
        print(f"[SCHEDULER] Erro Crítico: {e}")
    finally:
        db.close()

def start():
    """Inicia o Scheduler."""
    if not scheduler.running:
        scheduler.start()
        print("[SYSTEM] Scheduler de Automação Iniciado.")

def refresh_jobs():
    """
    Lê o banco de dados e reagenda tudo.
    Chamado quando o servidor inicia ou quando criamos uma nova tarefa.
    """
    scheduler.remove_all_jobs()
    
    db = database.SessionLocal()
    tasks = db.query(models.PeriodicTask).filter(models.PeriodicTask.is_active == True).all()
    
    for task in tasks:
        scheduler.add_job(
            run_pending_job, 
            'interval', 
            minutes=task.interval_minutes, 
            args=[task.id],
            id=str(task.id),
            replace_existing=True
        )
        print(f"[SCHEDULER] Agendado: {task.name} a cada {task.interval_minutes} min.")
    
    db.close()
