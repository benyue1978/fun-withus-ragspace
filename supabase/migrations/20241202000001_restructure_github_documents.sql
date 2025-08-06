-- Migration: Restructure GitHub documents to use parent-child relationship
-- This replaces the embedded children JSON with a relational parent_id foreign key

-- Remove the children column (if it exists)
ALTER TABLE documents DROP COLUMN IF EXISTS children;

-- Add parent_id column for parent-child relationship
ALTER TABLE documents ADD COLUMN IF NOT EXISTS parent_id uuid REFERENCES documents(id) ON DELETE CASCADE;

-- Create index on parent_id for better performance
CREATE INDEX IF NOT EXISTS idx_documents_parent_id ON documents(parent_id);

-- Update the type check constraint to include all content types
ALTER TABLE documents DROP CONSTRAINT IF EXISTS documents_type_check;
ALTER TABLE documents ADD CONSTRAINT documents_type_check 
  CHECK (type IN ('file', 'url', 'github', 'website', 'github_file', 'github_readme', 'github_repo', 'repository', 'document', 'code', 'config', 'readme')); 