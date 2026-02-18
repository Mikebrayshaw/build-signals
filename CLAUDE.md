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

## Project Status (as of 2026-02-17, end of session 6)

### PIPELINE UPGRADE: TESTING IN PROGRESS (Session 7)

**Phase 1 (Audit): COMPLETE**
**Phase 2 (Plan): COMPLETE**
**Phase 3 (Build): CODE COMPLETE**
**Phase 4 (Test): IN PROGRESS** ← session 7 started here, partially done

### Session 7 Progress (2026-02-18)

#### Local Script Testing — 5/7 PASS, 2 BLOCKED

| # | Script | Result | Notes |
|---|--------|--------|-------|
| 1 | `hn_listener.py` | **PASS** | 16 posts (7 ask, 9 show) |
| 2 | `fetch_github_trending.py` | **PASS** | 13 repos (GitHub only returned 13, not a bug) |
| 3 | `fetch_producthunt.py` | **PASS** | 20 posts |
| 4 | `fetch_google_trends.py` | **PASS** | 5 keywords, 3 rising. Needed `pip install pytrends` first |
| 5 | `score_signals.py` | **BLOCKED** | Anthropic API: "credit balance too low". Code runs, handles errors gracefully |
| 6 | `generate_tweets.py` | **BLOCKED** | Same Anthropic billing issue |
| 7 | `supabase_loader.py` | **PASS** | 54 records upserted (49 opportunities + 5 google_trends) |

- Test run output is in `runs/20260217_160406/`
- Data is **live in Supabase** — 49 opportunities + 5 google_trends rows

#### Streamlit Dashboard — IN PROGRESS (bugs being fixed)

- App starts, login works, connects to Supabase
- **Fixed (session 7):** `st.secrets.get()` crashes when no `secrets.toml` exists → added `_get_secret()` helper
- **Fixed (session 7):** `interest_over_time` and `related_queries` stored as JSON strings in Supabase, dashboard assumed parsed lists → added `json.loads()` for string fields
- **NOT YET VERIFIED:** Need to restart Streamlit and confirm all 3 tabs render without errors
- Signals tab will show "No scored signals" (expected — scoring was skipped due to billing)
- Tweet Drafts tab will show "No tweet drafts found" (expected — same reason)
- Trends tab should show 5 keywords with sparkline bars

### What to Do Next (Session 8)

1. **Restart Streamlit** and verify all 3 tabs render (the JSON string fix was applied but not tested yet)
2. **Top up Anthropic credits** → retest `score_signals.py` and `generate_tweets.py`
3. **Trigger GitHub Actions workflow** manually — test full CI pipeline
4. **Commit & push** changes in both repos
5. **Verify Streamlit on Railway** after push

### Uncommitted Changes (IMPORTANT)
- **build-signals**: `requirements.txt`, `.env.example` modified; `scripts/match_github.py` deleted
- **build-signals-ui**: `app.py` rewritten + 2 bug fixes from session 7:
  1. Added `_get_secret()` helper to avoid `secrets.toml` crash
  2. Added `json.loads()` for JSON string fields from Supabase
  3. Added `import json` at top

### Build Progress (Sessions 5-6) — All Done

| Step | File | Status |
|------|------|--------|
| 1. GitHub Trending Scraper | `scripts/fetch_github_trending.py` | DONE + TESTED |
| 2. Product Hunt | `scripts/fetch_producthunt.py` | DONE + TESTED |
| 3. Google Trends | `scripts/fetch_google_trends.py` | DONE + TESTED |
| 4. Claude AI Scoring | `scripts/score_signals.py` | DONE (needs API credits to test) |
| 5. Tweet Generation | `scripts/generate_tweets.py` | DONE (needs API credits to test) |
| 6. Supabase Migration | `docs/migrations/005_add_scoring_and_tweets.sql` | DONE + RUN |
| 7. Supabase Loader | `scripts/supabase_loader.py` | DONE + TESTED |
| 8. GitHub Actions | `.github/workflows/refresh-data.yml` | DONE (not yet triggered) |
| 9. Streamlit Dashboard | `build-signals-ui/app.py` | DONE + 2 bug fixes applied |
| - | `requirements.txt` + `.env.example` | DONE |

