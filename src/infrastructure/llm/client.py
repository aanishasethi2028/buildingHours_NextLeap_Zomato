"""LLM client port (provider-agnostic)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMRequest:
    system_prompt: str
    user_prompt: str
    model: str
    temperature: float
    max_tokens: int
    json_mode: bool = True


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str
    provider: str


class LLMClient(Protocol):
    """Adapter interface for chat completion providers."""

    def complete(self, request: LLMRequest) -> LLMResponse: ...
