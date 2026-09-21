#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path.home() / ".local" / "share" / "laya-router"
CONFIG_PATH = BASE / "config.json"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "runtime.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

_agent = None

DEFAULT_CONFIG = {
    "enabled": True,
    "model": "aac6fef/laya-multilingual-mlx",
    "dtype": "float16",
    "device": "gpu",
    "fallback_on_error": True,
    "persist_task_text": False,
}


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    try:
        data = json.loads(CONFIG_PATH.read_text())
        return {**DEFAULT_CONFIG, **data}
    except Exception:
        logging.exception("Failed to load config")
        return DEFAULT_CONFIG.copy()


def get_agent():
    global _agent
    cfg = load_config()
    if not cfg.get("enabled", True):
        raise RuntimeError("laya-router disabled")
    if _agent is None:
        import laya_mlx as laya
        _agent = laya.load(
            cfg["model"],
            dtype=cfg.get("dtype", "float16"),
            device=cfg.get("device", "gpu"),
        )
        logging.info("Loaded Laya model %s", cfg["model"])
    return _agent


def questions() -> dict[str, Any]:
    return {
        "task_type": {
            "type": "choice",
            "instructions": "Classify the primary software-engineering task type.",
            "criteria": {
                "simple": "tiny edit, wording change, formatting, trivial maintenance",
                "coding": "normal code implementation or refactor",
                "debugging": "investigating or fixing a defect",
                "architecture": "system design, large refactor, interfaces, architecture",
                "frontend": "UI, browser, desktop frontend, styling, interaction",
                "backend": "server, API, database, queue, backend logic",
                "devops": "build, deployment, CI, infrastructure, operating system",
                "security": "security review, auth, permissions, secrets, exposure",
                "research": "investigation, comparison, documentation research",
                "documentation": "documentation-only work",
                "other": "none of the above",
            },
        },
        "complexity": {
            "type": "score",
            "instructions": "Estimate overall task complexity.",
            "criteria": ["trivial", "normal", "complex", "very_complex"],
        },
        "needs_strong_reasoning": {
            "type": "noul",
            "instructions": "Would this task benefit materially from stronger multi-step reasoning?",
        },
        "needs_tools": {
            "type": "noul",
            "instructions": "Will this task likely require file, shell, git, web, MCP, or other tools?",
        },
        "security_sensitive": {
            "type": "noul",
            "instructions": "Does this task involve security, permissions, credentials, network exposure, destructive commands, or other sensitive system changes?",
        },
        "risk": {
            "type": "choice",
            "instructions": "Estimate execution risk if a coding agent acts on this task.",
            "criteria": {
                "low": "ordinary reversible development work",
                "medium": "meaningful changes requiring review or care",
                "high": "destructive, privileged, credential, security, production, or hard-to-reverse changes",
            },
        },
    }


def decide(task: str) -> dict[str, Any]:
    cfg = load_config()
    if not cfg.get("enabled", True):
        return {"status": "disabled", "advisory": True}
    try:
        agent = get_agent()
        result = agent.predict(task, questions())
        return {
            "status": "ok",
            "advisory": True,
            "answers": result.get("answers", {}),
            "action": result.get("action"),
            "usage": result.get("usage"),
        }
    except Exception as exc:
        logging.exception("Laya decision failed")
        if cfg.get("fallback_on_error", True):
            return {
                "status": "unavailable",
                "advisory": True,
                "fail_open": True,
                "error": str(exc),
            }
        raise


def run_cli() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    args = parser.parse_args()
    print(json.dumps(decide(args.task), ensure_ascii=False))
    return 0


def run_mcp() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        print(f"MCP runtime unavailable: {exc}", file=sys.stderr)
        return 2

    mcp = FastMCP("laya-router")

    @mcp.tool()
    def laya_decide(task: str) -> dict[str, Any]:
        """Classify and score a coding-agent task using local Laya-MLX. Advisory only."""
        return decide(task)

    @mcp.tool()
    def laya_health() -> dict[str, Any]:
        """Return Laya router configuration and model-load health."""
        cfg = load_config()
        try:
            get_agent()
            return {"status": "ok", "model": cfg["model"], "device": cfg["device"]}
        except Exception as exc:
            return {"status": "unavailable", "fail_open": True, "error": str(exc)}

    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    if "--mcp" in sys.argv:
        sys.argv.remove("--mcp")
        raise SystemExit(run_mcp())
    raise SystemExit(run_cli())
