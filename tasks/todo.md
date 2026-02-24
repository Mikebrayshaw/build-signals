# PLAN - Session 11 - Opportunity Intelligence Layer

Last updated: 2026-02-20

## Scope (from spec)
- Convert HN signals into validated opportunity cards (single unified view)
- Add opportunity type classification (1-2 types) and buyer-intent query generation (3-5 per source)
- Execute queries against Google Trends, Product Hunt, GitHub
- Synthesize narrative + compute confidence score
- Show 5-10 unified cards per day (no extra tabs)

## Files to touch
- `C:/Users/mike/build-signals/scripts/validate_opportunities.py` (classification types, query gen, evidence scoring, narrative/title output)
- `C:/Users/mike/build-signals-ui/app.py` (single unified opportunity view, evidence summaries, remove extra tabs)
- `C:/Users/mike/build-signals/scripts/supabase_loader.py` (only if required for new fields; ideally no change)
- `C:/Users/mike/build-signals/docs/notes.md` (append lessons after completion)

## Dependencies/Assumptions
- Anthropic API key available for live run
- pytrends installed for Google Trends (otherwise shows skipped)
- Supabase tables already include validated_opportunities (migration 006 applied)

## Risks / Edge Cases
- LLM output malformed JSON or missing fields
- Low/no evidence from sources (must state explicitly in narrative)
- Opportunity type list must match spec (schema uses TEXT)
- Google Trends rate limits or zero data
- Product Hunt API unavailable (fallback to local JSONL)
- GitHub API rate limits or empty results

## Plan
- [x] Update opportunity classification + query generation prompt to spec types and 3-5 buyer-intent queries per source
- [x] Add opportunity title generation (not HN title) and store as signal_title
- [x] Add deterministic evidence scoring + confidence computation per spec (Trends/PH/GitHub + HN strength)
- [x] Add evidence summaries (Trends/Products/GitHub) for display
- [x] Update Streamlit UI to single unified opportunity view (no extra tabs) and render card format per spec
- [ ] Verify with local dry-run and a live run (top-n 1 then 15) and ensure JSONL + UI render

## Verification (must run)
- [ ] python scripts/validate_opportunities.py --input-dir runs/<latest> --top-n 1 (sanity)
- [ ] python scripts/validate_opportunities.py --input-dir runs/<latest> --top-n 15 (full)
- [ ] python scripts/supabase_loader.py --input-dir runs/<latest> (validated_opportunities upsert)
- [ ] Launch Streamlit and verify unified cards + evidence summaries render
- [ ] Smoke test: locate the "elderly people struggling with modern web" signal and confirm the card narrative + evidence quality

---
# TODO â€” Build Signals Pipeline Upgrade

Last updated: 2026-02-18 (Session 8, end of session)

---

## STATUS: CI PIPELINE GREEN, RAILWAY DEPLOY IN PROGRESS

GitHub Actions workflow passes (with skip_scoring). Both repos committed and pushed. Railway redeploying after requirements fix.

---

## HALF-FINISHED â€” Needs Verification NOW

### 1. Railway Deploy (IN PROGRESS)
- [x] Pushed `build-signals-ui` with unpinned `supabase>=2.4.0` to fix `proxy` kwarg error
- [ ] **Verify Railway auto-redeploy succeeds** â€” check https://build-signals-ui-production.up.railway.app
- [ ] **Verify PASSWORD is set to `buildsignals123`** in Railway Variables
- [ ] **Verify these Railway env vars exist:**
  - `PASSWORD` = `buildsignals123`
  - `SUPABASE_URL` = `https://njwvtksauogsmberxrbd.supabase.co`
  - `SUPABASE_KEY` = anon key (starts `eyJ...ec8`)
  - `SUPABASE_SERVICE_KEY` = service role key (starts `eyJ...1mQ`)
- [ ] **Login and verify all 3 tabs render** on Railway

---

## BLOCKED â€” Waiting on Mike

### 2. Anthropic API Credits
- [ ] **Top up credits** at console.anthropic.com â†’ Plans & Billing
- [ ] **Re-run GitHub Actions workflow WITHOUT skip_scoring** to test full pipeline
- [ ] **Verify scored signals and tweet drafts appear in Supabase + dashboard**

---

## DONE (Session 8)

