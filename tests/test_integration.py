"""
Integration tests for RAGSpace
"""

import pytest
import requests
import subprocess
import time
import json
import os
from src.ragspace.storage.manager import docset_manager

class TestIntegration:
    """Integration tests for the complete RAGSpace system"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Clear any existing data
        docset_manager.docsets.clear()
        yield
        # Cleanup after test
        docset_manager.docsets.clear()
    
    def test_docset_operations(self):
        """Test DocSet creation and management"""
        # Test create docset
        result = docset_manager.create_docset("test-docset", "Test description")
        assert "created successfully" in result
        
        # Test list docsets
        result = docset_manager.list_docsets()
        assert "test-docset" in result
        assert "Test description" in result
        
        # Test add document
        result = docset_manager.add_document_to_docset(
            "test-docset", 
            "Test Document", 
            "This is test content",
            "file"
        )
        assert "added to docset" in result
        
        # Test list documents in docset
        result = docset_manager.list_documents_in_docset("test-docset")
        assert "Test Document" in result
        assert "test-docset" in result
    
    def test_query_functionality(self):
        """Test query functionality"""
        # Setup test data
        docset_manager.create_docset("test-query", "Test query docset")
        docset_manager.add_document_to_docset(
            "test-query",
            "Python Guide",
            "Python is a programming language. It is used for web development.",
            "file"
        )
        
        # Test query with specific docset
        result = docset_manager.query_knowledge_base("Python", "test-query")
        assert "Python Guide" in result
        assert "programming language" in result
        
        # Test query without docset (search all)
        result = docset_manager.query_knowledge_base("Python")
        assert "Python Guide" in result
        
        # Test query with non-existent docset
        result = docset_manager.query_knowledge_base("Python", "non-existent")
        assert "not found" in result
        
        # Test query with no matching content
        result = docset_manager.query_knowledge_base("JavaScript", "test-query")
        assert "No documents found" in result
    
    def test_mcp_tools_functionality(self):
        """Test MCP tools functionality"""
        from src.ragspace.mcp.tools import list_docset, ask
        
        # Test list_docset with existing data (seed data is loaded)
        result = list_docset()
        assert "gradio mcp" in result or "python examples" in result or "ai knowledge base" in result
        
        # Test ask with existing data
        result = ask("What is available?")
        assert "gradio" in result or "python" in result or "ai" in result
        
        # Setup test data
        docset_manager.create_docset("mcp-test", "MCP test docset")
        docset_manager.add_document_to_docset(
            "mcp-test",
            "MCP Documentation",
            "Model Context Protocol is a standard for LLM tools.",
            "file"
        )
        
        # Test list_docset with data (seed data + test data)
        result = list_docset()
        # Check that seed data is present
        assert "gradio mcp" in result or "python examples" in result or "ai knowledge base" in result
        
        # Test ask with specific docset (use existing seed data)
        result = ask("gradio", "gradio mcp")
        assert "gradio" in result.lower() or "mcp" in result.lower()
        
        # Test ask without docset
        result = ask("gradio")
        assert "gradio" in result.lower() or "mcp" in result.lower()
    
    def test_ui_handlers(self):
        """Test UI handler functions"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            add_url_to_docset,
            add_github_repo_to_docset,
            process_query,
            clear_chat
        )
        
        # Test create_docset_ui
        result = create_docset_ui("ui-test-unique", "UI test description")
        assert "created successfully" in result or "already exists" in result
        
        # Test upload_file_to_docset (mock)
        class MockFile:
            def __init__(self, name, size):
                self.name = name
                self.size = size
        
        mock_files = [MockFile("test.txt", 1024)]
        result = upload_file_to_docset(mock_files, "ui-test-unique")
        assert "Added: test.txt" in result
        
        # Test add_url_to_docset
        result = add_url_to_docset("https://example.com", "ui-test-unique", "docs")
        assert "added to docset" in result or "Error" in result
        
        # Test add_github_repo_to_docset
        result = add_github_repo_to_docset("owner/repo", "ui-test-unique")
        assert "added to docset" in result or "Error" in result
        
        # Test process_query
        history = []
        new_history, _ = process_query("Test query", history, "ui-test-unique")
        assert len(new_history) == 2  # user + assistant messages
        assert new_history[0]["role"] == "user"
        assert new_history[1]["role"] == "assistant"
        
        # Test clear_chat
        history = [{"role": "user", "content": "test"}]
        new_history, _ = clear_chat()
        assert new_history == []
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        # Test creating duplicate docset
        docset_manager.create_docset("duplicate", "First")
        result = docset_manager.create_docset("duplicate", "Second")
        assert "already exists" in result
        
        # Test adding document to non-existent docset
        result = docset_manager.add_document_to_docset(
            "non-existent", "Test", "Content", "file"
        )
        assert "not found" in result
        
        # Test listing documents in non-existent docset
        result = docset_manager.list_documents_in_docset("non-existent")
        assert "not found" in result
        
        # Test querying empty docset
        docset_manager.create_docset("empty", "Empty docset")
        result = docset_manager.list_documents_in_docset("empty")
        assert "is empty" in result
    
    def test_document_metadata(self):
        """Test document metadata handling"""
        docset_manager.create_docset("metadata-test", "Metadata test")
        
        # Test document with metadata
        metadata = {"url": "https://example.com", "type": "website"}
        result = docset_manager.add_document_to_docset(
            "metadata-test",
            "Test Document",
            "Test content",
            "website",
            metadata
        )
        assert "added to docset" in result
        
        # Verify metadata is stored
        docset = docset_manager.get_docset("metadata-test")
        assert len(docset.documents) == 1
        assert docset.documents[0].metadata["url"] == "https://example.com"
        assert docset.documents[0].metadata["type"] == "website"
    
    def test_document_search(self):
        """Test document search functionality"""
        docset_manager.create_docset("search-test", "Search test")
        
        # Add multiple documents
        docset_manager.add_document_to_docset(
            "search-test", "Python Guide", "Python programming language", "file"
        )
        docset_manager.add_document_to_docset(
            "search-test", "JavaScript Guide", "JavaScript programming language", "file"
        )
        docset_manager.add_document_to_docset(
            "search-test", "Web Development", "HTML, CSS, and JavaScript", "file"
        )
        
        # Test search for "Python"
        result = docset_manager.query_knowledge_base("Python", "search-test")
        assert "Python Guide" in result
        assert "Python programming" in result
        
        # Test search for "JavaScript"
        result = docset_manager.query_knowledge_base("JavaScript", "search-test")
        assert "JavaScript Guide" in result
        assert "Web Development" in result  # Should also match
        
        # Test search for "programming"
        result = docset_manager.query_knowledge_base("programming", "search-test")
        assert "Python Guide" in result
        assert "JavaScript Guide" in result 