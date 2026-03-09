# TODO — Build Signals

Last updated: 2026-03-09 (Session 20)

---

## STATUS: STRIPE DEPLOY IN PROGRESS — 2 of 4 manual steps done

Stripe product + webhook created. Migration 008 and Railway env vars still pending. Code ready to commit + deploy after.

---

## IMMEDIATE — Stripe Deploy (in progress)

### Manual Steps — Mike's Checklist
1. ~~**Stripe Dashboard**: Create product "Build Signals Pro", $99/year recurring~~ — DONE
   - Product ID: `prod_U5TPqYbDTYzFCB`
   - Price ID: `price_1T7ISG7pmIxaLWJWoMLw7a8u`
2. ~~**Stripe Dashboard**: Add webhook with 3 events~~ — DONE
   - Webhook secret: `whsec_pASdW9V6roYCoLMMFcJSiCE1gul7BAVm`
3. **Supabase SQL Editor**: Run `docs/migrations/008_add_subscriptions.sql` — **TODO**
4. **Railway env vars** — **TODO**
   - `STRIPE_SECRET_KEY` → Mike's Stripe secret key
   - `STRIPE_PRICE_ID` → `price_1T7ISG7pmIxaLWJWoMLw7a8u`
   - `STRIPE_WEBHOOK_SECRET` → `whsec_pASdW9V6roYCoLMMFcJSiCE1gul7BAVm`
   - `SUPABASE_SERVICE_KEY` → service role key (from `app/.env.local`)
   - `SUPABASE_URL` → `https://njwvtksauogsmberxrbd.supabase.co`

### Then (Claude does this after manual steps)
1. Commit Stripe changes in `signal-source-code/` (10 files) and `build-signals/` (migration)
2. `npm run build && railway up` to deploy
3. Test with `4242 4242 4242 4242`
4. Verify: blurred prompts -> checkout -> webhook -> prompt un-blurs -> refresh persists

---

## NEXT UP — After Stripe

- [ ] Full CI run: trigger `refresh-data.yml` WITHOUT `skip_scoring`
- [ ] Update landing page showcase signals (still showing Feb 26 data)
- [ ] Get PH_TOKEN for Product Hunt data in pipeline

---

## CARRIED FORWARD — Lower Priority

- [ ] Orphaned Codex files in build-signals-ui (`app_logic.py`, `tests/`, `TECH_STACK_AUDIT.md`)
- [ ] ~18 Codex branches on build-signals-ui remote
- [ ] `generate_tweets.py` cp1252 print crash (cosmetic — data is fine)
- [ ] `anthropic` SDK pin at `0.43.0` (works but old)

---

## COMPLETED

### Session 20 (2026-03-09)
- [x] Stripe product created ($99/year, Price ID: `price_1T7ISG7pmIxaLWJWoMLw7a8u`)
- [x] Stripe webhook created (3 events, secret: `whsec_pASdW9V6roYCoLMMFcJSiCE1gul7BAVm`)

### Session 19 (2026-03-07)
- [x] Full pipeline run (runs/20260307_084554): 226 signals -> 52 scored -> 15 validated -> 266 loaded to Supabase
- [x] Fixed .env \r line endings (was breaking all Anthropic API calls)
- [x] Restored Supabase from free-tier hibernation

### Session 18 (2026-02-28)
- [x] Stripe $99/year Pro paywall code complete (10 files in signal-source-code, 1 in build-signals)

### Session 17 (2026-02-26)
- [x] Landing page rewrite, committed `87280bc`, deployed to Railway

### Session 16 (2026-02-26)
- [x] Migration 007, validation re-run, Supabase loader, frontend deployed

### Sessions 1-15 (condensed)
- Pipeline end-to-end, Streamlit dashboard, Vite/React frontend, CI, 7 migrations

---

## Key Reference

- Pipeline repo: `C:/Users/mike/build-signals` (branch: `master`, commit: `3d5a1c9`)
- Dashboard repo: `C:/Users/mike/build-signals-ui` (branch: `main`)
- Vite frontend: `C:/Users/mike/signal-source-code` (branch: `main`, commit: `87280bc`)
- Latest run: `runs/20260307_084554`
- Landing: https://signal-source-code-production.up.railway.app/
- Dashboard: https://signal-source-code-production.up.railway.app/app/
- Password: `buildsignals123`
- Python: `C:/Users/mike/AppData/Local/Programs/Python/Python312/python.exe`
