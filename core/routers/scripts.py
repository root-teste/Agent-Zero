from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
from .. import models, database, schemas, executor

router = APIRouter()

# --- Modelos de Request ---
class RunRequest(BaseModel):
    args: Dict[str, Any] = {}

# --- Endpoints de Scripts ---

@router.get("/scripts/", response_model=List[schemas.Script])
def read_scripts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Script).offset(skip).limit(limit).all()

@router.get("/scripts/{script_id}", response_model=schemas.Script)
def read_script_by_id(script_id: int, db: Session = Depends(database.get_db)):
    script = db.query(models.Script).filter(models.Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script não encontrado")
    return script

@router.post("/scripts/", response_model=schemas.Script)
def create_script(script: schemas.ScriptCreate, db: Session = Depends(database.get_db)):
    if db.query(models.Script).filter(models.Script.name == script.name).first():
        raise HTTPException(status_code=400, detail="Script com este nome já existe.")
    
    db_script = models.Script(
        name=script.name,
        description=script.description,
        content=script.content,
        interpreter=script.interpreter,
        args_schema=script.args_schema
    )
    db.add(db_script)
    db.commit()
    db.refresh(db_script)
    return db_script

# --- Endpoint de Execução ---

@router.post("/run/{script_id}", response_model=schemas.Job)
def run_script(script_id: int, run_req: RunRequest = None, db: Session = Depends(database.get_db)):
    args = run_req.args if run_req else {}
    script = db.query(models.Script).filter(models.Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script não encontrado")
    
    job = models.Job(script_id=script.id, status="running", run_args=args)
    db.add(job)
    db.commit()
    
    result_data = executor.execute_script_logic(script, args)
    
    job.status = result_data["status"]
    job.started_at = result_data["started_at"]
    job.finished_at = result_data["finished_at"]
    job.stdout = result_data["stdout"]
    job.stderr = result_data["stderr"]
    
    db.commit()
    db.refresh(job)
    return job
