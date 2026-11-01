from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from core import database, models, scheduler_service
from core.config import settings
from core.main import app
from core.routers.agent import claim_job


def script(client, **extra):
    response = client.post("/scripts/", json={"name": "example", "content": "print('synthetic')", **extra})
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_tasks_and_notes_persist_after_lifespan(client):
    assert client.post("/tasks/", json={"title": "Synthetic task"}).status_code == 200
    assert client.get("/tasks/").json()[0]["title"] == "Synthetic task"
    area = client.post("/areas/", json={"name": "Test", "slug": "test"}).json()
    note = client.post("/notes/", json={"title": "Private synthetic note", "content": "marker", "area_id": area["id"]})
    assert note.status_code == 200
    with TestClient(app) as restarted:
        assert restarted.get("/notes/", headers={"x-api-key": settings.API_KEY}).json()[0]["content"] == "marker"


def test_auth_and_no_public_docs(client):
    assert client.get("/health").json()["status"] == "ok"
    with TestClient(app) as anonymous:
        assert anonymous.get("/tasks/").status_code == 401
        assert anonymous.get("/health").status_code == 401
        assert anonymous.get("/docs").status_code == 404
    assert client.get("/tasks/", headers={"x-api-key": "wrong"}).status_code == 401


def test_execution_disabled_by_default(client):
    sid = script(client)
    assert client.post(f"/run/{sid}").status_code == 403
    assert client.post("/agent/jobs/claim").status_code == 403
    assert client.get("/jobs").json() == []


def test_claim_is_atomic_between_workers(client, monkeypatch):
    monkeypatch.setattr(settings, "EXECUTION_ENABLED", True)
    sid = script(client)
    job = client.post(f"/run/{sid}").json()
    def claim(_):
        with database.SessionLocal() as db:
            try:
                return claim_job(db)["job_id"]
            except HTTPException as exc:
                return exc.status_code
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(claim, range(8)))
    assert results.count(job["id"]) == 1
    assert results.count(404) == 7
    assert client.get("/jobs").json()[0]["status"] == "running"
    assert client.get("/agent/jobs/pending").status_code == 404


def test_reports_validate_transition_and_retry(client, monkeypatch):
    monkeypatch.setattr(settings, "EXECUTION_ENABLED", True)
    sid = script(client)
    job = client.post(f"/run/{sid}").json()
    url = f"/agent/jobs/{job['id']}/report"
    payload = {"status": "success", "stdout": "ok", "finished_at": datetime.now().isoformat()}
    assert client.post(url, json=payload).status_code == 409
    client.post("/agent/jobs/claim")
    assert client.post(url, json={**payload, "status": "anything"}).status_code == 422
    assert client.post(url, json=payload).status_code == 200
    assert client.post(url, json=payload).status_code == 200
    assert client.post(url, json={**payload, "stdout": "changed"}).status_code == 409


def test_scheduler_does_not_duplicate_pending_or_running(client, monkeypatch):
    monkeypatch.setattr(settings, "EXECUTION_ENABLED", True)
    script(client, is_scheduled=True, schedule_interval=1)
    scheduler_service.check_scheduled_scripts()
    scheduler_service.check_scheduled_scripts()
    assert len(client.get("/jobs").json()) == 1
    client.post("/agent/jobs/claim")
    scheduler_service.check_scheduled_scripts()
    assert len(client.get("/jobs").json()) == 1


def test_scheduler_disabled_execution_never_enqueues(client):
    script(client, is_scheduled=True, schedule_interval=1)
    scheduler_service.check_scheduled_scripts()
    assert client.get("/jobs").json() == []


def test_scheduler_lifecycle(client, monkeypatch):
    monkeypatch.setattr(settings, "SCHEDULER_ENABLED", True)
    with TestClient(app):
        assert scheduler_service.scheduler.running
    assert not scheduler_service.scheduler.running


@pytest.mark.parametrize("payload", [{"is_scheduled": True}, {"schedule_interval": 0}, {"is_scheduled": None}, {"name": None}])
def test_invalid_schedule_updates(client, payload):
    sid = script(client)
    assert client.patch(f"/scripts/{sid}", json=payload).status_code == 422


def test_argument_schema_and_interpreter(client, monkeypatch):
    monkeypatch.setattr(settings, "EXECUTION_ENABLED", True)
    sid = script(client, args_schema={"type": "object", "required": ["count"], "properties": {"count": {"type": "integer"}}, "additionalProperties": False})
    assert client.post(f"/run/{sid}", json={"args": {"count": "bad"}}).status_code == 422
    assert client.post(f"/run/{sid}", json={"args": {"count": 2}}).status_code == 200


def test_missing_key_fails_startup(client, monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "")
    with pytest.raises(RuntimeError):
        with TestClient(app):
            pass


def test_claim_revalidates_scheduled_arguments(client, monkeypatch):
    monkeypatch.setattr(settings, "EXECUTION_ENABLED", True)
    sid = script(client, args_schema={"type": "object", "required": ["target"]}, is_scheduled=True, schedule_interval=1)
    scheduler_service.check_scheduled_scripts()
    assert client.post("/agent/jobs/claim").status_code == 409
    assert client.get("/jobs").json()[0]["status"] == "failed"


def test_http_client_no_redirect_no_unbounded_wait(monkeypatch):
    from core import http_client
    with patch("core.http_client._requests.request") as request:
        http_client.get("http://127.0.0.1:8000/health")
        options = request.call_args.kwargs
        assert options["timeout"] == 15
        assert options["headers"]["x-api-key"] == settings.API_KEY
        assert options["allow_redirects"] is False
