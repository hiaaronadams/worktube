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
        # Procurement notices whose title looks design/branding/web/comms
        # related, most recent first. Filtering at the source keeps the report
        # to signal instead of all ~1000 municipal notices.
        "where": (
            "section_name='Procurement' AND ("
            "upper(short_title) like '%DESIGN%' OR upper(short_title) like '%BRAND%' OR "
            "upper(short_title) like '%MARKETING%' OR upper(short_title) like '%COMMUNICAT%' OR "
            "upper(short_title) like '%WEBSITE%' OR upper(short_title) like '%CREATIVE%' OR "
            "upper(short_title) like '%GRAPHIC%' OR upper(short_title) like '%ADVERTIS%')"
        ),
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
