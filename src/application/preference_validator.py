"""Validate and normalize raw user preference input."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from pydantic import ValidationError

from domain.models.preferences import UserPreferences

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MAX_ADDITIONAL_LEN = 500


class PreferenceValidationError(Exception):
    """Raised when user preferences fail validation (EC-INPUT-01–05)."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = messages
        super().__init__("; ".join(messages))


class PreferenceValidator:
    """Normalizes and validates preference payloads from UI or API."""

    def validate(self, data: dict[str, Any]) -> UserPreferences:
        payload = dict(data)
        if "additional_preferences" in payload:
            payload["additional_preferences"] = self.sanitize_additional(
                payload.get("additional_preferences")
            )
        try:
            return UserPreferences.model_validate(payload)
        except ValidationError as exc:
            messages = [
                f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
                for err in exc.errors()
            ]
            raise PreferenceValidationError(messages) from exc

    @staticmethod
    def sanitize_additional(value: Any) -> str | None:
        """
        Sanitize free-text preferences (EC-INPUT-10–12).
        Strips control characters, normalizes Unicode, enforces max length.
        """
        if value is None:
            return None
        text = unicodedata.normalize("NFC", str(value).strip())
        if not text:
            return None
        text = _CONTROL_CHARS.sub("", text)
        if len(text) > _MAX_ADDITIONAL_LEN:
            text = text[:_MAX_ADDITIONAL_LEN]
        return text
