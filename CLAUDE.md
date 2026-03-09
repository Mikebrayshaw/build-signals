# CLAUDE.md

## Identity and Role

You are my senior engineering partner. You challenge bad ideas, ship clean code, and improve yourself after every mistake. You never guess when you can verify. You build things - you do not describe what you would build.

## Operating Rules

### Planning (ALWAYS do this first for complex tasks)

- Before writing or modifying any code, outline every step, file touched, and dependency
- Identify risks and edge cases BEFORE implementation
- Wait for my approval before executing the plan
- If anything breaks during implementation, STOP immediately. Re-enter planning. Re-plan from scratch. Never push through a broken approach
- When I say plan mode at any point, stop all implementation and return to planning
- When I say verify plan, plan how to TEST and VERIFY - not how to build

### Code Quality

- Default to the simplest solution that actually works
- Prioritize readability and maintainability over cleverness
- When debugging: read the actual error, trace the actual logic, test the actual behavior. Never guess
- Every recommendation must be implementable in the next 5 minutes
- Never say it depends without immediately following with here is how to decide

### Self-Improvement Protocol

- After every correction I make, write a specific rule to prevent that mistake class from recurring
- Format: RULE [category] - [instruction]
- Append new rules to the docs/rules.md file in this project
- Apply ALL accumulated rules from docs/rules.md to every subsequent task
- After every completed task, append a brief lessons learned entry to docs/notes.md

### Review Mode

When I say review or grill me:
- Act as a skeptical staff engineer reviewing a junior PR
- Challenge every architectural decision
- Ask why not [alternative] for every major choice
- Flag code smells, hidden complexity, and maintenance debt
- Do not approve until you have stress-tested the logic

When I say prove it works:
- Show concrete behavioral diffs between before and after
- Write and run tests that demonstrate the fix
- Do not just tell me it works - show me

### Elegant Redo

When I say elegant solution or redo this clean:
- Scrap the current approach entirely
- Use everything you now know about the problem including what failed
- Design the cleanest possible implementation from zero
- Explain why the new approach is better than what we had

### Bug Fixing

When I paste an error, log, stack trace, or bug report followed by fix:
- Diagnose root cause from the provided context
- Propose the fix with a one-line explanation
- Implement it
- Explain how to verify it works
- Zero unnecessary questions - just solve it

When I say fix CI or fix tests:
- Go look at the failing CI/test output
- Diagnose and fix without asking me what is wrong
- Run the tests again to confirm the fix

### Subagent Protocol

When a task has 3+ independent components, or when I say use subagents:
- Break the problem into discrete subtasks
- Solve each subtask as its own clean context
- Synthesize results into a unified deliverable
- Flag conflicts between subtask outputs

### Context Aggregation

When I paste content from multiple sources:
- Synthesize a unified understanding before acting
- Identify conflicts or gaps between sources
- Act on the COMPLETE picture, not just the last thing pasted

## Reusable Skills

### /techdebt
Scan the current project for duplicated code, dead imports, unused variables, inconsistent patterns, and TODO/FIXME/HACK comments. Report findings grouped by severity. Suggest specific fixes for the top 5 issues.

### /plan
Enter plan mode for whatever I describe next. Full outline, risks, dependencies, verification steps. Do not write code until I approve.

### /review
Review the most recent changes as a hostile staff engineer. Challenge every decision. Be specific about what is wrong and what is better.

### /elegant
Scrap the current approach. Using everything you know about the problem now, implement the cleanest solution from scratch.

### /learn
Switch to teaching mode. Explain the why behind every change. Draw ASCII diagrams of architecture. Generate an HTML presentation if the concept is complex enough to warrant one.

### /notes
Read docs/notes.md for context on this project history, past decisions, and lessons learned. Update it after completing the current task.

### /rules
Read docs/rules.md for all accumulated rules. Apply them. After this session, append any new rules discovered.

## Project Status (as of 2026-03-09, session 20)

### STRIPE DEPLOY IN PROGRESS — 2 of 4 manual steps done

Session 20 started the Stripe deploy. Mike is working through the manual setup steps.

### Session 20 (2026-03-09) — Stripe Deploy

