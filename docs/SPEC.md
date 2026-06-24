# RFP Aggregator System — Technical Spec (V1)

## 1. Overview

Build a private internal system that aggregates, normalizes, and ranks public
procurement and RFP opportunities from government, UN, and curated
nonprofit/institutional sources.

The system's purpose is to help a design studio identify high-fit opportunities
for branding, rebranding, web design, and communications work.

## 2. Goals

### Primary goals
* Aggregate RFP / procurement opportunities from multiple sources
* Normalize all opportunities into a single structured schema
* Filter and score opportunities based on design/studio relevance
* Provide a simple searchable dashboard
* Send daily or real-time alerts for high-fit opportunities

### Secondary goals
* Track opportunity status (new → reviewed → applied → won/lost)
* Avoid duplicate listings across sources
* Maintain historical record of opportunities and amendments

## 3. Non-goals
* Not a full public procurement search engine
* Not attempting to scrape "all nonprofits on the internet"
* Not a commercial GovSpend/GovWin competitor
* Not supporting complex bid submission workflows
* Not handling authentication-protected procurement portals initially

## 4. Data Sources (V1 scope)

### Tier 1 (API-based, required)
* SAM.gov (US federal procurement opportunities API)
* UNGM (United Nations Global Marketplace notices)

### Tier 2 (curated institutional sources)
* Selected state/local procurement portals (manual selection)
* University procurement / RFP pages
* Foundation and nonprofit procurement pages
* Arts/culture/media organization RFP pages

### Source strategy
Each source is classified as one of: API, RSS, HTML, Playwright, Manual.

## 5. System Architecture

Pipeline: Ingestion → Normalization → Enrichment → Storage → API → Frontend → Notifications.

## 6. Data Model (Postgres)

### Table: opportunities
id, source_type, source_name, source_url, external_id, title, buyer_name,
buyer_type, summary, full_text, category_raw, category_normalized[], tags[],
location, country, posted_date, deadline, status, budget_min, budget_max,
currency, documents_url[], contact_email, relevance_score, design_fit_score,
last_seen_at, content_hash, created_at, updated_at.

### Table: sources
id, name, source_type, base_url, fetch_config (jsonb), schedule_interval,
last_fetched_at, last_success_at, status.

### Table: opportunity_status
id, opportunity_id, status, notes, updated_at.

## 7. Scoring System
* Design Fit Score (0–100) — weighted design keywords
* Sector Fit Score (0–100) — sector boosts
* Penalty keywords — construction, infra engineering, non-design IT, staffing, hardware
* Final = 60% design fit + 40% sector fit

## 8. Deduplication
Match on external_id, OR hash(title + buyer_name + deadline + source).
Maintain content_hash to detect updates/amendments.

## 9. Ingestion Frequency
SAM.gov 6–12h, UNGM 6–12h, curated daily, high-priority 4–6h optional.

## 10–11. Frontend & Notifications
List/detail/saved/pipeline views; filters by source/buyer/score/deadline/tags/region.
Daily digest of new high-score opps + upcoming deadlines. Email primary, Slack optional.

## 12. Infrastructure
Backend FastAPI, Postgres, optional Redis worker, Next.js frontend, simple hosting.

## 13. MVP Phases
1. Core ingestion (SAM + UNGM + schema + workers)
2. Curated sources (HTML/RSS + dedup)
3. Scoring + enrichment
4. UI dashboard
5. Alerts + workflow

## 14. Key Design Principle
Signal over completeness; curated quality over exhaustive scraping;
design-relevant filtering over raw procurement volume.

## 15. Future Extensions
Proposal generation, CRM integration, semantic matching, browser extension,
team collaboration.
