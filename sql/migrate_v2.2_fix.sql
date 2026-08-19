-- JobScout v2.2 Migration — Run this in Supabase SQL Editor
-- Adds the missing RLS policy for digest_history table
-- and the index on digest_history(created_at)

-- Fix: Enable RLS on digest_history (was missing)
ALTER TABLE IF EXISTS digest_history ENABLE ROW LEVEL SECURITY;

-- Fix: Add service access policy for digest_history (was missing, causing empty results)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'digest_history' 
        AND policyname = 'service_full_access_digest_history'
    ) THEN
        CREATE POLICY "service_full_access_digest_history" ON digest_history FOR ALL USING (true);
    END IF;
END $$;

-- Performance: Add index on digest_history(created_at) for faster history queries
CREATE INDEX IF NOT EXISTS idx_digest_history_created_at ON digest_history(created_at);
