# core/scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from .database import SessionLocal
from .models import Script, Job

def check_scheduled_scripts():
    """Verifica scripts agendados e cria jobs pendentes se necessário."""
    db = SessionLocal()
    try:
        # Busca scripts ativos para agendamento
        scripts = db.query(Script).filter(
            Script.is_scheduled == True, 
            Script.schedule_interval > 0
        ).all()
        
        for script in scripts:
            # Busca o último job finalizado deste script
            last_job = db.query(Job).filter(
                Job.script_id == script.id,
                Job.status != "pending"
            ).order_by(Job.id.desc()).first()
            
            now = datetime.utcnow()
            should_run = False
            
            if not last_job:
                should_run = True
            else:
                # Se o tempo desde a última execução for maior que o intervalo
                diff = now - (last_job.finished_at or last_job.started_at)
                if diff > timedelta(minutes=script.schedule_interval):
                    should_run = True
            
            if should_run:
                print(f"[SCHEDULER] Enfileirando Job para: {script.name}")
                new_job = Job(script_id=script.id, status="pending", run_args={})
                db.add(new_job)
        
        db.commit()
    except Exception as e:
        print(f"[SCHEDULER] Erro: {e}")
    finally:
        db.close()

scheduler = BackgroundScheduler()

def start_scheduler():
    """Inicia o relógio do sistema."""
    if not scheduler.running:
        # Roda a cada 30 segundos para precisão
        scheduler.add_job(check_scheduled_scripts, 'interval', seconds=30)
        scheduler.start()
        print("[SYSTEM] Scheduler iniciado com sucesso.")
