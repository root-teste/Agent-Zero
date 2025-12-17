from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any, List
from pydantic import BaseModel
from .. import models, database, schemas

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

# --- Endpoint de Atualização de Script ---
@router.patch("/scripts/{script_id}", response_model=schemas.Script)
def update_script(script_id: int, script_update: schemas.ScriptUpdate, db: Session = Depends(database.get_db)):
    script = db.query(models.Script).filter(models.Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script não encontrado")
    
    for key, value in script_update.dict(exclude_unset=True).items():
        setattr(script, key, value)
    
    db.commit()
    db.refresh(script)
    return script

# --- Endpoint para listar Jobs ---

@router.get("/jobs", response_model=List[schemas.Job])
def list_jobs(limit: int = 50, db: Session = Depends(database.get_db)):
    return db.query(models.Job).order_by(desc(models.Job.id)).limit(limit).all()

# --- Endpoint de Execução ---

@router.post("/run/{script_id}", response_model=schemas.Job)
def run_script(script_id: int, run_req: RunRequest = None, db: Session = Depends(database.get_db)):
    args = run_req.args if run_req else {}
    script = db.query(models.Script).filter(models.Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script não encontrado")
    
    job = models.Job(script_id=script.id, status="pending", run_args=args)
    db.add(job)
    db.commit()
    
    db.commit()
    db.refresh(job)
    return job
