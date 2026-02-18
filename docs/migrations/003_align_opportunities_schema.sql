-- Migration 003: Align opportunities table with unified loader schema
-- Combines migrations 001 (never run) + new column renames + PK change
-- Run this in Supabase SQL Editor
-- ⚠️  This will restructure the table. Only 3 rows exist, safe to migrate.

BEGIN;

-- 1. Add missing columns from migration 001 (source_id, tagline, topics)
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS source_id TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS tagline TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS topics JSONB DEFAULT '[]'::jsonb;

-- 2. Rename columns to match unified schema
ALTER TABLE opportunities RENAME COLUMN text TO description;
ALTER TABLE opportunities RENAME COLUMN github_repos TO github_data;

-- 3. Add new columns
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS github_url TEXT;

-- 4. Backfill source_id for existing rows
UPDATE opportunities
SET source_id = source || ':' || hn_id::text
WHERE source_id IS NULL AND hn_id IS NOT NULL;

-- 5. Convert id from serial integer to text (composite key)
--    Drop the old PK constraint, change column type, set new values
ALTER TABLE opportunities DROP CONSTRAINT IF EXISTS opportunities_pkey;
ALTER TABLE opportunities ALTER COLUMN id DROP DEFAULT;
-- Drop the sequence if it exists
DROP SEQUENCE IF EXISTS opportunities_id_seq;
ALTER TABLE opportunities ALTER COLUMN id TYPE TEXT USING (source || ':' || hn_id::text);
ALTER TABLE opportunities ADD PRIMARY KEY (id);

-- 6. Make source_id unique and indexed
ALTER TABLE opportunities ADD CONSTRAINT opportunities_source_id_unique UNIQUE (source_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_source ON opportunities(source);

-- 7. hn_id is no longer needed as a separate column, but keep it for reference
ALTER TABLE opportunities ALTER COLUMN hn_id DROP NOT NULL;

COMMIT;
