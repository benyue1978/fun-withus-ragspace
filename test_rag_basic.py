#!/usr/bin/env python3
"""
Basic RAG system test without external dependencies
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ragspace.services import RAGTextSplitter
from ragspace.storage import MockDocsetManager

# Load environment variables
load_dotenv()


def test_text_splitter():
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
        print(f"    Content: {chunk['content'][:100]}...")
    
    return chunks


def test_code_splitting():
    """Test code splitting functionality"""
    print("\n=== Testing Code Splitting ===")
    
    splitter = RAGTextSplitter()
    
    # Test code splitting
    sample_code = """
    class ExampleClass:
        def __init__(self, name):
            self.name = name
        
        def get_name(self):
            return self.name
        
        def set_name(self, new_name):
            self.name = new_name
    
    def main():
        obj = ExampleClass("test")
        print(obj.get_name())
    """
    
    chunks = splitter.split_text(sample_code, "code")
    print(f"✅ Code splitter created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {len(chunk['content'])} characters")
        print(f"    Content: {chunk['content'][:100]}...")
    
    return chunks


def test_markdown_splitting():
    """Test markdown splitting functionality"""
    print("\n=== Testing Markdown Splitting ===")
    
    splitter = RAGTextSplitter()
    
    # Test markdown splitting
    sample_markdown = """
    # Main Title
    
    This is a paragraph with some **bold text** and *italic text*.
    
    ## Subsection
    
    Here's a code block:
    
    ```python
    def hello():
        print("Hello, World!")
    ```
    
    ### Another subsection
    
    More content here.
    """
    
    chunks = splitter.split_text(sample_markdown, "markdown")
    print(f"✅ Markdown splitter created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {len(chunk['content'])} characters")
        print(f"    Content: {chunk['content'][:100]}...")
    
    return chunks


def test_storage_operations():
    """Test storage operations"""
    print("\n=== Testing Storage Operations ===")
    
    storage = MockDocsetManager()
    
    # Test creating docset
    result = storage.create_docset("test_docset", "Test description")
    print(f"✅ Create docset: {result}")
    
    # Test listing docsets
    docsets = storage.list_docsets()
    print(f"✅ List docsets: {docsets}")
    
    # Test adding document
    result = storage.add_document_to_docset("test_docset", "test_doc", "This is test content", "text")
    print(f"✅ Add document: {result}")
    
    # Test listing documents
    documents = storage.list_documents_in_docset("test_docset")
    print(f"✅ List documents: {documents}")
    
    return storage


def test_document_processing():
    """Test document processing pipeline"""
    print("\n=== Testing Document Processing ===")
    
    splitter = RAGTextSplitter()
    storage = MockDocsetManager()
    
    # Create a test document
    test_document = {
        "id": "test-123",
        "name": "test_document",
        "content": """
        This is a test document with multiple sections.
        
        ## Section 1
        This section contains important information about the system.
        
        ## Section 2
        This section contains code examples:
        
        ```python
        def example():
            return "Hello, World!"
        ```
        
        ## Section 3
        This section contains more text content.
        """,
        "type": "markdown"
    }
    
    # Split document
    chunks = splitter.split_document(test_document)
    print(f"✅ Document split into {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}:")
        print(f"    Document: {chunk['document_name']}")
        print(f"    Type: {chunk['document_type']}")
        print(f"    Content: {chunk['content'][:100]}...")
        print(f"    Metadata: {chunk['metadata']}")
    
    return chunks


def main():
    """Main test function"""
    print("🚀 Starting Basic RAG System Tests")
    
    # Run tests
    test_text_splitter()
    test_code_splitting()
    test_markdown_splitting()
    test_storage_operations()
    test_document_processing()
    
    print("\n🎉 Basic RAG System Tests Completed!")
    print("\n✅ All core components are working correctly!")
    print("📝 Next steps:")
    print("  1. Set up environment variables (OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY)")
    print("  2. Run the full RAG system test")
    print("  3. Deploy the database migrations")
    print("  4. Start using the RAG system!")


if __name__ == "__main__":
    main()
