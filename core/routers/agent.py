from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from jsonschema import Draft202012Validator, SchemaError, ValidationError
from .. import database, models, schemas
from ..security import require_script_execution

router = APIRouter(dependencies=[Depends(require_script_execution)])

class JobReport(BaseModel):
    status: Literal["success", "failed", "timeout"]
    stdout: str = Field(default="", max_length=100_000)
    stderr: str = Field(default="", max_length=100_000)
    finished_at: datetime

@router.post("/jobs/claim")
def claim_job(db: Session = Depends(database.get_db)):
    """Reserva atómica; interrupções exigem reconciliação manual nesta versão."""
    candidate = select(models.Job.id).where(models.Job.status == "pending").order_by(models.Job.id).limit(1).scalar_subquery()
    statement = update(models.Job).where(models.Job.id == candidate, models.Job.status == "pending").values(
        status="running", started_at=datetime.utcnow()).returning(models.Job.id)
    job_id = db.execute(statement).scalar_one_or_none()
    db.commit()
    if job_id is None:
        raise HTTPException(404, "Nenhum trabalho pendente")
    job = db.get(models.Job, job_id)
    script = db.get(models.Script, job.script_id)
    valid = script is not None and script.interpreter == "python3"
    if valid:
        try:
            Draft202012Validator.check_schema(script.args_schema or {})
            Draft202012Validator(script.args_schema or {}).validate(job.run_args or {})
        except (SchemaError, ValidationError):
            valid = False
    if not valid:
        job.status = "failed"
        job.stderr = "Script ausente, interpretador ou argumentos incompatíveis"
        job.finished_at = datetime.utcnow()
        db.commit()
        raise HTTPException(409, "Trabalho incompatível; marcado como falhado")
    return {"job_id": job.id, "script_content": script.content, "run_args": job.run_args or {}}

@router.post("/jobs/{job_id}/report", response_model=schemas.Job)
def report_job_status(job_id: int, report: JobReport, db: Session = Depends(database.get_db)):
    job = db.get(models.Job, job_id)
    if job is None:
        raise HTTPException(404, "Trabalho não encontrado")
    if job.status == report.status and job.stdout == report.stdout and job.stderr == report.stderr:
        return job
    if job.status != "running":
        raise HTTPException(409, "O trabalho não está em execução")
    job.status = report.status
    job.stdout = report.stdout
    job.stderr = report.stderr
    job.finished_at = report.finished_at
    db.commit()
    db.refresh(job)
    return job
