"""
RAG Retriever - Vector similarity search and reranking
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from dotenv import load_dotenv
import time

from .text_splitter import RAGTextSplitter
from ...storage.supabase_manager import SupabaseDocsetManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGRetriever:
    """RAG retriever for vector similarity search and result reranking"""
    
    def __init__(self, model_name: str = "openai"):
        """Initialize RAG retriever"""
        self.model_name = model_name
        self.storage = SupabaseDocsetManager()
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        self.openai_client = openai.OpenAI(api_key=api_key)
        
        # Embedding model configuration
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimensions = 1536
        
        # Retrieval configuration
        self.default_top_k = 5
        self.rerank_top_k = 3
        
        logger.info(f"✅ RAG retriever initialized with model: {self.embedding_model}")
    
    async def retrieve_chunks(self, query: str, docsets: Optional[List[str]] = None, 
                            top_k: int = None, use_rerank: bool = True) -> List[Dict]:
        """
        Retrieve relevant chunks using vector similarity search
        
        Args:
            query: Search query
            docsets: Optional list of docset names to search in
            top_k: Number of results to return
            use_rerank: Whether to use GPT reranking
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            top_k = top_k or self.default_top_k
            
            # Generate query embedding
            query_embedding = await self._generate_query_embedding(query)
            
            # Perform vector similarity search
            candidates = await self._vector_search(query_embedding, docsets, top_k * 2)
            
            if not candidates:
                logger.warning(f"No chunks found for query: {query}")
                return []
            
            # Apply GPT reranking if enabled
            if use_rerank and len(candidates) > 1:
                final_results = await self._gpt_rerank(query, candidates, top_k)
            else:
                final_results = candidates[:top_k]
            
            logger.info(f"✅ Retrieved {len(final_results)} chunks for query: {query}")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Error retrieving chunks for query '{query}': {e}")
            return []
    
    async def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=[query]
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ Error generating query embedding: {e}")
            raise
    
    async def _vector_search(self, query_embedding: List[float], 
                           docsets: Optional[List[str]] = None, top_k: int = 10) -> List[Dict]:
        """Perform vector similarity search using database functions"""
        try:
            # Try to use the vector similarity search function first
            try:
                # Convert docsets to array format for the function
                docsets_array = None
                if docsets and docsets != ["all"]:
                    docsets_array = docsets
                
                # Call the vector similarity search function
                result = self.storage.supabase.rpc(
                    'search_chunks_similarity',
                    {
                        'query_embedding': query_embedding,
                        'search_docsets': docsets_array,
                        'result_limit': top_k
                    }
                ).execute()
                
                if result.data:
                    logger.info(f"✅ Vector similarity search successful: {len(result.data)} results")
                    return result.data
                    
            except Exception as vector_error:
                logger.warning(f"⚠️ Vector similarity search failed: {vector_error}")
            
            # Fallback to basic search function
            try:
                # Convert docsets to array format for the function
                docsets_array = None
                if docsets and docsets != ["all"]:
                    docsets_array = docsets
                
                # Call the basic search function
                result = self.storage.supabase.rpc(
                    'search_chunks_basic',
                    {
                        'search_docsets': docsets_array,
                        'result_limit': top_k
                    }
                ).execute()
                
                if result.data:
                    logger.warning(f"⚠️ Using basic search without vector similarity")
                    return result.data
                    
            except Exception as basic_error:
                logger.warning(f"⚠️ Basic search function failed: {basic_error}")
            
            # Final fallback: direct table query
            try:
                query_builder = self.storage.supabase.table("chunks").select("*")
                
                if docsets and docsets != ["all"]:
                    query_builder = query_builder.in_("docset_name", docsets)
                
                # Add a filter to ensure we only get chunks with embeddings
                query_builder = query_builder.not_.is_("embedding", "null")
                
                # Use a simple order by and limit
                result = query_builder.order("chunk_index").limit(top_k).execute()
                
                logger.warning(f"⚠️ Using direct table query as final fallback")
                return result.data
                
            except Exception as table_error:
                logger.error(f"❌ Error in direct table query: {table_error}")
                return []
            
        except Exception as e:
            logger.error(f"❌ Error in vector search: {e}")
            return []
    
    async def _gpt_rerank(self, query: str, candidates: List[Dict], top_k: int) -> List[Dict]:
        """
        Use GPT to rerank search results
        
        Args:
            query: Original search query
            candidates: List of candidate chunks
            top_k: Number of top results to return
            
        Returns:
            Reranked list of chunks
        """
        try:
            if len(candidates) <= top_k:
                return candidates
            
            # Format candidates for reranking
            formatted_candidates = self._format_candidates_for_rerank(candidates)
            
            # Create reranking prompt
            prompt = f"""
            Rank these text snippets by relevance to the question. Consider:
            1. Direct answer to the question
            2. Supporting context and details
            3. Code examples if the question is about code
            4. Documentation quality and completeness
            
            Question: {query}
            
            Snippets:
            {formatted_candidates}
            
            Return only a JSON array with the indices of the top {top_k} most relevant snippets, ordered by relevance (most relevant first).
            Example: [2, 0, 1] means snippet 2 is most relevant, then snippet 0, then snippet 1.
            """
            
            # Get GPT reranking
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100
            )
            
            # Parse ranking
            ranking_text = response.choices[0].message.content.strip()
            ranking = json.loads(ranking_text)
            
            # Apply ranking
            reranked_results = [candidates[i] for i in ranking[:top_k] if i < len(candidates)]
            
            logger.info(f"✅ GPT reranking completed for {len(reranked_results)} chunks")
            return reranked_results
            
        except Exception as e:
            logger.error(f"❌ Error in GPT reranking: {e}")
            # Fallback to original order
            return candidates[:top_k]
    
    def _format_candidates_for_rerank(self, candidates: List[Dict]) -> str:
        """Format candidates for GPT reranking"""
        formatted = []
        
        for i, candidate in enumerate(candidates):
            content = candidate.get('content', '')[:500]  # Limit content length
            source = candidate.get('document_name', 'Unknown')
            
            formatted.append(f"{i}: [{source}] {content}")
        
        return "\n\n".join(formatted)
    
    def get_retrieval_stats(self, docset_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get retrieval statistics
        
        Args:
            docset_name: Optional docset name to filter
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get total chunks count
            query = self.storage.supabase.table("chunks").select("id", count="exact")
            
            if docset_name:
                query = query.eq("docset_name", docset_name)
            
            result = query.execute()
            total_chunks = result.count if result.count is not None else 0
            
            # Get documents with embeddings
            doc_query = self.storage.supabase.table("documents").select("id", count="exact").eq("embedding_status", "done")
            
            if docset_name:
                # Get docset ID
                docset_result = self.storage.supabase.table("docsets").select("id").eq("name", docset_name).execute()
                if docset_result.data:
                    docset_id = docset_result.data[0]['id']
                    doc_query = doc_query.eq("docset_id", docset_id)
            
            doc_result = doc_query.execute()
            embedded_docs = doc_result.count if doc_result.count is not None else 0
            
            return {
                "total_chunks": total_chunks,
                "embedded_documents": embedded_docs,
                "docset_name": docset_name or "all"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting retrieval stats: {e}")
            return {}
    
    async def hybrid_retrieve(self, query: str, docsets: Optional[List[str]] = None, 
                            top_k: int = None, use_rerank: bool = True) -> Dict[str, Any]:
        """
        Hybrid retrieval combining vector search and GPT reranking
        
        Args:
            query: Search query
            docsets: Optional list of docset names
            top_k: Number of results to return
            use_rerank: Whether to use GPT reranking
            
        Returns:
            Hybrid retrieval result with metadata
        """
        try:
            start_time = time.time()
            
            # Perform retrieval
            chunks = await self.retrieve_chunks(query, docsets, top_k, use_rerank)
            
            # Calculate retrieval time
            retrieval_time = time.time() - start_time
            
            # Get statistics
            stats = self.get_retrieval_stats(docsets[0] if docsets and len(docsets) == 1 else None)
            
            return {
                "status": "success",
                "query": query,
                "chunks": chunks,
                "retrieval_time": retrieval_time,
                "chunks_count": len(chunks),
                "use_rerank": use_rerank,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error in hybrid retrieval: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "chunks": []
            }
    
    def search_similar_chunks(self, chunk_id: str, top_k: int = 5) -> List[Dict]:
        """
        Find similar chunks to a given chunk
        
        Args:
            chunk_id: ID of the reference chunk
            top_k: Number of similar chunks to return
            
        Returns:
            List of similar chunks
        """
        try:
            # Get the reference chunk
            chunk_result = self.storage.supabase.table("chunks").select("*").eq("id", chunk_id).execute()
            
            if not chunk_result.data:
                return []
            
            reference_chunk = chunk_result.data[0]
            reference_embedding = reference_chunk.get('embedding')
            
            if not reference_embedding:
                return []
            
            # Try to use the vector similarity search function
            try:
                similar_result = self.storage.supabase.rpc(
                    'search_chunks_similarity',
                    {
                        'query_embedding': reference_embedding,
                        'search_docsets': None,
                        'result_limit': top_k + 1  # +1 to account for the reference chunk
                    }
                ).execute()
                
                if similar_result.data:
                    # Filter out the reference chunk itself
                    filtered_results = [chunk for chunk in similar_result.data if chunk['id'] != chunk_id]
                    return filtered_results[:top_k]
                    
            except Exception as func_error:
                logger.warning(f"⚠️ Vector similarity function failed: {func_error}")
            
            # Fallback to direct query
            try:
                similar_result = self.storage.supabase.table("chunks").select("*").neq("id", chunk_id).order(
                    f"embedding <-> '{reference_embedding}'"
                ).limit(top_k).execute()
                
                return similar_result.data
                
            except Exception as query_error:
                logger.error(f"❌ Error in fallback similar chunks search: {query_error}")
                return []
            
        except Exception as e:
            logger.error(f"❌ Error finding similar chunks: {e}")
            return []
