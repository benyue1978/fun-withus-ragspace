"""
UI Integration tests for RAGSpace
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest

class TestUIIntegration(UIBaseTest):
    """Test UI component integration"""
    
    def test_ui_component_integration(self):
        """Test UI component integration"""
        from src.ragspace.ui.handlers import process_query
        
        # Test chat interface
        history = []
        ask_result = process_query("hello", history)
        assert "Hello! This is a mock response to your greeting" in str(ask_result)
    
    def test_knowledge_management_integration(self):
        """Test knowledge management integration"""
        from src.ragspace.ui.handlers import create_docset
        
        # Test docset creation
        result, _ = create_docset("test-docset")
        assert "✅" in result
    
    def test_chat_interface_integration(self):
        """Test chat interface integration"""
        from src.ragspace.ui.handlers import process_query
        
        # Test chat query
        history = []
        result = process_query("test query", history)
        assert "This is a test response from the mock RAG system" in str(result)
    
    def test_mcp_tools_ui_integration(self):
        """Test MCP tools UI integration"""
        from src.ragspace.ui.handlers import test_ask_tool
        
        # Test MCP ask tool
        result = test_ask_tool("test query", None)
        assert "This is a test response from the mock RAG system" in str(result)
    
    def test_error_handling_integration(self):
        """Test error handling integration"""
        from src.ragspace.ui.handlers import test_ask_tool
        
        # Test error handling
        result = test_ask_tool("error test", None)
        assert "❌ Mock error" in str(result) 