from domain.models.restaurant import BudgetTier, Restaurant
from infrastructure.repository import RestaurantRepository


def _sample_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="1",
            name="A",
            location="bangalore",
            area="Koramangala",
            cuisine="Italian",
            cost="₹500 for two",
            cost_numeric=500,
            budget_tier=BudgetTier.MEDIUM,
            rating=4.5,
        ),
        Restaurant(
            id="2",
            name="B",
            location="bangalore",
            area="Indiranagar",
            cuisine="Chinese",
            cost="₹300 for two",
            cost_numeric=300,
            budget_tier=BudgetTier.LOW,
            rating=4.0,
        ),
        Restaurant(
            id="3",
            name="C",
            location="delhi",
            area="Connaught Place",
            cuisine="Italian",
            cost="₹900 for two",
            cost_numeric=900,
            budget_tier=BudgetTier.HIGH,
            rating=4.2,
        ),
    ]


class TestRestaurantRepository:
    def test_find_all(self):
        repo = RestaurantRepository(_sample_restaurants())
        assert repo.count() == 3
        assert len(repo.find_all()) == 3

    def test_find_by_location_case_insensitive(self):
        repo = RestaurantRepository(_sample_restaurants())
        assert len(repo.find_by_location("Bangalore")) == 2
        assert len(repo.find_by_location("delhi")) == 1

    def test_find_by_location_bengaluru_alias(self):
        repo = RestaurantRepository(_sample_restaurants())
        assert len(repo.find_by_location("Bengaluru")) == 2

    def test_find_by_id(self):
        repo = RestaurantRepository(_sample_restaurants())
        assert repo.find_by_id("2").name == "B"
        assert repo.find_by_id("missing") is None
