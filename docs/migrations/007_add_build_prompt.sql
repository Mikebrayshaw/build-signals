-- Migration 007: Add build_prompt column to validated_opportunities
-- Run in Supabase SQL Editor

ALTER TABLE validated_opportunities ADD COLUMN IF NOT EXISTS build_prompt TEXT;

COMMENT ON COLUMN validated_opportunities.build_prompt IS 'Structured Claude Code starter prompt for building the opportunity';
