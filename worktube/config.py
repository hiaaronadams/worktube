"""Configuration — plain env-driven values, no server framework needed."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _float(name: str, default: float) -> float:
    try:
        return float(os.environ[name])
    except (KeyError, ValueError):
        return default


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


@dataclass(frozen=True)
class Config:
    # SAM.gov (https://open.gsa.gov/api/get-opportunities-public-api/)
    sam_api_key: str = os.environ.get("SAM_API_KEY", "")
    sam_base_url: str = os.environ.get(
        "SAM_BASE_URL", "https://api.sam.gov/opportunities/v2/search"
    )
    # UNGM
    ungm_base_url: str = os.environ.get(
        "UNGM_BASE_URL", "https://www.ungm.org/Public/Notice/Search"
    )

    # HTTP fetching
    http_timeout_seconds: float = _float("HTTP_TIMEOUT_SECONDS", 30.0)
    http_max_retries: int = _int("HTTP_MAX_RETRIES", 3)
    ingest_lookback_days: int = _int("INGEST_LOOKBACK_DAYS", 7)

    # Scoring (SPEC §7): final = design_weight*design_fit + sector_weight*sector_fit
    design_weight: float = _float("DESIGN_WEIGHT", 0.6)
    sector_weight: float = _float("SECTOR_WEIGHT", 0.4)
    high_fit_threshold: float = _float("HIGH_FIT_THRESHOLD", 70.0)


config = Config()