### Infrastructure — All Done
- [x] Migration 005 run in Supabase (2026-02-17)
- [x] ANTHROPIC_API_KEY added to GitHub Secrets (2026-02-17)
- [x] SUPABASE_SERVICE_KEY added to Railway (2026-02-17)
- [x] match_github.py deleted (2026-02-17)

### Three Repos in Play

| Repo | Path | Purpose |
|------|------|---------|
| **build-signals** | `C:/Users/mike/build-signals` | Python pipeline (fetch → score → tweet → load) + Next.js app + landing page |
| **build-signals-ui** | `C:/Users/mike/build-signals-ui` | Streamlit dashboard (3-tab: Tweets, Signals, Trends) |
| **signal-source-code** | `C:/Users/mike/signal-source-code` | Vite/TS frontend with Supabase + Tailwind |

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
│   └── supabase_loader.py         # Multi-table upsert (opportunities, tweet_drafts, google_trends)
├── .github/workflows/
│   └── refresh-data.yml           # 7-step pipeline with skip_trends/skip_scoring inputs
├── docs/migrations/
│   ├── 001-004                    # Previous migrations (all applied)
│   └── 005_add_scoring_and_tweets.sql  # Applied 2026-02-17
```

Pipeline order (in workflow):
1. hn_listener.py → ask_hn.jsonl, show_hn.jsonl
2. fetch_github_trending.py → github_trending.jsonl
3. fetch_producthunt.py → producthunt.jsonl
4. fetch_google_trends.py → google_trends.jsonl (continue-on-error)
5. score_signals.py → scored_signals.jsonl (needs ANTHROPIC_API_KEY)
6. generate_tweets.py → tweet_drafts.jsonl (needs ANTHROPIC_API_KEY)
7. supabase_loader.py → upserts to 3 tables

### Env Vars

**Root `.env`** (used by Python scripts via `load_dotenv()`):
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_KEY` — anon key
- `GITHUB_TOKEN` — fine-grained GitHub PAT (working)
- `PH_TOKEN` — Product Hunt OAuth bearer token (working)
- `ANTHROPIC_API_KEY` — Claude API key (needed for scoring + tweets)

**`app/.env.local`** (used by Next.js app + supabase_loader.py):
- `NEXT_PUBLIC_SUPABASE_URL` — Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — public anon key
- `SUPABASE_SERVICE_ROLE_KEY` — bypasses RLS (used by loader)
- `STRIPE_SECRET_KEY` — Stripe live key
- `STRIPE_WEBHOOK_SECRET` — placeholder (not yet configured)

### Session History
- Session 1 (2026-02-09): Fixed httpx, supabase_loader env loading, migration 003
- Session 2 (2026-02-09): PH pipeline, runs/latest, requirements.txt, migration 004 written
- Session 3 (2026-02-10): GitHub PAT refresh, migration 004 applied, match_github re-run
- Session 4 (2026-02-15): Full audit of all 3 repos. Upgrade prompt reviewed. Phase 1 complete.
- Session 5 (2026-02-16): Pipeline upgrade build. Steps 1-8 of 9 done.
- Session 6 (2026-02-17): Streamlit rewrite, requirements.txt, .env.example, migration 005 run, all secrets added, match_github deleted. ALL CODE COMPLETE. Nothing tested yet.

### Open Low-Priority Items
- Verify GITHUB_TOKEN, PH_TOKEN, SUPABASE_SERVICE_ROLE_KEY are in GitHub Secrets
- STRIPE_WEBHOOK_SECRET still a placeholder in app/.env.local

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
