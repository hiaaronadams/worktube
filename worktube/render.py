"""Render a Report into a single self-contained static HTML file."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from worktube.pipeline import Report

TEMPLATE_PATH = Path(__file__).parent / "template.html"
PLACEHOLDER = "/*__REPORT_JSON__*/null"


def render_html(report: Report) -> str:
    payload = {
        "generated_at": report.generated_at,
        "demo": report.demo,
        "high_fit_threshold": report.high_fit_threshold,
        "source_stats": report.source_stats,
        "warnings": report.warnings,
        "opportunities": report.opportunities,
    }
    blob = json.dumps(payload, ensure_ascii=False)
    # Prevent the embedded JSON from accidentally closing the <script> tag.
    blob = blob.replace("</", "<\\/")
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    if PLACEHOLDER not in html:
        raise RuntimeError("template.html is missing the data placeholder")
    return html.replace(PLACEHOLDER, blob)


def write_report(report: Report, out_dir: str | Path = "reports") -> tuple[Path, Path]:
    """Write both a dated file and index.html (the latest). Returns both paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    html = render_html(report)
    dated = out / f"worktube-{date.today().isoformat()}.html"
    latest = out / "index.html"
    dated.write_text(html, encoding="utf-8")
    latest.write_text(html, encoding="utf-8")
    return dated, latest
