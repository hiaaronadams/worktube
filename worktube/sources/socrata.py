"""Socrata (SODA) adapter — US city/state open-data procurement datasets.

One adapter, many sources: any Socrata portal (NYC, NY State, many US cities)
exposes datasets at https://<domain>/resource/<dataset>.json with SoQL query
params ($where/$order/$limit). No key required for moderate use (an app token
just raises rate limits).

Column names differ per dataset, so each source supplies a `field_map` of
NormalizedOpportunity field -> list of candidate column names. The adapter logs
the real columns of the first row on each run so the map can be tuned.
"""
from __future__ import annotations

import logging

from worktube.config import config
from worktube.models import NormalizedOpportunity
from worktube.normalize import clean_text, parse_date
from worktube.sources.base import SourceAdapter, http_get_json

logger = logging.getLogger("worktube.sources.socrata")


def _pick(row: dict, candidates: list[str] | None):
    for c in candidates or []:
        v = row.get(c)
        if v not in (None, ""):
            return v
    return None


class SocrataAdapter(SourceAdapter):
    def __init__(self, *, key: str, name: str, domain: str, dataset: str,
                 field_map: dict[str, list[str]], buyer_type: str | None = None,
                 country: str | None = "United States", source_type: str = "socrata",
                 where: str | None = None, order: str | None = None, limit: int = 1000,
                 app_token: str | None = None, **_):
        self.key = key
        self.name = name
        self.domain = domain
        self.dataset = dataset
        self.field_map = field_map
        self.buyer_type = buyer_type
        self.country = country
        self.source_type = source_type
        self.where = where
        self.order = order
        self.limit = limit
        self.app_token = app_token

    def fetch(self) -> list[NormalizedOpportunity]:
        url = f"https://{self.domain}/resource/{self.dataset}.json"
        headers = {"X-App-Token": self.app_token} if self.app_token else None
        params: dict = {"$limit": self.limit}
        if self.where:
            params["$where"] = self.where
        if self.order:
            params["$order"] = self.order
        try:
            rows = http_get_json(url, params=params, headers=headers)
        except RuntimeError as exc:
            # A bad $where/$order column 400s the whole request — fall back to a
            # plain pull so we still get data and can see the real columns.
            logger.warning("Socrata %s filtered query failed (%s); retrying plain", self.name, exc)
            rows = http_get_json(url, params={"$limit": self.limit}, headers=headers)
        if not isinstance(rows, list):
            return []
        if rows:
            logger.info("Socrata %s: %d rows; columns=%s", self.name, len(rows), sorted(rows[0].keys()))
        return [self._map(r) for r in rows]

    def _map(self, row: dict) -> NormalizedOpportunity:
        fm = self.field_map
        return NormalizedOpportunity(
            source_type=self.source_type,
            source_name=self.name,
            external_id=str(_pick(row, fm.get("external_id")) or "") or None,
            source_url=_pick(row, fm.get("source_url")),
            title=clean_text(_pick(row, fm.get("title"))) or "(untitled)",
            buyer_name=clean_text(_pick(row, fm.get("buyer_name"))),
            buyer_type=self.buyer_type,
            summary=clean_text(_pick(row, fm.get("summary"))),
            category_raw=clean_text(_pick(row, fm.get("category_raw"))),
            country=self.country,
            posted_date=parse_date(_pick(row, fm.get("posted_date"))),
            deadline=parse_date(_pick(row, fm.get("deadline"))),
            status="open",
        )
