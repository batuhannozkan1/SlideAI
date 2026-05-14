from __future__ import annotations

from typing import Generic, Sequence, Type, TypeVar
from uuid import UUID

from django.db import models
from django.db.models import QuerySet

T = TypeVar("T", bound=models.Model)


class BaseRepository(Generic[T]):
    model: Type[T]

    # ---- Read ----

    def get_by_id(self, pk: UUID | int) -> T | None:
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def get_by_id_or_raise(self, pk: UUID | int) -> T:
        instance = self.get_by_id(pk)
        if instance is None:
            raise self.model.DoesNotExist(
                f"{self.model.__name__} with id={pk} not found"
            )
        return instance

    def list_all(self, *, limit: int = 100, offset: int = 0) -> Sequence[T]:
        return list(self.model.objects.all()[offset : offset + limit])

    def filter_by(self, **kwargs) -> QuerySet[T]:
        return self.model.objects.filter(**kwargs)

    def count(self, **kwargs) -> int:
        return self.model.objects.filter(**kwargs).count()

    def exists(self, **kwargs) -> bool:
        return self.model.objects.filter(**kwargs).exists()

    # ---- Write ----

    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)

    def bulk_create(self, instances: Sequence[T]) -> Sequence[T]:
        return self.model.objects.bulk_create(instances)

    def update(self, instance: T, **kwargs) -> T:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save(update_fields=list(kwargs.keys()))
        return instance

    def delete(self, instance: T) -> None:
        instance.delete()

    # ---- Soft delete ----

    def soft_delete(self, instance: T) -> T:
        from django.utils import timezone

        return self.update(instance, is_deleted=True, deleted_at=timezone.now())

    def list_active(self, **kwargs) -> QuerySet[T]:
        return self.model.objects.filter(is_deleted=False, **kwargs)
