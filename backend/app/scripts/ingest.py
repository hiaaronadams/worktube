"""Run an ingestion pass.

    python -m app.scripts.ingest --source sam
    python -m app.scripts.ingest --all
"""
from __future__ import annotations

import argparse
import json

from app.db import SessionLocal
from app.ingestion.orchestrator import ADAPTERS, run_all, run_source


def main() -> None:
    parser = argparse.ArgumentParser(description="Worktube ingestion")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", choices=sorted(ADAPTERS), help="run one source")
    group.add_argument("--all", action="store_true", help="run every source")
    args = parser.parse_args()

    with SessionLocal() as session:
        if args.all:
            results = run_all(session)
            print(json.dumps([r.as_dict() for r in results], indent=2))
        else:
            result = run_source(session, args.source)
            print(json.dumps(result.as_dict(), indent=2))


if __name__ == "__main__":
    main()
