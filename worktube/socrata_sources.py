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
        # Procurement notices only, most recent first.
        "where": "section_name='Procurement'",
        "order": "start_date DESC",
        "limit": 1000,
        "field_map": {
            "external_id": ["request_id", "pin"],
            "title": ["short_title", "title"],
            "buyer_name": ["agency_name", "agency"],
            "summary": ["description_of_services", "additional_description_1", "short_title"],
            "category_raw": ["type_of_notice_description", "category_description",
                              "selection_method_description"],
            "posted_date": ["start_date", "publication_date"],
            "deadline": ["end_date", "due_date"],
        },
    },
]
