BEGIN;

-- 1. Add scoring columns to opportunities
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS relevance_score SMALLINT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS content_potential SMALLINT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS one_line_hook TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS key_insight TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS scored_at TIMESTAMPTZ;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS model_used TEXT;

CREATE INDEX IF NOT EXISTS idx_opp_relevance ON opportunities(relevance_score DESC)
  WHERE relevance_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_opp_category ON opportunities(category)
  WHERE category IS NOT NULL;

-- 2. Create tweet_drafts table
CREATE TABLE IF NOT EXISTS tweet_drafts (
  id TEXT PRIMARY KEY,
  signal_id TEXT NOT NULL REFERENCES opportunities(id),
  source TEXT NOT NULL,
  category TEXT,
  hook TEXT,
  full_draft TEXT NOT NULL,
  word_count SMALLINT,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'draft',
  notes TEXT DEFAULT '',
  model_used TEXT,
  signal_title TEXT,
  signal_url TEXT,
  relevance_score SMALLINT,
  content_potential SMALLINT
);

CREATE INDEX IF NOT EXISTS idx_drafts_status ON tweet_drafts(status);
CREATE INDEX IF NOT EXISTS idx_drafts_date ON tweet_drafts(generated_at DESC);

ALTER TABLE tweet_drafts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_drafts" ON tweet_drafts FOR SELECT TO anon USING (true);
CREATE POLICY "service_full_drafts" ON tweet_drafts FOR ALL TO service_role USING (true) WITH CHECK (true);

-- 3. Create google_trends table
CREATE TABLE IF NOT EXISTS google_trends (
  id TEXT PRIMARY KEY,
  keyword TEXT NOT NULL UNIQUE,
  source_signals JSONB DEFAULT '[]'::jsonb,
  interest_over_time JSONB DEFAULT '[]'::jsonb,
  current_interest SMALLINT,
  year_ago_interest SMALLINT,
  yoy_growth_pct REAL,
  is_rising BOOLEAN DEFAULT false,
  related_queries JSONB DEFAULT '[]'::jsonb,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trends_rising ON google_trends(is_rising) WHERE is_rising = true;
CREATE INDEX IF NOT EXISTS idx_trends_growth ON google_trends(yoy_growth_pct DESC NULLS LAST);

ALTER TABLE google_trends ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_trends" ON google_trends FOR SELECT TO anon USING (true);
CREATE POLICY "service_full_trends" ON google_trends FOR ALL TO service_role USING (true) WITH CHECK (true);

COMMIT;
