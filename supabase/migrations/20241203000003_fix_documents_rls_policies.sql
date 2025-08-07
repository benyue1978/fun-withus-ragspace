-- Migration: Fix documents table RLS policies for UPDATE operations
-- Migration: 20241203000003_fix_documents_rls_policies.sql

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow public update access to documents" ON documents;
DROP POLICY IF EXISTS "Allow public delete access to documents" ON documents;

-- Create policies for UPDATE and DELETE operations
CREATE POLICY "Allow public update access to documents" ON documents
  FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow public delete access to documents" ON documents
  FOR DELETE USING (true);
