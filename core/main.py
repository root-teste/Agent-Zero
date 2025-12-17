# core/main.py
from fastapi import FastAPI
from . import models, database, scheduler_service
from .routers import scripts, tasks, agent
app.include_router(agent.router, prefix='/agent')

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

# Inclui os routers
app.include_router(tasks.router)
app.include_router(scripts.router)
