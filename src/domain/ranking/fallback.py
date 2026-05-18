"""Rating-based fallback when LLM is unavailable (architecture §8, edge-cases §Fallback)."""

from __future__ import annotations

from domain.models.preferences import UserPreferences
from domain.models.recommendation import Recommendation, RecommendationBatch
from domain.models.restaurant import Restaurant


def template_explanation(restaurant: Restaurant, preferences: UserPreferences, rank: int) -> str:
    rating_text = f"{restaurant.rating:.1f}" if restaurant.rating is not None else "N/A"
    parts = [
        f"#{rank}: {restaurant.name} serves {restaurant.cuisine} in {restaurant.location}",
        f"with a rating of {rating_text}.",
        f"It aligns with your {preferences.budget.value} budget and {preferences.cuisine} cuisine preference.",
    ]
    if preferences.additional_preferences:
        parts.append(
            f'Note: "{preferences.additional_preferences}" could not be verified in our data; '
            "this pick is based on rating and your hard filters."
        )
    return " ".join(parts)


def build_fallback_batch(
    preferences: UserPreferences,
    candidates: list[Restaurant],
    top_k: int,
    *,
    reason: str,
) -> RecommendationBatch:
    ranked = sorted(
        candidates,
        key=lambda r: (r.rating is not None, r.rating or 0.0),
        reverse=True,
    )[:top_k]

    recommendations = [
        Recommendation(
            restaurant=restaurant,
            rank=index,
            explanation=template_explanation(restaurant, preferences, index),
        )
        for index, restaurant in enumerate(ranked, start=1)
    ]

    summary = (
        f"Showing {len(recommendations)} top-rated matches for {preferences.cuisine} "
        f"in {preferences.location} (AI ranking unavailable)."
    )

    return RecommendationBatch(
        recommendations=recommendations,
        summary=summary,
        preferences_used=preferences,
        candidates_considered=len(candidates),
        used_fallback=True,
        fallback_reason=reason,
    )
