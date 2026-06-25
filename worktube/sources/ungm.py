"""UNGM adapter — United Nations Global Marketplace notices.

NOTE: UNGM has no fully documented public JSON API. `map_record` is tolerant
(multiple candidate keys) and isolated so it can be unit-tested and adjusted
once the live response schema is confirmed.
"""
from __future__ import annotations

import logging

import httpx

from worktube.config import config
from worktube.models import NormalizedOpportunity
from worktube.normalize import clean_text, parse_date
from worktube.sources.base import SourceAdapter

logger = logging.getLogger("worktube.sources.ungm")

NOTICE_PAGE = "https://www.ungm.org/Public/Notice"

# Graphic-design UNSPSC families (82140000 Graphic design + its groups).
DESIGN_UNSPSC = ["82140000", "82141500", "82141600"]

# Look like a browser — UNGM's search endpoint 403s plain API clients.
_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.ungm.org",
    "Referer": NOTICE_PAGE,
}


def _first(rec: dict, *keys: str):
    for k in keys:
        if rec.get(k) not in (None, ""):
            return rec[k]
    return None


def map_record(rec: dict) -> NormalizedOpportunity:
    external_id = _first(rec, "NoticeId", "Id", "Reference", "ReferenceNo")
    title = clean_text(_first(rec, "Title", "TitleEN", "Name")) or "(untitled)"
    buyer = clean_text(_first(rec, "Agency", "AgencyName", "UNOrganization", "Organization"))
    country = clean_text(_first(rec, "Country", "CountryName", "DutyStation"))
    category = clean_text(_first(rec, "UNSPSCs", "Category", "TypeName", "NoticeType"))

    deadline = parse_date(_first(rec, "Deadline", "DeadlineOn", "ClosingDate", "DeadlineUTC"))
    posted = parse_date(_first(rec, "Published", "PublishedOn", "PublishedUTC", "DatePublished"))

    link = _first(rec, "Link", "Url")
    if not link and external_id:
        link = f"https://www.ungm.org/Public/Notice/{external_id}"

    return NormalizedOpportunity(
        source_type="ungm",
        source_name="UNGM",
        source_url=link,
        external_id=str(external_id) if external_id is not None else None,
        title=title,
        buyer_name=buyer,
        buyer_type="UN",
        summary=clean_text(_first(rec, "Description", "Summary")),
        category_raw=category,
        location=country,
        country=country,
        posted_date=posted,
        deadline=deadline,
        status="open",
        contact_email=clean_text(_first(rec, "ContactEmail", "Email")),
    )


class UngmAdapter(SourceAdapter):
    key = "ungm"
    name = "UNGM"

    def __init__(self, *, page_size: int = 100):
        self.page_size = page_size

    def fetch(self) -> list[NormalizedOpportunity]:
        body = {
            "PageIndex": 0,
            "PageSize": self.page_size,
            "Title": "",
            "Description": "",
            "Reference": "",
            "Flags": [],
            "UNSPSCs": DESIGN_UNSPSC,
            "NoticeTypes": [],
            "Agencies": [],
            "Countries": [],
            "Regions": [],
            "SortField": "DatePublished",
            "Ascending": False,
        }
        # Share cookies between a page visit and the search POST to clear the
        # anti-bot 403.
        with httpx.Client(headers=_BROWSER_HEADERS, timeout=config.http_timeout_seconds,
                          follow_redirects=True) as client:
            client.get(NOTICE_PAGE)
            resp = client.post(config.ungm_base_url, json=body)
            resp.raise_for_status()
            payload = resp.json()

        if isinstance(payload, dict):
            records = payload.get("Notices") or payload.get("Results") or payload.get("data") or []
        else:
            records = payload
        logger.info("UNGM returned %d records", len(records))
        return [map_record(r) for r in records]
