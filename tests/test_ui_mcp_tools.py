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
    
    def test_ask_basic(self):
        """Test basic ask functionality"""
        with patch('src.ragspace.ui.handlers.get_rag_manager') as mock_get_rag:
            mock_rag = Mock()
            
            # Mock query_with_metadata method
            async def mock_query_with_metadata(query, docsets=None):
                return {
                    "status": "success",
                    "query": query,
                    "response": "This is a test response from the mock RAG system.",
                    "sources": [],
                    "metadata": {}
                }
            
            mock_rag.query_with_metadata = mock_query_with_metadata
            mock_get_rag.return_value = mock_rag
            
            result = ask("test query")
            
            # Check that the result contains the expected response
            assert "This is a test response from the mock RAG system" in str(result)
    
    def test_ask_empty_query(self):
        """Test ask with empty query"""
        result = ask("")
        assert "Please provide a query" in result
    
    def test_ask_with_docset(self):
        """Test ask with specific docset"""
        with patch('src.ragspace.ui.handlers.get_rag_manager') as mock_get_rag:
            mock_rag = Mock()
            
            # Mock query_with_metadata method
            async def mock_query_with_metadata(query, docsets=None):
                return {
                    "status": "success",
                    "query": query,
                    "response": "Hello! This is a mock response to your greeting.",
                    "sources": [],
                    "metadata": {}
                }
            
            mock_rag.query_with_metadata = mock_query_with_metadata
            mock_get_rag.return_value = mock_rag
            
            result = ask("hello", "test-docset")
            
            # Check that the result contains the expected response
            assert "Hello! This is a mock response to your greeting" in str(result)
    
    def test_ask_error_handling(self):
        """Test ask error handling"""
        with patch('src.ragspace.ui.handlers.get_rag_manager') as mock_get_rag:
            mock_rag = Mock()
            
            # Mock query_with_metadata method with error
            async def mock_query_with_metadata(query, docsets=None):
                return {
                    "status": "error",
                    "query": query,
                    "error": "❌ Mock error: This is a test error response.",
                    "response": "",
                    "sources": [],
                    "metadata": {}
                }
            
            mock_rag.query_with_metadata = mock_query_with_metadata
            mock_get_rag.return_value = mock_rag
            
            result = ask("error test")
            
            # Check that the result contains the error message
            assert "❌ Mock error" in str(result)
    
    def test_ask_help_query(self):
        """Test ask with help query"""
        with patch('src.ragspace.ui.handlers.get_rag_manager') as mock_get_rag:
            mock_rag = Mock()
            
            # Mock query_with_metadata method
            async def mock_query_with_metadata(query, docsets=None):
                return {
                    "status": "success",
                    "query": query,
                    "response": "I'm a mock RAG system. I can help you with test queries.",
                    "sources": [],
                    "metadata": {}
                }
            
            mock_rag.query_with_metadata = mock_query_with_metadata
            mock_get_rag.return_value = mock_rag
            
            result = ask("help me")
            
            # Check that the result contains the expected response
            assert "I'm a mock RAG system" in str(result)
            assert "help you with test queries" in str(result) 