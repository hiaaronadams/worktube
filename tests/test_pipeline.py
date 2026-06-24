from worktube.pipeline import build_report
from worktube.render import render_html


def test_demo_report_builds_sorted_and_scored():
    report = build_report(demo=True)
    assert report.demo is True
    assert report.total >= 6
    scores = [o["relevance_score"] for o in report.opportunities]
    assert scores == sorted(scores, reverse=True)
    top = report.opportunities[0]
    assert {"id", "relevance_score", "design_fit_score", "tags"} <= top.keys()
    assert report.high_fit_count >= 1


def test_render_embeds_data_and_is_self_contained():
    report = build_report(demo=True)
    html = render_html(report)
    assert "<!DOCTYPE html>" in html
    assert "/*__REPORT_JSON__*/null" not in html
    assert "World Health Foundation" in html
    assert "noindex" in html                       # crawler opt-out present
    assert "src=\"http" not in html
    assert "<link" not in html


def test_status_panel_reports_per_source_health(monkeypatch):
    """A failing source is recorded as 'failed' with a message; report still builds."""
    import worktube.pipeline as pl
    from worktube.sources.base import SourceAdapter

    class Boom(SourceAdapter):
        key = "ungm"
        name = "UNGM"

        def fetch(self):
            raise RuntimeError("network blocked")

    monkeypatch.setitem(pl.BUILTIN_ADAPTERS, "ungm", Boom)
    report = build_report(sources=["ungm"])

    statuses = {s["key"]: s for s in report.sources}
    assert statuses["ungm"]["status"] == "failed"
    assert "network blocked" in statuses["ungm"]["message"]
    # nothing live -> fell back to demo, which is reported as an ok source
    assert report.demo is True
    assert any(s["status"] == "ok" for s in report.sources)


def test_sam_reported_skipped_without_key(monkeypatch):
    import worktube.config as cfg
    monkeypatch.setattr(cfg.config, "sam_api_key", "", raising=False)
    report = build_report(sources=["sam"])
    statuses = {s["key"]: s for s in report.sources}
    assert statuses["sam"]["status"] == "skipped"
    assert "SAM_API_KEY" in statuses["sam"]["message"]
