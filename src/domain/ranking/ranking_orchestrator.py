"""Orchestrate LLM ranking, parsing, validation, and fallback."""

from __future__ import annotations

import logging

from domain.models.preferences import UserPreferences
from domain.models.recommendation import Recommendation, RecommendationBatch
from domain.models.restaurant import Restaurant
from domain.ranking.fallback import build_fallback_batch, template_explanation
from domain.ranking.prompt_builder import PromptBuilder
from domain.ranking.response_parser import (
    LLMResponseParseError,
    ParsedLLMOutput,
    parse_llm_output,
    validate_and_deduplicate,
)
from infrastructure.config import Settings, get_settings
from infrastructure.llm.client import LLMClient, LLMRequest
from infrastructure.llm.openai_client import LLMError

logger = logging.getLogger(__name__)


class RankingOrchestrator:
    def __init__(
        self,
        llm_client: LLMClient | None,
        settings: Settings | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self._llm_client = llm_client
        self._settings = settings or get_settings()
        self._prompt_builder = prompt_builder or PromptBuilder()

    def rank_and_explain(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
    ) -> RecommendationBatch:
        top_k = self._settings.top_k_results
        if not candidates:
            return RecommendationBatch(
                recommendations=[],
                preferences_used=preferences,
                candidates_considered=0,
            )

        if self._llm_client is None:
            return build_fallback_batch(
                preferences,
                candidates,
                top_k,
                reason="LLM not configured (missing API key or provider)",
            )

        try:
            batch = self._rank_with_llm(preferences, candidates, top_k, strict_retry=False)
            if len(batch.recommendations) >= min(top_k, len(candidates)):
                return batch
            # Retry once with stricter JSON instruction if too few valid items
            logger.warning("LLM returned insufficient valid items; retrying with strict JSON")
            batch = self._rank_with_llm(preferences, candidates, top_k, strict_retry=True)
            if batch.recommendations:
                return batch
        except (LLMError, LLMResponseParseError) as exc:
            logger.warning("LLM ranking failed: %s", exc)
            return build_fallback_batch(
                preferences,
                candidates,
                top_k,
                reason=str(exc),
            )

        return build_fallback_batch(
            preferences,
            candidates,
            top_k,
            reason="LLM output could not be validated after retry",
        )

    def _rank_with_llm(
        self,
        preferences: UserPreferences,
        candidates: list[Restaurant],
        top_k: int,
        *,
        strict_retry: bool,
    ) -> RecommendationBatch:
        system, user = self._prompt_builder.build(
            preferences,
            candidates,
            top_k,
            strict_json=strict_retry,
        )
        request = LLMRequest(
            system_prompt=system,
            user_prompt=user,
            model=self._settings.llm_model,
            temperature=self._settings.llm_temperature,
            max_tokens=self._settings.llm_max_tokens,
            json_mode=True,
        )
        response = self._llm_client.complete(request)  # type: ignore[union-attr]
        parsed = parse_llm_output(response.content)
        valid_ids = {c.id for c in candidates}
        validated = validate_and_deduplicate(parsed, valid_ids)
        recommendations = self._to_recommendations(validated, candidates, preferences, top_k)
        recommendations = self._backfill(recommendations, candidates, preferences, top_k)

        return RecommendationBatch(
            recommendations=recommendations[:top_k],
            summary=validated.summary,
            preferences_used=preferences,
            candidates_considered=len(candidates),
            used_fallback=False,
        )

    def _to_recommendations(
        self,
        parsed: ParsedLLMOutput,
        candidates: list[Restaurant],
        preferences: UserPreferences,
        top_k: int,
    ) -> list[Recommendation]:
        by_id = {c.id: c for c in candidates}
        results: list[Recommendation] = []
        for item in sorted(parsed.recommendations, key=lambda r: r.rank):
            restaurant = by_id.get(item.restaurant_id)
            if restaurant is None:
                continue
            explanation = item.explanation or template_explanation(
                restaurant, preferences, item.rank
            )
            results.append(
                Recommendation(
                    restaurant=restaurant,
                    rank=len(results) + 1,
                    explanation=explanation,
                    score=item.score,
                )
            )
            if len(results) >= top_k:
                break
        return results

    def _backfill(
        self,
        current: list[Recommendation],
        candidates: list[Restaurant],
        preferences: UserPreferences,
        top_k: int,
    ) -> list[Recommendation]:
        """Fill remaining slots from rating sort when LLM returns too few valid IDs."""
        if len(current) >= top_k:
            return current
        used_ids = {r.restaurant.id for r in current}
        remaining = sorted(
            [c for c in candidates if c.id not in used_ids],
            key=lambda r: (r.rating is not None, r.rating or 0.0),
            reverse=True,
        )
        results = list(current)
        for restaurant in remaining:
            if len(results) >= top_k:
                break
            rank = len(results) + 1
            results.append(
                Recommendation(
                    restaurant=restaurant,
                    rank=rank,
                    explanation=template_explanation(restaurant, preferences, rank),
                )
            )
        return results
