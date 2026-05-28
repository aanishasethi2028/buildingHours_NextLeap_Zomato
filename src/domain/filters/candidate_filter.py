"""Deterministic hard-filter pipeline before LLM ranking."""

from __future__ import annotations

import logging

from domain.filters.filter_result import FilterResult, FilterStageCounts
from domain.models.preferences import UserBudget, UserPreferences
from domain.models.restaurant import BudgetTier, Restaurant
from domain.normalization import cuisine_matches
from infrastructure.config import Settings, get_settings
from infrastructure.repository import RestaurantRepository

logger = logging.getLogger(__name__)

_BUDGET_ADJACENT: dict[UserBudget, list[str]] = {
    UserBudget.LOW: ["try budget: medium"],
    UserBudget.MEDIUM: ["try budget: low", "try budget: high"],
    UserBudget.HIGH: ["try budget: medium"],
}


class CandidateFilter:
    """
    Applies location → budget → cuisine → min_rating filters, then caps by rating.
    Additional preferences are deferred to the LLM (Phase 3).
    """

    def __init__(
        self,
        repository: RestaurantRepository,
        settings: Settings | None = None,
    ) -> None:
        self._repository = repository
        self._settings = settings or get_settings()

    def filter(self, preferences: UserPreferences) -> FilterResult:
        all_restaurants = self._repository.find_all()
        counts = FilterStageCounts(total=len(all_restaurants))

        current = self._apply_location(all_restaurants, preferences)
        counts = counts.model_copy(update={"after_location": len(current)})

        current = self._apply_budget(current, preferences)
        counts = counts.model_copy(update={"after_budget": len(current)})

        current = self._apply_cuisine(current, preferences)
        counts = counts.model_copy(update={"after_cuisine": len(current)})

        current = self._apply_min_rating(current, preferences)
        counts = counts.model_copy(update={"after_rating": len(current)})

        total_before_cap = len(current)
        capped = total_before_cap > self._settings.max_candidates
        current = self._apply_cap(current)
        counts = counts.model_copy(update={"after_cap": len(current)})

        soft_note = self._soft_preferences_note(preferences)

        if not current:
            reason, suggestions = self._empty_state(counts, preferences)
            logger.info(
                "Filter empty for location=%s cuisine=%s: %s",
                preferences.canonical_location,
                preferences.cuisine,
                reason,
            )
            return FilterResult(
                candidates=[],
                stage_counts=counts,
                is_empty=True,
                empty_reason=reason,
                suggestions=suggestions,
                soft_preferences_note=soft_note,
                capped=False,
                total_before_cap=0,
            )

        if capped:
            logger.info(
                "Capped candidates from %d to %d (EC-FILTER-03)",
                total_before_cap,
                len(current),
            )

        return FilterResult(
            candidates=current,
            stage_counts=counts,
            is_empty=False,
            soft_preferences_note=soft_note,
            capped=capped,
            total_before_cap=total_before_cap,
        )

    def _apply_location(
        self, restaurants: list[Restaurant], preferences: UserPreferences
    ) -> list[Restaurant]:
        city = preferences.canonical_location
        from domain.normalization import normalize_match_key
        target = normalize_match_key(city)
        return [
            r for r in restaurants
            if normalize_match_key(r.location) == target
            or (r.area and normalize_match_key(r.area) == target)
        ]

    def _apply_budget(
        self, restaurants: list[Restaurant], preferences: UserPreferences
    ) -> list[Restaurant]:
        target = BudgetTier(preferences.budget.value)
        return [
            r
            for r in restaurants
            if r.budget_tier == target  # excludes UNKNOWN (EC-FILTER-10)
        ]

    def _apply_cuisine(
        self, restaurants: list[Restaurant], preferences: UserPreferences
    ) -> list[Restaurant]:
        return [r for r in restaurants if cuisine_matches(r.cuisine, preferences.cuisine)]

    def _apply_min_rating(
        self, restaurants: list[Restaurant], preferences: UserPreferences
    ) -> list[Restaurant]:
        minimum = preferences.min_rating
        return [
            r
            for r in restaurants
            if r.rating is not None and r.rating >= minimum
        ]

    def _apply_cap(self, restaurants: list[Restaurant]) -> list[Restaurant]:
        ranked = sorted(
            restaurants,
            key=lambda r: (r.rating is not None, r.rating or 0.0),
            reverse=True,
        )
        return ranked[: self._settings.max_candidates]

    def _soft_preferences_note(self, preferences: UserPreferences) -> str | None:
        if preferences.additional_preferences:
            return (
                "Additional preferences will be considered during AI ranking (Phase 3); "
                "they are not used as hard filters."
            )
        return None

    def _empty_state(
        self, counts: FilterStageCounts, preferences: UserPreferences
    ) -> tuple[str, list[str]]:
        suggestions: list[str] = []

        if counts.after_location == 0:
            reason = f"No restaurants found in '{preferences.location}'."
            suggestions = self._location_suggestions(preferences)
            suggestions.append("Check spelling or try a supported city")
            return reason, suggestions

        if counts.after_budget == 0:
            reason = "No restaurants match your budget in this location."
            suggestions = list(_BUDGET_ADJACENT.get(preferences.budget, []))
            suggestions.append("Try a different budget tier")
            return reason, suggestions

        if counts.after_cuisine == 0:
            reason = f"No '{preferences.cuisine}' restaurants found for your location and budget."
            suggestions = ["Try a broader cuisine type", "Check cuisine spelling"]
            return reason, suggestions

        if counts.after_rating == 0:
            reason = "No restaurants meet your minimum rating."
            suggestions = ["Lower your minimum rating", "Relax budget or cuisine filters"]
            return reason, suggestions

        return "No restaurants matched your criteria.", ["Try relaxing one or more filters"]

    def _location_suggestions(self, preferences: UserPreferences) -> list[str]:
        cities = sorted({r.location for r in self._repository.find_all() if r.location})
        if not cities:
            return []
        preview = ", ".join(cities[:8])
        return [f"Available cities include: {preview}"]
