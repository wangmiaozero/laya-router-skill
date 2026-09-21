from __future__ import annotations

import importlib.util
from typing import Any

from .base import LayaBackend


class MLXBackend(LayaBackend):
    name = "mlx"
    runtime = "laya-mlx"

    def __init__(self, config: dict):
        self.config = config
        self._router = None

    def load(self) -> None:
        if self._router is None:
            from laya_mlx import Router
            device = self.config["device"]
            if device not in {"auto", "gpu", "cpu"}:
                raise RuntimeError(f"Unsupported MLX device: {device}")
            self._router = Router(dtype="float16", device=None if device == "auto" else device, max_loaded=2, preload=False)

    def predict(self, state: str, questions: dict[str, Any]) -> dict[str, Any]:
        self.load()
        options = {}
        if self.config["model"] != "auto":
            options["model"] = self.config["model"]
        if self.config["language"] != "auto":
            options["lang"] = self.config["language"]
        return self._router.predict(state, questions, **options)

    def health(self) -> dict[str, Any]:
        return {"package": importlib.util.find_spec("laya_mlx") is not None, "loaded": self._router is not None}

    def info(self) -> dict[str, Any]:
        return {"backend": self.name, "runtime": self.runtime, "device": "gpu" if self.config["device"] == "auto" else self.config["device"], "model": self.config["model"]}
