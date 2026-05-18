from pydantic import BaseModel, Field

from domain.models.preferences import UserPreferences
from domain.models.restaurant import Restaurant


class Recommendation(BaseModel):
    """A ranked restaurant with AI-generated rationale."""

    restaurant: Restaurant
    rank: int = Field(ge=1)
    explanation: str
    score: float | None = None

    model_config = {"frozen": True}


class RecommendationBatch(BaseModel):
    """Top recommendations returned to the presentation layer."""

    recommendations: list[Recommendation] = Field(default_factory=list)
    summary: str | None = None
    preferences_used: UserPreferences
    candidates_considered: int = 0
    used_fallback: bool = False
    fallback_reason: str | None = None

    model_config = {"frozen": True}
