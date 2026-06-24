"""FastAPI application entry point."""
from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api import opportunities

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Worktube — RFP Aggregator",
    description="Aggregates, normalizes, and ranks RFP/procurement opportunities.",
    version="0.1.0",
)

app.include_router(opportunities.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
