"""Normalization helpers: dates, currency, text cleanup, hashing."""
from __future__ import annotations

import hashlib
import re
from datetime import date, datetime

from dateutil import parser as dateparser

_WHITESPACE = re.compile(r"\s+")
_HTML_TAG = re.compile(r"<[^>]+>")


def clean_text(value: str | None) -> str | None:
    """Strip HTML tags and collapse whitespace."""
    if value is None:
        return None
    no_tags = _HTML_TAG.sub(" ", value)
    collapsed = _WHITESPACE.sub(" ", no_tags).strip()
    return collapsed or None


def parse_date(value: str | date | datetime | None) -> date | None:
    """Best-effort parse to a `date`. Returns None on failure."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return dateparser.parse(str(value)).date()
    except (ValueError, OverflowError, TypeError):
        return None


# Common currency symbols / codes -> ISO 4217 code.
_CURRENCY_MAP = {
    "$": "USD",
    "us$": "USD",
    "usd": "USD",
    "€": "EUR",
    "eur": "EUR",
    "£": "GBP",
    "gbp": "GBP",
}


def normalize_currency(value: str | None) -> str | None:
    if not value:
        return None
    key = value.strip().lower()
    if key in _CURRENCY_MAP:
        return _CURRENCY_MAP[key]
    # Already a 3-letter code?
    if re.fullmatch(r"[A-Za-z]{3}", value.strip()):
        return value.strip().upper()
    return None


def parse_money(value) -> float | None:
    """Pull a numeric amount out of a string like '$1,200,000' or 50000."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^0-9.]", "", str(value))
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def sha256(*parts: str | None) -> str:
    """Stable hash over the given parts (None treated as empty)."""
    joined = "".join((p or "").strip().lower() for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
