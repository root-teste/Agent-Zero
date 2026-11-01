# core/schemas.py
from pydantic import BaseModel, ConfigDict, Field
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
    
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Projeto (Project) ---
class ProjectBase(BaseModel):
    name: str
    area_id: int

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    tasks: List[Task] = []

    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Área (Area) ---
class AreaBase(BaseModel):
    name: str
    slug: str

class AreaCreate(AreaBase):
    pass

class Area(AreaBase):
    id: int
    projects: List[Project] = []

    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Scripts ---
class ScriptBase(BaseModel):
    name: str
    description: Optional[str] = None
    interpreter: str = "python3"
    content: str
    # Definição de Argumentos (JSON)
    args_schema: Dict[str, Any] = Field(default_factory=dict)
    is_scheduled: bool = False
    schedule_interval: Optional[int] = Field(default=None, ge=1)

class ScriptCreate(ScriptBase):
    pass

class Script(ScriptBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Atualização de Script ---
class ScriptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_scheduled: Optional[bool] = None
    schedule_interval: Optional[int] = Field(default=None, ge=1)

# --- Schemas de Notas (Note) ---
class NoteBase(BaseModel):
    title: str
    content: str
    area_id: int
    project_id: Optional[int] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
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
    
    model_config = ConfigDict(from_attributes=True)
# core/schemas.py

