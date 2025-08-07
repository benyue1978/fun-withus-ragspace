"""
UI tests for MCP Tools component
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest
from src.ragspace.mcp.tools import list_docsets, ask

class TestMCPToolsUI(UIBaseTest):
    """Test MCP Tools UI functionality"""
    
    def test_list_docsets_basic(self, setup_mock_storage):
        """Test basic docset listing via MCP"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("mcp-test", "MCP test docset")
        mock_manager.add_document_to_docset(
            "mcp-test",
            "MCP Document",
            "This is a test document for MCP tools.",
            "file"
        )
        
        # Test list_docsets
        result = list_docsets()
        
        # Verify response
        assert "Available DocSets:" in result
        assert "mcp-test" in result
        assert "MCP test docset" in result
    
    def test_list_docsets_empty(self, setup_mock_storage):
        """Test list_docsets with no docsets"""
        result = list_docsets()
        
        # Verify response
        assert "No docsets found" in result
    
    def test_ask_basic(self, setup_mock_storage, setup_mock_rag):
        """Test basic ask functionality via MCP"""
        # Test ask with mock RAG
        result = ask("test query")
        
        # Verify response from mock RAG
        assert "This is a test response from the mock RAG system" in result
    
    def test_ask_empty_query(self, setup_mock_storage, setup_mock_rag):
        """Test ask with empty query"""
        result = ask("")
        
        # Verify error response
        assert "Please provide a query" in result
    
    def test_ask_with_docset(self, setup_mock_storage, setup_mock_rag):
        """Test ask with specific docset"""
        # Setup test data
        mock_manager = setup_mock_storage
        mock_manager.create_docset("test-docset", "Test docset")
        
        # Test ask with docset
        result = ask("hello", "test-docset")
        
        # Verify response from mock RAG
        assert "Hello! This is a mock response to your greeting" in result
    
    def test_ask_error_handling(self, setup_mock_storage, setup_mock_rag):
        """Test ask error handling"""
        result = ask("error test")
        
        # Verify error response from mock RAG
        assert "❌ Mock error" in result
    
    def test_ask_help_query(self, setup_mock_storage, setup_mock_rag):
        """Test ask with help query"""
        result = ask("help me")
        
        # Verify help response from mock RAG
        assert "I'm a mock RAG system" in result
        assert "help you with test queries" in result 