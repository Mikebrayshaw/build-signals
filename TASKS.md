# TASKS.md — Build Signals

> Last updated: 2026-02-23, session 12 in progress

## Status: OPPORTUNITY INTELLIGENCE LAYER — VALIDATION STILL BLOCKED, UI RUNS BUT EMOJI MOJIBAKE

The original pipeline is operational. The Intelligence Layer has been updated to the new spec (opportunity types, buyer-intent queries, evidence summaries, deterministic confidence). Local validation was attempted but Anthropic API calls are blocked by outbound network policy.

---

## Session 12 — Verification Attempts + Local UI Run (2026-02-22/23)

### DONE
- [x] Ran validator on `runs\local_001` (top-n 1 and top-n 15) — completed but all LLM calls failed with `Connection error`
- [x] Installed `build-signals-ui` dependencies (Streamlit available locally)
- [x] Created `C:\Users\mike\build-signals-ui\.streamlit\secrets.toml` with PASSWORD + SUPABASE keys
- [x] Streamlit app opens locally (user confirmed)

### HALF-FINISHED / NOT YET VERIFIED
- [ ] **Fix outbound HTTPS for Anthropic** (still blocking LLM classify/summarize)
- [ ] **Set `GITHUB_TOKEN` and `PH_TOKEN` locally** for full evidence (GitHub skipped; PH fallback used)
- [ ] **Re-run live validator** (top-n 1, then top-n 15) once network is allowed
- [ ] **Supabase loader** with validated_opportunities output
- [ ] **Streamlit UI smoke test** for unified cards and evidence summaries (with real data)
- [ ] **Fix emoji mojibake in `build-signals-ui/app.py`**
  - Partial fix inserted broken `EMOJI_*` constants as escaped strings
  - Page icon and several UI strings still garbled
  - Clean up to real Unicode escapes or ASCII
- [ ] **Smoke test requirement**: "elderly people struggling with modern web" card must read well

### Files Changed (NOT YET COMMITTED)
- MODIFIED: `C:\Users\mike\build-signals-ui\app.py` (emoji fix attempt inserted broken `EMOJI_*` constants)
- ADDED: `C:\Users\mike\build-signals-ui\.streamlit\secrets.toml` (local secrets; do not commit)

---

## Session 11 — Intelligence Layer Spec Alignment (2026-02-20)

### DONE
- [x] Updated `scripts/validate_opportunities.py` to:
  - Use spec opportunity types (1–2 types per signal)
  - Generate 3–5 buyer-intent queries per source
  - Compute evidence summaries + deterministic confidence (HN strength + Trends/PH/GitHub)
  - Generate an opportunity title (not HN title)
  - Synthesize narrative from evidence summaries with fallback narrative
- [x] Updated `build-signals-ui/app.py` to:
  - Single unified Opportunity view (no tabs)
  - Render type badges, evidence summaries, and confidence
  - Show 5/10/20 cards per view
- [x] Installed Python 3.12 locally and installed `build-signals/requirements.txt`

### HALF-FINISHED / NOT YET VERIFIED
- [x] **Live validator run attempted** (top-n 1) on `runs\local_001` — FAILED due to Anthropic connection error (re-tested 2026-02-21)
- [ ] **Fix outbound network access to HTTPS** (TCP blocked to `api.anthropic.com:443` and `google.com:443`; ping OK)
- [ ] **Set `GITHUB_TOKEN` and `PH_TOKEN` locally** for full evidence (GitHub skipped; PH local fallback used)
- [ ] **Re-run live validator** (top-n 1, then top-n 15) once network is allowed
- [ ] **Supabase loader** with validated_opportunities output
- [ ] **Streamlit UI smoke test** for unified cards and evidence summaries
- [ ] **Smoke test requirement**: "elderly people struggling with modern web" card must read well

### NEXT STEPS (RESUME HERE)
1. Fix emoji mojibake in `C:\Users\mike\build-signals-ui\app.py` (remove broken `EMOJI_*` block, replace garbled chars).
2. Allow outbound HTTPS to `api.anthropic.com:443` (or configure proxy) and re-test connectivity (also fails to `google.com:443`).
3. Re-run validator (live):
   - `python scripts\validate_opportunities.py --input-dir runs\local_001 --top-n 1`
   - `python scripts\validate_opportunities.py --input-dir runs\local_001 --top-n 15`
4. Load to Supabase:
   - `python scripts\supabase_loader.py --input-dir runs\local_001`
5. Run Streamlit:
   - `python -m streamlit run C:\Users\mike\build-signals-ui\app.py`
6. Evaluate the "elderly web" opportunity card for narrative + evidence quality.

### Files Changed (NOT YET COMMITTED)

**build-signals/**
- MODIFIED: `scripts/validate_opportunities.py` (spec alignment, confidence, summaries, titles)

**build-signals-ui/**
- MODIFIED: `app.py` (single unified opportunity view)

---

## From Session 10 — Still Open

### High Priority
- [ ] **Verify CI end-to-end**: Trigger `refresh-data.yml` WITHOUT `skip_scoring` (now includes validation step)

### Medium Priority
- [ ] **Update `anthropic` pin**: `requirements.txt` pins `anthropic==0.43.0` but `0.81.0` works locally

### Low Priority
- [ ] **signal-source-code frontend**: Vite/TS app not connected
- [ ] **STRIPE_WEBHOOK_SECRET**: Still placeholder
- [ ] **Clean up Codex branches**: ~18 remote branches on build-signals-ui
- [ ] **Windows-only bugs**: symlink + unicode console issues (non-blocking)

---

## Key Info for Next Session

### Credentials
- **ANTHROPIC_API_KEY**: Stored in `C:\Users\mike\build-signals\.env` (do not commit). API calls blocked by outbound policy.
- **Supabase service role key**: In `app/.env.local` and GitHub Secrets (`SUPABASE_KEY`)
- **Dashboard password**: `buildsignals123`
- **Railway URL**: https://build-signals-ui-production.up.railway.app

### Python / PATH
- Python 3.12 installed at: `C:\Users\mike\AppData\Local\Programs\Python\Python312\python.exe`
- `python` and `py` commands still point to stubs (use full path above)
