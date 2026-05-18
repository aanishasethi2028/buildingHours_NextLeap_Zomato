"""In-memory restaurant repository."""

from __future__ import annotations

from domain.models.restaurant import Restaurant
from domain.normalization import canonical_user_location


class RestaurantRepository:
    """Read-only in-memory access to normalized restaurants."""

    def __init__(self, restaurants: list[Restaurant] | None = None) -> None:
        self._restaurants: list[Restaurant] = list(restaurants or [])
        self._by_id: dict[str, Restaurant] = {r.id: r for r in self._restaurants}

    def load(self, restaurants: list[Restaurant]) -> None:
        """Replace all records (e.g. after ingestion)."""
        self._restaurants = list(restaurants)
        self._by_id = {r.id: r for r in self._restaurants}

    def count(self) -> int:
        return len(self._restaurants)

    def find_by_id(self, restaurant_id: str) -> Restaurant | None:
        return self._by_id.get(restaurant_id)

    def find_all(self) -> list[Restaurant]:
        return list(self._restaurants)

    def find_by_location(self, location: str) -> list[Restaurant]:
        """Match normalized city key (case-insensitive)."""
        key = canonical_user_location(location)
        if not key:
            return []
        return [r for r in self._restaurants if r.location == key]

    @classmethod
    def from_ingestion(cls, restaurants: list[Restaurant]) -> RestaurantRepository:
        return cls(restaurants)
