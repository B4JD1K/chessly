-- =====================================================
-- Migration 002: Add puzzle source column
-- Run this script to add support for multiple puzzle sources
-- =====================================================

-- Add source column to track where puzzles come from (lichess, chess.com, etc.)
ALTER TABLE puzzles ADD COLUMN IF NOT EXISTS source VARCHAR(50);

-- Remove unique constraint from daily_date if it exists
-- This allows multiple puzzles per day (one from each source)
DO $$
BEGIN
    -- Check and drop unique constraint if it exists
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'puzzles_daily_date_key'
        AND conrelid = 'puzzles'::regclass
    ) THEN
        ALTER TABLE puzzles DROP CONSTRAINT puzzles_daily_date_key;
        RAISE NOTICE 'Dropped unique constraint puzzles_daily_date_key';
    END IF;

    -- Check for unique index and drop it if exists
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'puzzles_daily_date_key'
        AND tablename = 'puzzles'
    ) THEN
        DROP INDEX puzzles_daily_date_key;
        RAISE NOTICE 'Dropped unique index puzzles_daily_date_key';
    END IF;
END $$;

-- Ensure regular index exists on daily_date (for faster queries)
CREATE INDEX IF NOT EXISTS ix_puzzles_daily_date ON puzzles(daily_date);

-- Add compound index for source + daily_date queries
CREATE INDEX IF NOT EXISTS ix_puzzles_source_daily_date ON puzzles(source, daily_date);

-- Optional: Update existing puzzles without source to 'manual' or 'unknown'
-- UPDATE puzzles SET source = 'manual' WHERE source IS NULL;

-- Done!
-- Now you can have multiple puzzles per day from different sources:
-- - lichess
-- - chess.com
-- - manual (your own puzzles)
