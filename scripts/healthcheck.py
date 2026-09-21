#!/usr/bin/env python3
"""Lightweight health check; never downloads model weights."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from laya_router import __version__
from laya_router.config import CONFIG_PATH, load_config
from laya_router.router import RouterCore
from install import data_dir, python_in_venv, skill_paths


def inspect() -> dict:
    base = data_dir()
    cfg = load_config()
    info = RouterCore(config=cfg).info()
    runtime = info.get("runtime")
    package = "laya_mlx" if runtime == "laya-mlx" else "laya"
    agents = {name: {"detected": bool(shutil.which(name)), "skill": path.exists()} for name, path in skill_paths().items()}
    hub = Path(os.environ.get("HF_HUB_CACHE", Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"))
    cached = bool(list(hub.glob("models--aac6fef--laya*")) + list(hub.glob("models--convaiinnovations--laya*"))) if hub.exists() else False
    codex_mcp = "SKIP"
    if shutil.which("codex"):
        try:
            codex_mcp = "OK" if subprocess.run(["codex", "mcp", "get", "laya-router"], capture_output=True, timeout=5).returncode == 0 else "ABSENT"
        except (OSError, subprocess.TimeoutExpired):
            codex_mcp = "UNAVAILABLE"
    return {"version": __version__, "platform": info.get("platform"), "python": sys.version.split()[0],
            "backend": info.get("backend"), "runtime": runtime, "runtime_package": importlib.util.find_spec(package) is not None,
            "torch": importlib.util.find_spec("torch") is not None, "mlx": importlib.util.find_spec("mlx") is not None,
            "device": info.get("device"), "model_cache": "present (unverified)" if cached else "absent", "config": str(CONFIG_PATH),
            "config_exists": CONFIG_PATH.exists(), "venv": (base / ".venv").exists(), "agents": agents,
            "mcp_adapter": importlib.util.find_spec("mcp") is not None, "codex_mcp": codex_mcp,
            "status": "READY" if info.get("status") == "ready" else "UNAVAILABLE", "fail_open": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--lightweight", action="store_true")
    args = parser.parse_args(argv)
    private_python = python_in_venv(data_dir() / ".venv")
    if private_python.exists() and Path(sys.executable).resolve() != private_python.resolve():
        os.execv(str(private_python), [str(private_python), str(Path(__file__).resolve()), *(argv if argv is not None else sys.argv[1:])])
    result = inspect()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Laya Router Health")
        for key, value in result.items():
            if key != "agents":
                print(f"{key:18} {value}")
        for name, detail in result["agents"].items():
            print(f"{name:18} {'SKIP' if not detail['detected'] else 'OK' if detail['skill'] else 'WARN'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
