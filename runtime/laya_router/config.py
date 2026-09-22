from __future__ import annotations

import json
import logging
from pathlib import Path

try:
    from platformdirs import user_data_dir
except ImportError:  # source-checkout diagnostics before installing dependencies
    def user_data_dir(appname: str, appauthor: str) -> str:
        import os
        import sys
        if sys.platform == "darwin":
            return str(Path.home() / "Library" / "Application Support" / appname)
        if os.name == "nt":
            return str(Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / appauthor / appname)
        return str(Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / appname)

DEFAULT_CONFIG = {
    "enabled": True,
    "backend": "auto",
    "model": "auto",
    "language": "auto",
    "device": "auto",
    "fallback_on_error": True,
    "persist_task_text": False,
    "log_level": "INFO",
}
DATA_DIR = Path(user_data_dir("laya-router", "laya-router"))
CONFIG_PATH = DATA_DIR / "config.json"


def load_config(path: Path | None = None) -> dict:
    path = path or CONFIG_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        if not isinstance(data, dict):
            raise ValueError("config must be a JSON object")
        result = {**DEFAULT_CONFIG, **{key: value for key, value in data.items() if key in DEFAULT_CONFIG}}
        if result["backend"] not in {"auto", "mlx", "torch"} or result["model"] not in {"auto", "english", "multilingual", "typed-decisions"} or result["language"] not in {"auto", "en", "multilingual"} or result["device"] not in {"auto", "cpu", "cuda", "mps", "gpu"}:
            raise ValueError("invalid backend, model, language, or device")
        for key in ("enabled", "fallback_on_error", "persist_task_text"):
            if not isinstance(result[key], bool):
                raise ValueError(f"{key} must be boolean")
        return result
    except (OSError, ValueError, TypeError) as exc:
        logging.warning("Invalid router config; defaults used: %s", type(exc).__name__)
        return DEFAULT_CONFIG.copy()
