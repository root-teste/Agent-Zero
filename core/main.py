# core/main.py
from fastapi import FastAPI, Depends
from core.security import get_api_key
from . import models, database, scheduler_service
from core.scheduler_service import start_scheduler
from .routers import scripts, tasks, agent

# 1. Cria as tabelas
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Sistema Pessoal Core", version="0.3.0", dependencies=[Depends(get_api_key)])

app.include_router(agent.router, prefix='/agent')

@app.on_event("startup")
def startup_event():
    # Inicia o relógio
    try:
        scheduler_service.start()
        scheduler_service.refresh_jobs()
        scheduler_service.start_scheduler()
    except Exception as e:
        print(f"Erro ao iniciar Scheduler: {e}")

# Inclui os routers
app.include_router(tasks.router)
app.include_router(scripts.router)
