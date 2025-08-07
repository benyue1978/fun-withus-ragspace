#!/usr/bin/env python3
"""
Vector search functionality test
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ragspace.services.rag import RAGRetriever, RAGManager

# Load environment variables
load_dotenv()

async def test_vector_search():
    """Test vector search functionality"""
    print("🧪 Testing Vector Search...")
    
    try:
        # Initialize RAG retriever
        retriever = RAGRetriever()
        print("✅ RAG Retriever initialized successfully")
        
        # Test query
        test_query = "What is the main functionality?"
        
        # Test vector retrieval
        result = await retriever.hybrid_retrieve(test_query)
        
        if result["status"] == "success":
            print(f"✅ Vector search successful")
            print(f"  Chunks found: {len(result['chunks'])}")
            print(f"  Retrieval time: {result.get('retrieval_time', 0):.2f}s")
            return True
        else:
            print(f"❌ Vector search failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        return False

async def test_rag_manager():
    """Test RAG manager functionality"""
    print("🧪 Testing RAG Manager...")
    
    try:
        # Initialize RAG manager
        manager = RAGManager()
        print("✅ RAG Manager initialized successfully")
        
        # Test system status
        status = await manager.get_system_status()
        print(f"✅ System status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Manager test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Vector Search Tests...")
    
    # Check environment variables
    required_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        print("Please set these variables before running the test.")
        return False
    
    # Run tests
    tests = [
        test_rag_manager(),
        test_vector_search()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # Count successful tests
    successful_tests = sum(1 for result in results if result is True)
    total_tests = len(tests)
    
    print(f"\n📊 Test Results: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    asyncio.run(main())
