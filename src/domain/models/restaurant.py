from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class BudgetTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class Restaurant(BaseModel):
    """Canonical restaurant record after ingestion normalization."""

    id: str
    name: str
    location: str  # Normalized city for filtering (e.g. bangalore)
    area: str = ""  # Locality / neighborhood from dataset
    cuisine: str
    cost: str = "Not available"  # Display string (e.g. "800 for two")
    cost_numeric: float | None = None  # Parsed INR for two, when available
    budget_tier: BudgetTier = BudgetTier.UNKNOWN
    rating: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}
