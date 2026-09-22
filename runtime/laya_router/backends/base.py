from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LayaBackend(ABC):
    name: str
    runtime: str

    @abstractmethod
    def load(self) -> None: ...

    @abstractmethod
    def predict(self, state: str, questions: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def health(self) -> dict[str, Any]: ...

    @abstractmethod
    def info(self) -> dict[str, Any]: ...
