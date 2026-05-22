"""Factory for constructing RecommendationService with its dependencies (Phase 4)."""

from __future__ import annotations

from application.recommendation_service import RecommendationService
from domain.filters.candidate_filter import CandidateFilter
from domain.ranking.ranking_orchestrator import RankingOrchestrator
from infrastructure.config import Settings, get_settings
from infrastructure.ingestion import DataIngestionService
from infrastructure.llm.factory import create_llm_client
from infrastructure.repository import RestaurantRepository


def create_recommendation_service(settings: Settings | None = None) -> RecommendationService:
    """
    Bootstrap the data repository, load LLM configurations, and construct
    the RecommendationService.
    """
    settings_obj = settings or get_settings()

    # 1. Ingest/load data and initialize repository
    ingestion_service = DataIngestionService(settings_obj)
    restaurants = ingestion_service.load_or_ingest()
    repository = RestaurantRepository.from_ingestion(restaurants)

    # 2. Build candidate filter
    candidate_filter = CandidateFilter(repository, settings_obj)

    # 3. Create LLM client and ranking orchestrator
    llm_client = create_llm_client(settings_obj)
    ranking_orchestrator = RankingOrchestrator(llm_client, settings_obj)

    # 4. Construct the orchestrating service
    return RecommendationService(
        candidate_filter=candidate_filter,
        ranking_orchestrator=ranking_orchestrator,
    )
