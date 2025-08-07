"""
UI Integration tests for RAGSpace
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest

class TestUIIntegration(UIBaseTest):
    """Test UI component integration"""
    
    def test_ui_component_integration(self, setup_mock_storage, setup_mock_rag):
        """Test UI component integration"""
        from src.ragspace.mcp.tools import list_docsets, ask
        
        # Test MCP tools integration
        list_result = list_docsets()
        assert "No docsets found" in list_result or "available" in list_result
        
        ask_result = ask("hello")
        assert "Hello! This is a mock response to your greeting" in ask_result
    
    def test_knowledge_management_integration(self, setup_mock_storage, setup_mock_rag):
        """Test knowledge management integration"""
        # Test docset creation
        from src.ragspace.ui.handlers import create_docset_ui
        result = create_docset_ui("integration-test", "Integration test docset")
        assert "✅" in result
        
        # Test file upload
        from src.ragspace.ui.handlers import upload_file_to_docset
        mock_file = Mock()
        mock_file.name = "/path/to/test.txt"
        mock_file.size = 1024
        mock_file.type = "text/plain"
        
        result = upload_file_to_docset([mock_file], "integration-test")
        assert "✅ Added: test.txt" in result
    
    def test_chat_interface_integration(self, setup_mock_storage, setup_mock_rag):
        """Test chat interface integration"""
        from src.ragspace.ui.handlers import process_query, clear_chat
        
        # Test query processing
        history = []
        new_history, _ = process_query("test query", history, "test-docset")
        assert len(new_history) == 2  # user + assistant messages
        assert new_history[0]["role"] == "user"
        assert new_history[1]["role"] == "assistant"
        
        # Test clear chat
        new_history, _ = clear_chat()
        assert new_history == []
    
    def test_mcp_tools_ui_integration(self, setup_mock_storage, setup_mock_rag):
        """Test MCP tools UI integration"""
        from src.ragspace.mcp.tools import list_docsets, ask
        
        # Test list_docsets
        result = list_docsets()
        assert "No docsets found" in result or "available" in result
        
        # Test ask with mock RAG
        result = ask("test query")
        assert "This is a test response from the mock RAG system" in result
    
    def test_error_handling_integration(self, setup_mock_storage, setup_mock_rag):
        """Test error handling across UI components"""
        from src.ragspace.mcp.tools import ask
        
        # Test RAG error handling
        result = ask("error test")
        assert "❌ Mock error" in result
        
        # Test empty query
        result = ask("")
        assert "Please provide a query" in result 