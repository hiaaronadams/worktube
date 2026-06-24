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
        "sources": report.sources,
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


def write_report(
    report: Report, out_dir: str | Path = "reports", *, write_dated: bool = True
) -> tuple[Path, Path | None]:
    """Write index.html (the latest) and, optionally, a dated copy.

    Returns (index_path, dated_path | None).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    html = render_html(report)
    latest = out / "index.html"
    latest.write_text(html, encoding="utf-8")
    dated: Path | None = None
    if write_dated:
        dated = out / f"worktube-{date.today().isoformat()}.html"
        dated.write_text(html, encoding="utf-8")
    return latest, dated

