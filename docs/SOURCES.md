# Sources — what we pull, and what we can add

Each source shows a ✓ (working) / ✕ (failing) / ○ (not configured) status in the
report's left panel, so it's always obvious what's live.

## Currently wired

| Source     | Type     | Key needed | Notes |
|------------|----------|-----------|-------|
| SAM.gov    | API      | yes       | US federal contract opportunities |
| Grants.gov | API      | no        | US federal grants (design/comms/outreach) |
| UNGM       | API-ish  | no        | UN agencies; undocumented endpoint, may be flaky |

## Easiest to add: RSS feeds

Lots of procurement/RFP pages publish an RSS feed. Adding one is a few lines in
`worktube/feeds.py` — it then appears as its own source with its own ✓/✕ status.
Look for an RSS icon on a site, or try `/rss`, `/feed`, `/rss.xml`.

## State / local — including New York

New York's main procurement portal is the **NYS Contract Reporter**
(`nyscr.ny.gov`). It does **not** offer a clean public JSON API, so the options
are, in order of effort:

1. **RSS** — if NYSCR (or a specific agency) exposes a feed, drop it into
   `feeds.py` and it works immediately. (Need to confirm a feed URL exists.)
2. **Socrata open-data** — `data.ny.gov` and NYC's `data.cityofnewyork.us` run
   Socrata, which *does* have a clean API (no key for light use). If we find a
   dataset of open solicitations, a small Socrata adapter covers NY **and** many
   other states/cities the same way. Recommended next step for state/local.
3. **HTML scraping** — last resort; brittle, and some portals need a login or
   JS rendering (would need Playwright). Avoid unless 1–2 fail.

Tell me which NY source you mean (NYSCR, a specific agency, NYC) and I'll wire
the feed or build the Socrata adapter.

## Other good candidates

| Source | Region | Access | Worth it for design? |
|--------|--------|--------|----------------------|
| NYC City Record (NYC Open Data / Socrata) | NYC | API | Yes — lots of agency RFPs |
| Contracts Finder | UK gov | API (OCDS) | Some branding/comms |
| TED (Tenders Electronic Daily) | EU | API | High volume, some design |
| CanadaBuys | Canada | API/open data | Some |
| Foundation / arts-org RFP pages | varies | RSS/HTML | High signal, low volume — curate |
| University procurement pages | US | RSS/HTML | Good for web/brand work |

## Principle

Per the spec: **signal over completeness**. A handful of high-quality curated
feeds beats scraping everything. Add sources deliberately; the scoring engine
keeps the noise down regardless.
