-- Migration: Create chunks table for RAG vector storage
-- Migration: 20241203000000_create_chunks_table.sql

-- Enable pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create chunks table for storing document chunks and embeddings
CREATE TABLE IF NOT EXISTS chunks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  docset_name text NOT NULL,
  document_name text NOT NULL,
  document_id uuid REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index integer NOT NULL,
  content text NOT NULL,
  embedding vector(1536),
  metadata jsonb DEFAULT '{}',
  created_at timestamp DEFAULT now(),
  
  -- Ensure unique chunks per document
  UNIQUE(document_id, chunk_index)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_chunks_docset_name ON chunks(docset_name);
CREATE INDEX IF NOT EXISTS idx_chunks_document_name ON chunks(document_name);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_metadata ON chunks USING GIN (metadata);

-- Create vector index for similarity search
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Enable Row Level Security
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (temporary, will be updated for multi-user)
CREATE POLICY "Allow public read access to chunks" ON chunks
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to chunks" ON chunks
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update access to chunks" ON chunks
  FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow public delete access to chunks" ON chunks
  FOR DELETE USING (true);

-- Add embedding status columns to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding_status text 
DEFAULT 'pending' CHECK (embedding_status IN ('pending', 'processing', 'done', 'error'));

ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding_updated_at timestamp;

-- Create index on embedding status for efficient querying
CREATE INDEX IF NOT EXISTS idx_documents_embedding_status ON documents(embedding_status);
