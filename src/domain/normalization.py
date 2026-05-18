"""Row normalization utilities for Zomato Hugging Face dataset."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from domain.models.restaurant import BudgetTier

# City aliases → canonical lowercase key used for filtering
CITY_ALIASES: dict[str, str] = {
    "bangalore": "bangalore",
    "bangalore.": "bangalore",
    "bengaluru": "bangalore",
    "bengalore": "bangalore",
    "banglore": "bangalore",
    "new delhi": "delhi",
    "delhi": "delhi",
    "gurgaon": "gurgaon",
    "gurugram": "gurgaon",
    "mumbai": "mumbai",
    "bombay": "mumbai",
    "hyderabad": "hyderabad",
    "chennai": "chennai",
    "madras": "chennai",
    "kolkata": "kolkata",
    "calcutta": "kolkata",
    "pune": "pune",
    "noida": "noida",
}

# INR approximate cost for two people → budget tier
BUDGET_LOW_MAX = 400
BUDGET_MEDIUM_MAX = 800

_RATE_PATTERN = re.compile(r"^\s*([\d.]+)\s*/\s*5\s*$", re.IGNORECASE)
_COST_DIGITS = re.compile(r"[\d,]+")


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def normalize_match_key(value: str | None) -> str:
    """Lowercase key for case-insensitive cuisine/location matching."""
    return normalize_text(value).lower()


def canonical_user_location(location: str | None) -> str:
    """
    Map user-entered location to canonical city key (e.g. Bengaluru → bangalore).
    Returns normalized lowercase string when no alias matches.
    """
    key = normalize_match_key(location)
    if not key:
        return ""
    if key in CITY_ALIASES:
        return CITY_ALIASES[key]
    for alias in sorted(CITY_ALIASES.keys(), key=len, reverse=True):
        if alias in key:
            return CITY_ALIASES[alias]
    return key


def cuisine_matches(restaurant_cuisine: str, user_cuisine: str) -> bool:
    """Case-insensitive token/substring match on comma-separated cuisines (EC-FILTER-07)."""
    needle = normalize_match_key(user_cuisine)
    if not needle:
        return False
    haystack = normalize_match_key(restaurant_cuisine)
    if needle in haystack:
        return True
    tokens = [t.strip() for t in haystack.split(",")]
    return needle in tokens or any(needle in t for t in tokens)


def parse_rating(raw: Any) -> float | None:
    """
    Parse dataset `rate` field.
    Examples: '4.1/5', None, 'NEW', '-'
    Invalid → None (row may be dropped or excluded from rating filters).
    """
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text.upper() in {"NEW", "-", "NAN", "NONE"}:
        return None
    match = _RATE_PATTERN.match(text)
    if match:
        rating = float(match.group(1))
        return rating if 0.0 <= rating <= 5.0 else None
    try:
        rating = float(text)
        return rating if 0.0 <= rating <= 5.0 else None
    except ValueError:
        return None


def parse_cost_numeric(raw: Any) -> float | None:
    """
    Parse `approx_cost(for two people)` e.g. '800', '1,200'.
    Returns None when unparseable (EC-DATA-07).
    """
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text.upper() in {"-", "N/A", "NA", "NONE"}:
        return None
    match = _COST_DIGITS.search(text.replace(",", ""))
    if not match:
        return None
    try:
        value = float(match.group().replace(",", ""))
        return value if value > 0 else None
    except ValueError:
        return None


def format_cost_display(raw: Any, cost_numeric: float | None) -> str:
    if cost_numeric is not None:
        amount = int(cost_numeric) if cost_numeric == int(cost_numeric) else cost_numeric
        return f"₹{amount} for two"
    text = normalize_text(str(raw) if raw is not None else "")
    return text if text else "Not available"


def derive_budget_tier(cost_numeric: float | None) -> BudgetTier:
    if cost_numeric is None:
        return BudgetTier.UNKNOWN
    if cost_numeric <= BUDGET_LOW_MAX:
        return BudgetTier.LOW
    if cost_numeric <= BUDGET_MEDIUM_MAX:
        return BudgetTier.MEDIUM
    return BudgetTier.HIGH


def extract_city_from_address(address: str | None) -> str:
    """
    Extract a known city from the address using alias matching.
    Returns empty string when no supported city is found (row skipped).
    """
    if not address:
        return ""

    lower = address.lower()
    # Longest alias first to avoid partial false positives
    for alias in sorted(CITY_ALIASES.keys(), key=len, reverse=True):
        if alias in lower:
            return CITY_ALIASES[alias]

    parts = [p.strip() for p in address.split(",") if p.strip()]
    if not parts:
        return ""
    candidate = parts[-1]
    candidate = re.sub(r"-?\s*\d{5,6}\.?$", "", candidate).strip()
    return _canonical_city(candidate)


def _canonical_city(raw_city: str) -> str:
    key = normalize_match_key(raw_city)
    if not key:
        return ""
    if key in CITY_ALIASES:
        return CITY_ALIASES[key]
    return ""


def generate_restaurant_id(row: dict[str, Any], name: str, address: str) -> str:
    url = normalize_text(row.get("url"))
    if url:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    payload = f"{name}|{address}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def row_to_restaurant_fields(row: dict[str, Any]) -> dict[str, Any] | None:
    """
    Map a raw HF dataset row to Restaurant constructor kwargs.
    Returns None if row should be skipped (missing name or location city).
    """
    name = normalize_text(row.get("name"))
    if not name:
        return None

    address = normalize_text(row.get("address"))
    city = extract_city_from_address(address)
    if not city:
        return None

    area = normalize_text(row.get("location"))
    cuisine = normalize_text(row.get("cuisines")) or "Unknown"
    raw_cost = row.get("approx_cost(for two people)")
    cost_numeric = parse_cost_numeric(raw_cost)
    rating = parse_rating(row.get("rate"))

    restaurant_id = generate_restaurant_id(row, name, address)

    metadata: dict[str, Any] = {
        "url": row.get("url"),
        "address": address,
        "rest_type": row.get("rest_type"),
        "dish_liked": row.get("dish_liked"),
        "online_order": row.get("online_order"),
        "book_table": row.get("book_table"),
        "votes": row.get("votes"),
        "listed_in_type": row.get("listed_in(type)"),
        "listed_in_city": row.get("listed_in(city)"),
        "raw_rate": row.get("rate"),
        "raw_cost": raw_cost,
    }

    return {
        "id": restaurant_id,
        "name": name,
        "location": city,
        "area": area,
        "cuisine": cuisine,
        "cost": format_cost_display(raw_cost, cost_numeric),
        "cost_numeric": cost_numeric,
        "budget_tier": derive_budget_tier(cost_numeric),
        "rating": rating,
        "metadata": metadata,
    }
