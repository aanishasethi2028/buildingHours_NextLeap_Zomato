"""Load Zomato dataset from Hugging Face, normalize, and cache locally."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from datasets import load_dataset

from domain.models.restaurant import Restaurant
from domain.normalization import row_to_restaurant_fields
from infrastructure.config import Settings, get_settings

logger = logging.getLogger(__name__)

CACHE_VERSION = 1


class DataIngestionError(Exception):
    """Raised when ingestion fails and no usable cache exists."""


class DataIngestionService:
    """Fetches, normalizes, caches, and loads restaurant records."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def settings(self) -> Settings:
        return self._settings

    def load_or_ingest(self, force_refresh: bool | None = None) -> list[Restaurant]:
        """
        Load restaurants from cache when available; otherwise ingest from Hugging Face.
        """
        refresh = (
            force_refresh
            if force_refresh is not None
            else self._settings.force_refresh_cache
        )
        cache_path = self._settings.data_cache_path

        if not refresh and self._cache_exists(cache_path):
            logger.info("Loading restaurants from cache: %s", cache_path)
            return self.load_from_cache(cache_path)

        logger.info("Ingesting dataset from Hugging Face: %s", self._settings.hf_dataset_id)
        restaurants = self.ingest_from_huggingface()
        if not restaurants:
            raise DataIngestionError("Ingestion produced zero restaurants (EC-DATA-03)")
        self.save_cache(restaurants, cache_path)
        return restaurants

    def ingest_from_huggingface(self) -> list[Restaurant]:
        dataset = load_dataset(
            self._settings.hf_dataset_id,
            split=self._settings.hf_dataset_split,
        )
        max_rows = self._settings.max_ingest_rows
        total = len(dataset) if max_rows is None else min(len(dataset), max_rows)

        restaurants: list[Restaurant] = []
        skipped = 0

        for index in range(total):
            row = dict(dataset[index])
            fields = row_to_restaurant_fields(row)
            if fields is None:
                skipped += 1
                continue
            restaurants.append(Restaurant(**fields))

        logger.info(
            "Ingestion complete: %d restaurants, %d rows skipped",
            len(restaurants),
            skipped,
        )
        return restaurants

    def load_from_cache(self, path: Path | None = None) -> list[Restaurant]:
        cache_path = path or self._settings.data_cache_path
        try:
            raw = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DataIngestionError(
                f"Corrupt cache at {cache_path} (EC-DATA-11); delete and re-ingest"
            ) from exc

        if not isinstance(raw, list):
            raise DataIngestionError(f"Invalid cache format at {cache_path}")

        return [Restaurant.model_validate(item) for item in raw]

    def save_cache(self, restaurants: list[Restaurant], path: Path | None = None) -> None:
        cache_path = path or self._settings.data_cache_path
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        payload = [r.model_dump(mode="json") for r in restaurants]
        temp_path = cache_path.with_suffix(".tmp")

        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=0),
            encoding="utf-8",
        )
        temp_path.replace(cache_path)

        meta: dict[str, Any] = {
            "version": CACHE_VERSION,
            "dataset_id": self._settings.hf_dataset_id,
            "split": self._settings.hf_dataset_split,
            "row_count": len(restaurants),
            "written_at": datetime.now(timezone.utc).isoformat(),
        }
        self._settings.cache_meta_path.write_text(
            json.dumps(meta, indent=2),
            encoding="utf-8",
        )
        logger.info("Wrote %d restaurants to %s", len(restaurants), cache_path)

    def _cache_exists(self, path: Path) -> bool:
        return path.is_file() and path.stat().st_size > 0
