-- Migration 004: Drop legacy columns
-- These columns are no longer used after migration 003 aligned the schema.
-- hn_id was replaced by source_id + composite text PK
-- keywords was never populated by the loader (only existed in JSONL output)

ALTER TABLE opportunities DROP COLUMN IF EXISTS hn_id;
ALTER TABLE opportunities DROP COLUMN IF EXISTS keywords;
