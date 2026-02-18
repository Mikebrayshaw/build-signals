# Build Signals

Pain point discovery database for vibe coders. Find what to build + the GitHub repos to help build it.

**Data Sources:**
- Hacker News (Ask HN / Show HN) - problems people are asking about
- Product Hunt - launched products with validated traction
- GitHub Trending - repos gaining traction
- Google Trends - YoY keyword interest data

## Quick Start (Windows + Git Bash)

```bash
# Setup
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your tokens

# Run pipeline
python scripts/hn_listener.py --days 7 --out-dir runs/my_run
python scripts/fetch_github_trending.py --out-dir runs/my_run
python scripts/fetch_producthunt.py --days 7 --out-dir runs/my_run
python scripts/fetch_google_trends.py --input-dir runs/my_run --out-dir runs/my_run
python scripts/score_signals.py --input-dir runs/my_run --out-dir runs/my_run
python scripts/generate_tweets.py --input-dir runs/my_run --out-dir runs/my_run
python scripts/supabase_loader.py --input-dir runs/my_run
```

## Environment & Secret Management

1. Copy `.env.example` to `.env` for local runs.
2. Fill placeholder values only in `.env` (never commit real tokens).
3. Configure repository secrets for GitHub Actions:
   - `PH_TOKEN`, `GITHUB_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY` (data refresh workflow)
   - `ANTHROPIC_API_KEY` (scoring + tweet generation)
   - `LANDING_SUPABASE_URL`, `LANDING_SUPABASE_ANON_KEY` (landing page deploy workflow)

The landing page source (`landing/index.html`) intentionally contains `__SUPABASE_URL__` and `__SUPABASE_ANON_KEY__` placeholders. The deploy workflow replaces those placeholders at build time using GitHub Actions secrets before publishing to Pages.

## GitHub Actions Workflow

The `refresh-data.yml` workflow runs daily at 6 AM UTC (or manually via `workflow_dispatch`):

1. Fetch HN, GitHub Trending, Product Hunt data
2. Enrich with Google Trends (optional, `skip_trends`)
3. Score with Claude AI (optional, `skip_scoring`)
4. Generate tweet drafts
5. Load to Supabase

## Output

```
runs/
└── 20250130_120000/
    ├── ask_hn.jsonl
    ├── show_hn.jsonl
    ├── producthunt.jsonl
    ├── github_trending.jsonl
    ├── google_trends.jsonl
    ├── scored_signals.jsonl
    └── tweet_drafts.jsonl
```

## Supabase Schema

Migrations in `docs/migrations/` (apply in order via SQL Editor):

1. `001_add_producthunt_support.sql`
2. `002_add_subscribers_and_rls.sql`
3. `003_align_opportunities_schema.sql`
4. `004_drop_legacy_columns.sql`
5. `005_add_scoring_and_tweets.sql`

## Tokens

- **GitHub**: https://github.com/settings/tokens (no special scopes needed)
- **Product Hunt**: https://www.producthunt.com/v2/oauth/applications
- **Anthropic**: https://console.anthropic.com/settings/keys

## Preventing Accidental Key Commits

A dedicated `Secret Scan` CI workflow runs [gitleaks](https://github.com/gitleaks/gitleaks-action) on pushes and pull requests. If a key-like value is committed, CI fails so the secret can be removed and rotated before merge.
