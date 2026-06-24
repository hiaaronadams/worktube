"""Application settings, loaded from environment / .env file."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+psycopg2://worktube:worktube@localhost:5432/worktube"

    # SAM.gov
    sam_api_key: str = ""
    sam_base_url: str = "https://api.sam.gov/opportunities/v2/search"

    # UNGM
    ungm_base_url: str = "https://www.ungm.org/Public/Notice/Search"

    # Ingestion
    http_timeout_seconds: float = 30.0
    http_max_retries: int = 3
    ingest_lookback_days: int = 7

    # Scoring weights (see SPEC §7)
    design_weight: float = 0.6
    sector_weight: float = 0.4
    high_fit_threshold: float = 70.0

    # Frontend dev origins allowed to call the API (comma-separated in env)
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


settings = Settings()
