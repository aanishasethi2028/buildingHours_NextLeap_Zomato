from domain.normalization import canonical_user_location, cuisine_matches


class TestCanonicalUserLocation:
    def test_bengaluru_alias(self):
        assert canonical_user_location("Bengaluru") == "bangalore"

    def test_unknown_city_passthrough(self):
        assert canonical_user_location("Paris") == "paris"


class TestCuisineMatches:
    def test_case_insensitive(self):
        assert cuisine_matches("North Indian, Chinese", "chinese")

    def test_token_in_list(self):
        assert cuisine_matches("Italian, Pizza, Fast Food", "italian")
