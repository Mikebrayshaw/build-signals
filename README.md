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
python -m scripts.github_matcher --input runs/latest
```

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
python -m scripts.github_matcher --input runs/20250130_120000

# Use the latest run
python -m scripts.github_matcher --input $(cat runs/latest)

# Only high-scoring posts (50+ upvotes)
python -m scripts.github_matcher --input runs/latest --min-score 50

# More repos per post
python -m scripts.github_matcher --input runs/latest --repos-per-post 10
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


## Landing Page Runtime Config (GitHub Pages)

The landing page reads Supabase settings from `landing/config.js` via `window.BUILD_SIGNALS_CONFIG`.
The committed `landing/config.js` only contains placeholders for local/dev safety.

In GitHub, set these secrets on the repository or in the `github-pages` environment:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

During `.github/workflows/deploy-pages.yml`, a deploy-time step rewrites `landing/config.js` from secrets before uploading the Pages artifact.
This keeps real values out of versioned HTML/source while still shipping runtime config to Pages.

## Workflow

1. **Sunday**: Run `hn_listener` + `github_matcher`
2. **Monday**: Review `*_matched.jsonl` files, pick top 5 opportunities
3. **Tuesday**: Write newsletter
4. **Wednesday**: Send via ConvertKit

## GitHub Token

Create a Personal Access Token at https://github.com/settings/tokens

- No special scopes needed (public repo search)
- Classic or fine-grained both work
- Rate limit: 5000 requests/hour
