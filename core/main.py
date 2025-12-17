# core/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from . import models, database, schemas, executor
from . import scheduler_service 

# 1. Cria as tabelas
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Sistema Pessoal Core", version="0.3.0")

@app.on_event("startup")
def startup_event():
    # Inicia o relógio
    try:
        scheduler_service.start()
        scheduler_service.refresh_jobs()
    except Exception as e:
        print(f"Erro ao iniciar Scheduler: {e}")

# --- Modelos de Request ---
class RunRequest(BaseModel):
    args: Dict[str, Any] = {}

# --- Endpoints de Leitura ---

@app.get("/areas/", response_model=List[schemas.Area])
def read_areas(db: Session = Depends(database.get_db)):
    return db.query(models.Area).all()

@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    # CORRIGIDO AQUI (era "ós criadef")
    return db.query(models.Project).offset(skip).limit(limit).all()

@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Task).offset(skip).limit(limit).all()

@app.get("/scripts/", response_model=List[schemas.Script])
def read_scripts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Script).offset(skip).limit(limit).all()

@app.get("/scripts/{script_id}", response_model=schemas.Script)
def read_script_by_id(script_id: int, db: Session = Depends(database.get_db)):
    script = db.query(models.Script).filter(models.Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script não encontrado")
    return script

# --- Endpoints de Escrita ---

@app.post("/areas/", response_model=schemas.Area)
def create_area(area: schemas.AreaCreate, db: Session = Depends(database.get_db)):
    db_area = models.Area(name=area.name, slug=area.slug)
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area

@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    db_project = models.Project(name=project.name, area_id=project.area_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    db_task = models.Task(title=task.title, project_id=task.project_id, status=task.status)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.post("/scripts/", response_model=schemas.Script)
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

@app.post("/run/{script_id}", response_model=schemas.Job)
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

# --- Agendamento ---

@app.post("/schedule/", response_model=schemas.PeriodicTask)
def create_schedule(task: schemas.PeriodicTaskCreate, db: Session = Depends(database.get_db)):
    db_task = models.PeriodicTask(
        name=task.name,
        script_id=task.script_id,
        interval_minutes=task.interval_minutes,
        run_args=task.run_args
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    scheduler_service.refresh_jobs()
    return db_task

@app.get("/schedule/", response_model=List[schemas.PeriodicTask])
def list_schedules(db: Session = Depends(database.get_db)):
    return db.query(models.PeriodicTask).all()

# --- Setup ---
@app.post("/setup-inicial/")
def setup_inicial(db: Session = Depends(database.get_db)):
    if db.query(models.Area).first():
        return {"message": "Setup já realizado."}
    area = models.Area(name="Tecnologia", slug="tech")
    db.add(area)
    db.commit()
    db.refresh(area)
    proj = models.Project(name="Sistema Pessoal", area_id=area.id)
    db.add(proj)
    db.commit()
    return {"message": "Setup concluído!", "area": area.name}
