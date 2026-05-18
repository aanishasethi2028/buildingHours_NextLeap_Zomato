#!/usr/bin/env python
"""CLI to ingest Zomato dataset and write local cache."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Allow running without editable install
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from infrastructure.config import get_settings  # noqa: E402
from infrastructure.ingestion import DataIngestionError, DataIngestionService  # noqa: E402
from infrastructure.repository import RestaurantRepository  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("ingest")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest Zomato restaurant dataset")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download and rebuild cache even if cache exists",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Limit rows ingested (overrides MAX_INGEST_ROWS env)",
    )
    args = parser.parse_args()

    settings = get_settings()
    if args.max_rows is not None:
        settings = settings.model_copy(update={"max_ingest_rows": args.max_rows})

    service = DataIngestionService(settings)

    try:
        restaurants = service.load_or_ingest(force_refresh=args.force)
    except DataIngestionError as exc:
        logger.error("%s", exc)
        return 1

    repo = RestaurantRepository.from_ingestion(restaurants)
    logger.info("Repository ready: %d restaurants", repo.count())

    # Sample stats
    cities: dict[str, int] = {}
    for r in restaurants:
        cities[r.location] = cities.get(r.location, 0) + 1
    top_cities = sorted(cities.items(), key=lambda x: -x[1])[:5]
    logger.info("Top cities: %s", top_cities)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
