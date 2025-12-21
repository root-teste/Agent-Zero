# core/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

# --- Enums para Padronização ---
class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class ScriptInterpreter(str, enum.Enum):
    PYTHON = "python3"
    BASH = "bash"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

# --- Modelos de Organização ---

class Area(Base):
    __tablename__ = "areas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True)
    
    projects = relationship("Project", back_populates="area")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    area = relationship("Area", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    status = Column(String, default=TaskStatus.TODO)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Link com Automação
    linked_script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True)
    
    project = relationship("Project", back_populates="tasks")
    script = relationship("Script")

# --- Modelos de Execução (Engine) ---

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False) # O código fonte
    interpreter = Column(String, default=ScriptInterpreter.PYTHON)
    
    # Definição de Argumentos (JSON)
    args_schema = Column(JSON, default={})
    cron_schedule = Column(String, nullable=True)
    is_active_automation = Column(Boolean, default=False)
    is_scheduled = Column(Boolean, default=False)
    schedule_interval = Column(Integer, nullable=True)
    
    jobs = relationship("Job", back_populates="script")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"))
    
    # CORREÇÃO AQUI: run_args recebe (=) a coluna, não subtrai (-)
    run_args = Column(JSON, default={})
    
    status = Column(String, default=JobStatus.PENDING)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    
    # Logs de execução
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    
    script = relationship("Script", back_populates="jobs")
# core/models.py


