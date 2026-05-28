import json
import pytest
from pathlib import Path

from application.recommendation_service import RecommendationService
from domain.filters.candidate_filter import CandidateFilter
from domain.models.preferences import UserBudget, UserPreferences
from domain.ranking.ranking_orchestrator import RankingOrchestrator
from fixtures.restaurants import sample_restaurants
from infrastructure.config import Settings
from infrastructure.llm.mock_client import MockLLMClient
from infrastructure.repository import RestaurantRepository


def _prefs(location="bangalore", budget=UserBudget.MEDIUM, cuisine="Italian", min_rating=4.0) -> UserPreferences:
    return UserPreferences(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
    )


def _mock_response(candidates) -> str:
    items = []
    for i, c in enumerate(candidates[:2], start=1):
        items.append(
            {
                "restaurant_id": c.id,
                "rank": i,
                "explanation": f"{c.name} is a strong match for your preferences.",
                "score": 0.95,
            }
        )
    return json.dumps(
        {
            "summary": "AI summary for top picks.",
            "recommendations": items,
        }
    )


class TestRecommendationFlowIntegration:
    def test_e2e_happy_path(self):
        candidates = sample_restaurants()
        repo = RestaurantRepository(candidates)
        settings = Settings(top_k_results=2)

        # 1. candidate filter
        candidate_filter = CandidateFilter(repo, settings)

        # 2. mock LLM client and orchestrator
        # Under medium budget Italian in bangalore, Trattoria (id=1) matches.
        mock_llm = MockLLMClient(response_content=_mock_response([candidates[0]]))
        orchestrator = RankingOrchestrator(mock_llm, settings)

        # 3. recommendation service
        service = RecommendationService(candidate_filter, orchestrator)

        # Execute
        batch = service.recommend(_prefs())

        # Assertions
        assert not batch.used_fallback
        assert batch.fallback_reason is None
        assert batch.candidates_considered == 1
        assert len(batch.recommendations) == 1
        assert batch.recommendations[0].restaurant.name == "Trattoria"
        assert batch.recommendations[0].rank == 1
        assert batch.summary == "AI summary for top picks."

    def test_e2e_empty_filter_results(self):
        candidates = sample_restaurants()
        repo = RestaurantRepository(candidates)
        settings = Settings(top_k_results=2)

        # Filter
        candidate_filter = CandidateFilter(repo, settings)
        # Orchestrator
        mock_llm = MockLLMClient(response_content="{}")
        orchestrator = RankingOrchestrator(mock_llm, settings)
        # Service
        service = RecommendationService(candidate_filter, orchestrator)

        # Execute for location with 0 matches (e.g. Hyderabad)
        batch = service.recommend(_prefs(location="hyderabad"))

        # Assertions
        assert not batch.used_fallback
        assert len(batch.recommendations) == 0
        assert batch.candidates_considered == 0
        assert "No restaurants found in 'hyderabad'" in batch.summary
        assert len(mock_llm.calls) == 0  # No LLM call made!

    def test_e2e_llm_failure_triggers_fallback(self):
        candidates = sample_restaurants()
        repo = RestaurantRepository(candidates)
        settings = Settings(top_k_results=2)

        # Filter
        candidate_filter = CandidateFilter(repo, settings)
        # Orchestrator (configured to fail)
        mock_llm = MockLLMClient(should_fail=True)
        orchestrator = RankingOrchestrator(mock_llm, settings)
        # Service
        service = RecommendationService(candidate_filter, orchestrator)

        # Execute
        batch = service.recommend(_prefs())

        # Assertions
        assert batch.used_fallback
        assert "mock LLM failure" in batch.fallback_reason
        assert batch.candidates_considered == 1
        assert len(batch.recommendations) == 1
        assert batch.recommendations[0].restaurant.name == "Trattoria"
        assert "AI ranking unavailable" in batch.summary
