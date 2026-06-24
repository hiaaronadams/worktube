"""Ingestion orchestrator: fetch -> score -> dedup -> upsert."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enrichment.scoring import score_text
from app.ingestion.base import SourceAdapter
from app.ingestion.dedup import compute_content_hash, compute_dedup_key
from app.ingestion.sam import SamAdapter
from app.ingestion.ungm import UngmAdapter
from app.models import Opportunity, OpportunityStatus, PipelineStatus, Source
from app.schemas import NormalizedOpportunity

logger = logging.getLogger("worktube.orchestrator")

# Registry of available adapters by key.
ADAPTERS: dict[str, type[SourceAdapter]] = {
    SamAdapter.key: SamAdapter,
    UngmAdapter.key: UngmAdapter,
}


@dataclass
class IngestStats:
    source: str
    fetched: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    errors: int = 0

    def as_dict(self) -> dict:
        return self.__dict__


def _apply(opp: Opportunity, norm: NormalizedOpportunity, content_hash: str) -> None:
    """Copy normalized fields + scores onto an ORM row."""
    score = score_text(
        title=norm.title,
        summary=norm.summary,
        full_text=norm.full_text,
        category_raw=norm.category_raw,
        buyer_name=norm.buyer_name,
    )
    opp.source_type = norm.source_type
    opp.source_name = norm.source_name
    opp.source_url = norm.source_url
    opp.external_id = norm.external_id
    opp.title = norm.title
    opp.buyer_name = norm.buyer_name
    opp.buyer_type = norm.buyer_type
    opp.summary = norm.summary
    opp.full_text = norm.full_text
    opp.category_raw = norm.category_raw
    opp.category_normalized = score.category_normalized
    opp.tags = score.tags
    opp.location = norm.location
    opp.country = norm.country
    opp.posted_date = norm.posted_date
    opp.deadline = norm.deadline
    opp.status = norm.status
    opp.budget_min = norm.budget_min
    opp.budget_max = norm.budget_max
    opp.currency = norm.currency
    opp.documents_url = norm.documents_url
    opp.contact_email = norm.contact_email
    opp.design_fit_score = score.design_fit_score
    opp.relevance_score = score.relevance_score
    opp.content_hash = content_hash
    opp.last_seen_at = datetime.now(timezone.utc)


def persist(session: Session, norm: NormalizedOpportunity, stats: IngestStats) -> None:
    dedup_key = compute_dedup_key(norm)
    content_hash = compute_content_hash(norm)

    existing = session.scalar(
        select(Opportunity).where(Opportunity.dedup_key == dedup_key)
    )

    if existing is None:
        opp = Opportunity(dedup_key=dedup_key)
        _apply(opp, norm, content_hash)
        session.add(opp)
        session.flush()
        # seed the pipeline status as "new"
        session.add(
            OpportunityStatus(opportunity_id=opp.id, status=PipelineStatus.new.value)
        )
        stats.created += 1
    elif existing.content_hash != content_hash:
        _apply(existing, norm, content_hash)
        stats.updated += 1
    else:
        existing.last_seen_at = datetime.now(timezone.utc)
        stats.unchanged += 1


def run_source(session: Session, key: str) -> IngestStats:
    if key not in ADAPTERS:
        raise ValueError(f"Unknown source '{key}'. Known: {sorted(ADAPTERS)}")

    stats = IngestStats(source=key)
    adapter = ADAPTERS[key]()
    source_row = session.scalar(select(Source).where(Source.name == adapter.name))
    if source_row:
        source_row.last_fetched_at = datetime.now(timezone.utc)

    try:
        records = adapter.fetch()
        stats.fetched = len(records)
        for norm in records:
            try:
                persist(session, norm, stats)
            except Exception:  # noqa: BLE001 — one bad record shouldn't kill the run
                logger.exception("Failed to persist a %s record", key)
                stats.errors += 1
        session.commit()
        if source_row:
            source_row.last_success_at = datetime.now(timezone.utc)
            source_row.status = "active"
            session.commit()
    except Exception:
        session.rollback()
        if source_row:
            source_row.status = "error"
            session.commit()
        logger.exception("Ingestion failed for source %s", key)
        raise

    logger.info("Ingest %s: %s", key, stats.as_dict())
    return stats


def run_all(session: Session) -> list[IngestStats]:
    results = []
    for key in ADAPTERS:
        try:
            results.append(run_source(session, key))
        except Exception:  # noqa: BLE001
            results.append(IngestStats(source=key, errors=1))
    return results
