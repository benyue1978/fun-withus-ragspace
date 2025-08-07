#!/usr/bin/env python3
"""
Test vector search functionality
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ragspace.services import RAGRetriever, RAGManager
from ragspace.storage import SupabaseDocsetManager

# Load environment variables
load_dotenv()


async def test_vector_search():
    """Test vector search functionality"""
    print("\n=== Testing Vector Search ===")
    
    try:
        # Initialize retriever
        retriever = RAGRetriever()
        print("✅ RAGRetriever initialized")
        
        # Test basic retrieval without vector similarity
        print("\n🔄 Testing basic retrieval...")
        result = await retriever.hybrid_retrieve("test query", use_rerank=False)
        
        print(f"✅ Basic retrieval result: {result}")
        
        if result["status"] == "success":
            print(f"  - Retrieved {len(result['chunks'])} chunks")
            print(f"  - Retrieval time: {result.get('retrieval_time', 0):.3f}s")
        else:
            print(f"  - Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in vector search test: {e}")
        return None


async def test_rag_manager():
    """Test RAG manager functionality"""
    print("\n=== Testing RAG Manager ===")
    
    try:
        # Initialize RAG manager
        manager = RAGManager()
        print("✅ RAGManager initialized")
        
        # Test system status
        print("\n🔄 Testing system status...")
        status = manager.get_system_status()
        print(f"✅ System status: {status}")
        
        # Test available docsets
        print("\n🔄 Testing available docsets...")
        docsets = manager.get_available_docsets()
        print(f"✅ Available docsets: {docsets}")
        
        # Test embedding progress
        print("\n🔄 Testing embedding progress...")
        progress = manager.get_embedding_progress()
        print(f"✅ Embedding progress: {progress}")
        
        return {
            "status": status,
            "docsets": docsets,
            "progress": progress
        }
        
    except Exception as e:
        print(f"❌ Error in RAG manager test: {e}")
        return None


async def test_storage_operations():
    """Test storage operations"""
    print("\n=== Testing Storage Operations ===")
    
    try:
        # Initialize storage
        storage = SupabaseDocsetManager()
        print("✅ SupabaseDocsetManager initialized")
        
        # Test listing docsets
        print("\n🔄 Testing docset listing...")
        docsets = storage.get_docsets_dict()
        print(f"✅ Available docsets: {docsets}")
        
        # Test listing documents
        if docsets:
            first_docset = list(docsets.keys())[0]
            print(f"\n🔄 Testing document listing for docset: {first_docset}")
            documents = storage.list_documents_in_docset(first_docset)
            print(f"✅ Documents in {first_docset}: {len(documents)} documents")
            
            # Test listing chunks
            if documents:
                first_doc = documents[0]
                print(f"\n🔄 Testing chunk listing for document: {first_doc['name']}")
                chunks_result = storage.supabase.table("chunks").select("*").eq("document_id", first_doc['id']).execute()
                print(f"✅ Chunks for document: {len(chunks_result.data)} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in storage operations test: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Starting Vector Search Tests")
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {missing_vars}")
        print("Please set these variables in your .env file")
        return
    
    # Run tests
    vector_result = await test_vector_search()
    manager_result = await test_rag_manager()
    storage_result = await test_storage_operations()
    
    print("\n🎉 Vector Search Tests Completed!")
    
    if vector_result and manager_result and storage_result:
        print("✅ All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())
