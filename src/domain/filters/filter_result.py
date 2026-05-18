from pydantic import BaseModel, Field

from domain.models.restaurant import Restaurant


class FilterStageCounts(BaseModel):
    """Restaurant counts after each hard-filter stage (for diagnostics and UX)."""

    total: int = 0
    after_location: int = 0
    after_budget: int = 0
    after_cuisine: int = 0
    after_rating: int = 0
    after_cap: int = 0

    model_config = {"frozen": True}


class FilterResult(BaseModel):
    """Output of candidate filtering before LLM ranking (Phase 2)."""

    candidates: list[Restaurant] = Field(default_factory=list)
    stage_counts: FilterStageCounts = Field(default_factory=FilterStageCounts)
    is_empty: bool = False
    empty_reason: str | None = None
    suggestions: list[str] = Field(default_factory=list)
    # EC-FILTER-09: additional prefs are not hard-filtered in Phase 2
    soft_preferences_note: str | None = None
    capped: bool = False
    total_before_cap: int = 0

    model_config = {"frozen": True}
