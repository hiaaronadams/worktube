"""Adapter mapping tests against sample payloads (no network)."""
from datetime import date

from app.ingestion.sam import map_record as sam_map
from app.ingestion.ungm import map_record as ungm_map

SAM_SAMPLE = {
    "noticeId": "abc-123",
    "title": "Branding and Communications Services",
    "fullParentPathName": "DEPT OF EXAMPLE.OFFICE OF DESIGN",
    "organizationType": "OFFICE",
    "postedDate": "2026-06-01",
    "responseDeadLine": "2026-07-15T17:00:00-04:00",
    "type": "Solicitation",
    "naicsCode": "541430",
    "classificationCode": "R",
    "uiLink": "https://sam.gov/opp/abc-123/view",
    "active": "Yes",
    "description": "Seeking a vendor for visual identity and website redesign.",
    "pointOfContact": [{"email": "buyer@example.gov"}],
    "placeOfPerformance": {
        "city": {"name": "Washington"},
        "state": {"name": "DC"},
        "country": {"name": "United States"},
    },
    "resourceLinks": ["https://sam.gov/files/spec.pdf"],
}

UNGM_SAMPLE = {
    "NoticeId": 98765,
    "Title": "Consultancy for UN agency rebrand",
    "Agency": "UNICEF",
    "Country": "Kenya",
    "UNSPSCs": "Advertising",
    "Published": "2026-06-10",
    "Deadline": "2026-07-20",
    "Reference": "REF-9",
}


def test_sam_mapping():
    opp = sam_map(SAM_SAMPLE)
    assert opp.source_type == "sam"
    assert opp.external_id == "abc-123"
    assert opp.buyer_type == "government"
    assert opp.deadline == date(2026, 7, 15)
    assert opp.posted_date == date(2026, 6, 1)
    assert opp.contact_email == "buyer@example.gov"
    assert opp.location == "Washington, DC"
    assert opp.status == "open"
    assert opp.documents_url == ["https://sam.gov/files/spec.pdf"]


def test_ungm_mapping():
    opp = ungm_map(UNGM_SAMPLE)
    assert opp.source_type == "ungm"
    assert opp.external_id == "98765"
    assert opp.buyer_type == "UN"
    assert opp.buyer_name == "UNICEF"
    assert opp.country == "Kenya"
    assert opp.deadline == date(2026, 7, 20)
    assert opp.source_url.endswith("/98765")
