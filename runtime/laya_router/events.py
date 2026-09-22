"""Minimal, prompt-free evidence for agent integration checks."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

from .config import DATA_DIR

EVENT_LOG = DATA_DIR / "logs" / "events.jsonl"


def record_call(task: str, result: dict, *, source: str, tool: str, duration_ms: int) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "tool": tool,
        "backend": result.get("backend"),
        "runtime": result.get("runtime"),
        "status": result.get("status"),
        "duration_ms": duration_ms,
        "task_hash": "sha256:" + hashlib.sha256(task.encode("utf-8")).hexdigest(),
    }
    try:
        EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(EVENT_LOG, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        # Observability must not prevent an advisory decision or fail-open result.
        pass
