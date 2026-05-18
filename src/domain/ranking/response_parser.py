"""Parse and validate LLM JSON ranking responses."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


class LLMResponseParseError(Exception):
    """Invalid or unparseable LLM JSON (EC-LLM-05)."""


@dataclass(frozen=True)
class ParsedRecommendation:
    restaurant_id: str
    rank: int
    explanation: str
    score: float | None = None


@dataclass(frozen=True)
class ParsedLLMOutput:
    recommendations: list[ParsedRecommendation]
    summary: str | None = None


def extract_json_text(content: str) -> str:
    """Strip markdown code fences if present (EC-LLM-15)."""
    text = content.strip()
    match = _JSON_FENCE.search(text)
    if match:
        return match.group(1).strip()
    return text


def parse_llm_output(content: str) -> ParsedLLMOutput:
    text = extract_json_text(content)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMResponseParseError(f"Invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise LLMResponseParseError("Root JSON must be an object")

    raw_items = payload.get("recommendations")
    if not isinstance(raw_items, list):
        raise LLMResponseParseError("Missing 'recommendations' array")

    parsed: list[ParsedRecommendation] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        restaurant_id = str(item.get("restaurant_id", "")).strip()
        if not restaurant_id:
            continue
        try:
            rank = int(item.get("rank", 0))
        except (TypeError, ValueError):
            continue
        if rank < 1:
            continue
        explanation = str(item.get("explanation", "")).strip()
        score = _optional_float(item.get("score"))
        parsed.append(
            ParsedRecommendation(
                restaurant_id=restaurant_id,
                rank=rank,
                explanation=explanation,
                score=score,
            )
        )

    if not parsed:
        raise LLMResponseParseError("No valid recommendations in LLM output")

    summary = payload.get("summary")
    summary_text = str(summary).strip() if summary else None

    return ParsedLLMOutput(recommendations=parsed, summary=summary_text)


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_and_deduplicate(
    parsed: ParsedLLMOutput,
    valid_ids: set[str],
) -> ParsedLLMOutput:
    """
    Drop hallucinated IDs (EC-LLM-10) and duplicate restaurant_id entries.
    """
    seen: set[str] = set()
    kept: list[ParsedRecommendation] = []
    for item in sorted(parsed.recommendations, key=lambda r: r.rank):
        if item.restaurant_id not in valid_ids:
            continue
        if item.restaurant_id in seen:
            continue
        seen.add(item.restaurant_id)
        kept.append(item)
    return ParsedLLMOutput(recommendations=kept, summary=parsed.summary)
