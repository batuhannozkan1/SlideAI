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


@dataclass(frozen=True)
class DashboardStatsDTO:
    total_presentations: int
    total_slides: int
    presentations_this_month: int
    growth_percentage: float
    draft_count: int
    published_count: int
    chart_labels: tuple[str, ...]
    chart_values: tuple[int, ...]
    chart_max: int
