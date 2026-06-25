"""Curated RSS/Atom feeds — add your own sources here.

Each entry becomes its own source in the report, with its own ✓/✕ status.
Find a feed URL (look for an RSS icon, or try <site>/rss, /feed, /rss.xml),
then add a dict below and re-run `python generate_report.py`.

Fields:
  key         short unique id (no spaces), e.g. "ny_state"
  name        display name, e.g. "NY State Contract Reporter"
  url         the RSS/Atom feed URL
  source_type bucket label shown in the Source filter (default "rss")
  buyer_type  one of: government, nonprofit, UN, university, foundation (optional)
  country     optional, e.g. "United States"

Example (uncomment + replace with a real feed URL):

    {
        "key": "ny_state",
        "name": "NY State Contract Reporter",
        "url": "https://www.example.ny.gov/rfps/feed",
        "source_type": "state",
        "buyer_type": "government",
        "country": "United States",
    },
"""
from __future__ import annotations

FEEDS: list[dict] = [
    # rfpdb.com serves an incomplete TLS chain -> verify=False (public listings).
    {
        "key": "rfpdb_a",
        "name": "RFPDB (feed A)",
        "url": "https://rfpdb.com/view/feed/identifier/8870b1408f4d.rss",
        "source_type": "rfpdb",
        "country": "United States",
        "verify": False,
    },
    {
        "key": "rfpdb_b",
        "name": "RFPDB (feed B)",
        "url": "https://rfpdb.com/view/feed/identifier/701371781d3c.rss",
        "source_type": "rfpdb",
        "country": "United States",
        "verify": False,
    },
]
