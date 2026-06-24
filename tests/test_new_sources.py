from datetime import date

from worktube.sources.grants import map_record as grants_map
from worktube.sources.rss import parse_feed

GRANTS_SAMPLE = {
    "id": "350123",
    "number": "ABC-25-001",
    "title": "Communications and Outreach Design Services",
    "agency": "Department of Example",
    "openDate": "06/01/2026",
    "closeDate": "07/31/2026",
    "oppStatus": "posted",
    "cfdaList": ["12.345", "67.890"],
}

RSS_SAMPLE = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>NY RFPs</title>
  <item>
    <title>Rebranding services for state agency</title>
    <link>https://example.ny.gov/rfp/1</link>
    <description>Seeking branding and visual identity work.</description>
    <pubDate>Mon, 15 Jun 2026 09:00:00 GMT</pubDate>
  </item>
  <item>
    <title>Office furniture procurement</title>
    <link>https://example.ny.gov/rfp/2</link>
    <description>Chairs and desks.</description>
  </item>
</channel></rss>"""


def test_grants_mapping():
    opp = grants_map(GRANTS_SAMPLE)
    assert opp.source_type == "grants"
    assert opp.external_id == "350123"
    assert opp.buyer_type == "government"
    assert opp.deadline == date(2026, 7, 31)
    assert opp.posted_date == date(2026, 6, 1)
    assert opp.status == "open"
    assert opp.source_url.endswith("/350123")
    assert "12.345" in opp.category_raw


def test_rss_parsing():
    opps = parse_feed(
        RSS_SAMPLE, source_type="state", source_name="NY RFPs",
        buyer_type="government", country="United States",
    )
    assert len(opps) == 2
    first = opps[0]
    assert first.source_type == "state"
    assert first.buyer_type == "government"
    assert first.title == "Rebranding services for state agency"
    assert first.source_url == "https://example.ny.gov/rfp/1"
    assert first.posted_date == date(2026, 6, 15)
