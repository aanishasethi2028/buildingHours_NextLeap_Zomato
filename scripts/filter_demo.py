#!/usr/bin/env python
"""Demo CLI: validate preferences and run candidate filter on cached data."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from application.preference_validator import PreferenceValidationError, PreferenceValidator  # noqa: E402
from domain.filters.candidate_filter import CandidateFilter  # noqa: E402
from infrastructure.config import get_settings  # noqa: E402
from infrastructure.ingestion import DataIngestionService  # noqa: E402
from infrastructure.repository import RestaurantRepository  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter restaurants by preferences")
    parser.add_argument("--location", required=True)
    parser.add_argument("--budget", choices=["low", "medium", "high"], required=True)
    parser.add_argument("--cuisine", required=True)
    parser.add_argument("--min-rating", type=float, default=3.5)
    parser.add_argument("--additional", default=None)
    args = parser.parse_args()

    settings = get_settings()
    restaurants = DataIngestionService(settings).load_or_ingest()
    repo = RestaurantRepository.from_ingestion(restaurants)

    try:
        prefs = PreferenceValidator().validate(
            {
                "location": args.location,
                "budget": args.budget,
                "cuisine": args.cuisine,
                "min_rating": args.min_rating,
                "additional_preferences": args.additional,
            }
        )
    except PreferenceValidationError as exc:
        print(json.dumps({"error": exc.messages}, indent=2))
        return 1

    result = CandidateFilter(repo, settings).filter(prefs)
    output = {
        "is_empty": result.is_empty,
        "count": len(result.candidates),
        "capped": result.capped,
        "empty_reason": result.empty_reason,
        "suggestions": result.suggestions,
        "candidates": [
            {
                "name": c.name,
                "cuisine": c.cuisine,
                "rating": c.rating,
                "cost": c.cost,
                "budget_tier": c.budget_tier.value,
            }
            for c in result.candidates
        ],
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
