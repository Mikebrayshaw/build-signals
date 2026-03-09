# TASKS.md — Build Signals

> Last updated: 2026-03-09, session 20 in progress

## Status: STRIPE DEPLOY IN PROGRESS — 2 of 4 manual steps done

Stripe product + webhook created in Stripe Dashboard. Still need: run migration 008 in Supabase, set 5 Railway env vars. Then commit + build + deploy + test.

---

## Session 20 — Stripe Deploy (2026-03-09)

### DONE
- [x] Stripe product "Build Signals Pro" created ($99/year recurring)
  - Product ID: `prod_U5TPqYbDTYzFCB`
  - Price ID: `price_1T7ISG7pmIxaLWJWoMLw7a8u`
- [x] Stripe webhook endpoint created
  - URL: `https://signal-source-code-production.up.railway.app/api/stripe/webhook`
  - Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
  - Webhook secret: `whsec_pASdW9V6roYCoLMMFcJSiCE1gul7BAVm`

### HALF-FINISHED — Mike's Manual Steps (2 of 4 complete)
- [x] 1. Stripe product + price — DONE
- [x] 2. Stripe webhook — DONE
- [ ] 3. **Supabase SQL Editor**: Run `docs/migrations/008_add_subscriptions.sql`
  - Creates `subscriptions` table, indexes, RLS policies
- [ ] 4. **Railway env vars**: Add to `signal-source-code` service:
  - `STRIPE_SECRET_KEY` → Mike's Stripe secret key
  - `STRIPE_PRICE_ID` → `price_1T7ISG7pmIxaLWJWoMLw7a8u`
  - `STRIPE_WEBHOOK_SECRET` → `whsec_pASdW9V6roYCoLMMFcJSiCE1gul7BAVm`
  - `SUPABASE_SERVICE_KEY` → service role key (from `app/.env.local`)
  - `SUPABASE_URL` → `https://njwvtksauogsmberxrbd.supabase.co`

### AFTER MANUAL STEPS — Claude Does This
1. Commit all Stripe changes in `signal-source-code/` (10 files) and `build-signals/` (migration + docs)
2. `npm run build` in `signal-source-code/`
3. `railway up` to deploy
4. Test with Stripe test card `4242 4242 4242 4242`
5. Verify: blurred prompts -> checkout -> webhook -> prompt un-blurs -> refresh persists

### Uncommitted Stripe Code (written session 18)
**In `signal-source-code/` (10 files):**
- `package.json` — Added `stripe`, `dotenv` deps
- `server.js` — Rewritten with 3 API routes: `/api/stripe/webhook`, `/api/checkout`, `/api/subscription/:userId`
- `src/context/SubscriptionContext.tsx` — NEW: `isPro`, `loading`, `currentPeriodEnd`, `checkout()`, `refresh()`
- `src/App.tsx` — Wrapped with `<SubscriptionProvider>`
- `src/components/signals/SignalCard.tsx` — Pro: expandable prompt. Free: blurred + upgrade overlay
- `src/components/signals/SignalCardCompact.tsx` — Badge: "Build" for Pro, "Pro" (violet) for free
- `src/pages/SettingsPage.tsx` — New Subscription section
- `index.html` — Pro card: "$99/year", active CTA
- `vite.config.ts` — Added `/api` proxy to `localhost:8080`

**In `build-signals/` (1 file):**
- `docs/migrations/008_add_subscriptions.sql` — `subscriptions` table + RLS policies

---

## Remaining Work — Priority Order

### High Priority
- [ ] **Finish Stripe deploy** — steps 3-4 above, then commit + build + deploy
- [ ] **Full CI run** — trigger `refresh-data.yml` WITHOUT `skip_scoring`

### Medium Priority
- [ ] **Landing page showcase signals** — 3 hardcoded examples from Feb 26, update with fresh signals
- [ ] **PH_TOKEN** — get Product Hunt OAuth token for pipeline
- [ ] **Update `anthropic` pin** — `0.43.0` works but old

### Low Priority
- [ ] **Orphaned Codex files** in build-signals-ui (`app_logic.py`, `tests/`, `TECH_STACK_AUDIT.md`)
- [ ] **Codex branches cleanup** — ~18 remote branches on build-signals-ui
- [ ] **Windows cp1252 crash** in `generate_tweets.py` preview print (data fine)

---

## Completed

### Session 20 (2026-03-09)
- [x] Stripe product + price created in Stripe Dashboard
- [x] Stripe webhook endpoint created with 3 events

### Session 19 (2026-03-07)
- [x] Fresh pipeline run (52 scored, 15 validated, 266 loaded to Supabase)
- [x] Fixed .env \r line endings
- [x] Restored Supabase from hibernation

### Session 18 (2026-02-28)
- [x] Stripe $99/year Pro subscription paywall — code complete across 10 files
- [x] SubscriptionContext, SignalCard blur/overlay, SettingsPage subscription section
- [x] server.js rewritten with 3 Stripe API routes
- [x] Migration 008 written (subscriptions table + RLS)

### Session 17 (2026-02-26)
- [x] Landing page full rewrite, committed `87280bc`, deployed to Railway

### Session 16 (2026-02-26)
- [x] Migration 007, validation re-run, frontend deployed

### Sessions 1-15 (condensed)
- Pipeline end-to-end, Streamlit dashboard, Vite frontend, CI, 7 migrations

---

## Key Reference

- Pipeline repo: `C:/Users/mike/build-signals` (branch: `master`, commit: `3d5a1c9`)
- Dashboard repo: `C:/Users/mike/build-signals-ui` (branch: `main`, commit: `29d8eb6`)
- Vite frontend: `C:/Users/mike/signal-source-code` (branch: `main`, commit: `87280bc`)
- Latest pipeline run: `runs/20260307_084554` (2026-03-07)
- Landing page: https://signal-source-code-production.up.railway.app/
- Dashboard: https://signal-source-code-production.up.railway.app/app/
- Supabase: https://njwvtksauogsmberxrbd.supabase.co
- Railway (Streamlit): https://build-signals-ui-production.up.railway.app
- Railway project: `trustworthy-vibrancy`, service: `signal-source-code`
- Dashboard password: `buildsignals123`
- Python: `C:/Users/mike/AppData/Local/Programs/Python/Python312/python.exe`

## Git State (as of session 20)

- **build-signals**: `master`, uncommitted: CLAUDE.md, TASKS.md, tasks/todo.md, docs/migrations/008_add_subscriptions.sql
- **signal-source-code**: `main`, uncommitted: 10 Stripe files from session 18
- **build-signals-ui**: `main`, clean
