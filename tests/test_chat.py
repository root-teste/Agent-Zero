from core import local_model
from core.config import settings


def test_conversation_persists_and_failure_does_not_add_turn(client, monkeypatch):
    cid = client.post("/chat/conversations", json={"title": "Teste"}).json()["id"]
    monkeypatch.setattr(local_model, "chat", lambda messages: ("Resposta de teste", "modelo-teste"))
    response = client.post(f"/chat/conversations/{cid}/messages", json={"content": "Olá"})
    assert response.status_code == 200
    assert response.json()["model"] == "modelo-teste"
    def fail(messages):
        raise local_model.ModelUnavailable("Indisponível")
    monkeypatch.setattr(local_model, "chat", fail)
    assert client.post(f"/chat/conversations/{cid}/messages", json={"content": "Repetir"}).status_code == 503
    history = client.get(f"/chat/conversations/{cid}").json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[0]["content"] == "Olá"


def test_private_model_rejects_remote_before_network(monkeypatch):
    monkeypatch.setattr(settings, "LOCAL_MODEL_ENABLED", True)
    monkeypatch.setattr(settings, "OLLAMA_URL", "https://example.com")
    import pytest
    with pytest.raises(local_model.ModelUnavailable, match="loopback"):
        local_model.chat([])


def test_missing_conversation_and_auth(client):
    assert client.get("/chat/conversations/999").status_code == 404
    client.headers.clear()
    assert client.get("/chat/conversations").status_code in (401, 403, 422)
