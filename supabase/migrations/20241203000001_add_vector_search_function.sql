-- Migration: Add vector search function for RAG
-- Migration: 20241203000001_add_vector_search_function.sql

-- Create a function for vector similarity search
CREATE OR REPLACE FUNCTION search_chunks_similarity(
    query_embedding vector(1536),
    search_docsets text[] DEFAULT NULL,
    result_limit integer DEFAULT 10
)
RETURNS TABLE(
    id uuid,
    docset_name text,
    document_name text,
    document_id uuid,
    chunk_index integer,
    content text,
    embedding vector(1536),
    metadata jsonb,
    created_at timestamp,
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.docset_name,
        c.document_name,
        c.document_id,
        c.chunk_index,
        c.content,
        c.embedding,
        c.metadata,
        c.created_at,
        c.embedding <-> query_embedding as similarity
    FROM chunks c
    WHERE c.embedding IS NOT NULL
        AND (search_docsets IS NULL OR c.docset_name = ANY(search_docsets))
    ORDER BY c.embedding <-> query_embedding
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION search_chunks_similarity(vector(1536), text[], integer) TO anon;
GRANT EXECUTE ON FUNCTION search_chunks_similarity(vector(1536), text[], integer) TO authenticated;

-- Create a simpler function for basic search without vector similarity
CREATE OR REPLACE FUNCTION search_chunks_basic(
    search_docsets text[] DEFAULT NULL,
    result_limit integer DEFAULT 10
)
RETURNS TABLE(
    id uuid,
    docset_name text,
    document_name text,
    document_id uuid,
    chunk_index integer,
    content text,
    embedding vector(1536),
    metadata jsonb,
    created_at timestamp
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.docset_name,
        c.document_name,
        c.document_id,
        c.chunk_index,
        c.content,
        c.embedding,
        c.metadata,
        c.created_at
    FROM chunks c
    WHERE c.embedding IS NOT NULL
        AND (search_docsets IS NULL OR c.docset_name = ANY(search_docsets))
    ORDER BY c.created_at DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION search_chunks_basic(text[], integer) TO anon;
GRANT EXECUTE ON FUNCTION search_chunks_basic(text[], integer) TO authenticated;
