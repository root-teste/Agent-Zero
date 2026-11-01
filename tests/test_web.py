from pathlib import Path
from streamlit.testing.v1 import AppTest

from core import http_client


def test_web_renders_and_searches_memory(client, tmp_path, monkeypatch):
    import sqlite3
    from core.config import settings
    (tmp_path / "90-Config").mkdir()
    db = sqlite3.connect(tmp_path / "90-Config/memoria.sqlite")
    db.execute("CREATE VIRTUAL TABLE memory USING fts5(title,body,source UNINDEXED,path UNINDEXED,ref UNINDEXED)")
    db.execute("INSERT INTO memory VALUES ('Synthetic source','synthetic marker','test','note.md','r1')")
    db.commit()
    db.close()
    monkeypatch.setattr(settings, "SECOND_BRAIN_ROOT", str(tmp_path))
    def local_request(method, url, **kwargs):
        from urllib.parse import urlsplit
        return client.request(method, urlsplit(url).path, **kwargs)
    monkeypatch.setattr(http_client, "request", local_request)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "web/app.py"), default_timeout=15).run()
    assert not app.exception
    assert len(app.tabs) == 6
    app.text_input(key="memory_query").set_value("synthetic marker")
    app.button(key="memory_submit").click().run()
    assert not app.exception
    assert any(item.value == "Synthetic source" for item in app.subheader)


def test_models_are_disabled_without_network(monkeypatch):
    from unittest.mock import patch
    from ai_clients.ollama_bridge import generate_response
    from core.config import settings
    monkeypatch.setattr(settings, "LOCAL_MODEL_ENABLED", False)
    with patch("requests.post", side_effect=AssertionError("No model network")):
        assert "desativado" in generate_response("private synthetic marker")