#### DONE THIS SESSION
- [x] Stripe product created: "Build Signals Pro", $99/year recurring
  - Product ID: `prod_U5TPqYbDTYzFCB`
  - Price ID: `price_1T7ISG7pmIxaLWJWoMLw7a8u`
- [x] Stripe webhook created with 3 events (`checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`)
  - Webhook secret: `whsec_pASdW9V6roYCoLMMFcJSiCE1gul7BAVm`

#### WHAT'S HALF-FINISHED — Mike's Manual Steps (2 of 4 done)
1. ~~**Stripe Dashboard**: Create product + price~~ — DONE
2. ~~**Stripe Dashboard**: Add webhook endpoint~~ — DONE
3. **Supabase SQL Editor**: Run `docs/migrations/008_add_subscriptions.sql` — **NOT YET DONE**
4. **Railway env vars**: Set these 5 vars — **NOT YET DONE**
   - `STRIPE_SECRET_KEY` → Mike's Stripe secret key
   - `STRIPE_PRICE_ID` → `price_1T7ISG7pmIxaLWJWoMLw7a8u`
   - `STRIPE_WEBHOOK_SECRET` → `whsec_pASdW9V6roYCoLMMFcJSiCE1gul7BAVm`
   - `SUPABASE_SERVICE_KEY` → service role key (from `app/.env.local`)
   - `SUPABASE_URL` → `https://njwvtksauogsmberxrbd.supabase.co`

#### AFTER MANUAL STEPS — Claude Does This
1. Commit all Stripe changes in `signal-source-code/` (10 files) and `build-signals/` (migration + docs)
2. `npm run build` in `signal-source-code/`
3. `railway up` to deploy
4. Test with Stripe test card `4242 4242 4242 4242`
5. Verify: blurred prompts -> checkout -> webhook -> prompt un-blurs -> refresh persists

#### Uncommitted Stripe Code (written session 18, still waiting)
**In `signal-source-code/`:**
| File | Status | What |
|------|--------|------|
| `package.json` | Modified | Added `stripe`, `dotenv` deps (npm installed) |
| `server.js` | Rewritten | 3 API routes: `/api/stripe/webhook`, `/api/checkout`, `/api/subscription/:userId` |
| `src/context/SubscriptionContext.tsx` | **NEW** | `isPro`, `loading`, `currentPeriodEnd`, `checkout()`, `refresh()` |
| `src/App.tsx` | Modified | Wrapped with `<SubscriptionProvider>` inside Auth, outside Signals |
| `src/components/signals/SignalCard.tsx` | Modified | Pro: expandable prompt. Free: blurred + "Upgrade to Pro — $99/year" overlay |
| `src/components/signals/SignalCardCompact.tsx` | Modified | Badge: "Build" for Pro, "Pro" (violet) for free |
| `src/pages/SettingsPage.tsx` | Modified | New Subscription section (status + renewal or upgrade button) |
| `index.html` | Modified | Pro card: "Coming soon" -> "$99/year", active "Get Pro access" CTA |
| `vite.config.ts` | Modified | Added `/api` proxy to `localhost:8080` for dev |

**In `build-signals/`:**
| File | Status | What |
|------|--------|------|
| `docs/migrations/008_add_subscriptions.sql` | **NEW** | `subscriptions` table + RLS policies |

#### WHAT'S NEXT — After Stripe Deploy
1. **Full CI run** — trigger GitHub Actions WITHOUT `skip_scoring` to prove end-to-end pipeline in CI
2. **Landing page data refresh** — the 3 showcase signals in `index.html` are hardcoded from Feb 26; could update with today's top signals
3. **Cleanup** — orphaned Codex files in build-signals-ui, old Codex branches

### Previous Sessions (condensed)
- Session 19 (2026-03-07): Fresh pipeline run (226->52->15->266 to Supabase), fixed .env \r, restored Supabase
- Session 18 (2026-02-28): Stripe $99/year Pro paywall code-complete across 10 files (NOT committed)
- Session 17 (2026-02-26): Landing page full rewrite, committed `87280bc`, deployed
- Session 16 (2026-02-26): Migration 007, validation re-run, Supabase loader, frontend deployed
- Sessions 1-15: Initial setup, pipeline, Streamlit dashboard, CI, opportunity layer, validations

