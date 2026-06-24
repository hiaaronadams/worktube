"""SAM.gov adapter — US federal procurement opportunities (Get Opportunities API v2).

Docs: https://open.gsa.gov/api/get-opportunities-public-api/
Requires SAM_API_KEY. Mapping is isolated in `map_record` so it can be unit
tested against a saved sample payload without hitting the network.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

from app.config import settings
from app.ingestion.base import SourceAdapter, http_get_json
from app.normalize import clean_text, parse_date
from app.schemas import NormalizedOpportunity

logger = logging.getLogger("worktube.ingestion.sam")

_DATE_FMT = "%m/%d/%Y"


def map_record(rec: dict) -> NormalizedOpportunity:
    contacts = rec.get("pointOfContact") or []
    contact_email = None
    for c in contacts:
        if c.get("email"):
            contact_email = c["email"]
            break

    category_parts = [
        rec.get("type"),
        rec.get("naicsCode"),
        rec.get("classificationCode"),
    ]
    category_raw = " / ".join(p for p in category_parts if p) or None

    pop = rec.get("placeOfPerformance") or {}
    country = (pop.get("country") or {}).get("name") if isinstance(pop.get("country"), dict) else pop.get("country")
    city = (pop.get("city") or {}).get("name") if isinstance(pop.get("city"), dict) else None
    state = (pop.get("state") or {}).get("name") if isinstance(pop.get("state"), dict) else None
    location = ", ".join(p for p in (city, state) if p) or None

    links = rec.get("resourceLinks") or []

    return NormalizedOpportunity(
        source_type="sam",
        source_name="SAM.gov",
        source_url=rec.get("uiLink"),
        external_id=rec.get("noticeId") or rec.get("solicitationNumber"),
        title=clean_text(rec.get("title")) or "(untitled)",
        buyer_name=clean_text(rec.get("fullParentPathName")) or rec.get("organizationType"),
        buyer_type="government",
        summary=clean_text(rec.get("description")),
        full_text=None,
        category_raw=category_raw,
        location=location,
        country=country or "United States",
        posted_date=parse_date(rec.get("postedDate")),
        deadline=parse_date(rec.get("responseDeadLine")),
        status="open" if (rec.get("active") in (True, "Yes", "true")) else "unknown",
        documents_url=[u for u in links if isinstance(u, str)],
        contact_email=contact_email,
    )


class SamAdapter(SourceAdapter):
    key = "sam"
    name = "SAM.gov"

    def __init__(self, *, lookback_days: int | None = None, limit: int = 100):
        self.lookback_days = lookback_days or settings.ingest_lookback_days
        self.limit = limit

    def fetch(self) -> list[NormalizedOpportunity]:
        if not settings.sam_api_key:
            raise RuntimeError("SAM_API_KEY is not set; cannot fetch SAM.gov.")

        today = date.today()
        params = {
            "api_key": settings.sam_api_key,
            "postedFrom": (today - timedelta(days=self.lookback_days)).strftime(_DATE_FMT),
            "postedTo": today.strftime(_DATE_FMT),
            "limit": self.limit,
            "offset": 0,
        }
        payload = http_get_json(settings.sam_base_url, params=params)
        records = payload.get("opportunitiesData") or []
        logger.info("SAM.gov returned %d records", len(records))
        return [map_record(r) for r in records]
