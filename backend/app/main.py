"""FastAPI application entry point."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import opportunities
from app.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Worktube — RFP Aggregator",
    description="Aggregates, normalizes, and ranks RFP/procurement opportunities.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(opportunities.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
