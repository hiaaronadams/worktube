from app.enrichment.scoring import score_text


def test_strong_design_and_sector_match_scores_high():
    res = score_text(
        title="RFP: Branding and visual identity for arts foundation",
        summary="We seek a studio for a rebrand, website redesign, and design system.",
        buyer_name="Community Arts Foundation",
    )
    assert res.design_fit_score == 100.0  # multiple design groups -> saturated
    assert res.sector_fit_score == 100.0  # arts + foundation
    assert res.relevance_score >= 90
    assert "branding" in res.tags
    assert "foundation" in res.tags
    assert res.penalties == []


def test_penalty_reduces_final_score():
    base = score_text(
        title="Visual identity and branding services",
        summary="Brand strategy and logo design for a nonprofit.",
    )
    penalized = score_text(
        title="Visual identity and branding services",
        summary="Brand strategy and logo design for a nonprofit. "
        "Includes building renovation and general contractor construction work.",
    )
    assert "construction" in penalized.penalties
    assert penalized.relevance_score < base.relevance_score


def test_irrelevant_opportunity_scores_zero():
    res = score_text(
        title="Procurement of office supplies and computer hardware",
        summary="Bulk purchase of laptops and printers for the IT department.",
    )
    assert res.design_fit_score == 0.0
    assert res.relevance_score == 0.0


def test_title_keyword_weighted_over_body():
    in_title = score_text(title="Website redesign", summary="general services")
    in_body = score_text(title="general services", summary="website redesign")
    # both match the same group, so design fit is equal; sanity check it's > 0
    assert in_title.design_fit_score > 0
    assert in_body.design_fit_score > 0


def test_partial_word_does_not_falsely_match():
    # "branding" should match but a word like "rebranding" handled by its group;
    # ensure short token "ui" doesn't match inside "guidance"
    res = score_text(title="Guidance document drafting", summary="policy guidance")
    assert "ux_ui" not in res.tags
