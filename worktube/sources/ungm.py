"""UNGM adapter — United Nations Global Marketplace notices.

NOTE: UNGM has no fully documented public JSON API. `map_record` is tolerant
(multiple candidate keys) and isolated so it can be unit-tested and adjusted
once the live response schema is confirmed.
"""
from __future__ import annotations

import logging

from worktube.config import config
from worktube.models import NormalizedOpportunity
from worktube.normalize import clean_text, parse_date
from worktube.sources.base import SourceAdapter, http_post_json

logger = logging.getLogger("worktube.sources.ungm")


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
            "NoticeTypes": [],
            "SortField": "DatePublished",
            "Ascending": False,
        }
        payload = http_post_json(
            config.ungm_base_url,
            json=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        if isinstance(payload, dict):
            records = payload.get("Notices") or payload.get("Results") or payload.get("data") or []
        else:
            records = payload
        logger.info("UNGM returned %d records", len(records))
        return [map_record(r) for r in records]
