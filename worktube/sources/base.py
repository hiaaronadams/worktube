"""Base class + HTTP helpers for source adapters."""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod

import httpx

from worktube.config import config
from worktube.models import NormalizedOpportunity

logger = logging.getLogger("worktube.sources")


class SourceAdapter(ABC):
    """Fetches raw data from one source and emits NormalizedOpportunity rows."""

    key: str
    name: str

    @classmethod
    def available(cls) -> tuple[bool, str]:
        """(is_configured, reason_if_not). Override to gate on API keys etc."""
        return True, ""

    @abstractmethod
    def fetch(self) -> list[NormalizedOpportunity]:
        ...


def http_get_json(url: str, *, params: dict | None = None, headers: dict | None = None) -> dict:
    """GET with retries + exponential backoff; returns parsed JSON."""
    last_exc: Exception | None = None
    for attempt in range(1, config.http_max_retries + 1):
        try:
            resp = httpx.get(url, params=params, headers=headers, timeout=config.http_timeout_seconds)
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_exc = exc
            backoff = 2 ** (attempt - 1)
            logger.warning("GET %s failed (%d/%d): %s", url, attempt, config.http_max_retries, exc)
            if attempt < config.http_max_retries:
                time.sleep(backoff)
    raise RuntimeError(f"GET {url} failed after {config.http_max_retries} attempts") from last_exc


def http_post_json(
    url: str, *, json: dict | None = None, headers: dict | None = None
) -> dict | list:
    """POST with retries + exponential backoff; returns parsed JSON."""
    last_exc: Exception | None = None
    for attempt in range(1, config.http_max_retries + 1):
        try:
            resp = httpx.post(url, json=json, headers=headers, timeout=config.http_timeout_seconds)
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_exc = exc
            backoff = 2 ** (attempt - 1)
            logger.warning("POST %s failed (%d/%d): %s", url, attempt, config.http_max_retries, exc)
            if attempt < config.http_max_retries:
                time.sleep(backoff)
    raise RuntimeError(f"POST {url} failed after {config.http_max_retries} attempts") from last_exc
