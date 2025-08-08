"""
Integration tests for RAGSpace
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest

class TestIntegration(UIBaseTest):
    """Test integration between different components"""
    
    def test_mcp_tools_functionality(self):
        """Test MCP tools functionality"""
        from src.ragspace.mcp.tools import list_docsets, ask
        
        # Test list_docsets
        result = list_docsets()
        assert "No docsets found" in result or "available" in result
        
        # Test ask with mock
        with patch('src.ragspace.ui.handlers.get_rag_manager') as mock_get_rag:
            mock_rag = Mock()
            
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
            assert "This is a test response from the mock RAG system" in str(result)
    
    def test_ui_component_integration(self):
        """Test UI component integration"""
        from src.ragspace.ui.handlers import process_query
        
        # Test chat interface with mock
        with patch('src.ragspace.ui.handlers.get_rag_manager') as mock_get_rag:
            mock_rag = Mock()
            
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
            
            history = []
            ask_result = process_query("hello", history)
            assert "Hello! This is a mock response to your greeting" in str(ask_result)
    
    def test_storage_and_rag_integration(self):
        """Test storage and RAG integration"""
        from src.ragspace.mcp.tools import ask
        
        # Test RAG query with mock
        with patch('src.ragspace.ui.handlers.get_rag_manager') as mock_get_rag:
            mock_rag = Mock()
            
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
            
            result = ask("test")
            assert "This is a test response from the mock RAG system" in str(result)
    
    def test_error_handling_integration(self):
        """Test error handling integration"""
        from src.ragspace.mcp.tools import ask
        
        # Test error handling with mock
        with patch('src.ragspace.ui.handlers.get_rag_manager') as mock_get_rag:
            mock_rag = Mock()
            
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
            assert "❌ Mock error" in str(result) 