import sqlite3

import pytest

from core.config import settings


@pytest.fixture
def brain(tmp_path, monkeypatch):
    (tmp_path / "90-Config").mkdir()
    with sqlite3.connect(tmp_path / "90-Config/memoria.sqlite") as db:
        db.execute("CREATE VIRTUAL TABLE memory USING fts5(title,body,source UNINDEXED,path UNINDEXED,ref UNINDEXED)")
        db.execute("INSERT INTO memory VALUES (?,?,?,?,?)", ("Synthetic", "private marker test", "test", "note.md", "record-1"))
        db.execute("INSERT INTO memory VALUES (?,?,?,?,?)", ("Outside", "private marker test", "test", "../outside.md", ""))
    monkeypatch.setattr(settings, "SECOND_BRAIN_ROOT", str(tmp_path))
    return tmp_path


def test_read_only_private_search(client, brain, monkeypatch):
    from unittest.mock import patch
    index = brain / "90-Config/memoria.sqlite"
    before = index.read_bytes()
    with patch("requests.request", side_effect=AssertionError("Network forbidden")):
        response = client.post("/memory/search", json={"query": "private marker"})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["external_delegation"] is False
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["classification"] == "private"
    assert response.json()["results"][0]["path"] == "note.md"
    assert index.read_bytes() == before


def test_search_requires_configuration(client, monkeypatch):
    monkeypatch.setattr(settings, "SECOND_BRAIN_ROOT", None)
    assert client.post("/memory/search", json={"query": "marker"}).status_code == 503


def test_search_limits_and_literal_fts_input(client, brain):
    assert client.post("/memory/search", json={"query": "marker", "limit": 1000}).status_code == 422
    assert client.post("/memory/search", json={"query": "* OR ("}).status_code == 200
    assert client.post("/memory/search", json={"query": "!"}).json()["results"] == []
