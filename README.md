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

- a **Sources** panel showing each feed's health (✓ working / ✕ failing /
  ○ not configured, with the count or error on hover)
- ranked list of opportunities (best design/sector fit first)
- filters: search, min fit score, deadline window (7/14/30/60d), source,
  buyer type, tags, and a "saved only" toggle
- per-opportunity: **save**, **pipeline status**, **notes**, **copy summary**,
  and a link to the original listing
- saved/status/notes persist in the browser via localStorage

## Sources

Wired in: **SAM.gov** (US federal contracts, needs a key), **Grants.gov** (US
federal grants, no key), **UNGM** (UN). Add curated **RSS feeds** (state/local
portals, foundations, universities) in `worktube/feeds.py` — each becomes its
own source with its own ✓/✕ status. See [`docs/SOURCES.md`](docs/SOURCES.md)
for the full list of candidates and how to add New York / state-local sources.

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

### Refreshing the report — automated (GitHub Actions)

You don't run anything locally. A scheduled GitHub Action
([`.github/workflows/report.yml`](.github/workflows/report.yml)) regenerates
`index.html` with live data on GitHub's servers, commits it, and Hostinger
auto-deploys. One-time setup, all in the browser:

1. **GitHub → Settings → Secrets and variables → Actions → New repository
   secret:** `SAM_API_KEY` = your SAM.gov key. (Optional — Grants.gov needs no
   key, so the report has real data either way.)
2. **GitHub → Actions tab →** enable workflows if prompted → **"Build report" →
   Run workflow** for the first run.
3. **Hostinger → your Git deployment →** enable **Auto-Deployment** so each
   commit to `main` updates the site.

After that it refreshes twice daily automatically; hit **Run workflow** anytime
for an on-demand refresh.

### Refreshing manually (optional)

```bash
python generate_report.py --out . --no-dated   # SAM_API_KEY via .env for live data
git commit -am "update report" && git push
```

### Keeping it off Google

The repo ships three layers so search engines don't index the subdomain:
`robots.txt` (Disallow all), a `<meta name="robots" content="noindex">` in the
page, and an `X-Robots-Tag` header via `.htaccess`. The same `.htaccess` also
404s the Python source files that git-deploy copies into `public_html`, so only
`index.html` (and `robots.txt`) are reachable. Nothing else to configure — it
deploys with the repo.

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
