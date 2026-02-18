# TASKS.md — Build Signals

> Last updated: 2026-02-19, end of session 9

## Status: FULLY OPERATIONAL

The entire pipeline works end-to-end. Data flows from sources → Claude scoring → Supabase → Railway dashboard.

---

## DONE (Session 9)

- [x] Railway deploy verified — all 3 tabs show live data
- [x] Anthropic API credits topped up ($20) and working
- [x] Full pipeline ran locally: HN (213) + GitHub (21) + PH (100) → scored (77/334) → tweets (5) → Supabase (339 records)
- [x] Dashboard shows Tweet Drafts, Signals, Trends — all populated
- [x] `SUPABASE_KEY` GitHub secret updated to service role key (was anon key, caused RLS 42501 errors)

## TODO — Next Session (Session 10)

### High Priority
- [ ] **Verify CI end-to-end**: Trigger `refresh-data.yml` from GitHub Actions UI WITHOUT `skip_scoring`. Confirm scoring + tweets + Supabase load all pass in CI (local run is proven, CI not yet tested with scoring enabled)
- [ ] **Review daily cron output**: Workflow runs daily at 6 AM UTC. After first automated run, check Actions tab for success/failure

### Medium Priority
- [ ] **Update `anthropic` pin**: `requirements.txt` pins `anthropic==0.43.0` but `0.81.0` is installed locally and works. Update to `anthropic>=0.43.0` or pin to current version to avoid CI issues
- [ ] **Fix Windows-only bugs** (non-blocking, only affect local dev):
  - `hn_listener.py` line 212: `runs/latest` symlink fails on Windows (data files write fine)
  - `generate_tweets.py` line 300: unicode `→` crashes cp1252 console on Windows (JSONL file writes fine)

### Low Priority
- [ ] **signal-source-code frontend**: Vite/TS app not yet connected or worked on. Decide if this replaces Streamlit dashboard or serves a different purpose
- [ ] **STRIPE_WEBHOOK_SECRET**: Still a placeholder in `app/.env.local`
- [ ] **Clean up Codex branches**: ~18 remote Codex branches on build-signals-ui can be deleted

## BLOCKED — Nothing Currently Blocked

## Key Info for Next Session

### Credentials
- **ANTHROPIC_API_KEY**: Must be `export`ed in shell (not in .env file). Key starts with `sk-ant-api03-cbbt...`
- **Supabase service role key**: In `app/.env.local` and GitHub Secrets (`SUPABASE_KEY`)
- **Dashboard password**: `buildsignals123`
- **Railway URL**: https://build-signals-ui-production.up.railway.app

### How to Run Pipeline Locally
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
mkdir -p runs/local_002
python scripts/hn_listener.py --days 7 --limit 200 --out-dir runs/local_002
python scripts/fetch_github_trending.py --since both --out-dir runs/local_002
export PH_TOKEN="lwLNC52ziX7GhgQu5siiVxWkCCaWGMlcDwVSyTwQZyQ"
python scripts/fetch_producthunt.py --days 7 --limit 100 --min-votes 50 --out-dir runs/local_002
python scripts/score_signals.py --input-dir runs/local_002 --out-dir runs/local_002
python scripts/generate_tweets.py --input-dir runs/local_002 --out-dir runs/local_002 --top-n 5
export SUPABASE_URL="https://njwvtksauogsmberxrbd.supabase.co"
export SUPABASE_KEY="<service-role-key-from-app/.env.local>"
python scripts/supabase_loader.py --input-dir runs/local_002
```

### How to Trigger CI
Go to GitHub → Actions → "Refresh Build Signals Data" → Run workflow → leave `skip_scoring` unchecked → Run
