-- Migration: Update documents type constraint to include all ContentType enum values
-- This adds support for all content types returned by crawlers

-- Update the type check constraint to include all content types
ALTER TABLE documents DROP CONSTRAINT IF EXISTS documents_type_check;
ALTER TABLE documents ADD CONSTRAINT documents_type_check 
  CHECK (type IN (
    'file', 'url', 'github', 'website', 
    'github_file', 'github_readme', 'github_repo', 
    'repository', 'document', 'code', 'config', 'readme',
    'documentation', 'configuration', 'data', 'image', 'binary', 'unknown'
  ));
