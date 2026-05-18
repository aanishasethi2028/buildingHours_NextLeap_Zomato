import pytest

from domain.filters.candidate_filter import CandidateFilter
from domain.models.preferences import UserBudget, UserPreferences
from domain.models.restaurant import BudgetTier, Restaurant
from infrastructure.config import Settings
from infrastructure.repository import RestaurantRepository
from fixtures.restaurants import sample_restaurants


def _prefs(**kwargs: object) -> UserPreferences:
    defaults = {
        "location": "bangalore",
        "budget": UserBudget.MEDIUM,
        "cuisine": "Italian",
        "min_rating": 4.0,
    }
    defaults.update(kwargs)
    return UserPreferences(**defaults)


class TestCandidateFilter:
    def setup_method(self) -> None:
        self.repo = RestaurantRepository(sample_restaurants())
        self.settings = Settings(max_candidates=30)
        self.filter = CandidateFilter(self.repo, self.settings)

    def test_matching_preferences(self):
        result = self.filter.filter(_prefs())
        assert not result.is_empty
        assert len(result.candidates) == 1
        assert result.candidates[0].name == "Trattoria"

    def test_cuisine_substring_multi_value(self):
        result = self.filter.filter(_prefs(cuisine="pizza", budget=UserBudget.MEDIUM))
        assert len(result.candidates) == 1
        assert result.candidates[0].id == "1"

    def test_location_alias_bengaluru(self):
        result = self.filter.filter(_prefs(location="Bengaluru"))
        assert not result.is_empty
        assert all(r.location == "bangalore" for r in result.candidates)

    def test_excludes_unknown_budget_tier(self):
        result = self.filter.filter(
            _prefs(budget=UserBudget.LOW, min_rating=4.5, cuisine="Italian")
        )
        names = {c.name for c in result.candidates}
        assert "Unknown Budget Spot" not in names

    def test_min_rating_excludes_null_and_low(self):
        result = self.filter.filter(_prefs(min_rating=4.1))
        ids = {c.id for c in result.candidates}
        assert "4" not in ids  # Unrated Cafe
        assert "2" not in ids  # rating 4.0

    def test_empty_wrong_city(self):
        result = self.filter.filter(_prefs(location="Paris"))
        assert result.is_empty
        assert result.empty_reason is not None
        assert result.suggestions

    def test_empty_budget_mismatch(self):
        result = self.filter.filter(_prefs(budget=UserBudget.HIGH))
        assert result.is_empty
        assert "budget" in result.empty_reason.lower()

    def test_soft_preferences_note(self):
        prefs = UserPreferences(
            location="bangalore",
            budget=UserBudget.MEDIUM,
            cuisine="Italian",
            min_rating=4.0,
            additional_preferences="quick service",
        )
        result = self.filter.filter(prefs)
        assert result.soft_preferences_note is not None

    def test_candidate_cap(self):
        many = [
            Restaurant(
                id=str(i),
                name=f"R{i}",
                location="bangalore",
                cuisine="Italian",
                cost_numeric=500,
                budget_tier=BudgetTier.MEDIUM,
                rating=3.0 + (i % 10) * 0.1,
            )
            for i in range(50)
        ]
        repo = RestaurantRepository(many)
        filt = CandidateFilter(repo, Settings(max_candidates=10))
        result = filt.filter(_prefs(min_rating=0.0))
        assert len(result.candidates) == 10
        assert result.capped
        assert result.total_before_cap == 50
        ratings = [c.rating for c in result.candidates]
        assert ratings == sorted(ratings, reverse=True)

    def test_fewer_than_top_k_not_padded(self):
        result = self.filter.filter(_prefs())
        assert len(result.candidates) < 5
