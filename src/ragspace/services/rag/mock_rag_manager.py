"""
Mock RAG Manager for testing
"""

import asyncio
from typing import Dict, List, Optional, Any
from unittest.mock import Mock

class MockRAGManager:
    """Mock RAG Manager for testing purposes"""
    
    def __init__(self):
        self.mock_responses = {
            "default": "This is a mock RAG response for testing purposes.",
            "test": "This is a test response from the mock RAG system.",
            "hello": "Hello! This is a mock response to your greeting.",
            "help": "I'm a mock RAG system. I can help you with test queries.",
            "error": "Mock error response for testing error handling."
        }
    
    async def query_knowledge_base(self, query: str, docset_name: Optional[str] = None):
        """Mock query method that returns predefined responses as async generator"""
        # Simulate async processing
        await asyncio.sleep(0.1)
        
        # Return mock response based on query
        query_lower = query.lower().strip()
        
        if "error" in query_lower:
            yield "❌ Mock error: This is a test error response."
            return
        
        if "test" in query_lower:
            yield self.mock_responses["test"]
            return
        
        if "hello" in query_lower or "hi" in query_lower:
            yield self.mock_responses["hello"]
            return
        
        if "help" in query_lower:
            yield self.mock_responses["help"]
            return
        
        # Default response
        yield self.mock_responses["default"]
    
    async def process_document_embeddings(self, docset_name: Optional[str] = None) -> str:
        """Mock embedding processing"""
        await asyncio.sleep(0.1)
        return "✅ Mock embedding processing completed successfully."
    
    def get_embedding_status(self) -> str:
        """Mock embedding status"""
        return "Mock embedding status: 5 documents processed, 2 pending, 0 failed"
    
    def list_documents(self, docset_name: Optional[str] = None) -> str:
        """Mock document listing"""
        if docset_name:
            return f"Mock documents in {docset_name}:\n- Document 1\n- Document 2\n- Document 3"
        else:
            return "Mock documents across all docsets:\n- Docset1: 3 documents\n- Docset2: 2 documents"
    
    async def query_with_metadata(self, query: str, docsets: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock query method with metadata for testing purposes"""
        # Simulate async processing
        await asyncio.sleep(0.1)
        
        # Return mock response based on query
        query_lower = query.lower().strip()
        
        if "error" in query_lower:
            return {
                "status": "error",
                "query": query,
                "error": "Mock error for testing",
                "response": "❌ Mock error: This is a test error response.",
                "sources": [],
                "metadata": {}
            }
        
        # Prepare mock sources
        mock_sources = [
            {
                "document_name": "Mock Document 1",
                "docset_name": "test_docset",
                "source_url": "https://github.com/test/repo/blob/main/README.md#L1-L10",
                "content_preview": "This is a mock document for testing purposes...",
                "chunk_index": 0,
                "metadata": {
                    "source_type": "github",
                    "owner": "test",
                    "repo": "repo",
                    "path": "README.md",
                    "start_line": 1,
                    "end_line": 10
                }
            }
        ]
        
        if "test" in query_lower:
            response = self.mock_responses["test"]
        elif "hello" in query_lower or "hi" in query_lower:
            response = self.mock_responses["hello"]
        elif "help" in query_lower:
            response = self.mock_responses["help"]
        else:
            response = self.mock_responses["default"]
        
        return {
            "status": "success",
            "query": query,
            "response": response,
            "sources": mock_sources,
            "metadata": {
                "chunks_retrieved": 1,
                "retrieval_time": 0.1,
                "generation_time": 0.05,
                "total_time": 0.15,
                "context_length": len(response),
                "response_length": len(response)
            }
        }
