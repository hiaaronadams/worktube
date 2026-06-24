"""Sample data — a realistic spread used for demo reports and as a fallback
when no live source is configured/reachable. Deadlines are relative to today
so the report always looks current.
"""
from __future__ import annotations

from datetime import date, timedelta

from worktube.models import NormalizedOpportunity
from worktube.sources.base import SourceAdapter


def _d(days: int) -> date:
    return date.today() + timedelta(days=days)


def sample_opportunities() -> list[NormalizedOpportunity]:
    return [
        NormalizedOpportunity(
            source_type="ungm", source_name="UNGM", external_id="SAMPLE-UN-1",
            source_url="https://www.ungm.org/Public/Notice/SAMPLE-UN-1",
            title="Rebrand and visual identity system for global health foundation",
            buyer_name="World Health Foundation", buyer_type="foundation",
            summary="Seeking a design studio to lead a full rebrand: brand strategy, "
                    "visual identity, design system, and a website redesign.",
            category_raw="Advertising and brand management",
            country="Switzerland", location="Geneva",
            posted_date=_d(-3), deadline=_d(21), status="open",
            contact_email="procurement@whf.example.org",
        ),
        NormalizedOpportunity(
            source_type="nonprofit", source_name="Arts Council RFP", external_id="SAMPLE-ARTS-1",
            source_url="https://example.org/arts-rfp",
            title="Editorial design and annual report for arts & culture nonprofit",
            buyer_name="Metropolitan Arts Alliance", buyer_type="nonprofit",
            summary="Editorial design of our annual report and a refreshed visual "
                    "identity for an arts and culture grantmaking nonprofit.",
            category_raw="Graphic design services",
            country="United States", location="New York, NY",
            posted_date=_d(-5), deadline=_d(12), status="open",
        ),
        NormalizedOpportunity(
            source_type="sam", source_name="SAM.gov", external_id="SAMPLE-SAM-1",
            source_url="https://sam.gov/opp/sample-1/view",
            title="Communications strategy and campaign assets for public health agency",
            buyer_name="Department of Public Health", buyer_type="government",
            summary="Communications strategy, creative campaign, and campaign assets "
                    "for a community health equity initiative.",
            category_raw="Solicitation / 541810 / R",
            country="United States", location="Atlanta, GA",
            posted_date=_d(-2), deadline=_d(30), status="open",
            contact_email="contracts@dph.example.gov",
        ),
        NormalizedOpportunity(
            source_type="university", source_name="University Procurement", external_id="SAMPLE-UNI-1",
            source_url="https://example.edu/procurement/web-redesign",
            title="University website redesign and design system",
            buyer_name="State University", buyer_type="university",
            summary="Website redesign with a reusable design system and UX/UI "
                    "improvements across the main .edu domain.",
            category_raw="Web design services",
            country="United States", location="Madison, WI",
            posted_date=_d(-7), deadline=_d(45), status="open",
        ),
        NormalizedOpportunity(
            source_type="ungm", source_name="UNGM", external_id="SAMPLE-UN-2",
            source_url="https://www.ungm.org/Public/Notice/SAMPLE-UN-2",
            title="Graphic design services for climate & sustainability programme",
            buyer_name="UN Environment Programme", buyer_type="UN",
            summary="Graphic design and marketing collateral for a climate and "
                    "sustainability awareness programme.",
            category_raw="Graphic design",
            country="Kenya", location="Nairobi",
            posted_date=_d(-1), deadline=_d(9), status="open",
        ),
        NormalizedOpportunity(
            source_type="nonprofit", source_name="Foundation RFP", external_id="SAMPLE-MEDIA-1",
            source_url="https://example.org/journalism-rebrand",
            title="Brand refresh for independent journalism nonprofit",
            buyer_name="Independent Newsroom Fund", buyer_type="nonprofit",
            summary="Brand refresh and editorial design for a nonprofit supporting "
                    "independent journalism and public media.",
            category_raw="Branding",
            country="United States", location="Remote",
            posted_date=_d(-4), deadline=_d(60), status="open",
        ),
        # --- Lower-fit / penalized examples (show the scoring working) ---
        NormalizedOpportunity(
            source_type="sam", source_name="SAM.gov", external_id="SAMPLE-SAM-2",
            source_url="https://sam.gov/opp/sample-2/view",
            title="Computer hardware procurement and IT support services",
            buyer_name="General Services Administration", buyer_type="government",
            summary="Bulk computer hardware procurement and ongoing IT support services, "
                    "including network infrastructure.",
            category_raw="Solicitation / 541512",
            country="United States", location="Washington, DC",
            posted_date=_d(-6), deadline=_d(25), status="open",
        ),
        NormalizedOpportunity(
            source_type="state", source_name="State Procurement", external_id="SAMPLE-STATE-1",
            source_url="https://example.gov/construction-rfp",
            title="General contractor for building renovation and construction",
            buyer_name="State Facilities Office", buyer_type="government",
            summary="General contractor for a building renovation and construction "
                    "project including civil engineering work.",
            category_raw="Construction services",
            country="United States", location="Sacramento, CA",
            posted_date=_d(-8), deadline=_d(40), status="open",
        ),
    ]


class SampleAdapter(SourceAdapter):
    key = "sample"
    name = "Sample data"

    def fetch(self) -> list[NormalizedOpportunity]:
        return sample_opportunities()
