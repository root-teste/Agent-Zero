from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from . import database, models, scheduler_service
from .config import settings
from .routers import agent, chat, memory, notes, scripts, tasks
from .security import get_api_key

@asynccontextmanager
async def lifespan(app):
    settings.validate()
    models.Base.metadata.create_all(bind=database.engine)
    if settings.SCHEDULER_ENABLED:
        scheduler_service.start_scheduler()
    try:
        yield
    finally:
        scheduler_service.stop_scheduler()

app = FastAPI(title="Agente Zero — núcleo local", version="0.4.0", lifespan=lifespan,
              dependencies=[Depends(get_api_key)], docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(agent.router, prefix="/agent")
app.include_router(tasks.router)
app.include_router(scripts.router)
app.include_router(notes.router)
app.include_router(memory.router)
app.include_router(chat.router)

@app.middleware("http")
async def private_responses(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/health")
def health():
    return {"status": "ok", "script_execution_enabled": settings.EXECUTION_ENABLED}
