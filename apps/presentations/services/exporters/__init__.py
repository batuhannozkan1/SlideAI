from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence, Type

from apps.core.exceptions import ValidationError


@dataclass(frozen=True)
class ExportResult:
    content: bytes
    content_type: str
    filename: str


class BaseExporter(ABC):
    @abstractmethod
    def export(self, presentation: Any, slides: Sequence, theme: Any | None) -> ExportResult: ...


_registry: dict[str, Type[BaseExporter]] = {}


def register_exporter(format_name: str, exporter_class: Type[BaseExporter]) -> None:
    _registry[format_name] = exporter_class


def get_exporter(format_name: str) -> BaseExporter:
    if format_name not in _registry:
        available = ", ".join(_registry.keys()) or "none"
        raise ValidationError({"format": [f"Desteklenmeyen format: {format_name}. Mevcut: {available}"]})
    return _registry[format_name]()


def list_available_formats() -> list[str]:
    return list(_registry.keys())
