"""Pydantic schemas: the unified normalized record + API responses."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class NormalizedOpportunity(BaseModel):
    """The single unified shape every source adapter must emit.

    This is the contract between the ingestion layer and storage. Scoring and
    dedup keys are computed downstream from these fields.
    """

    source_type: str
    source_name: str
    source_url: str | None = None
    external_id: str | None = None

    title: str
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

    documents_url: list[str] = Field(default_factory=list)
    contact_email: str | None = None


class OpportunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_type: str
    source_name: str
    source_url: str | None
    external_id: str | None
    title: str
    buyer_name: str | None
    buyer_type: str | None
    summary: str | None
    category_normalized: list[str]
    tags: list[str]
    location: str | None
    country: str | None
    posted_date: date | None
    deadline: date | None
    status: str
    budget_min: float | None
    budget_max: float | None
    currency: str | None
    documents_url: list[str]
    contact_email: str | None
    relevance_score: float
    design_fit_score: float
    saved: bool
    pipeline_status: str
    notes: str | None
    last_seen_at: datetime
    created_at: datetime


class OpportunityListOut(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[OpportunityOut]


class OpportunityUpdate(BaseModel):
    """Partial update for the dashboard actions (save/ignore, status, notes)."""

    saved: bool | None = None
    pipeline_status: str | None = None
    notes: str | None = None


class Facets(BaseModel):
    """Distinct filter values for populating the dashboard filter controls."""

    source_types: list[str]
    buyer_types: list[str]
    tags: list[str]
    countries: list[str]
    pipeline_statuses: list[str]
