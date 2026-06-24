# Worktube — RFP Aggregator System

A private internal system that aggregates, normalizes, and ranks public
procurement and RFP opportunities from government, UN, and curated
nonprofit/institutional sources — to help a design studio surface high-fit
branding, web, and communications work.

Design principle: **signal over completeness**. Curated high-quality sources
and design-relevant filtering over exhaustive procurement volume.

See [`docs/SPEC.md`](docs/SPEC.md) for the full technical specification.

## Stack

| Layer        | Choice                          |
|--------------|---------------------------------|
| Backend/API  | Python + FastAPI                |
| Database     | PostgreSQL 16                   |
| ORM          | SQLAlchemy 2.0                  |
| HTTP client  | httpx                           |
| Frontend     | Next.js (Phase 4 — not yet)     |
| Queue        | Redis + worker (Phase 5 — opt.) |

## Status — implementation phases

- [x] **Phase 1 — Core ingestion (in progress)**
  - [x] Postgres data model (`opportunities`, `sources`, `opportunity_status`)
  - [x] Unified normalization schema
  - [x] Scoring engine (design fit / sector fit / penalties) — **fully tested**
  - [x] Deduplication (external_id + dedup hash + content_hash)
  - [x] SAM.gov ingestion adapter
  - [x] UNGM ingestion adapter
  - [x] Ingestion orchestrator
  - [x] Read API (`/opportunities`) with filters
- [ ] **Phase 2** — Curated HTML/RSS sources
- [ ] **Phase 3** — Tagging + enrichment expansion
- [ ] **Phase 4** — Next.js dashboard
- [ ] **Phase 5** — Email/Slack digests + deadline alerts

## Quick start

```bash
# 1. Start Postgres
docker compose up -d db

# 2. Install backend deps
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp ../.env.example ../.env   # then edit values (DB url, SAM_API_KEY, ...)

# 4. Create tables + seed default sources
python -m app.scripts.init_db

# 5. Run the API
uvicorn app.main:app --reload
# -> http://localhost:8000/docs

# 6. Run an ingestion pass (requires SAM_API_KEY for SAM.gov)
python -m app.scripts.ingest --source sam
python -m app.scripts.ingest --all

# Tests (no DB / network required for the scoring + normalize suites)
pytest
```

## Layout

```
backend/
  app/
    main.py            FastAPI app + router wiring
    config.py          Settings (env-driven)
    db.py              SQLAlchemy engine/session
    models.py          ORM models (matches docs/SPEC.md §6)
    schemas.py         Pydantic request/response + normalized schema
    api/               REST routes
    ingestion/         Source adapters + orchestrator + dedup
    enrichment/        Scoring engine + keyword config
    normalize.py       Date/currency/text normalization helpers
    scripts/           init_db, ingest CLIs
  tests/               Unit tests (scoring, dedup, normalize)
docs/SPEC.md           Full spec (V1)
docker-compose.yml     Local Postgres
```
