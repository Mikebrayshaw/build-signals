-- Migration: Add Product Hunt support to opportunities table
-- Run this in Supabase SQL Editor

-- Add source_id column for unified deduplication across sources
-- Format: "source:original_id" (e.g., "producthunt:12345", "hn_ask:67890")
ALTER TABLE opportunities
ADD COLUMN IF NOT EXISTS source_id TEXT UNIQUE;

-- Backfill source_id for existing HN records
UPDATE opportunities
SET source_id = source || ':' || hn_id::text
WHERE source_id IS NULL AND hn_id IS NOT NULL;

-- Add Product Hunt specific columns (nullable for HN records)
ALTER TABLE opportunities
ADD COLUMN IF NOT EXISTS tagline TEXT;

ALTER TABLE opportunities
ADD COLUMN IF NOT EXISTS topics JSONB DEFAULT '[]'::jsonb;

-- Create index on source for filtering
CREATE INDEX IF NOT EXISTS idx_opportunities_source ON opportunities(source);

-- Create index on source_id for upserts
CREATE INDEX IF NOT EXISTS idx_opportunities_source_id ON opportunities(source_id);
