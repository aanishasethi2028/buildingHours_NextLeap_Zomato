"""Recommendation orchestration service (Phase 4)."""

from __future__ import annotations

import logging

from domain.filters.candidate_filter import CandidateFilter
from domain.models.preferences import UserPreferences
from domain.models.recommendation import RecommendationBatch
from domain.ranking.ranking_orchestrator import RankingOrchestrator

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Orchestrates the restaurant recommendation workflow:
    filters candidates deterministically, then ranks and explains using LLM.
    """

    def __init__(
        self,
        candidate_filter: CandidateFilter,
        ranking_orchestrator: RankingOrchestrator,
    ) -> None:
        self._candidate_filter = candidate_filter
        self._ranking_orchestrator = ranking_orchestrator

    def recommend(self, preferences: UserPreferences) -> RecommendationBatch:
        """
        Run the end-to-end recommendation flow.
        """
        logger.info(
            "Recommending for location=%s, budget=%s, cuisine=%s",
            preferences.canonical_location,
            preferences.budget.value,
            preferences.cuisine,
        )
        
        # 1. Deterministic hard filtering
        filter_result = self._candidate_filter.filter(preferences)
        
        # 2. Check for empty candidate set
        if filter_result.is_empty:
            logger.info("No candidates matched hard filters. Returning empty batch.")
            return RecommendationBatch(
                recommendations=[],
                summary=filter_result.empty_reason,
                preferences_used=preferences,
                candidates_considered=0,
                used_fallback=False,
            )

        # 3. LLM ranking / explanations (or rating fallback if LLM client is None/fails)
        return self._ranking_orchestrator.rank_and_explain(
            preferences=preferences,
            candidates=filter_result.candidates,
        )
