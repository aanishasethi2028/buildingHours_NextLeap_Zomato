import json

import pytest

from domain.ranking.response_parser import (
    LLMResponseParseError,
    parse_llm_output,
    validate_and_deduplicate,
)


class TestResponseParser:
    def test_parse_valid_json(self):
        content = json.dumps(
            {
                "summary": "Great Italian options",
                "recommendations": [
                    {
                        "restaurant_id": "abc",
                        "rank": 1,
                        "explanation": "Best fit",
                        "score": 0.9,
                    }
                ],
            }
        )
        parsed = parse_llm_output(content)
        assert parsed.summary == "Great Italian options"
        assert len(parsed.recommendations) == 1
        assert parsed.recommendations[0].restaurant_id == "abc"

    def test_parse_markdown_fence(self):
        inner = json.dumps(
            {
                "recommendations": [
                    {"restaurant_id": "x", "rank": 1, "explanation": "Nice"}
                ]
            }
        )
        parsed = parse_llm_output(f"```json\n{inner}\n```")
        assert parsed.recommendations[0].restaurant_id == "x"

    def test_invalid_json_raises(self):
        with pytest.raises(LLMResponseParseError):
            parse_llm_output("not json")

    def test_reject_unknown_ids(self):
        parsed = parse_llm_output(
            json.dumps(
                {
                    "recommendations": [
                        {"restaurant_id": "real", "rank": 1, "explanation": "a"},
                        {"restaurant_id": "fake", "rank": 2, "explanation": "b"},
                    ]
                }
            )
        )
        validated = validate_and_deduplicate(parsed, {"real"})
        assert len(validated.recommendations) == 1
        assert validated.recommendations[0].restaurant_id == "real"
