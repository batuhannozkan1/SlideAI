"""Architecture guard: API views/serializers are a pure adapter over services.

They must never touch the ORM directly (no .objects) and never import models or
repositories — those belong to the repository layer, called only via services.
"""
from __future__ import annotations

import pathlib

API_DIR = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = (".objects", "repositories import", "import repositories", "models import")


def _python_files(*subdirs: str):
    for sub in subdirs:
        yield from (API_DIR / sub).rglob("*.py")


def test_views_and_serializers_have_no_orm_access():
    offenders = []
    for path in _python_files("views", "serializers"):
        text = path.read_text(encoding="utf-8")
        for needle in FORBIDDEN:
            if needle in text:
                offenders.append(f"{path.name}: '{needle}'")
    assert not offenders, f"ORM/repository access found in API layer: {offenders}"
