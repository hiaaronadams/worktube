"""Socrata open-data procurement sources (US city/state). Add more by copying
an entry and pointing it at another portal's dataset. Each becomes its own
source with a ✓/✕ status. Column names are confirmed/refined from the run log
(the adapter logs the real columns each run).
"""
from __future__ import annotations

SOCRATA_SOURCES: list[dict] = [
    {
        "key": "nyc_cityrecord",
        "name": "NYC City Record",
        "domain": "data.cityofnewyork.us",
        "dataset": "dg92-zbpx",
        "source_type": "nyc",
        "buyer_type": "government",
        "country": "United States",
        # Pull recent procurement notices; the report's relevance floor (applied
        # uniformly across all sources) keeps only the design-relevant ones.
        "where": "section_name='Procurement'",
        "order": "start_date DESC",
        "limit": 1000,
        # Columns confirmed from the live dataset.
        "field_map": {
            "external_id": ["request_id", "pin"],
            "title": ["short_title"],
            "buyer_name": ["agency_name"],
            "summary": ["additional_description_1", "short_title"],
            "category_raw": ["type_of_notice_description", "category_description",
                              "selection_method_description"],
            "posted_date": ["start_date"],
            "deadline": ["end_date"],
        },
    },
]
