from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from .database import SessionLocal
from .models import Job, Script
from .config import settings

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone="UTC")

def check_scheduled_scripts():
    if not settings.EXECUTION_ENABLED:
        return
    with SessionLocal() as db:
        try:
            scripts = db.query(Script).filter(Script.is_scheduled.is_(True), Script.schedule_interval > 0).all()
            for script in scripts:
                active = db.query(Job.id).filter(Job.script_id == script.id, Job.status.in_(["pending", "running"])).first()
                if active:
                    continue
                last = db.query(Job).filter(Job.script_id == script.id).order_by(Job.id.desc()).first()
                now = datetime.utcnow()
                if last and now - (last.finished_at or last.started_at) < timedelta(minutes=script.schedule_interval):
                    continue
                db.add(Job(script_id=script.id, status="pending", run_args={}))
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Falha ao verificar agenda")
            raise

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(check_scheduled_scripts, "interval", seconds=30, id="scheduled-scripts",
                          replace_existing=True, max_instances=1, coalesce=True)
        scheduler.start()

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=True)
