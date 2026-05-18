import json

from domain.models.preferences import UserBudget, UserPreferences
from domain.ranking.prompt_builder import PromptBuilder
from fixtures.restaurants import sample_restaurants


class TestPromptBuilder:
    def test_build_includes_preferences_and_candidates(self):
        prefs = UserPreferences(
            location="Bangalore",
            budget=UserBudget.MEDIUM,
            cuisine="Italian",
            min_rating=4.0,
            additional_preferences="family-friendly",
        )
        candidates = sample_restaurants()[:2]
        system, user = PromptBuilder().build(prefs, candidates, top_k=3)

        assert "Zomato" in system or "dining" in system.lower()
        assert "Bangalore" in user
        assert "family-friendly" in user
        assert candidates[0].id in user
        payload = user.split("Candidate restaurants")[1]
        assert "Italian" in payload

    def test_strict_json_mode(self):
        _, user = PromptBuilder().build(
            UserPreferences(
                location="bangalore",
                budget=UserBudget.LOW,
                cuisine="Chinese",
                min_rating=3.0,
            ),
            sample_restaurants()[:1],
            top_k=1,
            strict_json=True,
        )
        assert "top 1" in user.lower() or "top 1 restaurants" in user.lower()
