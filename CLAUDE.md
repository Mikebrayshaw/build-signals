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

## Project Status (as of 2026-02-23, session 12 in progress)

### PIPELINE: FULLY OPERATIONAL + OPPORTUNITY INTELLIGENCE LAYER IN PROGRESS

**Phase 1-5: COMPLETE** — All original pipeline phases done
**Phase 6 (Opportunity Intelligence Layer): IN PROGRESS** — Spec aligned, verification pending

### Session 12 Summary (2026-02-22/23) — Verification Attempts + Local UI Run

#### What Got Done
- Ran `validate_opportunities.py` on `runs\local_001` with `--top-n 1` and `--top-n 15`
  - Both runs completed but all LLM classify/summarize calls failed with `Connection error`
  - Output JSONL is present but all opportunities are low confidence with boilerplate narratives
- Installed `build-signals-ui` dependencies (Streamlit is available locally)
- Created `C:\Users\mike\build-signals-ui\.streamlit\secrets.toml` with `PASSWORD`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`
- Streamlit app launches locally (user confirmed app opens)

#### What’s NOT Yet Tested (fully successful)
- Successful validator run with working Anthropic calls + live evidence (still blocked by outbound HTTPS)
- `supabase_loader.py` with validated_opportunities output (not run yet)
- UI verification with real, non-boilerplate opportunities
- Emoji rendering in UI (mojibake present)

#### Notes / Issues
- `validate_opportunities.py` runs are currently degraded:
  - No `GITHUB_TOKEN` (GitHub evidence skipped)
  - No `PH_TOKEN` (Product Hunt uses local fallback)
  - Anthropic calls fail (`Connection error`) → low-confidence output
- `build-signals-ui/app.py` has emoji mojibake due to encoding.
  - A partial fix attempted to insert `EMOJI_*` constants, but they were written as escaped strings (e.g. `EMOJI_SIGNAL = \"\\U0001F4E1\"`) and did not replace existing mojibake.
  - Page icon and several UI strings still show garbled characters.
  - Needs cleanup: replace mojibake with Unicode escapes or ASCII, and remove the broken constants block.

### Session 11 Summary (2026-02-21) — Intelligence Layer Spec Alignment + Local Validation Attempt

#### What Got Done
- Updated `scripts/validate_opportunities.py` to spec types, buyer‑intent query generation (3–5), evidence summaries, deterministic confidence scoring, and opportunity titles
- Updated `build-signals-ui/app.py` to a single unified Opportunity view (no tabs) with evidence summaries and type badges
- Installed Python 3.12 and dependencies from `requirements.txt`
 - Added `ANTHROPIC_API_KEY` to `C:\Users\mike\build-signals\.env` for local runs
 - Attempted local validation on `runs\local_001` with `--top-n 1` (re-run on 2026-02-21)

#### What’s Been Tested
- Python executable verified at `C:\Users\mike\AppData\Local\Programs\Python\Python312\python.exe`
- Dependencies installed successfully
 - Validator runs executed, but LLM calls failed due to outbound connection block (see below)

#### What’s NOT Yet Tested (fully successful)
- Successful live validator run (LLM calls currently blocked)
- `supabase_loader.py` with validated_opportunities output
- Streamlit UI render for the unified card view
- Smoke test for the “elderly people struggling with modern web” opportunity

#### Notes
- `python` and `py` commands still point to stubs; use the full Python path above
- Anthropic API calls fail locally with `Connection error` and socket permission error:
  - Connectivity tests to `api.anthropic.com:443` and `google.com:443` both fail (TCP blocked; ping OK)
  - Root cause appears to be outbound HTTPS blocked at OS/network level (not just Python firewall)
- Local validation run had no `GITHUB_TOKEN` (GitHub evidence skipped) and no `PH_TOKEN` (Product Hunt used local fallback)
- Because of the failure, `validated_opportunities.jsonl` contains:
  - `opportunity_type: "unknown"`, `queries: {}`
  - evidence blocks marked `no_queries`, all low confidence
  - narratives are boilerplate (no external evidence)
### Session 10 Summary (2026-02-20) — Opportunity Intelligence Layer

#### What Got Done
- Migration 006 (`validated_opportunities` table) — APPLIED in Supabase
- `scripts/validate_opportunities.py` — NEW script, fully implemented and tested with `--top-n 1`
- `scripts/supabase_loader.py` — Updated with Group 4 (validated_opportunities normalization + upsert)
- `build-signals-ui/app.py` — New "Opportunities" tab added as primary tab (4 tabs total now)
- `.github/workflows/refresh-data.yml` — Validation step added between tweets and Supabase load

#### What's Been Tested
- `validate_opportunities.py --top-n 1` ran successfully against `runs/local_001` (77 scored signals)
- All 3 source queries executed (Google Trends, GitHub API, Product Hunt local fallback)
- JSONL output verified with all expected fields

#### What's NOT Yet Tested
- Supabase loader with validated_opportunities.jsonl (need to run `supabase_loader.py`)
- Dashboard rendering of Opportunities tab (need to launch Streamlit locally or redeploy Railway)
- Full pipeline end-to-end with `--top-n 15` (tested only with 1)
- CI workflow with the new validation step

#### Previous Session (Session 9, 2026-02-19)
- Full pipeline proven end-to-end. All 3 original dashboard tabs working on Railway.

