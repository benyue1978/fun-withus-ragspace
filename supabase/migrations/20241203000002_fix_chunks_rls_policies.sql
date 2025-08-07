-- Migration: Fix chunks table RLS policies for UPSERT operations
-- Migration: 20241203000002_fix_chunks_rls_policies.sql

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow public update access to chunks" ON chunks;
DROP POLICY IF EXISTS "Allow public delete access to chunks" ON chunks;

-- Create policies for UPSERT operations
CREATE POLICY "Allow public update access to chunks" ON chunks
  FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow public delete access to chunks" ON chunks
  FOR DELETE USING (true);
