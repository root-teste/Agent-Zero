import os
import tempfile
from pathlib import Path

# Configuração antes do import do núcleo: nunca abrir o banco do utilizador.
TEMP = tempfile.TemporaryDirectory(prefix="agent-zero-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{(Path(TEMP.name) / 'test.db').as_posix()}"
os.environ["SYSTEM_API_KEY"] = "test-only-" + "a" * 40
os.environ["AGENT_ZERO_ENABLE_SCHEDULER"] = "false"
os.environ["AGENT_ZERO_ENABLE_SCRIPT_EXECUTION"] = "false"

import pytest
from fastapi.testclient import TestClient
from core.main import app
from core import database, models
from core.config import settings


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "EXECUTION_ENABLED", False)
    monkeypatch.setattr(settings, "SCHEDULER_ENABLED", False)
    models.Base.metadata.drop_all(database.engine)
    with TestClient(app) as client:
        client.headers["x-api-key"] = settings.API_KEY
        yield client


def pytest_sessionfinish(session, exitstatus):
    database.engine.dispose()
    TEMP.cleanup()
