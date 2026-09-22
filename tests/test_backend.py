import sys
from types import SimpleNamespace

from laya_router.backends.mlx import MLXBackend
from laya_router.backends.torch import TorchBackend
from laya_router.config import DEFAULT_CONFIG


def test_mlx_router_lazy_cached_and_language(monkeypatch):
    made = []
    class Router:
        def __init__(self, **kwargs):
            made.append(kwargs)
        def predict(self, state, questions, **kwargs):
            return {"answers": {}, "routing": kwargs}
    monkeypatch.setitem(sys.modules, "laya_mlx", SimpleNamespace(Router=Router))
    backend = MLXBackend({**DEFAULT_CONFIG, "language": "en"})
    assert not made
    assert backend.predict("task", {})["routing"] == {"lang": "en"}
    backend.predict("task", {})
    assert len(made) == 1 and made[0]["preload"] is False


def test_torch_router_lazy_cached_and_device(monkeypatch):
    made = []
    class Router:
        def __init__(self, **kwargs):
            made.append(kwargs)
        def predict(self, state, questions, **kwargs):
            return {"answers": {}, "routing": kwargs}
    monkeypatch.setitem(sys.modules, "laya", SimpleNamespace(Router=Router))
    backend = TorchBackend({**DEFAULT_CONFIG, "device": "cpu", "model": "multilingual"})
    backend.predict("task", {})
    backend.predict("task", {})
    assert len(made) == 1 and made[0]["device"] == "cpu"
    assert made[0]["preload"] is False
