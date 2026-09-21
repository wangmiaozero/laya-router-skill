from laya_router.config import DEFAULT_CONFIG, load_config
from laya_router.platform import preferred_backend, validate_backend
from laya_router.router import QUESTIONS, RouterCore
from laya_router.backends.torch import detect_device


def cfg(**overrides):
    return {**DEFAULT_CONFIG, **overrides}


def info(system, machine):
    return {"system": system, "machine": machine, "label": f"{system} {machine}"}


def test_platform_matrix():
    assert preferred_backend(info("Darwin", "arm64")) == "mlx"
    for system, machine in [("Darwin", "x86_64"), ("Windows", "AMD64"), ("Linux", "x86_64")]:
        assert preferred_backend(info(system, machine)) == "torch"
    try:
        validate_backend("mlx", info("Windows", "AMD64"))
        assert False
    except RuntimeError:
        pass


def test_cuda_detection():
    class Available:
        @staticmethod
        def is_available():
            return True
    class Absent:
        @staticmethod
        def is_available():
            return False
    class Torch:
        cuda = Available()
        class backends:
            mps = Absent()
    assert detect_device("auto", Torch) == "cuda"
    Torch.cuda = Absent()
    assert detect_device("auto", Torch) == "cpu"


def test_mlx_fallback_and_normalization():
    class Broken:
        def __init__(self, config):
            pass
        def predict(self, *_):
            raise MemoryError("secret task text")
    class Working:
        def __init__(self, config):
            pass
        def predict(self, *_):
            return {"answers": {"task_type": {"choice": "coding"}}, "routing": {"model": "english"}, "usage": {"tokens": 10}}
        def info(self):
            return {"backend": "torch", "runtime": "laya", "model": "auto", "device": "cpu"}
    router = RouterCore(cfg(), info("Darwin", "arm64"), {"mlx": Broken, "torch": Working})
    result = router.decide("secret task text")
    assert result["status"] == "ok" and result["backend"] == "torch"
    assert set(result["answers"]) == set(QUESTIONS)
    assert result["model"] == "english" and result["advisory"] is True


def test_torch_failure_is_fail_open_without_task_leak():
    class Broken:
        def __init__(self, config):
            pass
        def predict(self, *_):
            raise RuntimeError("private credential")
    router = RouterCore(cfg(), info("Linux", "x86_64"), {"torch": Broken})
    result = router.decide("private credential")
    assert result["status"] == "unavailable" and result["fail_open"] is True
    assert "private credential" not in result["error"]


def test_forced_backend_does_not_fallback():
    result = RouterCore(cfg(backend="mlx"), info("Linux", "x86_64")).decide("task")
    assert result["status"] == "unavailable" and "requires macOS" in result["error"]


def test_config_parsing_and_invalid_fallback(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"backend":"torch","persist_task_text":false}', encoding="utf-8")
    assert load_config(path)["backend"] == "torch"
    path.write_text('{"backend":"bad"}', encoding="utf-8")
    assert load_config(path) == DEFAULT_CONFIG
