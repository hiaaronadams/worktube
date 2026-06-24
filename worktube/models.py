"""The single unified opportunity shape every source emits."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class NormalizedOpportunity:
    source_type: str
    source_name: str
    title: str
    source_url: str | None = None
    external_id: str | None = None
    buyer_name: str | None = None
    buyer_type: str | None = None
    summary: str | None = None
    full_text: str | None = None
    category_raw: str | None = None
    location: str | None = None
    country: str | None = None
    posted_date: date | None = None
    deadline: date | None = None
    status: str = "unknown"
    budget_min: float | None = None
    budget_max: float | None = None
    currency: str | None = None
    documents_url: list[str] = field(default_factory=list)
    contact_email: str | None = None