### Bugs Fixed
- [x] Fixed `_get_secret()` infinite recursion in `build-signals-ui/app.py` (was calling itself instead of `st.secrets[key]`)
- [x] Fixed `httpx==0.27.2` pin conflicting with `supabase==2.4.0` in `build-signals/requirements.txt`
- [x] Unpinned `supabase` to `>=2.4.0` in both repos to resolve gotrue `proxy` kwarg error

### Streamlit Dashboard â€” Verified Locally
- [x] All 3 tabs render (Tweet Drafts, Signals, Trends)
- [x] Login works with `PASSWORD=buildsignals123`
- [x] Supabase connection works with env vars

### GitHub Actions Workflow â€” GREEN
- [x] Triggered manually with `skip_scoring=true`
- [x] All non-scoring steps pass: HN, GitHub Trending, Product Hunt, Google Trends, Supabase loader, artifact upload
- [x] Fresh data loaded to Supabase from CI run

### Commits & Pushes
- [x] **build-signals** pushed to `master` (3 commits):
  1. `b50f821` â€” Pipeline upgrade: new scripts, workflow, loader rewrite, migrations, CLAUDE.md
  2. `bca6f45` â€” Fix httpx version conflict (removed explicit pin)
  3. `6748c11` â€” Unpin supabase version to `>=2.4.0`
  - Resolved 3 merge conflicts with 6 Codex PRs on remote
- [x] **build-signals-ui** pushed to `main` (2 commits):
  1. `42d819a` â€” Full app.py rewrite (3-tab dark theme dashboard)
  2. `6f714dc` â€” Unpin supabase/streamlit versions for Railway
  - Resolved conflicts with 12 Codex PRs (our rewrite supersedes all)

### GitHub Secrets â€” All Configured
- [x] `SUPABASE_URL` â€” added
- [x] `SUPABASE_KEY` â€” added (service role key)
- [x] `PH_TOKEN` â€” added
- [x] `ANTHROPIC_API_KEY` â€” added (session 7, needs credits to work)

---

## DONE (Sessions 1-7)

### Phase 1: Audit â€” COMPLETE (Session 4)
### Phase 2: Plan â€” COMPLETE (Session 5)
### Phase 3: Build â€” CODE COMPLETE (Sessions 5-6)
### Phase 4: Test â€” MOSTLY COMPLETE (Sessions 7-8)

#### Local Script Test Results (Session 7)

| # | Script | Result | Output |
|---|--------|--------|--------|
| 1 | `hn_listener.py` | PASS | 16 posts (7 ask, 9 show) |
| 2 | `fetch_github_trending.py` | PASS | 13 repos |
| 3 | `fetch_producthunt.py` | PASS | 20 posts |
| 4 | `fetch_google_trends.py` | PASS | 5 keywords, 3 rising |
| 5 | `score_signals.py` | BLOCKED | Anthropic API: "credit balance too low" |
| 6 | `generate_tweets.py` | BLOCKED | Same billing issue |
| 7 | `supabase_loader.py` | PASS | 54 records upserted |

### Infrastructure â€” COMPLETE
- [x] Migration 005 run in Supabase â€” 2026-02-17
- [x] ANTHROPIC_API_KEY added to GitHub Secrets â€” 2026-02-17
- [x] SUPABASE_SERVICE_KEY added to Railway â€” 2026-02-17
- [x] match_github.py deleted â€” 2026-02-17
- [x] All 4 GitHub Actions secrets configured â€” 2026-02-18

---

## Open Low-Priority Items
- `gh` CLI not installed â€” can't trigger workflows or manage PRs from terminal
- STRIPE_WEBHOOK_SECRET still a placeholder in `app/.env.local`
- `ANTHROPIC_API_KEY` not in local `.env` file â€” only `export`ed in shell
- Codex created `app_logic.py`, `tests/`, `TECH_STACK_AUDIT.md` in build-signals-ui that are now orphaned (our rewrite doesn't use them)

---

## Key Reference

- Pipeline repo: `C:/Users/mike/build-signals` (branch: `master`)
- Dashboard repo: `C:/Users/mike/build-signals-ui` (branch: `main`)
- Signal source code: `C:/Users/mike/signal-source-code`
- Supabase: https://njwvtksauogsmberxrbd.supabase.co
- Railway: https://build-signals-ui-production.up.railway.app
- Stack: Python, Supabase, GitHub Actions (daily 6AM UTC), Streamlit on Railway
- Dashboard password: `buildsignals123`

