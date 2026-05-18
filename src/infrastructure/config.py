from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = "openai"  # openai | ollama | mock
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=2000, ge=256, le=16000)
    llm_timeout_seconds: float = Field(default=30.0, ge=5.0, le=120.0)
    ollama_base_url: str = "http://localhost:11434"
    max_candidates: int = Field(default=30, ge=1, le=200)
    top_k_results: int = Field(default=5, ge=1, le=50)

    data_cache_path: Path = Path("data/restaurants.json")
    hf_dataset_id: str = "ManikaSaini/zomato-restaurant-recommendation"
    hf_dataset_split: str = "train"
    max_ingest_rows: int | None = None
    force_refresh_cache: bool = False

    @property
    def cache_meta_path(self) -> Path:
        return self.data_cache_path.parent / "cache_meta.json"


def get_settings() -> Settings:
    return Settings()
