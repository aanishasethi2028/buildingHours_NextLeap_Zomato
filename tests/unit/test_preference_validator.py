import pytest

from application.preference_validator import PreferenceValidationError, PreferenceValidator
from domain.models.preferences import UserBudget


class TestPreferenceValidator:
    def setup_method(self) -> None:
        self.validator = PreferenceValidator()

    def test_valid_preferences(self):
        prefs = self.validator.validate(
            {
                "location": "Bangalore",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4.0,
                "additional_preferences": "family-friendly",
            }
        )
        assert prefs.budget == UserBudget.MEDIUM
        assert prefs.canonical_location == "bangalore"
        assert prefs.additional_preferences == "family-friendly"

    def test_budget_case_insensitive(self):
        prefs = self.validator.validate(
            {
                "location": "Delhi",
                "budget": "HIGH",
                "cuisine": "Chinese",
                "min_rating": 3.5,
            }
        )
        assert prefs.budget == UserBudget.HIGH

    def test_invalid_budget(self):
        with pytest.raises(PreferenceValidationError) as exc:
            self.validator.validate(
                {
                    "location": "Delhi",
                    "budget": "premium",
                    "cuisine": "Chinese",
                    "min_rating": 4.0,
                }
            )
        assert "budget" in str(exc.value).lower()

    def test_invalid_min_rating(self):
        with pytest.raises(PreferenceValidationError):
            self.validator.validate(
                {
                    "location": "Delhi",
                    "budget": "low",
                    "cuisine": "Chinese",
                    "min_rating": 6.0,
                }
            )

    def test_missing_location(self):
        with pytest.raises(PreferenceValidationError):
            self.validator.validate(
                {
                    "location": "  ",
                    "budget": "low",
                    "cuisine": "Chinese",
                    "min_rating": 4.0,
                }
            )

    def test_sanitize_additional_truncates(self):
        long_text = "a" * 600
        result = PreferenceValidator.sanitize_additional(long_text)
        assert result is not None
        assert len(result) == 500

    def test_sanitize_additional_whitespace_only(self):
        assert PreferenceValidator.sanitize_additional("   ") is None
