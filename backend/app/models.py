"""ORM models — mirrors docs/SPEC.md §6.

Enums are stored as plain text (with Python-side enums for validation) to keep
migrations cheap; tighten to native PG enums later if desired.
"""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class SourceType(str, enum.Enum):
    sam = "sam"
    ungm = "ungm"
    state = "state"
    university = "university"
    nonprofit = "nonprofit"
    foundation = "foundation"
    other = "other"


class BuyerType(str, enum.Enum):
    government = "government"
    nonprofit = "nonprofit"
    un = "UN"
    university = "university"
    foundation = "foundation"
    other = "other"


class OpportunityState(str, enum.Enum):
    open = "open"
    closed = "closed"
    awarded = "awarded"
    unknown = "unknown"


class PipelineStatus(str, enum.Enum):
    new = "new"
    reviewing = "reviewing"
    maybe = "maybe"
    pitched = "pitched"
    submitted = "submitted"
    won = "won"
    lost = "lost"
    ignored = "ignored"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    source_name: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_id: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)

    title: Mapped[str] = mapped_column(Text)
    buyer_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    buyer_type: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    category_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_normalized: Mapped[list[str]] = mapped_column(
        ARRAY(Text), default=list, server_default="{}"
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list, server_default="{}")

    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)

    posted_date: Mapped[date | None] = mapped_column(nullable=True)
    deadline: Mapped[date | None] = mapped_column(nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(16), default=OpportunityState.unknown.value
    )

    budget_min: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    budget_max: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)

    documents_url: Mapped[list[str]] = mapped_column(
        ARRAY(Text), default=list, server_default="{}"
    )
    contact_email: Mapped[str | None] = mapped_column(Text, nullable=True)

    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    design_fit_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Dedup key: external_id when present, else hash(title+buyer+deadline+source).
    dedup_key: Mapped[str] = mapped_column(Text, unique=True, index=True)
    # Detects amendments: hash of the normalized content fields.
    content_hash: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    status_history: Mapped[list["OpportunityStatus"]] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, unique=True)
    # api / rss / html / playwright / manual
    source_type: Mapped[str] = mapped_column(String(16))
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    fetch_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    schedule_interval: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(16), default="active")


class OpportunityStatus(Base):
    __tablename__ = "opportunity_status"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(16), default=PipelineStatus.new.value)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    opportunity: Mapped["Opportunity"] = relationship(back_populates="status_history")
