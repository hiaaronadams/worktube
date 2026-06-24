# Worktube — RFP Report Generator

Aggregates public procurement / RFP opportunities (government, UN, curated
sources), scores them for design-studio relevance, and bakes the results into a
**single self-contained HTML file** you can open or host anywhere.

No server, no database, no Docker. You run one command to "spin up" a report;
the output is just a static `.html` file. Saved items, notes, and pipeline
status are stored in the viewer's browser (localStorage).

Design principle: **signal over completeness** — curated sources and
design-relevant filtering over raw procurement volume. Full spec in
[`docs/SPEC.md`](docs/SPEC.md).

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Generate a report (no API key needed — falls back to sample data):
python generate_report.py --demo

# Open the result:
#   reports/index.html   (latest)
#   reports/worktube-YYYY-MM-DD.html
open reports/index.html        # macOS  (use xdg-open on Linux, or just double-click)
```

With a SAM.gov API key, it pulls live US federal opportunities. Put the key in
a local `.env` file (gitignored — never committed):

```bash
cp .env.example .env
# edit .env and set SAM_API_KEY=...   (https://open.gsa.gov/api/get-opportunities-public-api/)

python generate_report.py                 # live sources; falls back to demo if none reachable
python generate_report.py --sources sam   # just SAM.gov
```

(You can also `export SAM_API_KEY=...` instead of using `.env`.)

## The report

The generated HTML is a small self-contained app:

- ranked list of opportunities (best design/sector fit first)
- filters: search, min fit score, deadline window (7/14/30/60d), source,
  buyer type, tags, and a "saved only" toggle
- per-opportunity: **save**, **pipeline status**, **notes**, **copy summary**,
  and a link to the original listing
- saved/status/notes persist in the browser via localStorage

## Hosting it (e.g. Hostinger)

The repo's **root `index.html` is the deployable website** — it's committed, so
the repo can be served as-is. Any static host works (Hostinger, Netlify, S3),
or run `python -m http.server` locally.

### Deploy to Hostinger via GitHub

1. hPanel → **Websites → Git** (or **Advanced → GIT**).
2. Repository: `https://github.com/hiaaronadams/worktube.git`, branch `main`,
   directory `public_html`.
3. Deploy. Visiting your domain serves the root `index.html`.
4. (Optional) enable **Auto-Deployment** so each `git push` updates the site.

### Refreshing the report

Regenerate the root `index.html`, commit, and push:

```bash
python generate_report.py --out . --no-dated   # add SAM_API_KEY for live data
git commit -am "update report" && git push     # Hostinger auto-deploys
```

> Note: the homepage is `index.html`; the Python source files sit alongside it
> in the repo and are harmless (not linked). To hide them from the web, drop an
> `.htaccess` in `public_html` or have Hostinger serve only `index.html`.

## Layout

```
generate_report.py     CLI entry point -> writes the HTML report
worktube/
  config.py            env-driven settings (API keys, scoring weights)
  models.py            NormalizedOpportunity (the unified shape)
  normalize.py         date / currency / text / hashing helpers
  keywords.py          scoring keyword lists (tune these)
  scoring.py           design-fit / sector-fit / penalty scoring (SPEC §7)
  dedup.py             dedup + content-hash (SPEC §8)
  pipeline.py          fetch -> dedup -> score -> sorted rows
  render.py            bakes a report into template.html
  template.html        the self-contained static report (HTML+CSS+JS)
  sources/             sam.py, ungm.py, sample.py (+ base.py)
tests/                 unit tests (scoring, dedup, normalize, sources, pipeline)
docs/SPEC.md           full spec
```

## Tests

```bash
pytest
```

## Notes / limits

- **State is per-browser.** Saved items and notes live in localStorage, so they
  don't sync across people or devices. Fine for solo use; that was the explicit
  tradeoff for keeping this server-free.
- **UNGM** has no documented public JSON API; that adapter's field mapping is
  best-effort and should be confirmed against a live response.
- SAM.gov needs a (free) API key for live data.
