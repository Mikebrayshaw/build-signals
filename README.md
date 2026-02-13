# Build Signals

Pain point discovery database for vibe coders. Find what to build + the GitHub repos to help build it.

## Quick Start (Windows + Git Bash)

```bash
# Setup
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# Configure GitHub token
cp .env.example .env
# Edit .env with your GitHub PAT (https://github.com/settings/tokens)

# Step 1: Fetch HN posts (last 7 days)
python -m scripts.hn_listener --days 7

# Step 2: Match to GitHub repos
python scripts/match_github.py --input runs/latest
```


## Environment & Secret Management

1. Copy `.env.example` to `.env` for local runs.
2. Fill placeholder values only in `.env` (never commit real tokens).
3. Configure repository secrets for GitHub Actions:
   - `PH_TOKEN`, `GITHUB_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY` (data refresh workflow)
   - `LANDING_SUPABASE_URL`, `LANDING_SUPABASE_ANON_KEY` (landing page deploy workflow)

The landing page source (`landing/index.html`) intentionally contains `__SUPABASE_URL__` and `__SUPABASE_ANON_KEY__` placeholders. The deploy workflow replaces those placeholders at build time using GitHub Actions secrets before publishing to Pages.

## Commands

### HN Listener

```bash
# Fetch last 7 days (default)
python -m scripts.hn_listener

# Fetch last 30 days
python -m scripts.hn_listener --days 30

# Only Ask HN
python -m scripts.hn_listener --type ask

# Only Show HN
python -m scripts.hn_listener --type show
```

### GitHub Matcher

```bash
# Match all files in a run directory
python scripts/match_github.py --input runs/20250130_120000

# Use the latest run
python scripts/match_github.py --input $(cat runs/latest)

# Only high-scoring posts (50+ upvotes)
python scripts/match_github.py --input runs/latest --min-score 50

# More repos per post
python scripts/match_github.py --input runs/latest --repos-per-post 10
```

## Output

```
runs/
└── 20250130_120000/
    ├── ask_hn.jsonl           # Raw Ask HN posts
    ├── ask_hn_matched.jsonl   # With GitHub repos attached
    ├── show_hn.jsonl          # Raw Show HN posts
    └── show_hn_matched.jsonl  # With GitHub repos attached
```

### Matched Record Schema

```json
{
  "source": "hn_ask",
  "id": 42373343,
  "title": "Ask HN: How do you manage multiple AI subscriptions?",
  "url": "https://news.ycombinator.com/item?id=42373343",
  "author": "someuser",
  "score": 487,
  "descendants": 234,
  "text": "...",
  "created_utc": 1735312800,
  "created_iso": "2024-12-27T12:00:00Z",
  "keywords": ["ai", "subscriptions", "manage"],
  "github_repos": [
    {
      "name": "user/openai-cost-tracker",
      "url": "https://github.com/user/openai-cost-tracker",
      "description": "Track OpenAI API costs",
      "stars": 1247,
      "language": "Python",
      "topics": ["openai", "billing"],
      "updated_at": "2025-01-15T..."
    }
  ]
}
```


## Supabase schema and RLS

The canonical schema for loader + landing preview lives in:

- `supabase/migrations/202602130001_create_opportunities.sql`

### Apply order

1. Apply `202602130001_create_opportunities.sql` first (creates table, constraints, indexes, trigger, and RLS policies).
2. Apply any future migration files in lexical/timestamp order.

### Environment-specific apply steps

#### Hosted Supabase project (SQL Editor)

1. Open Supabase dashboard → **SQL Editor**.
2. Paste and run `supabase/migrations/202602130001_create_opportunities.sql`.
3. Verify table + policies:
   - `select count(*) from public.opportunities;`
   - `select policyname, roles, cmd from pg_policies where schemaname='public' and tablename='opportunities';`

#### Supabase CLI / local stack

```bash
# Start local Supabase stack (first time may take a minute)
supabase start

# Apply migrations in order
supabase db push
```

#### Runtime credentials and expected access

- **Landing page** should use the **anon key** and relies on policy `public read opportunities` (read-only SELECT).
- **Loader / backend jobs** should use the **service role key** (`SUPABASE_KEY`) and rely on policy `service role write opportunities` for upserts and updates.
- Never expose the service role key in frontend code or static assets.

## Workflow

1. **Sunday**: Run `hn_listener` + `match_github.py`
2. **Monday**: Review `*_matched.jsonl` files, pick top 5 opportunities
3. **Tuesday**: Write newsletter
4. **Wednesday**: Send via ConvertKit

## GitHub Token

Create a Personal Access Token at https://github.com/settings/tokens

- No special scopes needed (public repo search)
- Classic or fine-grained both work
- Rate limit: 5000 requests/hour


## Preventing Accidental Key Commits

A dedicated `Secret Scan` CI workflow runs [gitleaks](https://github.com/gitleaks/gitleaks-action) on pushes and pull requests. If a key-like value is committed, CI fails so the secret can be removed and rotated before merge.
