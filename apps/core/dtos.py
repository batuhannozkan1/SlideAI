from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True)
class ServiceResult:
    success: bool
    data: Any = None
    errors: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def ok(cls, data: Any = None) -> ServiceResult:
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, errors: dict[str, list[str]]) -> ServiceResult:
        return cls(success=False, errors=errors)


@dataclass(frozen=True)
class PaginatedResult:
    items: Sequence[Any]
    total_count: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return -(-self.total_count // self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1
