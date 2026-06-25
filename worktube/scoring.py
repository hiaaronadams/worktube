"""Scoring engine (SPEC §7).

Computes design_fit, sector_fit, and a weighted relevance score (minus
penalties) from an opportunity's text. Pure functions — fully unit-tested.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

from worktube.config import config
from worktube.keywords import DESIGN_KEYWORDS, PENALTY_KEYWORDS, SECTOR_KEYWORDS

# Summed matched-weight at which a dimension saturates to 100.
DESIGN_SATURATION = 2.5
SECTOR_SATURATION = 2.0

# The buyer's known type is an authoritative sector signal (text keywords may
# not mention it). All of these are valid target sectors for the studio, so a
# recognized buyer_type gets baseline sector credit — otherwise government RFPs
# get ~0 sector fit and can never clear the high-fit line.
BUYER_TYPE_SECTOR = {
    "nonprofit": 1.0,
    "foundation": 1.0,
    "university": 0.9,
    "un": 0.8,
    "government": 0.7,
}


@dataclass
class ScoreResult:
    design_fit_score: float
    sector_fit_score: float
    relevance_score: float
    tags: list[str] = field(default_factory=list)
    category_normalized: list[str] = field(default_factory=list)
    penalties: list[str] = field(default_factory=list)


@lru_cache(maxsize=512)
def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    return re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.IGNORECASE)


def _match_groups(
    text: str, groups: dict[str, tuple[float, list[str]]]
) -> tuple[float, list[str]]:
    total = 0.0
    matched: list[str] = []
    for tag, (weight, phrases) in groups.items():
        if any(_phrase_pattern(p).search(text) for p in phrases):
            total += weight
            matched.append(tag)
    return total, matched


def _saturate(weight: float, saturation: float) -> float:
    if saturation <= 0:
        return 0.0
    return min(100.0, (weight / saturation) * 100.0)


def build_corpus(
    *,
    title: str | None = None,
    summary: str | None = None,
    full_text: str | None = None,
    category_raw: str | None = None,
    buyer_name: str | None = None,
) -> str:
    """Concatenate searchable fields; title counted twice so it weighs more."""
    parts = [
        (title or ""),
        (title or ""),
        summary or "",
        full_text or "",
        category_raw or "",
        buyer_name or "",
    ]
    return " ".join(parts).lower()


def score_text(
    *,
    title: str | None = None,
    summary: str | None = None,
    full_text: str | None = None,
    category_raw: str | None = None,
    buyer_name: str | None = None,
    buyer_type: str | None = None,
) -> ScoreResult:
    corpus = build_corpus(
        title=title,
        summary=summary,
        full_text=full_text,
        category_raw=category_raw,
        buyer_name=buyer_name,
    )

    design_weight, design_tags = _match_groups(corpus, DESIGN_KEYWORDS)
    sector_weight, sector_tags = _match_groups(corpus, SECTOR_KEYWORDS)

    # Add baseline sector credit from the authoritative buyer_type.
    if buyer_type:
        baseline = BUYER_TYPE_SECTOR.get(buyer_type.strip().lower())
        if baseline:
            sector_weight += baseline
            if buyer_type.strip().lower() not in sector_tags:
                sector_tags.append(buyer_type.strip().lower())

    design_fit = _saturate(design_weight, DESIGN_SATURATION)
    sector_fit = _saturate(sector_weight, SECTOR_SATURATION)

    penalty_total = 0.0
    penalties: list[str] = []
    for tag, (points, phrases) in PENALTY_KEYWORDS.items():
        if any(_phrase_pattern(p).search(corpus) for p in phrases):
            penalty_total += points
            penalties.append(tag)

    combined = config.design_weight * design_fit + config.sector_weight * sector_fit
    relevance = max(0.0, min(100.0, combined - penalty_total))

    return ScoreResult(
        design_fit_score=round(design_fit, 2),
        sector_fit_score=round(sector_fit, 2),
        relevance_score=round(relevance, 2),
        tags=sorted(design_tags + sector_tags),
        category_normalized=sorted(design_tags),
        penalties=sorted(penalties),
    )
