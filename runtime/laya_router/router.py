from __future__ import annotations

import logging
from typing import Any

from .backends.mlx import MLXBackend
from .backends.torch import TorchBackend
from .config import load_config
from .platform import preferred_backend, system_info, validate_backend

QUESTIONS: dict[str, Any] = {
    "task_type": {"type": "choice", "instructions": "Classify the primary software engineering task.", "criteria": {
        "simple": "tiny edit or formatting", "coding": "implementation or refactor", "debugging": "investigate a defect",
        "architecture": "system design", "frontend": "UI or interaction", "backend": "API or database",
        "devops": "build, deployment or infrastructure", "security": "security or authentication",
        "research": "investigation or comparison", "documentation": "documentation", "testing": "tests or quality assurance",
        "data": "data analysis or pipelines", "ai": "machine learning or AI", "other": "none of these"}},
    "complexity": {"type": "score", "instructions": "Estimate task complexity.", "criteria": ["trivial", "normal", "complex", "very_complex"]},
    "needs_strong_reasoning": {"type": "noul", "instructions": "Would this task benefit from stronger multi-step reasoning?"},
    "needs_tools": {"type": "noul", "instructions": "Will this task likely require tools?"},
    "security_sensitive": {"type": "noul", "instructions": "Does this task involve security, credentials, permissions, or destructive changes?"},
    "risk": {"type": "choice", "instructions": "Estimate execution risk, advisory only.", "criteria": {
        "low": "ordinary reversible work", "medium": "meaningful change requiring review", "high": "destructive, privileged, credential or production change"}},
}


class RouterCore:
    def __init__(self, config: dict | None = None, info: dict | None = None, factories: dict | None = None):
        self.config = config if config is not None else load_config()
        self.platform = info if info is not None else system_info()
        self.factories = factories if factories is not None else {"mlx": MLXBackend, "torch": TorchBackend}
        self._instances: dict[str, Any] = {}
        self._active_backend: str | None = None

    def candidates(self) -> list[str]:
        selected = self.config["backend"]
        validate_backend(selected, self.platform)
        if selected != "auto":
            return [selected]
        preferred = preferred_backend(self.platform)
        return ["mlx", "torch"] if preferred == "mlx" else ["torch"]

    def _get(self, name: str):
        if name not in self._instances:
            self._instances[name] = self.factories[name](self.config)
        return self._instances[name]

    def decide(self, task: str) -> dict[str, Any]:
        if not self.config["enabled"]:
            return {"status": "unavailable", "advisory": True, "fail_open": True, "error": "Router disabled", "backend": self.config["backend"]}
        errors = []
        try:
            candidates = self.candidates()
        except (RuntimeError, ValueError) as exc:
            return {"status": "unavailable", "advisory": True, "fail_open": True, "error": str(exc), "backend": self.config["backend"]}
        for name in candidates:
            try:
                backend = self._get(name)
                raw = backend.predict(task, QUESTIONS)
                if not isinstance(raw, dict) or not isinstance(raw.get("answers"), dict):
                    raise ValueError("Malformed Laya result")
                details = backend.info()
                self._active_backend = name
                routing = raw.get("routing") or {}
                model = routing.get("model", details["model"]) if isinstance(routing, dict) else details["model"]
                return {"status": "ok", **details, "model": model, "advisory": True,
                        "answers": {key: raw["answers"].get(key, {}) for key in QUESTIONS},
                        "routing": routing, "usage": raw.get("usage") or {}}
            except Exception as exc:
                logging.warning("Laya backend %s unavailable: %s", name, type(exc).__name__)
                errors.append(f"{name}: {type(exc).__name__}")
        return {"status": "unavailable", "advisory": True, "fail_open": True,
                "error": "; ".join(errors), "backend": candidates[-1]}

    def info(self) -> dict[str, Any]:
        try:
            if self._active_backend:
                return {"status": "ready", "platform": self.platform["label"], **self._get(self._active_backend).info(), "advisory": True}
            names = self.candidates()
            for name in names:
                backend = self._get(name)
                if backend.health().get("package"):
                    try:
                        backend.load()
                    except Exception:
                        continue
                    return {"status": "ready", "platform": self.platform["label"], **backend.info(), "advisory": True}
            return {"status": "unavailable", "platform": self.platform["label"], **self._get(names[0]).info(), "advisory": True, "fail_open": True}
        except Exception as exc:
            return {"status": "unavailable", "platform": self.platform["label"], "backend": self.config["backend"], "advisory": True, "fail_open": True, "error": str(exc)}


_CORE: RouterCore | None = None


def core() -> RouterCore:
    global _CORE
    if _CORE is None:
        _CORE = RouterCore()
    return _CORE


def decide(task: str) -> dict[str, Any]:
    return core().decide(task)
