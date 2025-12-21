from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, database, schemas

router = APIRouter()

# --- Endpoints de Áreas ---

@router.get("/areas/", response_model=List[schemas.Area])
def read_areas(db: Session = Depends(database.get_db)):
    return db.query(models.Area).all()

@router.post("/areas/", response_model=schemas.Area)
def create_area(area: schemas.AreaCreate, db: Session = Depends(database.get_db)):
    db_area = models.Area(name=area.name, slug=area.slug)
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area

# --- Endpoints de Projetos ---

@router.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Project).offset(skip).limit(limit).all()

@router.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    db_project = models.Project(name=project.name, area_id=project.area_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# --- Endpoints de Tarefas ---

@router.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Task).offset(skip).limit(limit).all()

@router.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    db_task = models.Task(title=task.title, project_id=task.project_id, status=task.status)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
