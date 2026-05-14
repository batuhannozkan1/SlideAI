from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreatePresentationDTO:
    title: str
    description: str
    owner_id: int
    theme_id: UUID | None = None


@dataclass(frozen=True)
class UpdatePresentationDTO:
    title: str | None = None
    description: str | None = None
    theme_id: UUID | None = None
    is_public: bool | None = None


@dataclass(frozen=True)
class CreateSlideDTO:
    presentation_id: UUID
    heading: str
    body: str
    position: int
    notes: str = ""
    layout: str = "content"


@dataclass(frozen=True)
class UpdateSlideDTO:
    heading: str | None = None
    body: str | None = None
    notes: str | None = None
    layout: str | None = None
