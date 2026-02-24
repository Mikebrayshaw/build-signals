BEGIN;

-- Validated opportunities: cross-referenced signals with evidence from multiple sources
CREATE TABLE IF NOT EXISTS validated_opportunities (
  id TEXT PRIMARY KEY,
  signal_id TEXT NOT NULL REFERENCES opportunities(id),
  signal_title TEXT NOT NULL,
  signal_url TEXT,
  signal_source TEXT NOT NULL,
  signal_score INTEGER DEFAULT 0,
  signal_comments INTEGER DEFAULT 0,
  relevance_score SMALLINT,
  content_potential SMALLINT,
  opportunity_type TEXT NOT NULL,
  queries JSONB DEFAULT '{}'::jsonb,
  evidence_google_trends JSONB DEFAULT '{}'::jsonb,
  evidence_producthunt JSONB DEFAULT '{}'::jsonb,
  evidence_github JSONB DEFAULT '{}'::jsonb,
  sources_confirming SMALLINT DEFAULT 0,
  confidence TEXT NOT NULL DEFAULT 'low',
  narrative TEXT,
  one_line_hook TEXT,
  key_insight TEXT,
  validated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  model_used TEXT
);

CREATE INDEX IF NOT EXISTS idx_validated_confidence ON validated_opportunities(confidence);
CREATE INDEX IF NOT EXISTS idx_validated_type ON validated_opportunities(opportunity_type);
CREATE INDEX IF NOT EXISTS idx_validated_sources ON validated_opportunities(sources_confirming DESC);
CREATE INDEX IF NOT EXISTS idx_validated_date ON validated_opportunities(validated_at DESC);

ALTER TABLE validated_opportunities ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_validated" ON validated_opportunities FOR SELECT TO anon USING (true);
CREATE POLICY "service_full_validated" ON validated_opportunities FOR ALL TO service_role USING (true) WITH CHECK (true);

COMMIT;
