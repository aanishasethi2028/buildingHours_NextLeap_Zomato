import json
from pathlib import Path

import pytest

from domain.models.restaurant import BudgetTier, Restaurant
from infrastructure.ingestion import DataIngestionService
from infrastructure.repository import RestaurantRepository


@pytest.fixture
def sample_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="abc",
            name="Test Place",
            location="bangalore",
            cuisine="Italian",
            cost="₹600 for two",
            cost_numeric=600,
            budget_tier=BudgetTier.MEDIUM,
            rating=4.0,
        )
    ]


class TestCacheRoundTrip:
    def test_save_and_load_cache(self, tmp_path: Path, sample_restaurants: list[Restaurant]):
        from infrastructure.config import Settings

        cache_file = tmp_path / "restaurants.json"
        settings = Settings(data_cache_path=cache_file, hf_dataset_id="test/dataset")
        service = DataIngestionService(settings)

        service.save_cache(sample_restaurants)
        loaded = service.load_from_cache()

        assert len(loaded) == 1
        assert loaded[0].name == "Test Place"
        assert loaded[0].id == "abc"

    def test_load_or_ingest_uses_cache(self, tmp_path: Path, sample_restaurants: list[Restaurant]):
        from infrastructure.config import Settings

        cache_file = tmp_path / "restaurants.json"
        settings = Settings(data_cache_path=cache_file)
        service = DataIngestionService(settings)
        service.save_cache(sample_restaurants)

        loaded = service.load_or_ingest(force_refresh=False)
        assert len(loaded) == 1

    def test_corrupt_cache_raises(self, tmp_path: Path):
        from infrastructure.config import Settings
        from infrastructure.ingestion import DataIngestionError

        cache_file = tmp_path / "restaurants.json"
        cache_file.write_text("not json", encoding="utf-8")
        settings = Settings(data_cache_path=cache_file)
        service = DataIngestionService(settings)

        with pytest.raises(DataIngestionError):
            service.load_from_cache()

    def test_ingest_fallback_to_cache(self, tmp_path: Path, sample_restaurants: list[Restaurant], monkeypatch: pytest.MonkeyPatch):
        from infrastructure.config import Settings
        from infrastructure.ingestion import DataIngestionError

        cache_file = tmp_path / "restaurants.json"
        settings = Settings(data_cache_path=cache_file, force_refresh_cache=True)
        service = DataIngestionService(settings)
        service.save_cache(sample_restaurants)

        def mock_ingest():
            raise RuntimeError("Hugging Face API is down")

        monkeypatch.setattr(service, "ingest_from_huggingface", mock_ingest)

        loaded = service.load_or_ingest()
        assert len(loaded) == 1
        assert loaded[0].name == "Test Place"

    def test_ingest_fails_no_cache(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        from infrastructure.config import Settings
        from infrastructure.ingestion import DataIngestionError

        cache_file = tmp_path / "restaurants.json"
        settings = Settings(data_cache_path=cache_file, force_refresh_cache=True)
        service = DataIngestionService(settings)

        if cache_file.exists():
            cache_file.unlink()

        def mock_ingest():
            raise RuntimeError("Hugging Face API is down")

        monkeypatch.setattr(service, "ingest_from_huggingface", mock_ingest)

        with pytest.raises(DataIngestionError) as exc_info:
            service.load_or_ingest()
        assert "no cache is present" in str(exc_info.value)


class TestRepositoryFromIngestion:
    def test_load(self, sample_restaurants: list[Restaurant]):
        repo = RestaurantRepository.from_ingestion(sample_restaurants)
        assert repo.count() == 1
        assert repo.find_by_location("bangalore")[0].cuisine == "Italian"
