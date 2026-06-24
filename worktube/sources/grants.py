"""Grants.gov adapter — US federal grant opportunities (Search2 API).

Public JSON API, no key required:
  POST https://api.grants.gov/v1/api/search2
Useful for design/communications/outreach grants. `map_record` is isolated for
unit testing against a sample payload.
"""
from __future__ import annotations

import logging

from worktube.config import config
from worktube.models import NormalizedOpportunity
from worktube.normalize import clean_text, parse_date
from worktube.sources.base import SourceAdapter, http_post_json

logger = logging.getLogger("worktube.sources.grants")

API_URL = "https://api.grants.gov/v1/api/search2"
# Broad design/comms keyword query — scoring narrows it further downstream.
DEFAULT_KEYWORD = "design"


def map_record(rec: dict) -> NormalizedOpportunity:
    ext = rec.get("id") or rec.get("number")
    agency = clean_text(rec.get("agency") or rec.get("agencyName") or rec.get("agencyCode"))
    cfda = rec.get("cfdaList")
    if isinstance(cfda, list):
        cfda = ", ".join(str(c) for c in cfda)
    return NormalizedOpportunity(
        source_type="grants",
        source_name="Grants.gov",
        source_url=f"https://www.grants.gov/search-results-detail/{ext}" if ext else None,
        external_id=str(ext) if ext is not None else None,
        title=clean_text(rec.get("title")) or "(untitled)",
        buyer_name=agency,
        buyer_type="government",
        summary=clean_text(rec.get("description")),
        category_raw=clean_text(cfda) or rec.get("docType"),
        country="United States",
        posted_date=parse_date(rec.get("openDate")),
        deadline=parse_date(rec.get("closeDate")),
        status="open" if (rec.get("oppStatus") or "").lower() == "posted" else "unknown",
    )


class GrantsAdapter(SourceAdapter):
    key = "grants"
    name = "Grants.gov"

    def __init__(self, *, keyword: str | None = None, rows: int = 100, **_):
        self.keyword = keyword or DEFAULT_KEYWORD
        self.rows = rows

    def fetch(self) -> list[NormalizedOpportunity]:
        body = {
            "keyword": self.keyword,
            "oppStatuses": "posted",
            "rows": self.rows,
            "startRecordNum": 0,
        }
        payload = http_post_json(API_URL, json=body, headers={"Content-Type": "application/json"})
        data = payload.get("data") if isinstance(payload, dict) else None
        hits = (data or {}).get("oppHits") or []
        logger.info("Grants.gov returned %d records", len(hits))
        return [map_record(r) for r in hits]
