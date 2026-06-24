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


def _request_json(method: str, url: str, **kwargs):
    """Shared GET/POST with retries. On failure raises RuntimeError carrying the
    real reason (HTTP status + the API's error body), so the report's ✕ tooltip
    is diagnostic. 4xx auth/validation errors are not retried (they won't fix
    themselves) — only 429 and network/5xx errors back off and retry.
    """
    last_detail = "unknown error"
    for attempt in range(1, config.http_max_retries + 1):
        try:
            resp = httpx.request(method, url, timeout=config.http_timeout_seconds, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            body = exc.response.text.strip().replace("\n", " ")[:180]
            last_detail = f"HTTP {code} {exc.response.reason_phrase}" + (f" — {body}" if body else "")
            # Don't retry client errors except rate-limiting.
            if 400 <= code < 500 and code != 429:
                break
        except httpx.HTTPError as exc:
            last_detail = f"{type(exc).__name__}: {exc}"
        except ValueError as exc:
            last_detail = f"invalid JSON response: {exc}"
        logger.warning("%s %s failed (%d/%d): %s", method, url, attempt,
                       config.http_max_retries, last_detail)
        if attempt < config.http_max_retries:
            time.sleep(2 ** (attempt - 1))
    raise RuntimeError(last_detail)


def http_get_json(url: str, *, params: dict | None = None, headers: dict | None = None) -> dict:
    return _request_json("GET", url, params=params, headers=headers)


def http_post_json(url: str, *, json: dict | None = None, headers: dict | None = None) -> dict | list:
    return _request_json("POST", url, json=json, headers=headers)
