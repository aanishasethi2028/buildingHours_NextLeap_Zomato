import pytest

from domain.models.restaurant import BudgetTier
from domain.normalization import (
    derive_budget_tier,
    extract_city_from_address,
    generate_restaurant_id,
    parse_cost_numeric,
    parse_rating,
    row_to_restaurant_fields,
)


class TestParseRating:
    def test_standard_format(self):
        assert parse_rating("4.1/5") == pytest.approx(4.1)

    def test_new_or_missing(self):
        assert parse_rating("NEW") is None
        assert parse_rating(None) is None
        assert parse_rating("-") is None

    def test_out_of_range(self):
        assert parse_rating("6.0/5") is None


class TestParseCost:
    def test_integer(self):
        assert parse_cost_numeric("800") == 800.0

    def test_with_comma(self):
        assert parse_cost_numeric("1,200") == 1200.0

    def test_invalid(self):
        assert parse_cost_numeric("-") is None
        assert parse_cost_numeric(None) is None


class TestBudgetTier:
    def test_tiers(self):
        assert derive_budget_tier(300) == BudgetTier.LOW
        assert derive_budget_tier(400) == BudgetTier.LOW
        assert derive_budget_tier(500) == BudgetTier.MEDIUM
        assert derive_budget_tier(800) == BudgetTier.MEDIUM
        assert derive_budget_tier(1200) == BudgetTier.HIGH
        assert derive_budget_tier(None) == BudgetTier.UNKNOWN


class TestCityExtraction:
    def test_bangalore_address(self):
        addr = "942, 21st Main Road, 2nd Stage, Banashankari, Bangalore"
        assert extract_city_from_address(addr) == "bangalore"

    def test_bengaluru_alias(self):
        assert extract_city_from_address("Some Street, Bengaluru") == "bangalore"

    def test_pincode_stripped(self):
        assert extract_city_from_address("Block, Bangalore-560085") == "bangalore"


class TestRowMapping:
    def test_valid_row(self):
        row = {
            "url": "https://www.zomato.com/bangalore/test",
            "name": "Jalsa",
            "address": "942, Banashankari, Bangalore",
            "location": "Banashankari",
            "cuisines": "North Indian, Chinese",
            "approx_cost(for two people)": "800",
            "rate": "4.1/5",
        }
        fields = row_to_restaurant_fields(row)
        assert fields is not None
        assert fields["name"] == "Jalsa"
        assert fields["location"] == "bangalore"
        assert fields["budget_tier"] == BudgetTier.MEDIUM
        assert fields["rating"] == pytest.approx(4.1)

    def test_skip_missing_name(self):
        assert row_to_restaurant_fields({"address": "x, Bangalore"}) is None

    def test_skip_no_city(self):
        assert row_to_restaurant_fields({"name": "X", "address": "Unknown Place"}) is None


class TestIdGeneration:
    def test_stable_from_url(self):
        row = {"url": "https://example.com/r/1", "name": "A"}
        id1 = generate_restaurant_id(row, "A", "")
        id2 = generate_restaurant_id(row, "A", "")
        assert id1 == id2
        assert len(id1) == 16
