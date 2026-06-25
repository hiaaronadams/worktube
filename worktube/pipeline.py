"""Build a report: fetch from sources -> dedup -> score -> sorted display rows.

No database. Each source's health (ok / failed / skipped) is tracked so the
report can show a ✓/✕ status panel.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone

from worktube.config import config
from worktube.dedup import compute_content_hash, compute_dedup_key
from worktube.feeds import FEEDS
from worktube.models import NormalizedOpportunity
from worktube.scoring import score_text
from worktube.socrata_sources import SOCRATA_SOURCES
from worktube.sources.base import SourceAdapter
from worktube.sources.grants import GrantsAdapter
from worktube.sources.rss import RssAdapter
from worktube.sources.sam import SamAdapter
from worktube.sources.sample import SampleAdapter
from worktube.sources.socrata import SocrataAdapter
from worktube.sources.ungm import UngmAdapter

logger = logging.getLogger("worktube.pipeline")

# Built-in live sources, available via --sources.
BUILTIN_ADAPTERS: dict[str, type[SourceAdapter]] = {
    "sam": SamAdapter,
    "grants": GrantsAdapter,
    "ungm": UngmAdapter,
}

# Sources run automatically (no --sources given).
#  - grants excluded: federal grants are money to orgs, not design RFPs (noise).
#  - ungm excluded: no API; its endpoint returns a JS shim, so it needs a
#    headless browser to scrape — not worth running in CI.
# Both remain available on demand via --sources. Curated RSS feeds (feeds.py)
# always run in addition to these.
DEFAULT_SOURCES: list[str] = ["sam"]


@dataclass
class SourceStatus:
    key: str
    name: str
    status: str          # "ok" | "failed" | "skipped"
    count: int = 0
    message: str = ""


@dataclass
class Report:
    generated_at: str
    demo: bool
    opportunities: list[dict]
    sources: list[dict]
    warnings: list[str] = field(default_factory=list)
    high_fit_threshold: float = config.high_fit_threshold

    @property
    def total(self) -> int:
        return len(self.opportunities)

    @property
    def high_fit_count(self) -> int:
        return sum(1 for o in self.opportunities if o["relevance_score"] >= self.high_fit_threshold)


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _to_row(opp: NormalizedOpportunity) -> dict:
    score = score_text(
        title=opp.title,
        summary=opp.summary,
        full_text=opp.full_text,
        category_raw=opp.category_raw,
        buyer_name=opp.buyer_name,
        buyer_type=opp.buyer_type,
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


def _run_one(key: str, lookback_days: int | None) -> tuple[SourceStatus, list[NormalizedOpportunity]]:
    """Run a single built-in source, returning its status and any records."""
    adapter_cls = BUILTIN_ADAPTERS[key]
    available, reason = adapter_cls.available()
    if not available:
        return SourceStatus(key, adapter_cls.name, "skipped", message=reason), []
    try:
        kwargs = {"lookback_days": lookback_days} if key == "sam" else {}
        records = adapter_cls(**kwargs).fetch()
        return SourceStatus(key, adapter_cls.name, "ok", count=len(records)), records
    except Exception as exc:  # noqa: BLE001 — a bad source shouldn't kill the report
        logger.warning("Source %s failed: %s", key, exc)
        return SourceStatus(key, adapter_cls.name, "failed", message=str(exc)[:200]), []


def _run_configured(adapter_cls, cfg: dict) -> tuple[SourceStatus, list[NormalizedOpportunity]]:
    """Run a config-driven source (RSS feed, Socrata dataset, ...)."""
    name = cfg.get("name", cfg.get("key", adapter_cls.__name__))
    key = cfg.get("key", name)
    try:
        records = adapter_cls(**cfg).fetch()
        return SourceStatus(key, name, "ok", count=len(records)), records
    except Exception as exc:  # noqa: BLE001
        logger.warning("Source %s failed: %s", name, exc)
        return SourceStatus(key, name, "failed", message=str(exc)[:200]), []


# Config-driven source lists: (adapter class, list of config dicts).
CONFIGURED_SOURCES = [
    (RssAdapter, FEEDS),
    (SocrataAdapter, SOCRATA_SOURCES),
]


def build_report(
    *,
    sources: list[str] | None = None,
    demo: bool = False,
    lookback_days: int | None = None,
) -> Report:
    statuses: list[SourceStatus] = []
    collected: list[NormalizedOpportunity] = []

    chosen = sources or DEFAULT_SOURCES

    # Always list every configured source so the panel is informative — in demo
    # mode we list them (without fetching); otherwise we actually ping them.
    for key in chosen:
        cls = BUILTIN_ADAPTERS.get(key)
        if cls is None:
            statuses.append(SourceStatus(key, key, "failed", message="unknown source"))
            continue
        if demo:
            ok, reason = cls.available()
            statuses.append(SourceStatus(
                key, cls.name, "skipped", message=reason or "not run (demo mode)"))
            continue
        status, records = _run_one(key, lookback_days)
        statuses.append(status)
        collected.extend(records)

    # Config-driven sources (RSS feeds, Socrata datasets) — only when not
    # restricted to a specific built-in source list.
    if sources is None:
        for adapter_cls, cfgs in CONFIGURED_SOURCES:
            for cfg in cfgs:
                name = cfg.get("name", cfg.get("key", "source"))
                if demo:
                    statuses.append(SourceStatus(
                        cfg.get("key", name), name, "skipped", message="not run (demo mode)"))
                    continue
                status, records = _run_configured(adapter_cls, cfg)
                statuses.append(status)
                collected.extend(records)

    # Fall back to sample data if nothing live came through.
    is_demo = demo or not collected
    if is_demo and not collected:
        collected = SampleAdapter().fetch()
        statuses.append(SourceStatus("sample", "Sample data", "ok", count=len(collected)))

    # Dedup (keep first occurrence of each key).
    seen: set[str] = set()
    rows: list[dict] = []
    for opp in collected:
        key = compute_dedup_key(opp)
        if key in seen:
            continue
        seen.add(key)
        rows.append(_to_row(opp))

    # Relevance floor — keep design signal, drop the municipal/procurement noise.
    floor = config.report_min_score
    kept = [r for r in rows if r["relevance_score"] >= floor]
    # Safety net: if the floor would empty the report, keep the top 25 anyway.
    if not kept and rows:
        kept = sorted(rows, key=lambda r: -r["relevance_score"])[:25]
    rows = kept

    rows.sort(key=lambda r: (-r["relevance_score"], r["deadline"] or "9999-12-31"))

    warnings = [
        f"{s.name}: {s.message}" for s in statuses if s.status != "ok" and s.message
    ]
    if is_demo and not demo:
        warnings.append("No live data available — showing sample/demo opportunities.")

    return Report(
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        demo=is_demo,
        opportunities=rows,
        sources=[asdict(s) for s in statuses],
        warnings=warnings,
    )
