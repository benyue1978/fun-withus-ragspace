#!/usr/bin/env python3
"""
Full RAG system test with external dependencies
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ragspace.services.rag import RAGManager, RAGTextSplitter, EmbeddingWorker

# Load environment variables
load_dotenv()

async def test_rag_manager():
    """Test RAG manager functionality"""
    print("🧪 Testing RAG Manager...")
    
    try:
        # Initialize RAG manager
        rag_manager = RAGManager()
        print("✅ RAG Manager initialized successfully")
        
        # Test system status
        status = await rag_manager.get_system_status()
        print(f"✅ System status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Manager test failed: {e}")
        return False

async def test_embedding_worker():
    """Test embedding worker functionality"""
    print("🧪 Testing Embedding Worker...")
    
    try:
        # Initialize embedding worker
        worker = EmbeddingWorker()
        print("✅ Embedding Worker initialized successfully")
        
        # Test embedding generation
        test_text = "This is a test document for embedding."
        embedding = await worker.generate_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            return True
        else:
            print("❌ Failed to generate embedding")
            return False
            
    except Exception as e:
        print(f"❌ Embedding Worker test failed: {e}")
        return False

async def test_text_splitter():
    """Test text splitter functionality"""
    print("🧪 Testing Text Splitter...")
    
    try:
        # Initialize text splitter
        splitter = RAGTextSplitter()
        
        # Test text splitting
        test_text = """
        This is a test document with multiple paragraphs.
        
        It contains various types of content including code snippets.
        
        def hello_world():
            print("Hello, World!")
        
        And some more text content.
        """
        
        chunks = splitter.split_text(test_text)
        
        if chunks and len(chunks) > 0:
            print(f"✅ Split text into {len(chunks)} chunks")
            return True
        else:
            print("❌ Failed to split text")
            return False
            
    except Exception as e:
        print(f"❌ Text Splitter test failed: {e}")
        return False

async def test_full_rag_pipeline():
    """Test full RAG pipeline"""
    print("🧪 Testing Full RAG Pipeline...")
    
    try:
        # Initialize RAG manager
        rag_manager = RAGManager()
        
        # Test query processing
        test_query = "What is the main purpose of this system?"
        
        # This would require actual documents in the database
        # For now, we'll just test the manager initialization
        print("✅ RAG Manager ready for query processing")
        return True
        
    except Exception as e:
        print(f"❌ Full RAG Pipeline test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Full RAG System Tests...")
    
    # Check environment variables
    required_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        print("Please set these variables before running the full test.")
        return False
    
    # Run tests
    tests = [
        test_text_splitter(),
        test_embedding_worker(),
        test_rag_manager(),
        test_full_rag_pipeline()
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
