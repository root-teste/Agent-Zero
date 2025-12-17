# core/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

# --- Enums (Espelhados do Model) ---
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# --- Schemas de Tarefa (Task) ---
class TaskBase(BaseModel):
    title: str
    status: TaskStatus = TaskStatus.TODO
    project_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    linked_script_id: Optional[int] = None
    
    class Config:
        from_attributes = True 

# --- Schemas de Projeto (Project) ---
class ProjectBase(BaseModel):
    name: str
    area_id: int

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    tasks: List[Task] = []

    class Config:
        from_attributes = True

# --- Schemas de Área (Area) ---
class AreaBase(BaseModel):
    name: str
    slug: str

class AreaCreate(AreaBase):
    pass

class Area(AreaBase):
    id: int
    projects: List[Project] = []

    class Config:
        from_attributes = True

# --- Schemas de Scripts ---
class ScriptBase(BaseModel):
    name: str
    description: Optional[str] = None
    interpreter: str = "python3"
    content: str
    # Definição de Argumentos (JSON)
    args_schema: Optional[Dict[str, Any]] = {}

class ScriptCreate(ScriptBase):
    pass

class Script(ScriptBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Schemas de Jobs (Execuções) ---
class JobBase(BaseModel):
    script_id: int
    status: str = "pending"
    # Argumentos usados na execução
    run_args: Optional[Dict[str, Any]] = {}

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    
    class Config:
        from_attributes = True
# core/schemas.py

class PeriodicTaskBase(BaseModel):
    name: str
    script_id: int
    interval_minutes: int
    run_args: Optional[dict] = {}
    is_active: bool = True

class PeriodicTaskCreate(PeriodicTaskBase):
    pass

class PeriodicTask(PeriodicTaskBase):
    id: int
    last_run: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# core/schemas.py (Adicione isso no final)

# --- Schemas de Agendamento (PeriodicTask) ---
class PeriodicTaskBase(BaseModel):
    name: str
    script_id: int
    interval_minutes: int = 60
    run_args: Optional[dict] = {}
    is_active: bool = True

class PeriodicTaskCreate(PeriodicTaskBase):
    pass

class PeriodicTask(PeriodicTaskBase):
    id: int
    last_run: Optional[datetime] = None
    
    class Config:
        from_attributes = True
