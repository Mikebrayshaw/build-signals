# TASKS.md — Build Signals

> Last updated: 2026-02-25, session 13 complete

## Status: OPPORTUNITY INTELLIGENCE LAYER — FULLY VERIFIED AND DEPLOYED

The entire pipeline is operational: fetch, score, validate, load, and display. All 15 validated opportunities are in Supabase and rendering on Railway. Both repos committed and pushed.

---

## Session 13 — Full Verification + Deploy (2026-02-25)

### ALL DONE
- [x] Anthropic API connectivity restored (was blocked in sessions 11-12, now working)
- [x] `validate_opportunities.py --top-n 1` — PASS (high confidence, real LLM narrative)
- [x] `validate_opportunities.py --top-n 15` — PASS (9 high, 6 medium, 0 low)
- [x] `supabase_loader.py --input-dir runs/local_001` — PASS (15 validated opps + 354 total records)
- [x] Streamlit runs locally (unified opportunity view with evidence cards)
- [x] Fixed `st.expander()` `key=` kwarg error (used unique label text instead)
- [x] Emoji constants verified correct (proper Unicode, renders in browser)
- [x] Railway deploy verified — all 15 cards rendering on production (user confirmed)
- [x] **build-signals** committed and pushed: `e2b47b7` on `master`
- [x] **build-signals-ui** committed and pushed: `29d8eb6` on `main`

---

## Remaining Work

### High Priority
- [ ] **Full CI run**: Trigger `refresh-data.yml` WITHOUT `skip_scoring` to verify the complete pipeline runs in GitHub Actions (includes the new validation step)

### Medium Priority
- [ ] **signal-source-code frontend**: Vite/TS app at `C:/Users/mike/signal-source-code` — not yet connected or worked on
- [ ] **Update `anthropic` pin**: `requirements.txt` pins `anthropic==0.43.0` but `0.81.0` works locally

### Low Priority
- [ ] **STRIPE_WEBHOOK_SECRET**: Still placeholder in `app/.env.local`
- [ ] **Clean up orphaned Codex files** in build-signals-ui: `app_logic.py`, `tests/`, `TECH_STACK_AUDIT.md`
- [ ] **Clean up Codex branches**: ~18 remote branches on build-signals-ui
- [ ] **Windows-only bugs**: `runs/latest` symlink + unicode console display (non-blocking)

---

## Key Info for Next Session

### Credentials
- **ANTHROPIC_API_KEY**: In `C:\Users\mike\build-signals\.env` (loaded by dotenv). Working as of session 13.
- **Supabase service role key**: In `app/.env.local` and GitHub Secrets (`SUPABASE_KEY`)
- **Dashboard password**: `buildsignals123`
- **Railway URL**: https://build-signals-ui-production.up.railway.app
- **Supabase URL**: https://njwvtksauogsmberxrbd.supabase.co

### Python / PATH
- Python 3.12 at: `C:\Users\mike\AppData\Local\Programs\Python\Python312\python.exe`
- `python` and `py` may point to stubs — use full path or verify
- `streamlit` not on PATH — use `python -m streamlit` instead

### Git State (clean)
- **build-signals**: `master` branch, latest `e2b47b7`, pushed to origin
- **build-signals-ui**: `main` branch, latest `29d8eb6`, pushed to origin
- No uncommitted changes in either repo (CLAUDE.md/TASKS.md updates need committing)
