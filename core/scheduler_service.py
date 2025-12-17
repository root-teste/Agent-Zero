# core/scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime
from . import database, models
from datetime import datetime

def check_schedules(db: Session):
    """
    Verifica scripts com automação ativa e cria jobs para eles.
    """
    scripts = db.query(models.Script).filter(models.Script.is_active_automation == True).all()
    for script in scripts:
        print(f"[SCHEDULER] Criando job para script automatizado: {script.name}")
        job = models.Job(script_id=script.id, status="pending", run_args={})
        db.add(job)
    db.commit()

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
        print('Agendamento: Job criado na fila (Lógica de execução remota pendente)')
        
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
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: print("Scheduler Ativo"), 'interval', minutes=1)
    scheduler.add_job(lambda: check_schedules(database.SessionLocal()), 'interval', seconds=60)
    scheduler.start()
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import SessionLocal
from .models import Script, Job

def check_scheduled_scripts():
    """
    Verifica scripts agendados e cria jobs se necessário.
    """
    db = SessionLocal()
    try:
        scripts = db.query(Script).filter(Script.is_scheduled == True, Script.schedule_interval > 0).all()
        for script in scripts:
            last_job = db.query(Job).filter(Job.script_id == script.id).order_by(Job.finished_at.desc()).first()
            now = datetime.utcnow()
            if not last_job or (now - last_job.finished_at) > timedelta(minutes=script.schedule_interval):
                print(f"[SCHEDULER] Criando job para script agendado: {script.name}")
                new_job = Job(script_id=script.id, status="pending", run_args={})
                db.add(new_job)
        db.commit()
    finally:
        db.close()

# Instância global do scheduler
scheduler = BackgroundScheduler()

def start_scheduler():
    """Inicia o Scheduler."""
    scheduler.add_job(check_scheduled_scripts, 'interval', seconds=60)
    scheduler.start()
    print("[SYSTEM] Scheduler de Automação Iniciado.")
