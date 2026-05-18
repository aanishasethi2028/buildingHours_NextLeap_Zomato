"""Application entrypoint — loads data layer (Phase 1)."""

from __future__ import annotations

import logging
import sys

from infrastructure.config import get_settings
from infrastructure.ingestion import DataIngestionError, DataIngestionService
from infrastructure.repository import RestaurantRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def bootstrap_repository() -> RestaurantRepository:
    """Load or ingest dataset and return a populated repository."""
    settings = get_settings()
    logger.info("Config: cache=%s dataset=%s", settings.data_cache_path, settings.hf_dataset_id)

    service = DataIngestionService(settings)
    try:
        restaurants = service.load_or_ingest()
    except DataIngestionError as exc:
        logger.error("Failed to load restaurant data: %s", exc)
        raise

    repo = RestaurantRepository.from_ingestion(restaurants)
    logger.info("Loaded %d restaurants", repo.count())
    return repo


def main() -> int:
    try:
        bootstrap_repository()
    except DataIngestionError:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
