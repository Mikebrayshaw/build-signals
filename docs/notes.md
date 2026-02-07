# Project Notes

Claude maintains this file. After every completed task or PR, a lessons-learned entry is appended.
Format: date, task summary, what worked, what did not, what to do differently.

---

## 2026-02-06: Added Product Hunt as data source

**Task:** Integrate Product Hunt alongside Hacker News for validated idea discovery.

**What was done:**
- Created `scripts/ph_listener.py` using PH GraphQL API v2
- Updated `github_matcher.py` to process producthunt.jsonl files
- Updated `supabase_loader.py` with `source_id` field for multi-source deduplication
- Updated GitHub Actions workflow with optional PH fetch step
- Created SQL migration for new columns (source_id, tagline, topics)

**Key decisions:**
- Used Developer Token auth (simpler than OAuth, sufficient for read-only)
- Made PH fetch optional with `continue-on-error: true` in workflow
- Used `source_id` format `source:id` for unified deduplication across sources
- Kept `hn_id` column for backward compatibility with existing data

**What worked:** PH API is straightforward GraphQL, good documentation.

**What to watch:** PH rate limits (monitor if fetching more data), token expiry.

## 2026-02-07: Wired frontend to live data + deploy pipeline

**Task:** Connect landing page to Supabase, add deploy workflow, failure alerts, and custom domain config.

**What was done:**
- Added Supabase JS CDN to `landing/index.html` and replaced hardcoded signals with live DB queries
- `fetchSignals()` queries `opportunities` table (20 most recent), maps DB rows to card format
- `fetchCounts()` gets month's total + unanswered counts for counter bar
- Fallback to hardcoded `FALLBACK_SIGNALS` array if Supabase is unreachable
- Created `.github/workflows/deploy-pages.yml` (triggers on `landing/**` changes to `master`)
- Added failure notification step to `refresh-data.yml` (uses `::error::` annotation + step summary)
- Created `landing/CNAME` for `www.thinktypewrite.com`

**Key decisions:**
- Anon key in frontend is safe — RLS must be enabled with SELECT-only policy (manual step)
- `renderSignals()` now takes signals as argument instead of using global
- Counter `data-target` attributes updated dynamically before observer fires animation
- Used `head: true` with `count: 'exact'` for counter queries to avoid fetching row data

**What to watch:**
- RLS policy must be applied manually in Supabase SQL Editor before frontend works
- GitHub Pages source must be set to "GitHub Actions" in repo settings
- DNS records (CNAME + A records) are manual steps
- Credential rotation (Step 5) is entirely manual

