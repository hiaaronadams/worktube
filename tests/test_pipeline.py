from worktube.pipeline import build_report
from worktube.render import render_html


def test_demo_report_builds_sorted_and_scored():
    report = build_report(demo=True)
    assert report.demo is True
    assert report.total >= 6
    # sorted by relevance descending
    scores = [o["relevance_score"] for o in report.opportunities]
    assert scores == sorted(scores, reverse=True)
    # every row carries scores, an id, and tags
    top = report.opportunities[0]
    assert {"id", "relevance_score", "design_fit_score", "tags"} <= top.keys()
    # the arts/health/foundation samples should be high-fit
    assert report.high_fit_count >= 1


def test_render_embeds_data_and_is_self_contained():
    report = build_report(demo=True)
    html = render_html(report)
    assert "<!DOCTYPE html>" in html
    assert "/*__REPORT_JSON__*/null" not in html  # placeholder replaced
    assert "World Health Foundation" in html      # data embedded
    # no external asset references (fully self-contained)
    assert "src=\"http" not in html
    assert "<link" not in html


def test_live_sources_fall_back_to_demo_without_keys(monkeypatch):
    # No SAM key + UNGM unreachable in tests -> should still produce a report.
    import worktube.pipeline as pl

    class _Boom:
        def __init__(self, **kw):
            pass

        def fetch(self):
            raise RuntimeError("network blocked")

    monkeypatch.setitem(pl.LIVE_ADAPTERS, "ungm", _Boom)
    report = build_report(sources=["ungm"])
    assert report.demo is True          # fell back
    assert report.total >= 6
    assert any("fail" in w.lower() or "no live data" in w.lower() for w in report.warnings)
