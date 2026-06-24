"""Application settings, loaded from environment / .env file."""
from __future__ import annotations

from pydantic import field_validator
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

    # Comma-separated list of allowed browser origins. Bare hostnames are
    # assumed https://. Not needed when the API is served same-origin (behind
    # the Caddy /api proxy) but kept for split-origin / dev setups.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @field_validator("database_url")
    @classmethod
    def _normalize_db_scheme(cls, v: str) -> str:
        # Managed Postgres providers hand out postgres:// or postgresql:// URLs;
        # SQLAlchemy + psycopg2 needs the explicit driver in the scheme.
        if v.startswith("postgres://"):
            return "postgresql+psycopg2://" + v[len("postgres://"):]
        if v.startswith("postgresql://"):
            return "postgresql+psycopg2://" + v[len("postgresql://"):]
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        origins: list[str] = []
        for raw in self.cors_origins.split(","):
            origin = raw.strip()
            if not origin:
                continue
            if not origin.startswith(("http://", "https://")):
                origin = "https://" + origin
            origins.append(origin)
        return origins


settings = Settings()
