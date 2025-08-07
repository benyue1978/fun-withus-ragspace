#!/usr/bin/env python3
"""
Basic RAG functionality test with mock
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from unittest.mock import patch, Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ragspace.services.rag.mock_rag_manager import MockRAGManager

# Load environment variables
load_dotenv()

async def test_mock_rag_manager():
    """Test mock RAG manager functionality"""
    print("🧪 Testing Mock RAG Manager...")
    
    # Initialize mock RAG manager
    mock_rag = MockRAGManager()
    
    # Test basic query
    result = await mock_rag.query_knowledge_base("test query")
    print(f"✅ Basic query result: {result}")
    assert "This is a test response from the mock RAG system" in result
    
    # Test hello query
    result = await mock_rag.query_knowledge_base("hello")
    print(f"✅ Hello query result: {result}")
    assert "Hello! This is a mock response to your greeting" in result
    
    # Test error query
    result = await mock_rag.query_knowledge_base("error test")
    print(f"✅ Error query result: {result}")
    assert "❌ Mock error" in result
    
    # Test embedding processing
    result = await mock_rag.process_document_embeddings()
    print(f"✅ Embedding processing result: {result}")
    assert "✅ Mock embedding processing completed successfully" in result
    
    # Test embedding status
    result = mock_rag.get_embedding_status()
    print(f"✅ Embedding status: {result}")
    assert "Mock embedding status" in result
    
    # Test document listing
    result = mock_rag.list_documents()
    print(f"✅ Document listing: {result}")
    assert "Mock documents across all docsets" in result
    
    return True

async def main():
    """Main test function"""
    print("🚀 Starting RAG Basic Tests with Mock...")
    
    # Test mock RAG manager
    success = await test_mock_rag_manager()
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
