from datetime import date

from worktube.dedup import compute_content_hash, compute_dedup_key
from worktube.models import NormalizedOpportunity


def _opp(**kw):
    base = dict(
        source_type="sam",
        source_name="SAM.gov",
        title="Branding services",
        buyer_name="City of Example",
        deadline=date(2026, 7, 1),
    )
    base.update(kw)
    return NormalizedOpportunity(**base)


def test_dedup_key_prefers_external_id():
    assert compute_dedup_key(_opp(external_id="ABC123")) == "sam:ABC123"


def test_dedup_key_falls_back_to_hash():
    key = compute_dedup_key(_opp())
    assert key.startswith("hash:")
    assert key == compute_dedup_key(_opp())


def test_dedup_key_differs_by_source():
    assert compute_dedup_key(_opp(source_type="sam")) != compute_dedup_key(
        _opp(source_type="ungm")
    )


def test_content_hash_changes_on_amendment():
    before = compute_content_hash(_opp(summary="original"))
    after = compute_content_hash(_opp(summary="amended deadline extended"))
    assert before != after
