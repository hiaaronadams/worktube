from worktube.scoring import score_text


def test_strong_design_and_sector_match_scores_high():
    res = score_text(
        title="RFP: Branding and visual identity for arts foundation",
        summary="We seek a studio for a rebrand, website redesign, and design system.",
        buyer_name="Community Arts Foundation",
    )
    assert res.design_fit_score == 100.0
    assert res.sector_fit_score == 100.0
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


def test_partial_word_does_not_falsely_match():
    res = score_text(title="Guidance document drafting", summary="policy guidance")
    assert "ux_ui" not in res.tags