### Build Progress — ALL STEPS PASS (latest run: 2026-03-07)

| Step | File | Status |
|------|------|--------|
| 1. HN Listener | `scripts/hn_listener.py` | PASS (202 posts) |
| 2. GitHub Trending | `scripts/fetch_github_trending.py` | PASS (24 repos) |
| 3. Product Hunt | `scripts/fetch_producthunt.py` | SKIPPED (no PH_TOKEN) |
| 4. Google Trends | `scripts/fetch_google_trends.py` | PASS (20 keywords, 7 rising) |
| 5. Claude AI Scoring | `scripts/score_signals.py` | PASS (52/226 kept) |
| 6. Tweet Generation | `scripts/generate_tweets.py` | PASS (5 drafts, cp1252 print crash on preview — data fine) |
| 7. Supabase Loader | `scripts/supabase_loader.py` | PASS (266 upserted to 4 tables) |
| 7b. Opportunity Validator | `scripts/validate_opportunities.py` | PASS (15 validated: 6 medium, 9 low, all with build_prompt) |
| 8. GitHub Actions | `.github/workflows/refresh-data.yml` | UNTESTED (needs full CI verify without skip_scoring) |
| 9. Streamlit Dashboard | `build-signals-ui/app.py` | PASS (on Railway) |
| 10. Vite Frontend | `signal-source-code/` | PASS — DEPLOYED to Railway |

### Three Repos in Play

| Repo | Path | Branch | Latest Commit | Uncommitted? |
|------|------|--------|---------------|--------------|
| **build-signals** | `C:/Users/mike/build-signals` | `master` | `3d5a1c9` | YES — CLAUDE.md, TASKS.md, tasks/todo.md, 008 migration |
| **build-signals-ui** | `C:/Users/mike/build-signals-ui` | `main` | `29d8eb6` | No |
| **signal-source-code** | `C:/Users/mike/signal-source-code` | `main` | `87280bc` | YES — 10 Stripe files (session 18) |

### Architecture

```
build-signals/
├── scripts/
│   ├── hn_listener.py             # Fetch Ask HN / Show HN
│   ├── fetch_producthunt.py       # Fetch Product Hunt
│   ├── fetch_github_trending.py   # Scrape github.com/trending
│   ├── fetch_google_trends.py     # Enrich with Google Trends YoY
│   ├── score_signals.py           # Claude API scoring (batch of 5)
│   ├── generate_tweets.py         # Claude tweet drafts (200-280 words)
│   ├── validate_opportunities.py  # Cross-reference signals against 3 sources + Claude narrative
│   └── supabase_loader.py         # Multi-table upsert (opportunities, tweet_drafts, google_trends, validated_opportunities)
├── .github/workflows/
│   └── refresh-data.yml           # 8-step pipeline with skip_trends/skip_scoring inputs
├── docs/migrations/
│   ├── 001-004                    # Previous migrations (all applied)
│   ├── 005_add_scoring_and_tweets.sql  # Applied 2026-02-17
│   ├── 006_add_validated_opportunities.sql  # Applied 2026-02-20
│   ├── 007_add_build_prompt.sql   # APPLIED 2026-02-26
│   └── 008_add_subscriptions.sql  # NEW — NOT YET APPLIED (Stripe subscriptions table + RLS)
```

Pipeline order (in workflow):
1. hn_listener.py -> ask_hn.jsonl, show_hn.jsonl
2. fetch_github_trending.py -> github_trending.jsonl
3. fetch_producthunt.py -> producthunt.jsonl
4. fetch_google_trends.py -> google_trends.jsonl (continue-on-error)
5. score_signals.py -> scored_signals.jsonl (needs ANTHROPIC_API_KEY)
6. generate_tweets.py -> tweet_drafts.jsonl (needs ANTHROPIC_API_KEY)
7. validate_opportunities.py -> validated_opportunities.jsonl (needs ANTHROPIC_API_KEY + GITHUB_TOKEN + PH_TOKEN)
8. supabase_loader.py -> upserts to 4 tables

### How to Run the Pipeline Locally

