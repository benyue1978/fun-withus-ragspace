-- Add GitHub children support to documents table
-- Migration: 20241202000000_add_github_children.sql

-- Add children field to documents table for GitHub repo structure
ALTER TABLE documents ADD COLUMN IF NOT EXISTS children jsonb DEFAULT '[]';

-- Add index for children field for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_children ON documents USING GIN (children);

-- Add metadata field for additional GitHub information
ALTER TABLE documents ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}';

-- Add index for metadata field
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING GIN (metadata);

-- Update the type check to include new GitHub-related types
ALTER TABLE documents DROP CONSTRAINT IF EXISTS documents_type_check;
ALTER TABLE documents ADD CONSTRAINT documents_type_check 
  CHECK (type IN ('file', 'url', 'github', 'website', 'github_file', 'github_readme'));

-- Add comment to explain the children field structure
COMMENT ON COLUMN documents.children IS 'JSON array of child documents for GitHub repositories. Structure: [{"type": "file", "name": "README.md", "url": "...", "content": "..."}]';

-- Add comment to explain the metadata field
COMMENT ON COLUMN documents.metadata IS 'Additional metadata for documents. For GitHub: {"repo": "owner/repo", "branch": "main", "path": "src/", "size": 1024}'; 