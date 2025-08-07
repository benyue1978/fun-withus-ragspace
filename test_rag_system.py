#!/usr/bin/env python3
"""
Test script for RAG system components
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ragspace.services import RAGManager, RAGTextSplitter, EmbeddingWorker
from ragspace.storage import SupabaseDocsetManager

# Load environment variables
load_dotenv()


async def test_text_splitter():
    """Test text splitter functionality"""
    print("\n=== Testing Text Splitter ===")
    
    splitter = RAGTextSplitter()
    
    # Test text splitting
    sample_text = """
    This is a sample document with multiple paragraphs.
    
    It contains various types of content including code examples.
    
    def example_function():
        return "Hello, World!"
    
    And some more text content.
    """
    
    chunks = splitter.split_text(sample_text, "text")
    print(f"✅ Text splitter created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {len(chunk['content'])} characters")
    
    return chunks


async def test_embedding_worker():
    """Test embedding worker functionality"""
    print("\n=== Testing Embedding Worker ===")
    
    try:
        worker = EmbeddingWorker()
        print("✅ Embedding worker initialized")
        
        # Get embedding status
        status = worker.get_embedding_status_summary()
        print(f"✅ Embedding status: {status}")
        
        return worker
        
    except Exception as e:
        print(f"❌ Error initializing embedding worker: {e}")
        return None


async def test_rag_manager():
    """Test RAG manager functionality"""
    print("\n=== Testing RAG Manager ===")
    
    try:
        manager = RAGManager()
        print("✅ RAG manager initialized")
        
        # Get system status
        status = manager.get_system_status()
        print(f"✅ System status retrieved: {status.get('embedding_status', {})}")
        
        # Get available docsets
        docsets = manager.get_available_docsets()
        print(f"✅ Available docsets: {len(docsets)}")
        
        return manager
        
    except Exception as e:
        print(f"❌ Error initializing RAG manager: {e}")
        return None


async def test_rag_query():
    """Test RAG query functionality"""
    print("\n=== Testing RAG Query ===")
    
    try:
        manager = RAGManager()
        
        # Test query
        query = "What is the main functionality of this system?"
        
        print(f"🔄 Testing query: {query}")
        
        # Test with metadata
        result = await manager.query_with_metadata(query)
        
        if result["status"] == "success":
            print(f"✅ Query successful")
            print(f"  Response length: {len(result['response'])}")
            print(f"  Sources found: {len(result['sources'])}")
            print(f"  Retrieval time: {result['metadata'].get('retrieval_time', 0):.2f}s")
            print(f"  Generation time: {result['metadata'].get('generation_time', 0):.2f}s")
            print(f"  Response: {result['response']}")
        else:
            print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing RAG query: {e}")
        return None


async def test_storage_operations():
    """Test storage operations"""
    print("\n=== Testing Storage Operations ===")
    
    try:
        storage = SupabaseDocsetManager()
        
        # List docsets
        docsets_list = storage.list_docsets()
        print(f"✅ DocSets: {docsets_list}")
        
        # Get docsets dict
        docsets_dict = storage.get_docsets_dict()
        print(f"✅ DocSets dict: {len(docsets_dict)} docsets")
        
        return storage
        
    except Exception as e:
        print(f"❌ Error testing storage operations: {e}")
        return None


async def test_embedding_process():
    """Test embedding process"""
    print("\n=== Testing Embedding Process ===")
    
    try:
        manager = RAGManager()
        
        # Get embedding progress
        progress = manager.get_embedding_progress()
        print(f"✅ Embedding progress: {progress}")
        
        # Test processing (this will only process pending documents)
        print("🔄 Starting embedding process...")
        result = await manager.process_document_embeddings()
        print(f"✅ Embedding process result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing embedding process: {e}")
        return None


async def main():
    """Main test function"""
    print("🚀 Starting RAG System Tests")
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these variables in your .env file")
        return
    
    print("✅ Environment variables configured")
    
    # Run tests
    await test_text_splitter()
    await test_embedding_worker()
    await test_rag_manager()
    await test_storage_operations()
    await test_embedding_process()
    await test_rag_query()
    
    print("\n🎉 RAG System Tests Completed!")


if __name__ == "__main__":
    asyncio.run(main())
