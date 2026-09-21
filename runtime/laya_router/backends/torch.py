from __future__ import annotations

import importlib.util
from typing import Any

from .base import LayaBackend


def detect_device(configured: str = "auto", torch_module=None) -> str:
    if configured == "cpu":
        return "cpu"
    if torch_module is None:
        import torch as torch_module
    if configured == "auto":
        if torch_module.cuda.is_available():
            return "cuda"
        if hasattr(torch_module.backends, "mps") and torch_module.backends.mps.is_available():
            return "mps"
        return "cpu"
    if configured == "cuda" and not torch_module.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    if configured == "mps" and not (hasattr(torch_module.backends, "mps") and torch_module.backends.mps.is_available()):
        raise RuntimeError("MPS requested but unavailable")
    if configured not in {"cpu", "cuda", "mps"}:
        raise RuntimeError(f"Unsupported PyTorch device: {configured}")
    return configured


class TorchBackend(LayaBackend):
    name = "torch"
    runtime = "laya"

    def __init__(self, config: dict):
        self.config = config
        self._router = None
        self._device = None

    def load(self) -> None:
        if self._router is None:
            import laya
            self._device = detect_device(self.config["device"])
            self._router = laya.Router(device=self._device, max_loaded=2, preload=False)

    def predict(self, state: str, questions: dict[str, Any]) -> dict[str, Any]:
        self.load()
        options = {}
        if self.config["model"] != "auto":
            options["model"] = self.config["model"]
        if self.config["language"] != "auto":
            options["lang"] = self.config["language"]
        return self._router.predict(state, questions, **options)

    def health(self) -> dict[str, Any]:
        return {"package": importlib.util.find_spec("laya") is not None, "torch": importlib.util.find_spec("torch") is not None, "loaded": self._router is not None}

    def info(self) -> dict[str, Any]:
        device = self._device
        if device is None:
            try:
                device = detect_device(self.config["device"])
            except (ImportError, RuntimeError):
                device = "unavailable"
        return {"backend": self.name, "runtime": self.runtime, "device": device, "model": self.config["model"]}
