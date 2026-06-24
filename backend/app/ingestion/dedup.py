"""Deduplication + persistence (SPEC §8).

Dedup key:
  * external_id (namespaced by source) when available, otherwise
  * hash(title + buyer_name + deadline + source)

content_hash detects amendments to an already-seen opportunity.
"""
from __future__ import annotations

from app.normalize import sha256
from app.schemas import NormalizedOpportunity


def compute_dedup_key(opp: NormalizedOpportunity) -> str:
    if opp.external_id:
        return f"{opp.source_type}:{opp.external_id}"
    return "hash:" + sha256(
        opp.title,
        opp.buyer_name,
        opp.deadline.isoformat() if opp.deadline else None,
        opp.source_type,
    )


def compute_content_hash(opp: NormalizedOpportunity) -> str:
    """Hash of the fields whose change constitutes an amendment."""
    return sha256(
        opp.title,
        opp.summary,
        opp.full_text,
        opp.deadline.isoformat() if opp.deadline else None,
        opp.status,
        str(opp.budget_min),
        str(opp.budget_max),
    )
