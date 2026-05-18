"""Mock LLM client for tests and offline demos."""

from __future__ import annotations

import json
import re

from infrastructure.llm.client import LLMRequest, LLMResponse

_ID_PATTERN = re.compile(r'"id":\s*"([^"]+)"')


class MockLLMClient:
    def __init__(
        self,
        *,
        response_content: str | None = None,
        should_fail: bool = False,
        fail_message: str = "mock LLM failure",
    ) -> None:
        self._response_content = response_content
        self._should_fail = should_fail
        self._fail_message = fail_message
        self.calls: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        if self._should_fail:
            from infrastructure.llm.openai_client import LLMError

            raise LLMError(self._fail_message)
        if self._response_content is not None:
            content = self._response_content
        else:
            content = _synthetic_ranking_json(request.user_prompt)
        return LLMResponse(content=content, model=request.model, provider="mock")


def _synthetic_ranking_json(user_prompt: str, top_k: int = 5) -> str:
    """Build a valid ranking JSON from candidate IDs embedded in the prompt."""
    ids = _ID_PATTERN.findall(user_prompt)
    seen: list[str] = []
    for rid in ids:
        if rid not in seen:
            seen.append(rid)
    recommendations = [
        {
            "restaurant_id": rid,
            "rank": i,
            "explanation": f"Recommended based on your preferences (mock rank #{i}).",
            "score": 0.85,
        }
        for i, rid in enumerate(seen[:top_k], start=1)
    ]
    return json.dumps(
        {
            "summary": "Mock AI summary: top picks from your filtered candidates.",
            "recommendations": recommendations,
        }
    )
