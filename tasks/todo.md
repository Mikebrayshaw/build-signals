# TODO — Build Signals

Last updated: 2026-02-26 (Session 15)

---

## STATUS: "BUILD THIS" FEATURE CODE-COMPLETE, NOT YET RUN OR DEPLOYED

All code is written and TypeScript builds pass. Migration not yet applied, pipeline not yet re-run, frontend not yet visually verified.

---

## IMMEDIATE — Do These First Next Session

### 1. Apply Migration 007 (Supabase SQL Editor)
```sql
ALTER TABLE validated_opportunities ADD COLUMN IF NOT EXISTS build_prompt TEXT;
```
- Go to https://njwvtksauogsmberxrbd.supabase.co → SQL Editor → Run

### 2. Re-run Validation Pipeline (generates build_prompt content)
```bash
cd C:/Users/mike/build-signals
python scripts/validate_opportunities.py --input-dir runs/local_001 --top-n 15
```
- Check JSONL output: each record should have a `build_prompt` field with structured content (## Problem, ## Target User, ## MVP Scope, ## Tech Stack, ## Build Prompt)

### 3. Re-run Supabase Loader
```bash
python scripts/supabase_loader.py --input-dir runs/local_001
```
- Query Supabase to confirm `build_prompt` column populated:
  `SELECT id, signal_title, LEFT(build_prompt, 100) FROM validated_opportunities WHERE build_prompt IS NOT NULL;`

### 4. Visually Verify Vite Frontend
```bash
cd C:/Users/mike/signal-source-code
npm run dev
```
- Open http://localhost:5173/app/ (or 5174)
- Cards should show collapsible "Build This" section
- Click to expand — should show preformatted prompt
- "Copy" button should copy to clipboard
- Compact view should show "Build" badge on cards that have prompts

### 5. Commit + Push
- **build-signals** (on `master`):
  - `docs/migrations/007_add_build_prompt.sql`
  - `scripts/validate_opportunities.py` (SYNTHESIZE_PROMPT + build_prompt in output)
  - `scripts/supabase_loader.py` (build_prompt in normalize_validated_opportunity)
- **signal-source-code** (on `main`):
  - ALL changes from session 14 (validated_opportunities rewire) AND session 15 (build_prompt UI)
  - `src/lib/types.ts`, `src/lib/mappers.ts`
  - `src/components/signals/SignalCard.tsx`, `src/components/signals/SignalCardCompact.tsx`
  - Plus all the session 14 files (constants, context, filters, stats, layout, etc.)

---

## HALF-FINISHED — Needs Attention

### Vite Frontend Visual Verification (from Session 14)
- Session 14 rewired all 14 files from `opportunities` to `validated_opportunities`
- Column name mismatch found and fixed (signal_title, signal_source, evidence_*)
- `npm run build` passes but **cards have NEVER been visually verified with live data**
- Must confirm: cards render, evidence shows, filters work, sort works

---

## CARRIED FORWARD — Lower Priority

- [ ] Full CI run: trigger GitHub Actions WITHOUT `skip_scoring` to test end-to-end pipeline
- [ ] Deploy Vite frontend to Vercel/Railway/etc
- [ ] STRIPE_WEBHOOK_SECRET still a placeholder in `app/.env.local`
- [ ] Orphaned Codex files in build-signals-ui (`app_logic.py`, `tests/`, `TECH_STACK_AUDIT.md`) — can delete
- [ ] `gh` CLI not installed — limits workflow triggering from terminal

---

## FILES CHANGED THIS SESSION (Session 15) — Uncommitted

### build-signals/ (Python pipeline)
| File | Change |
|------|--------|
| `docs/migrations/007_add_build_prompt.sql` | NEW — adds `build_prompt TEXT` column |
| `scripts/validate_opportunities.py` | MODIFIED — SYNTHESIZE_PROMPT now requests build_prompt, response parsing extracts it, output record includes it |
| `scripts/supabase_loader.py` | MODIFIED — `normalize_validated_opportunity()` passes through `build_prompt` |

### signal-source-code/ (Vite frontend)
| File | Change |
|------|--------|
| `src/lib/types.ts` | MODIFIED — `build_prompt?: string` on Signal + ValidatedOpportunityRow |
| `src/lib/mappers.ts` | MODIFIED — maps `row.build_prompt` into Signal |
| `src/components/signals/SignalCard.tsx` | MODIFIED — collapsible "Build This" `<details>` with Copy button |
| `src/components/signals/SignalCardCompact.tsx` | MODIFIED — "Build" badge when prompt exists |

---

## Key Reference

- Pipeline repo: `C:/Users/mike/build-signals` (branch: `master`)
- Dashboard repo: `C:/Users/mike/build-signals-ui` (branch: `main`)
- Vite frontend: `C:/Users/mike/signal-source-code` (branch: `main`)
- Supabase: https://njwvtksauogsmberxrbd.supabase.co
- Railway (Streamlit): https://build-signals-ui-production.up.railway.app
- Dashboard password: `buildsignals123`
- Python: `C:/Users/mike/AppData/Local/Programs/Python/Python312/python.exe`
