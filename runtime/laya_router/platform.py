from __future__ import annotations

import platform


def system_info(system: str | None = None, machine: str | None = None) -> dict[str, str]:
    system = system or platform.system()
    machine = machine or platform.machine()
    if system not in {"Darwin", "Windows", "Linux"}:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")
    return {"system": system, "machine": machine, "label": f"{'macOS' if system == 'Darwin' else system} {machine}"}


def preferred_backend(info: dict[str, str]) -> str:
    return "mlx" if info["system"] == "Darwin" and info["machine"].lower() in {"arm64", "aarch64"} else "torch"


def validate_backend(backend: str, info: dict[str, str]) -> None:
    if backend not in {"auto", "mlx", "torch"}:
        raise ValueError(f"Invalid backend: {backend}")
    if backend == "mlx" and preferred_backend(info) != "mlx":
        raise RuntimeError("MLX requires macOS on Apple Silicon; choose torch or auto")