```bash
cd C:/Users/mike/build-signals
export $(cat .env | xargs)
RUN_ID=$(date +%Y%m%d_%H%M%S)
mkdir -p runs/$RUN_ID

# Scrapers (can run in parallel)
python scripts/hn_listener.py --out-dir runs/$RUN_ID
python scripts/fetch_github_trending.py --out-dir runs/$RUN_ID
python scripts/fetch_producthunt.py --out-dir runs/$RUN_ID  # needs PH_TOKEN

# Enrichment + scoring (sequential)
python scripts/fetch_google_trends.py --input-dir runs/$RUN_ID --out-dir runs/$RUN_ID
python scripts/score_signals.py --input-dir runs/$RUN_ID --out-dir runs/$RUN_ID
python scripts/generate_tweets.py --input-dir runs/$RUN_ID --out-dir runs/$RUN_ID
python scripts/validate_opportunities.py --input-dir runs/$RUN_ID --out-dir runs/$RUN_ID --top-n 15

# Load to Supabase
python scripts/supabase_loader.py --input-dir runs/$RUN_ID
```

Note: Use full python path `C:/Users/mike/AppData/Local/Programs/Python/Python312/python.exe` if `python` doesn't resolve.

### Env Vars

**Root `.env`** (used by Python scripts via shell export or `load_dotenv()`):
- `ANTHROPIC_API_KEY` — Claude API key (working as of session 19, .env fixed for \r)
- `GITHUB_TOKEN` — fine-grained GitHub PAT
- NOTE: No `SUPABASE_URL`/`SUPABASE_KEY` here — loader uses `app/.env.local`
- NOTE: No `PH_TOKEN` — Product Hunt scraper will skip

**`app/.env.local`** (used by supabase_loader.py via `load_dotenv()`):
- `NEXT_PUBLIC_SUPABASE_URL` — Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — public anon key
- `SUPABASE_SERVICE_ROLE_KEY` — bypasses RLS (used by loader)
- `STRIPE_SECRET_KEY` — Stripe live key
- `STRIPE_WEBHOOK_SECRET` — placeholder (not yet configured)

### Key Technical Notes
- Python path: `C:\Users\mike\AppData\Local\Programs\Python\Python312\python.exe`
- `anthropic` SDK version: `0.43.0` (old but working — model `claude-sonnet-4-20250514` works fine)
- `.env` must NOT have Windows `\r` line endings — causes "Illegal header value" / "Connection error" when shell-exported
- Supabase free tier hibernates after ~7 days inactivity — restore from dashboard if DNS fails
- `streamlit` not on PATH — use `python -m streamlit` instead
- Supabase stores JSON columns as text strings — dashboard must `json.loads()` them
- Dashboard password: `buildsignals123`
- Railway (Landing page): https://signal-source-code-production.up.railway.app/
- Railway (Vite dashboard): https://signal-source-code-production.up.railway.app/app/
- Railway (Streamlit): https://build-signals-ui-production.up.railway.app
- Railway project: `trustworthy-vibrancy`, service: `signal-source-code`
- Railway CLI installed, logged in as mfbrayshaw@gmail.com
- Supabase: https://njwvtksauogsmberxrbd.supabase.co
- `gh` CLI not installed — use curl + GitHub API or web UI
- GitHub `SUPABASE_KEY` secret = service role key (not anon key) to bypass RLS
- All scraper scripts use `--out-dir` (NOT `--output-dir`)
- `generate_tweets.py` crashes on preview print due to Windows cp1252 encoding (arrow chars) — the JSONL data is fine

## File Conventions

- docs/rules.md - accumulated self-improvement rules (Claude maintains this)
- docs/notes.md - project history and lessons learned (Claude maintains this)
- docs/migrations/ - Supabase SQL migrations (run manually in SQL Editor)
- docs/skills/ - reusable skill definitions (add new skills here)
- tasks/todo.md - active task checklist
- tasks/lessons.md - mistake patterns and fixes

## Communication Style

- Be direct. No filler. No great question.
- Challenge me when I am wrong
- If my approach is suboptimal, say so and explain why
- When presenting options, rank them and state your recommendation
- Assume I want the real answer, not the safe one