### Build Progress — All Steps PASS

| Step | File | Status |
|------|------|--------|
| 1. HN Listener | `scripts/hn_listener.py` | PASS |
| 2. GitHub Trending | `scripts/fetch_github_trending.py` | PASS |
| 3. Product Hunt | `scripts/fetch_producthunt.py` | PASS |
| 4. Google Trends | `scripts/fetch_google_trends.py` | PASS |
| 5. Claude AI Scoring | `scripts/score_signals.py` | PASS (77/334 kept) |
| 6. Tweet Generation | `scripts/generate_tweets.py` | PASS (5 drafts) |
| 7. Supabase Loader | `scripts/supabase_loader.py` | PASS (339 upserted) |
| 7b. Opportunity Validator | `scripts/validate_opportunities.py` | UPDATED (spec aligned; needs top-1/15 + loader test) |
| 8. GitHub Actions | `.github/workflows/refresh-data.yml` | UPDATED (validation step added, needs CI verify) |
| 9. Streamlit Dashboard | `build-signals-ui/app.py` | UPDATED (single unified Opportunities view; needs visual verify) |

### Infrastructure — All Done
- [x] Migration 005 run in Supabase (2026-02-17)
- [x] ANTHROPIC_API_KEY added to GitHub Secrets (2026-02-17)
- [x] SUPABASE_SERVICE_KEY added to Railway (2026-02-17)
- [x] match_github.py deleted (2026-02-17)
- [x] All 4 GitHub Actions secrets configured (2026-02-18)
- [x] Both repos committed and pushed (2026-02-18)
- [x] supabase/httpx version conflicts resolved in both repos (2026-02-18)
- [x] SUPABASE_KEY GitHub secret updated to service role key (2026-02-19)
- [x] Anthropic credits topped up and verified (2026-02-19)
- [x] Full pipeline run locally with real data (2026-02-19)
- [x] Migration 006 (`validated_opportunities` table) applied in Supabase (2026-02-20)

### Three Repos in Play

| Repo | Path | Purpose |
|------|------|---------|
| **build-signals** | `C:/Users/mike/build-signals` | Python pipeline (fetch → score → validate → tweet → load) + Next.js app + landing page |
| **build-signals-ui** | `C:/Users/mike/build-signals-ui` | Streamlit dashboard (single unified Opportunity view) |
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
│   ├── validate_opportunities.py  # Cross-reference signals against 3 sources + Claude narrative
│   └── supabase_loader.py         # Multi-table upsert (opportunities, tweet_drafts, google_trends, validated_opportunities)
├── .github/workflows/
│   └── refresh-data.yml           # 8-step pipeline with skip_trends/skip_scoring inputs
├── docs/migrations/
│   ├── 001-004                    # Previous migrations (all applied)
│   ├── 005_add_scoring_and_tweets.sql  # Applied 2026-02-17
│   └── 006_add_validated_opportunities.sql  # Applied 2026-02-20
```

Pipeline order (in workflow):
1. hn_listener.py → ask_hn.jsonl, show_hn.jsonl
2. fetch_github_trending.py → github_trending.jsonl
3. fetch_producthunt.py → producthunt.jsonl
4. fetch_google_trends.py → google_trends.jsonl (continue-on-error)
5. score_signals.py → scored_signals.jsonl (needs ANTHROPIC_API_KEY)
6. generate_tweets.py → tweet_drafts.jsonl (needs ANTHROPIC_API_KEY)
7. validate_opportunities.py → validated_opportunities.jsonl (needs ANTHROPIC_API_KEY + GITHUB_TOKEN + PH_TOKEN)
8. supabase_loader.py → upserts to 4 tables

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
- Session 7-8 (2026-02-18): CI green with skip_scoring. Fixed 3 bugs. Railway deploying.
- Session 9 (2026-02-19): FULL PIPELINE WORKING. Scoring + tweets + Supabase + Railway dashboard all verified. SUPABASE_KEY secret fixed to service role key.
- Session 10 (2026-02-20): Opportunity Intelligence Layer. All code written (5 files). Migration 006 applied. Validator tested with --top-n 1. Loader + dashboard + CI NOT yet tested. Changes NOT committed.

### What's Left to Test (Session 12)
- [ ] Fix emoji mojibake in `build-signals-ui/app.py` (remove broken `EMOJI_*` block, replace garbled chars)
- [ ] Re-run `validate_opportunities.py --top-n 1` with working Anthropic connectivity
- [ ] Re-run `validate_opportunities.py --top-n 15` with working Anthropic connectivity
- [ ] Run `supabase_loader.py` to upsert validated_opportunities
- [ ] Launch Streamlit and verify unified opportunity cards render with real evidence
- [ ] Smoke test: “elderly people struggling with modern web” card reads well

### Open Low-Priority Items
- Trigger GitHub Actions workflow WITHOUT skip_scoring to verify CI end-to-end
- STRIPE_WEBHOOK_SECRET still a placeholder in app/.env.local
- `hn_listener.py` fails on `runs/latest` symlink on Windows (non-blocking)
- `generate_tweets.py` print preview crashes on Windows cp1252 console (non-blocking)
- `requirements.txt` pins `anthropic==0.43.0` but local has `0.81.0` — consider updating pin
- `signal-source-code` Vite/TS frontend — not yet connected or worked on

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



