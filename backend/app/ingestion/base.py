"""Base classes + HTTP helper for source adapters."""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod

import httpx

from app.config import settings
from app.schemas import NormalizedOpportunity

logger = logging.getLogger("worktube.ingestion")


class SourceAdapter(ABC):
    """A source adapter fetches raw data and emits NormalizedOpportunity rows.

    Subclasses implement `fetch()`. Keep adapters side-effect free with respect
    to the database — persistence is handled by the orchestrator.
    """

    #: stable key, also used as Opportunity.source_type
    key: str
    #: human-readable name (Opportunity.source_name)
    name: str

    @abstractmethod
    def fetch(self) -> list[NormalizedOpportunity]:
        ...


def http_get_json(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
) -> dict:
    """GET with retries + exponential backoff; returns parsed JSON."""
    last_exc: Exception | None = None
    for attempt in range(1, settings.http_max_retries + 1):
        try:
            resp = httpx.get(
                url,
                params=params,
                headers=headers,
                timeout=settings.http_timeout_seconds,
            )
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPError, ValueError) as exc:  # ValueError = bad JSON
            last_exc = exc
            backoff = 2 ** (attempt - 1)
            logger.warning(
                "GET %s failed (attempt %d/%d): %s — retrying in %ss",
                url, attempt, settings.http_max_retries, exc, backoff,
            )
            if attempt < settings.http_max_retries:
                time.sleep(backoff)
    raise RuntimeError(f"GET {url} failed after {settings.http_max_retries} attempts") from last_exc


def http_post_json(
    url: str,
    *,
    json: dict | None = None,
    data: dict | None = None,
    headers: dict | None = None,
) -> dict | list:
    """POST with retries + exponential backoff; returns parsed JSON."""
    last_exc: Exception | None = None
    for attempt in range(1, settings.http_max_retries + 1):
        try:
            resp = httpx.post(
                url,
                json=json,
                data=data,
                headers=headers,
                timeout=settings.http_timeout_seconds,
            )
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_exc = exc
            backoff = 2 ** (attempt - 1)
            logger.warning(
                "POST %s failed (attempt %d/%d): %s — retrying in %ss",
                url, attempt, settings.http_max_retries, exc, backoff,
            )
            if attempt < settings.http_max_retries:
                time.sleep(backoff)
    raise RuntimeError(f"POST {url} failed after {settings.http_max_retries} attempts") from last_exc
