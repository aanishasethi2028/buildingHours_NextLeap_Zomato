#!/usr/bin/env python
"""Demo: filter candidates then rank with LLM (or fallback)."""

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
from domain.ranking.ranking_orchestrator import RankingOrchestrator  # noqa: E402
from infrastructure.config import get_settings  # noqa: E402
from infrastructure.ingestion import DataIngestionService  # noqa: E402
from infrastructure.llm.factory import create_llm_client  # noqa: E402
from infrastructure.repository import RestaurantRepository  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> int:
    parser = argparse.ArgumentParser(description="Get AI restaurant recommendations")
    parser.add_argument("--location", required=True)
    parser.add_argument("--budget", choices=["low", "medium", "high"], required=True)
    parser.add_argument("--cuisine", required=True)
    parser.add_argument("--min-rating", type=float, default=3.5)
    parser.add_argument("--additional", default=None)
    parser.add_argument("--provider", default=None, help="Override LLM_PROVIDER")
    args = parser.parse_args()

    settings = get_settings()
    if args.provider:
        settings = settings.model_copy(update={"llm_provider": args.provider})

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

    filter_result = CandidateFilter(repo, settings).filter(prefs)
    if filter_result.is_empty:
        print(
            json.dumps(
                {
                    "is_empty": True,
                    "empty_reason": filter_result.empty_reason,
                    "suggestions": filter_result.suggestions,
                },
                indent=2,
            )
        )
        return 0

    llm_client = create_llm_client(settings)
    batch = RankingOrchestrator(llm_client, settings).rank_and_explain(
        prefs, filter_result.candidates
    )

    output = {
        "used_fallback": batch.used_fallback,
        "fallback_reason": batch.fallback_reason,
        "summary": batch.summary,
        "candidates_considered": batch.candidates_considered,
        "recommendations": [
            {
                "rank": r.rank,
                "name": r.restaurant.name,
                "cuisine": r.restaurant.cuisine,
                "rating": r.restaurant.rating,
                "cost": r.restaurant.cost,
                "explanation": r.explanation,
            }
            for r in batch.recommendations
        ],
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
