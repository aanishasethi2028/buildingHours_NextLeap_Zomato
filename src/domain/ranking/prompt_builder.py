"""Assemble LLM prompts for restaurant ranking (architecture §7.2)."""

from __future__ import annotations

import json

from domain.models.preferences import UserPreferences
from domain.models.restaurant import Restaurant


class PromptBuilder:
    def build(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
        top_k: int,
        *,
        strict_json: bool = False,
    ) -> tuple[str, str]:
        system = self._system_prompt(strict_json=strict_json)
        user = self._user_prompt(preferences, candidates, top_k)
        return system, user

    def _system_prompt(self, *, strict_json: bool) -> str:
        extra = (
            " Respond with ONLY valid JSON matching the schema. No markdown, no code fences."
            if strict_json
            else ""
        )
        return (
            "You are an expert dining recommender for Indian cities, similar to Zomato. "
            "You rank only from the candidate list provided. "
            "Never invent restaurants or IDs. "
            "Explain why each pick fits the user's stated preferences."
            + extra
        )

    def _user_prompt(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
        top_k: int,
    ) -> str:
        prefs_payload = {
            "location": preferences.location,
            "canonical_location": preferences.canonical_location,
            "budget": preferences.budget.value,
            "cuisine": preferences.cuisine,
            "min_rating": preferences.min_rating,
            "additional_preferences": preferences.additional_preferences,
        }
        candidate_payload = [
            {
                "id": c.id,
                "name": c.name,
                "location": c.location,
                "area": c.area,
                "cuisine": c.cuisine,
                "rating": c.rating,
                "cost": c.cost,
                "budget_tier": c.budget_tier.value,
            }
            for c in candidates
        ]

        schema = {
            "summary": "One paragraph overview of the selection",
            "recommendations": [
                {
                    "restaurant_id": "id from candidates only",
                    "rank": 1,
                    "explanation": "Why this fits the user",
                    "score": 0.95,
                }
            ],
        }

        return (
            f"User preferences:\n{json.dumps(prefs_payload, indent=2)}\n\n"
            f"Candidate restaurants (use ONLY these IDs):\n"
            f"{json.dumps(candidate_payload, indent=2)}\n\n"
            f"Task: Rank the top {top_k} restaurants for this user. "
            f"Return JSON matching this schema:\n{json.dumps(schema, indent=2)}\n"
            f"Rules:\n"
            f"- restaurant_id must be one of: {[c.id for c in candidates]}\n"
            f"- ranks must be 1..{top_k} without duplicates\n"
            f"- reference budget, cuisine, location, and additional_preferences when relevant\n"
        )
