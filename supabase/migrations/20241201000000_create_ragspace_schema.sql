-- Create RAGSpace database schema
-- Migration: 20241201000000_create_ragspace_schema.sql

-- Enable UUIDable extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 文档集合表
CREATE TABLE IF NOT EXISTS docsets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  description text,
  created_at timestamp DEFAULT now()
);

-- 文档表
CREATE TABLE IF NOT EXISTS documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  docset_id uuid REFERENCES docsets(id) ON DELETE CASCADE,
  name text,
  type text CHECK (type IN ('file', 'url', 'github', 'website')),
  url text,
  content text,
  added_date timestamp DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_docset_id ON documents(docset_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(type);
CREATE INDEX IF NOT EXISTS idx_documents_added_date ON documents(added_date);

-- Enable Row Level Security (RLS) - for future multi-user support
ALTER TABLE docsets ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (temporary, will be updated for multi-user)
CREATE POLICY "Allow public read access to docsets" ON docsets
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to docsets" ON docsets
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to documents" ON documents
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to documents" ON documents
  FOR INSERT WITH CHECK (true); 