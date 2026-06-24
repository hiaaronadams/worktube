"""Build a report: fetch from sources -> dedup -> score -> sorted display rows.

No database. Everything lives in memory and is handed to the renderer, which
bakes it into a single static HTML file.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone

from worktube.config import config
from worktube.dedup import compute_content_hash, compute_dedup_key
from worktube.models import NormalizedOpportunity
from worktube.scoring import score_text
from worktube.sources.base import SourceAdapter
from worktube.sources.sam import SamAdapter
from worktube.sources.sample import SampleAdapter
from worktube.sources.ungm import UngmAdapter

logger = logging.getLogger("worktube.pipeline")

# Sources that pull live data (sample is handled separately as a fallback).
LIVE_ADAPTERS: dict[str, type[SourceAdapter]] = {
    "sam": SamAdapter,
    "ungm": UngmAdapter,
}


@dataclass
class Report:
    generated_at: str
    demo: bool
    opportunities: list[dict]
    source_stats: dict[str, int]
    warnings: list[str] = field(default_factory=list)
    high_fit_threshold: float = config.high_fit_threshold

    @property
    def total(self) -> int:
        return len(self.opportunities)

    @property
    def high_fit_count(self) -> int:
        return sum(
            1 for o in self.opportunities if o["relevance_score"] >= self.high_fit_threshold
        )


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _to_row(opp: NormalizedOpportunity) -> dict:
    """NormalizedOpportunity + scores -> a JSON-serializable display row."""
    score = score_text(
        title=opp.title,
        summary=opp.summary,
        full_text=opp.full_text,
        category_raw=opp.category_raw,
        buyer_name=opp.buyer_name,
    )
    row = asdict(opp)
    row["posted_date"] = _iso(opp.posted_date)
    row["deadline"] = _iso(opp.deadline)
    row["id"] = compute_dedup_key(opp)
    row["content_hash"] = compute_content_hash(opp)
    row["relevance_score"] = score.relevance_score
    row["design_fit_score"] = score.design_fit_score
    row["sector_fit_score"] = score.sector_fit_score
    row["tags"] = score.tags
    row["category_normalized"] = score.category_normalized
    row["penalties"] = score.penalties
    return row


def build_report(
    *,
    sources: list[str] | None = None,
    demo: bool = False,
    lookback_days: int | None = None,
) -> Report:
    warnings: list[str] = []
    stats: dict[str, int] = {}
    collected: list[NormalizedOpportunity] = []

    chosen = sources or list(LIVE_ADAPTERS)

    if not demo:
        for key in chosen:
            adapter_cls = LIVE_ADAPTERS.get(key)
            if adapter_cls is None:
                warnings.append(f"Unknown source '{key}' skipped.")
                continue
            if key == "sam" and not config.sam_api_key:
                warnings.append("SAM.gov skipped — SAM_API_KEY not set.")
                continue
            try:
                kwargs = {"lookback_days": lookback_days} if key == "sam" else {}
                records = adapter_cls(**kwargs).fetch()
                stats[key] = len(records)
                collected.extend(records)
            except Exception as exc:  # noqa: BLE001 — a bad source shouldn't kill the report
                warnings.append(f"{key} failed: {exc}")
                logger.warning("Source %s failed: %s", key, exc)

    # Fall back to sample data if we got nothing live (or demo was requested).
    is_demo = demo or not collected
    if is_demo and not collected:
        collected = SampleAdapter().fetch()
        stats["sample"] = len(collected)
        if not demo:
            warnings.append("No live data available — showing sample/demo opportunities.")

    # Dedup (keep first occurrence of each key).
    seen: set[str] = set()
    rows: list[dict] = []
    for opp in collected:
        key = compute_dedup_key(opp)
        if key in seen:
            continue
        seen.add(key)
        rows.append(_to_row(opp))

    # Sort: best fit first, then soonest deadline.
    rows.sort(
        key=lambda r: (-r["relevance_score"], r["deadline"] or "9999-12-31")
    )

    return Report(
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        demo=is_demo,
        opportunities=rows,
        source_stats=stats,
        warnings=warnings,
    )
