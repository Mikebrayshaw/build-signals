# Project Notes

Claude maintains this file. After every completed task or PR, a lessons-learned entry is appended.
Format: date, task summary, what worked, what did not, what to do differently.

---

## 2026-02-06: Added Product Hunt as data source

**Task:** Integrate Product Hunt alongside Hacker News for validated idea discovery.

**What was done:**
- Created `scripts/ph_listener.py` using PH GraphQL API v2
- Updated `match_github.py` to process producthunt.jsonl files
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

## 2026-02-09: Fixed Supabase loader pipeline end-to-end

**Task:** Get supabase_loader.py working to load JSONL data into Supabase.

**What was done:**
- Fixed httpx version mismatch (0.25.2 → 0.27.2) — gotrue 2.9.1 passes `proxy` kwarg that requires httpx >=0.27
- Created migration 003 to align table schema with loader expectations: renamed `text`→`description`, `github_repos`→`github_data`, converted `id` from serial int to text composite PK (`source:hn_id`), added `source_id`, `github_url`, `tagline`, `topics` columns
- Fixed supabase_loader.py to load env from `app/.env.local` instead of CWD
- Fixed supabase_loader.py to fall back to `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` env var names
- Added deduplication in loader — posts appearing in both base and matched JSONL files caused Postgres ON CONFLICT errors within same batch
- Successfully loaded 165 unique records (204 raw, 39 dupes across files)

**What went wrong:**
- Tried full `pip install --upgrade supabase` first — failed because new `storage3` pulls in `pyiceberg` → `pyroaring` which needs MSVC C++ build tools
- Migration 001 was never applied to production — had to combine it into migration 003
- `runs/latest` is a plain text file, not a symlink or directory — caused confusion when passing it as `--input-dir`

**Lessons:**
- Always check actual table schema before writing a loader (query a row, don't trust comments)
- When upgrading Python packages on Windows, check for C extension dependencies before upgrading the whole tree
- Deduplicate records before batch upsert — Postgres ON CONFLICT can't handle the same row twice in one batch

