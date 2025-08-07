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
