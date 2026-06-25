"""Generic RSS/Atom adapter — the easiest way to add curated sources.

Many procurement portals, foundations, arts orgs, and universities publish an
RSS feed of new RFPs/notices. Add one by editing worktube/feeds.py; each feed
becomes its own source (with its own ✓/✕ status in the report).

Parsing uses the stdlib XML parser (no extra deps). Deadlines rarely appear in
feed items, so deadline is left blank unless present in the item.
"""
from __future__ import annotations

import logging
from xml.etree import ElementTree as ET

import httpx

from worktube.config import config
from worktube.models import NormalizedOpportunity
from worktube.normalize import clean_text, parse_date
from worktube.sources.base import SourceAdapter

logger = logging.getLogger("worktube.sources.rss")


def _text(el, *tags):
    for tag in tags:
        found = el.find(tag)
        if found is not None and (found.text or "").strip():
            return found.text.strip()
        # Atom links carry the URL in an attribute
        if found is not None and found.get("href"):
            return found.get("href")
    return None


def parse_feed(xml: str, *, source_type: str, source_name: str, buyer_type: str | None,
               country: str | None) -> list[NormalizedOpportunity]:
    root = ET.fromstring(xml)
    # RSS <item> or Atom <entry> (namespaces stripped for simplicity)
    items = root.iter("item")
    out: list[NormalizedOpportunity] = []
    found_any = False
    for it in items:
        found_any = True
        out.append(_map_item(it, source_type, source_name, buyer_type, country, atom=False))
    if not found_any:
        for it in root.iter("{http://www.w3.org/2005/Atom}entry"):
            out.append(_map_item(it, source_type, source_name, buyer_type, country, atom=True))
    return out


def _map_item(it, source_type, source_name, buyer_type, country, *, atom):
    if atom:
        ns = "{http://www.w3.org/2005/Atom}"
        title = _text(it, f"{ns}title")
        link = _text(it, f"{ns}link")
        summary = _text(it, f"{ns}summary", f"{ns}content")
        posted = _text(it, f"{ns}updated", f"{ns}published")
    else:
        title = _text(it, "title")
        link = _text(it, "link")
        summary = _text(it, "description")
        posted = _text(it, "pubDate")
    return NormalizedOpportunity(
        source_type=source_type,
        source_name=source_name,
        source_url=link,
        external_id=link,
        title=clean_text(title) or "(untitled)",
        buyer_type=buyer_type,
        summary=clean_text(summary),
        country=country,
        posted_date=parse_date(posted),
        status="open",
    )


class RssAdapter(SourceAdapter):
    def __init__(self, *, key: str, name: str, url: str, source_type: str = "rss",
                 buyer_type: str | None = None, country: str | None = None, **_):
        self.key = key
        self.name = name
        self.url = url
        self.source_type = source_type
        self.buyer_type = buyer_type
        self.country = country

    def fetch(self) -> list[NormalizedOpportunity]:
        resp = httpx.get(self.url, timeout=config.http_timeout_seconds,
                         headers={"User-Agent": "worktube/1.0"})
        resp.raise_for_status()
        items = parse_feed(
            resp.text,
            source_type=self.source_type,
            source_name=self.name,
            buyer_type=self.buyer_type,
            country=self.country,
        )
        sample = items[0].title if items else "(none)"
        logger.info("RSS %s returned %d items; first: %r", self.name, len(items), sample)
        return items
