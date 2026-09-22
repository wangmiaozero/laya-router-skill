import json

from laya_router import events


def test_call_log_has_evidence_without_prompt(tmp_path, monkeypatch):
    path = tmp_path / "events.jsonl"
    monkeypatch.setattr(events, "EVENT_LOG", path)
    task = "private credential token"
    events.record_call(task, {"status": "ok", "backend": "mlx", "runtime": "laya-mlx"},
                       source="mcp", tool="laya_decide", duration_ms=12)
    raw = path.read_text(encoding="utf-8")
    event = json.loads(raw)
    assert task not in raw
    assert set(event) == {"timestamp", "source", "tool", "backend", "runtime", "status", "duration_ms", "task_hash"}
    assert event["source"] == "mcp" and event["status"] == "ok"
    assert event["task_hash"].startswith("sha256:")


def test_call_log_failure_does_not_raise(tmp_path, monkeypatch):
    monkeypatch.setattr(events, "EVENT_LOG", tmp_path / "missing" / "events.jsonl")
    monkeypatch.setattr(events.os, "open", lambda *args, **kwargs: (_ for _ in ()).throw(PermissionError()))
    events.record_call("task", {"status": "unavailable"}, source="cli", tool="laya_decide", duration_ms=1)
