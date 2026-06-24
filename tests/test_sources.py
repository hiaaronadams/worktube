from datetime import date

from worktube.sources.sam import map_record as sam_map
from worktube.sources.ungm import map_record as ungm_map
from worktube.sources.sample import sample_opportunities

SAM_SAMPLE = {
    "noticeId": "abc-123",
    "title": "Branding and Communications Services",
    "fullParentPathName": "DEPT OF EXAMPLE.OFFICE OF DESIGN",
    "postedDate": "2026-06-01",
    "responseDeadLine": "2026-07-15T17:00:00-04:00",
    "type": "Solicitation",
    "naicsCode": "541430",
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
}


def test_sam_mapping():
    opp = sam_map(SAM_SAMPLE)
    assert opp.source_type == "sam"
    assert opp.external_id == "abc-123"
    assert opp.buyer_type == "government"
    assert opp.deadline == date(2026, 7, 15)
    assert opp.contact_email == "buyer@example.gov"
    assert opp.location == "Washington, DC"
    assert opp.documents_url == ["https://sam.gov/files/spec.pdf"]


def test_ungm_mapping():
    opp = ungm_map(UNGM_SAMPLE)
    assert opp.source_type == "ungm"
    assert opp.external_id == "98765"
    assert opp.buyer_type == "UN"
    assert opp.country == "Kenya"
    assert opp.deadline == date(2026, 7, 20)
    assert opp.source_url.endswith("/98765")


def test_sample_data_is_non_empty():
    opps = sample_opportunities()
    assert len(opps) >= 6
    assert all(o.title for o in opps)
