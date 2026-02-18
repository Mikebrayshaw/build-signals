-- 002: Add subscribers table and RLS policies
-- Run this in Supabase SQL Editor

-- ── Subscribers table ──
CREATE TABLE IF NOT EXISTS subscribers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  stripe_customer_id TEXT,
  stripe_session_id TEXT,
  paid_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ── RLS on subscribers ──
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;

-- Users can only read their own subscriber record
CREATE POLICY "Users can read own subscriber record"
  ON subscribers
  FOR SELECT
  USING (email = (auth.jwt() ->> 'email'));

-- ── RLS on opportunities ──
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;

-- Anon users can SELECT (keeps landing page preview working)
CREATE POLICY "Anon users can read opportunities"
  ON opportunities
  FOR SELECT
  TO anon
  USING (true);

-- Authenticated users with a subscriber record can SELECT
CREATE POLICY "Subscribers can read opportunities"
  ON opportunities
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM subscribers
      WHERE subscribers.email = (auth.jwt() ->> 'email')
    )
  );

-- Note: Pipeline scripts use the service role key, which bypasses RLS entirely.
-- No additional policies needed for INSERT/UPDATE by the pipeline.
