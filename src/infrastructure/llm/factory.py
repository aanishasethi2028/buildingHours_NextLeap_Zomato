"""Construct LLM client from application settings."""

from __future__ import annotations

import logging

from infrastructure.config import Settings
from infrastructure.llm.client import LLMClient
from infrastructure.llm.mock_client import MockLLMClient
from infrastructure.llm.ollama_client import OllamaLLMClient
from infrastructure.llm.openai_client import OpenAILLMClient
from infrastructure.llm.groq_client import GroqLLMClient

logger = logging.getLogger(__name__)


def create_llm_client(settings: Settings) -> LLMClient | None:
    """
    Return an LLM client for the configured provider.
    Returns None when provider is openai or groq but API key is missing (triggers fallback).
    """
    provider = settings.llm_provider.strip().lower()

    if provider == "mock":
        logger.info("Using mock LLM client")
        return MockLLMClient()

    if provider == "ollama":
        logger.info("Using Ollama LLM at %s", settings.ollama_base_url)
        return OllamaLLMClient(settings)

    if provider == "openai":
        if not settings.llm_api_key:
            logger.warning("LLM_API_KEY not set; ranking will use fallback (EC-LLM-01)")
            return None
        return OpenAILLMClient(settings)

    if provider == "groq":
        if not settings.llm_api_key:
            logger.warning("LLM_API_KEY not set; ranking will use fallback (EC-LLM-01)")
            return None
        return GroqLLMClient(settings)

    logger.warning("Unknown LLM_PROVIDER=%s; using fallback", provider)
    return None
