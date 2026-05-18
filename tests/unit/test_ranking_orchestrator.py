import json

from domain.models.preferences import UserBudget, UserPreferences
from domain.ranking.ranking_orchestrator import RankingOrchestrator
from fixtures.restaurants import sample_restaurants
from infrastructure.config import Settings
from infrastructure.llm.mock_client import MockLLMClient


def _prefs() -> UserPreferences:
    return UserPreferences(
        location="bangalore",
        budget=UserBudget.MEDIUM,
        cuisine="Italian",
        min_rating=4.0,
    )


def _mock_response(candidates, include_fake: bool = False) -> str:
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
    if include_fake:
        items.append(
            {
                "restaurant_id": "hallucinated-id",
                "rank": 99,
                "explanation": "Should be dropped",
            }
        )
    return json.dumps(
        {
            "summary": "Here are your top Italian picks in Bangalore.",
            "recommendations": items,
        }
    )


class TestRankingOrchestrator:
    def test_llm_success(self):
        candidates = sample_restaurants()[:3]
        mock = MockLLMClient(response_content=_mock_response(candidates))
        orchestrator = RankingOrchestrator(mock, Settings(top_k_results=2))

        batch = orchestrator.rank_and_explain(_prefs(), candidates)

        assert not batch.used_fallback
        assert batch.summary is not None
        assert len(batch.recommendations) == 2
        assert batch.recommendations[0].rank == 1
        assert all(
            r.restaurant.id in {c.id for c in candidates} for r in batch.recommendations
        )
        assert len(mock.calls) == 1

    def test_strips_hallucinated_ids_and_backfills(self):
        candidates = sample_restaurants()[:3]
        mock = MockLLMClient(response_content=_mock_response(candidates, include_fake=True))
        orchestrator = RankingOrchestrator(mock, Settings(top_k_results=3))

        batch = orchestrator.rank_and_explain(_prefs(), candidates)

        assert len(batch.recommendations) == 3
        assert "hallucinated-id" not in {r.restaurant.id for r in batch.recommendations}

    def test_fallback_when_llm_fails(self):
        candidates = sample_restaurants()[:3]
        mock = MockLLMClient(should_fail=True)
        orchestrator = RankingOrchestrator(mock, Settings(top_k_results=2))

        batch = orchestrator.rank_and_explain(_prefs(), candidates)

        assert batch.used_fallback
        assert batch.fallback_reason is not None
        assert len(batch.recommendations) == 2
        assert batch.recommendations[0].restaurant.rating is not None

    def test_fallback_when_no_llm_client(self):
        candidates = sample_restaurants()[:3]
        orchestrator = RankingOrchestrator(None, Settings(top_k_results=2))

        batch = orchestrator.rank_and_explain(_prefs(), candidates)

        assert batch.used_fallback
        assert len(batch.recommendations) == 2

    def test_empty_candidates(self):
        orchestrator = RankingOrchestrator(MockLLMClient(), Settings())
        batch = orchestrator.rank_and_explain(_prefs(), [])
        assert batch.recommendations == []
        assert batch.candidates_considered == 0

    def test_invalid_json_triggers_fallback(self):
        candidates = sample_restaurants()[:2]
        mock = MockLLMClient(response_content="not valid json {{{")
        orchestrator = RankingOrchestrator(mock, Settings(top_k_results=2))

        batch = orchestrator.rank_and_explain(_prefs(), candidates)

        assert batch.used_fallback
        assert len(batch.recommendations) == 2
