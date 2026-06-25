"""SAM.gov adapter — US federal procurement opportunities (Get Opportunities v2).

Docs: https://open.gsa.gov/api/get-opportunities-public-api/  (requires SAM_API_KEY)
`map_record` is isolated so it can be unit-tested against a sample payload.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

from worktube.config import config
from worktube.models import NormalizedOpportunity
from worktube.normalize import clean_text, parse_date
from worktube.sources.base import SourceAdapter, http_get_json

logger = logging.getLogger("worktube.sources.sam")

_DATE_FMT = "%m/%d/%Y"

# Design-relevant NAICS codes. SAM's public keys allow only ~10 requests/day,
# and we make one request per code — so keep this list short (one run = N
# requests). These four cover the studio's core work.
DESIGN_NAICS = [
    "541430",  # Graphic Design Services
    "541490",  # Other Specialized Design Services
    "541810",  # Advertising Agencies (campaigns / comms)
    "541511",  # Custom Computer Programming (web design / build)
]


def map_record(rec: dict) -> NormalizedOpportunity:
    contacts = rec.get("pointOfContact") or []
    contact_email = next((c["email"] for c in contacts if c.get("email")), None)

    category_parts = [rec.get("type"), rec.get("naicsCode"), rec.get("classificationCode")]
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
        # NOTE: SAM's "description" field is an API URL (needs the key), not
        # text — never use it as the summary. Title + NAICS carry the signal.
        summary=None,
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

    @classmethod
    def available(cls) -> tuple[bool, str]:
        return (bool(config.sam_api_key), "" if config.sam_api_key else "SAM_API_KEY not set")

    def __init__(self, *, lookback_days: int | None = None, limit: int = 100,
                 naics: list[str] | None = None):
        self.lookback_days = lookback_days or config.ingest_lookback_days
        self.limit = limit
        self.naics = naics or DESIGN_NAICS

    def fetch(self) -> list[NormalizedOpportunity]:
        if not config.sam_api_key:
            raise RuntimeError("SAM_API_KEY is not set; cannot fetch SAM.gov.")
        today = date.today()
        posted_from = (today - timedelta(days=self.lookback_days)).strftime(_DATE_FMT)
        posted_to = today.strftime(_DATE_FMT)

        seen: set[str] = set()
        records: list[dict] = []
        for code in self.naics:
            params = {
                "api_key": config.sam_api_key,
                "postedFrom": posted_from,
                "postedTo": posted_to,
                "ncode": code,
                "limit": self.limit,
                "offset": 0,
            }
            payload = http_get_json(config.sam_base_url, params=params)
            for rec in payload.get("opportunitiesData") or []:
                key = rec.get("noticeId") or rec.get("solicitationNumber") or id(rec)
                if key in seen:
                    continue
                seen.add(key)
                records.append(rec)
        logger.info("SAM.gov returned %d design-relevant records across %d NAICS",
                    len(records), len(self.naics))
        return [map_record(r) for r in records]
