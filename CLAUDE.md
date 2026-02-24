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

## Project Status (as of 2026-02-25, session 13)

### PIPELINE + OPPORTUNITY INTELLIGENCE: FULLY OPERATIONAL AND DEPLOYED

**All phases COMPLETE.** Pipeline runs, scores, validates, loads to Supabase, and renders on Railway.

### Session 13 (2026-02-25) — Opportunity Intelligence Layer VERIFIED AND SHIPPED

#### DONE
- [x] `validate_opportunities.py --top-n 1` — PASS (sanity check, high confidence, real narrative)
- [x] `validate_opportunities.py --top-n 15` — PASS (9 high, 6 medium, 0 low confidence)
- [x] `supabase_loader.py --input-dir runs/local_001` — PASS (15 validated opps + 354 total records upserted)
- [x] Streamlit UI locally — PASS (unified opportunity view with evidence cards)
- [x] Fixed `st.expander()` `key=` kwarg not supported in installed Streamlit (used unique label text instead)
- [x] Emoji constants verified correct (Unicode escapes render in browser, cp1252 console is just display)
- [x] Railway deploy — PASS (all 15 cards rendering on production, confirmed by user)
- [x] Committed and pushed both repos:
  - **build-signals** `e2b47b7` on `master`
  - **build-signals-ui** `29d8eb6` on `main`

#### NOT DONE (carried forward)
- [ ] Full CI run: trigger GitHub Actions WITHOUT `skip_scoring` to test end-to-end
- [ ] `signal-source-code` Vite/TS frontend — not yet connected or worked on
- [ ] STRIPE_WEBHOOK_SECRET still a placeholder in `app/.env.local`
- [ ] Orphaned Codex files in build-signals-ui (`app_logic.py`, `tests/`, `TECH_STACK_AUDIT.md`)

### Previous Sessions (condensed)
- Sessions 1-3 (2026-02-09/10): Initial setup, bug fixes, PH pipeline, migrations 003-004
- Sessions 4-6 (2026-02-15/17): Full audit, pipeline upgrade build, Streamlit rewrite, all code complete
- Sessions 7-8 (2026-02-18): CI green with skip_scoring, 3 bugs fixed, Railway deploying
- Session 9 (2026-02-19): Full pipeline proven end-to-end, all dashboard tabs working on Railway
- Session 10 (2026-02-20): Opportunity Intelligence Layer code written (5 files), migration 006 applied
- Sessions 11-12 (2026-02-21/23): Spec alignment, local validation attempts (blocked by network), emoji fixes
- Session 13 (2026-02-25): All validation runs PASS, Supabase loaded, Railway deployed, both repos pushed

### Build Progress — All Steps PASS

| Step | File | Status |
|------|------|--------|
| 1. HN Listener | `scripts/hn_listener.py` | PASS |
| 2. GitHub Trending | `scripts/fetch_github_trending.py` | PASS |
| 3. Product Hunt | `scripts/fetch_producthunt.py` | PASS |
| 4. Google Trends | `scripts/fetch_google_trends.py` | PASS |
| 5. Claude AI Scoring | `scripts/score_signals.py` | PASS (77/334 kept) |
| 6. Tweet Generation | `scripts/generate_tweets.py` | PASS (5 drafts) |
| 7. Supabase Loader | `scripts/supabase_loader.py` | PASS (354 upserted to 4 tables) |
| 7b. Opportunity Validator | `scripts/validate_opportunities.py` | PASS (15 validated: 9 high, 6 medium) |
| 8. GitHub Actions | `.github/workflows/refresh-data.yml` | PASS (needs full CI verify without skip_scoring) |
| 9. Streamlit Dashboard | `build-signals-ui/app.py` | PASS (unified opportunity view on Railway) |

### Three Repos in Play

| Repo | Path | Branch | Latest Commit |
|------|------|--------|---------------|
| **build-signals** | `C:/Users/mike/build-signals` | `master` | `e2b47b7` |
| **build-signals-ui** | `C:/Users/mike/build-signals-ui` | `main` | `29d8eb6` |
| **signal-source-code** | `C:/Users/mike/signal-source-code` | — | Not yet worked on |

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
1. hn_listener.py -> ask_hn.jsonl, show_hn.jsonl
2. fetch_github_trending.py -> github_trending.jsonl
3. fetch_producthunt.py -> producthunt.jsonl
4. fetch_google_trends.py -> google_trends.jsonl (continue-on-error)
5. score_signals.py -> scored_signals.jsonl (needs ANTHROPIC_API_KEY)
6. generate_tweets.py -> tweet_drafts.jsonl (needs ANTHROPIC_API_KEY)
7. validate_opportunities.py -> validated_opportunities.jsonl (needs ANTHROPIC_API_KEY + GITHUB_TOKEN + PH_TOKEN)
8. supabase_loader.py -> upserts to 4 tables

### Env Vars

**Root `.env`** (used by Python scripts via `load_dotenv()`):
- `ANTHROPIC_API_KEY` — Claude API key (working as of session 13)
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_KEY` — anon key
- `GITHUB_TOKEN` — fine-grained GitHub PAT
- `PH_TOKEN` — Product Hunt OAuth bearer token

**`app/.env.local`** (used by Next.js app + supabase_loader.py):
- `NEXT_PUBLIC_SUPABASE_URL` — Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — public anon key
- `SUPABASE_SERVICE_ROLE_KEY` — bypasses RLS (used by loader)
- `STRIPE_SECRET_KEY` — Stripe live key
- `STRIPE_WEBHOOK_SECRET` — placeholder (not yet configured)

### Key Technical Notes
- Python path: `C:\Users\mike\AppData\Local\Programs\Python\Python312\python.exe`
- `streamlit` not on PATH — use `python -m streamlit` instead
- `st.expander()` key= kwarg not supported — use unique label text
- Supabase stores JSON columns as text strings — dashboard must `json.loads()` them
- Dashboard password: `buildsignals123`
- Railway URL: https://build-signals-ui-production.up.railway.app
- Supabase: https://njwvtksauogsmberxrbd.supabase.co
- `gh` CLI not installed — use curl + GitHub API or web UI
- GitHub `SUPABASE_KEY` secret = service role key (not anon key) to bypass RLS

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



