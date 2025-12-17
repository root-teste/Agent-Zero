from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, database, schemas

router = APIRouter()

# --- Endpoint para buscar Job pendente ---
@router.get("/jobs/pending")
def get_pending_job(db: Session = Depends(database.get_db)):
    job = db.query(models.Job).filter(models.Job.status == "pending").order_by(models.Job.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Nenhum Job pendente encontrado")
    
    script = db.query(models.Script).filter(models.Script.id == job.script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script associado não encontrado")
    
    return {
        "job_id": job.id,
        "script_content": script.content,
        "run_args": job.run_args or {}
    }

# --- Endpoint para atualizar Job ---
@router.post("/jobs/{job_id}/report")
def report_job_status(job_id: int, report: schemas.Job, db: Session = Depends(database.get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job.status = report.status
    job.stdout = report.stdout
    job.stderr = report.stderr
    job.finished_at = report.finished_at
    
    db.commit()
    db.refresh(job)
    return job
