import json
import pytest
from pathlib import Path

from application.recommendation_service import RecommendationService
from application.factory import create_recommendation_service
from domain.filters.candidate_filter import CandidateFilter
from domain.models.preferences import UserBudget, UserPreferences
from domain.ranking.ranking_orchestrator import RankingOrchestrator
from fixtures.restaurants import sample_restaurants
from infrastructure.config import Settings
from infrastructure.llm.mock_client import MockLLMClient
from infrastructure.ingestion import DataIngestionService
from infrastructure.repository import RestaurantRepository


def _prefs() -> UserPreferences:
    return UserPreferences(
        location="bangalore",
        budget=UserBudget.MEDIUM,
        cuisine="Italian",
        min_rating=4.0,
    )


def _mock_response(candidates) -> str:
    items = []
    for i, c in enumerate(candidates[:3], start=1):
        items.append(
            {
                "restaurant_id": c.id,
                "rank": i,
                "explanation": f"{c.name} is a strong match for your preferences.",
                "score": 0.9,
            }
        )
    return json.dumps(
        {
            "summary": "Here are your top Italian picks in Bangalore.",
            "recommendations": items,
        }
    )


class TestRecommendationService:
    def test_recommend_success(self):
        candidates = sample_restaurants()
        repo = RestaurantRepository(candidates)
        settings = Settings(top_k_results=2)
        
        candidate_filter = CandidateFilter(repo, settings)
        
        # Filter matches Trattoria (id=1, medium, 4.5 rating) and Unknown Budget Spot (which has unknown budget tier, so budget filter filters it out).
        # Wait, budget filter: Low matches id 2, 4. Medium matches id 1. High matches id 3.
        # So for Medium budget, only id 1 (Trattoria) matches. Let's make sure.
        # Trattoria has rating 4.5, budget medium, location bangalore, cuisine Italian, pizza.
        # So Trattoria (id 1) is the only candidate matching _prefs().
        
        mock_llm = MockLLMClient(response_content=_mock_response([candidates[0]]))
        orchestrator = RankingOrchestrator(mock_llm, settings)
        
        service = RecommendationService(candidate_filter, orchestrator)
        
        batch = service.recommend(_prefs())
        
        assert not batch.used_fallback
        assert len(batch.recommendations) == 1
        assert batch.recommendations[0].restaurant.id == "1"
        assert batch.candidates_considered == 1
        assert batch.summary == "Here are your top Italian picks in Bangalore."

    def test_recommend_empty_candidates(self):
        # Setup repo with only delhi restaurants to guarantee 0 matches for bangalore
        repo = RestaurantRepository([
            r for r in sample_restaurants() if r.location == "delhi"
        ])
        settings = Settings()
        
        candidate_filter = CandidateFilter(repo, settings)
        # Mock orchestrator should not be called
        orchestrator = RankingOrchestrator(None, settings)
        
        service = RecommendationService(candidate_filter, orchestrator)
        
        batch = service.recommend(_prefs())
        
        assert not batch.used_fallback
        assert len(batch.recommendations) == 0
        assert batch.candidates_considered == 0
        assert "No restaurants found in" in batch.summary

    def test_recommend_fallback(self):
        candidates = sample_restaurants()
        repo = RestaurantRepository(candidates)
        settings = Settings(top_k_results=1)
        
        candidate_filter = CandidateFilter(repo, settings)
        # Mock LLM is configured to fail, triggering fallback
        mock_llm = MockLLMClient(should_fail=True)
        orchestrator = RankingOrchestrator(mock_llm, settings)
        
        service = RecommendationService(candidate_filter, orchestrator)
        
        batch = service.recommend(_prefs())
        
        assert batch.used_fallback
        assert len(batch.recommendations) == 1
        assert batch.recommendations[0].restaurant.id == "1"  # Trattoria is top-rated medium Italian in Bangalore
        assert "AI ranking unavailable" in batch.summary

    def test_factory_creation(self, tmp_path: Path):
        cache_file = tmp_path / "restaurants.json"
        settings = Settings(
            data_cache_path=cache_file,
            llm_provider="mock",
            force_refresh_cache=False,
        )
        
        # Save sample data to cache to prevent Hugging Face API call
        ingestion_service = DataIngestionService(settings)
        ingestion_service.save_cache(sample_restaurants())
        
        # Create recommendation service via factory
        service = create_recommendation_service(settings)
        assert service is not None
        
        # Run recommendation and assert
        batch = service.recommend(_prefs())
        assert len(batch.recommendations) == 1
        assert batch.recommendations[0].restaurant.id == "1"
