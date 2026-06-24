"""Create tables and seed the default Tier-1 sources.

    python -m app.scripts.init_db

Idempotent: safe to re-run. For real schema migrations, adopt Alembic later.
"""
from __future__ import annotations

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import Source  # noqa: F401  (ensure models are imported)
from app import models  # noqa: F401

DEFAULT_SOURCES = [
    {
        "name": "SAM.gov",
        "source_type": "api",
        "base_url": "https://api.sam.gov/opportunities/v2/search",
        "schedule_interval": "12h",
        "fetch_config": {"lookback_days": 7},
    },
    {
        "name": "UNGM",
        "source_type": "api",
        "base_url": "https://www.ungm.org/Public/Notice/Search",
        "schedule_interval": "12h",
        "fetch_config": {"page_size": 100},
    },
]


def main() -> None:
    print("Creating tables...")
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        for spec in DEFAULT_SOURCES:
            exists = session.scalar(select(Source).where(Source.name == spec["name"]))
            if exists:
                print(f"  source '{spec['name']}' already present")
                continue
            session.add(Source(**spec))
            print(f"  seeded source '{spec['name']}'")
        session.commit()
    print("Done.")


if __name__ == "__main__":
    main()
