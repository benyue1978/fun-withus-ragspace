"""
RAG Manager for coordinating RAG system components
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, AsyncGenerator
from datetime import datetime

from .embedding_worker import EmbeddingWorker
from .rag_retriever import RAGRetriever
from .rag_response_generator import RAGResponseGenerator
from ..storage.supabase_manager import SupabaseDocsetManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGManager:
    """Manager for coordinating RAG system components"""
    
    def __init__(self, model_name: str = "openai"):
        """Initialize RAG manager"""
        self.model_name = model_name
        self.storage = SupabaseDocsetManager()
        self.embedding_worker = EmbeddingWorker(model_name)
        self.retriever = RAGRetriever(model_name)
        self.response_generator = RAGResponseGenerator(model_name)
        
        logger.info(f"✅ RAG manager initialized with model: {model_name}")
    
    async def process_document_embeddings(self, docset_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process document embeddings for a docset or all documents
        
        Args:
            docset_name: Optional docset name to process
            
        Returns:
            Processing result
        """
        try:
            logger.info(f"🔄 Starting document embedding process for docset: {docset_name or 'all'}")
            
            result = await self.embedding_worker.batch_process(docset_name)
            
            logger.info(f"✅ Document embedding process completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in document embedding process: {e}")
            return {"status": "error", "message": str(e)}
    
    async def query_knowledge_base(self, query: str, docsets: Optional[List[str]] = None,
                                  stream: bool = True) -> AsyncGenerator[str, None]:
        """
        Query knowledge base using RAG pipeline
        
        Args:
            query: User query
            docsets: Optional list of docset names
            stream: Whether to stream the response
            
        Yields:
            Response chunks
        """
        try:
            logger.info(f"🔄 Processing query: {query}")
            
            async for chunk in self.response_generator.generate_response(query, docsets, stream=stream):
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ Error in knowledge base query: {e}")
            yield f"❌ Error processing query: {str(e)}"
    
    async def query_with_metadata(self, query: str, docsets: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Query knowledge base with detailed metadata
        
        Args:
            query: User query
            docsets: Optional list of docset names
            
        Returns:
            Query result with metadata
        """
        try:
            logger.info(f"🔄 Processing query with metadata: {query}")
            
            result = await self.response_generator.generate_response_with_metadata(query, docsets)
            
            logger.info(f"✅ Query with metadata completed: {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in query with metadata: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "response": "",
                "sources": [],
                "metadata": {}
            }
    
    def get_system_status(self, docset_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get RAG system status
        
        Args:
            docset_name: Optional docset name to filter
            
        Returns:
            System status information
        """
        try:
            # Get embedding status
            embedding_status = self.embedding_worker.get_embedding_status_summary(docset_name)
            
            # Get retrieval stats
            retrieval_stats = self.retriever.get_retrieval_stats(docset_name)
            
            # Get docset information
            docsets_info = self.storage.get_docsets_dict()
            
            status = {
                "embedding_status": embedding_status,
                "retrieval_stats": retrieval_stats,
                "docsets": docsets_info,
                "model_info": {
                    "embedding_model": self.embedding_worker.embedding_model,
                    "llm_model": self.response_generator.llm_model,
                    "model_name": self.model_name
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ System status retrieved for docset: {docset_name or 'all'}")
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting system status: {e}")
            return {"error": str(e)}
    
    async def trigger_embedding_for_docset(self, docset_name: str) -> Dict[str, Any]:
        """
        Trigger embedding process for a specific docset
        
        Args:
            docset_name: Name of the docset
            
        Returns:
            Trigger result
        """
        try:
            logger.info(f"🔄 Triggering embedding for docset: {docset_name}")
            
            result = self.embedding_worker.trigger_embedding_for_docset(docset_name)
            
            if result["status"] == "success":
                # Start processing
                await self.process_document_embeddings(docset_name)
            
            logger.info(f"✅ Embedding trigger completed for docset: {docset_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error triggering embedding for docset '{docset_name}': {e}")
            return {"status": "error", "message": str(e)}
    
    async def test_rag_pipeline(self, query: str, docsets: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Test RAG pipeline components
        
        Args:
            query: Test query
            docsets: Optional docset names
            
        Returns:
            Test results
        """
        try:
            logger.info(f"🔄 Testing RAG pipeline with query: {query}")
            
            result = await self.response_generator.test_rag_pipeline(query, docsets)
            
            logger.info(f"✅ RAG pipeline test completed: {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error testing RAG pipeline: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_available_docsets(self) -> List[Dict[str, Any]]:
        """
        Get available docsets with status information
        
        Returns:
            List of docsets with status
        """
        try:
            docsets = self.storage.get_docsets_dict()
            
            # Add embedding status for each docset
            for docset_name, docset_info in docsets.items():
                embedding_status = self.embedding_worker.get_embedding_status_summary(docset_name)
                retrieval_stats = self.retriever.get_retrieval_stats(docset_name)
                
                docset_info["embedding_status"] = embedding_status
                docset_info["retrieval_stats"] = retrieval_stats
            
            return list(docsets.values())
            
        except Exception as e:
            logger.error(f"❌ Error getting available docsets: {e}")
            return []
    
    async def search_similar_content(self, chunk_id: str, top_k: int = 5) -> List[Dict]:
        """
        Find similar content to a given chunk
        
        Args:
            chunk_id: ID of the reference chunk
            top_k: Number of similar chunks to return
            
        Returns:
            List of similar chunks
        """
        try:
            logger.info(f"🔄 Searching similar content for chunk: {chunk_id}")
            
            similar_chunks = self.retriever.search_similar_chunks(chunk_id, top_k)
            
            logger.info(f"✅ Found {len(similar_chunks)} similar chunks")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"❌ Error searching similar content: {e}")
            return []
    
    def get_embedding_progress(self, docset_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get embedding processing progress
        
        Args:
            docset_name: Optional docset name to filter
            
        Returns:
            Progress information
        """
        try:
            status_summary = self.embedding_worker.get_embedding_status_summary(docset_name)
            
            total_docs = sum(status_summary.values())
            completed_docs = status_summary.get("done", 0)
            pending_docs = status_summary.get("pending", 0)
            processing_docs = status_summary.get("processing", 0)
            error_docs = status_summary.get("error", 0)
            
            progress = {
                "total_documents": total_docs,
                "completed": completed_docs,
                "pending": pending_docs,
                "processing": processing_docs,
                "error": error_docs,
                "completion_percentage": (completed_docs / total_docs * 100) if total_docs > 0 else 0,
                "status_summary": status_summary
            }
            
            return progress
            
        except Exception as e:
            logger.error(f"❌ Error getting embedding progress: {e}")
            return {"error": str(e)}
