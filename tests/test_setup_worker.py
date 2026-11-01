from unittest.mock import Mock, patch

import pytest


def test_setup_never_overwrites_configuration(tmp_path, monkeypatch):
    from core import setup
    monkeypatch.setattr(setup, "ROOT", tmp_path)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "data"))
    monkeypatch.setattr("sys.argv", ["setup"])
    setup.main()
    before = (tmp_path / ".env").read_bytes()
    assert b"AGENT_ZERO_ENABLE_SCRIPT_EXECUTION=false" in before
    with pytest.raises(SystemExit):
        setup.main()
    assert (tmp_path / ".env").read_bytes() == before


def test_worker_retries_report_without_rerunning_script():
    from agent import daemon
    claim = Mock(status_code=200)
    claim.json.return_value = {"job_id": 123, "script_content": "pass", "run_args": {}}
    report = Mock(status_code=200)
    error = daemon.requests.exceptions.ConnectionError("synthetic")
    result = {"status": "success", "stdout": "ok", "stderr": ""}
    with patch.object(daemon.requests, "post", side_effect=[claim, error, report]) as post, \
         patch.object(daemon, "execute_script_logic", return_value=result) as execute, \
         patch.object(daemon.time, "sleep"):
        assert daemon.run_once()
        assert execute.call_count == 1
        assert post.call_count == 3


def test_worker_refuses_disabled_execution(monkeypatch):
    from agent import daemon
    monkeypatch.setattr(daemon.settings, "EXECUTION_ENABLED", False)
    with patch.object(daemon, "run_once", side_effect=AssertionError("must not run")):
        with pytest.raises(RuntimeError):
            daemon.run_worker()


def test_core_credential_never_follows_other_origin():
    from core import http_client
    with patch("core.http_client._requests.request", side_effect=AssertionError("must not send")):
        with pytest.raises(ValueError):
            http_client.get("https://external.example/private")
