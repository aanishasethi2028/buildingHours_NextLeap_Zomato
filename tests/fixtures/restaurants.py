"""Shared restaurant fixtures for filter and repository tests."""

from domain.models.restaurant import BudgetTier, Restaurant


def sample_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="1",
            name="Trattoria",
            location="bangalore",
            area="Koramangala",
            cuisine="Italian, Pizza",
            cost="₹500 for two",
            cost_numeric=500,
            budget_tier=BudgetTier.MEDIUM,
            rating=4.5,
        ),
        Restaurant(
            id="2",
            name="Wok Express",
            location="bangalore",
            area="Indiranagar",
            cuisine="Chinese, Asian",
            cost="₹300 for two",
            cost_numeric=300,
            budget_tier=BudgetTier.LOW,
            rating=4.0,
        ),
        Restaurant(
            id="3",
            name="Delhi Italian",
            location="delhi",
            area="CP",
            cuisine="Italian",
            cost="₹900 for two",
            cost_numeric=900,
            budget_tier=BudgetTier.HIGH,
            rating=4.2,
        ),
        Restaurant(
            id="4",
            name="Unrated Cafe",
            location="bangalore",
            cuisine="Italian",
            cost="₹400 for two",
            cost_numeric=400,
            budget_tier=BudgetTier.LOW,
            rating=None,
        ),
        Restaurant(
            id="5",
            name="Unknown Budget Spot",
            location="bangalore",
            cuisine="Italian",
            cost="Not available",
            budget_tier=BudgetTier.UNKNOWN,
            rating=4.8,
        ),
    ]
