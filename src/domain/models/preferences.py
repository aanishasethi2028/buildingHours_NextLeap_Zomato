from enum import Enum

from pydantic import BaseModel, Field, field_validator

from domain.normalization import canonical_user_location, normalize_text


class UserBudget(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserPreferences(BaseModel):
    """Validated user input for restaurant filtering."""

    location: str
    budget: UserBudget
    cuisine: str
    min_rating: float = Field(ge=0.0, le=5.0)
    additional_preferences: str | None = None

    model_config = {"frozen": True}

    @property
    def canonical_location(self) -> str:
        return canonical_user_location(self.location)

    @field_validator("location", "cuisine", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> str:
        text = normalize_text(str(value) if value is not None else "")
        if not text:
            raise ValueError("must not be empty")
        return text

    @field_validator("budget", mode="before")
    @classmethod
    def normalize_budget(cls, value: object) -> UserBudget:
        if isinstance(value, UserBudget):
            return value
        text = normalize_text(str(value) if value is not None else "").lower()
        try:
            return UserBudget(text)
        except ValueError as exc:
            raise ValueError("budget must be one of: low, medium, high") from exc

    @field_validator("min_rating", mode="before")
    @classmethod
    def parse_min_rating(cls, value: object) -> float:
        try:
            rating = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("min_rating must be a number between 0 and 5") from exc
        if rating < 0.0 or rating > 5.0:
            raise ValueError("min_rating must be between 0 and 5")
        return rating
