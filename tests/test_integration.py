"""
Integration tests for RAGSpace
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest

class TestIntegration(UIBaseTest):
    """Test integration between different components"""
    
    def test_mcp_tools_functionality(self, setup_mock_storage, setup_mock_rag):
        """Test MCP tools functionality"""
        from src.ragspace.mcp.tools import list_docsets, ask
        
        # Test list_docsets
        result = list_docsets()
        assert "No docsets found" in result or "available" in result
        
        # Test ask with mock RAG
        result = ask("test query")
        assert "This is a test response from the mock RAG system" in result
    
    def test_ui_component_integration(self, setup_mock_storage, setup_mock_rag):
        """Test UI component integration"""
        from src.ragspace.mcp.tools import list_docsets, ask
        
        # Test MCP tools integration
        list_result = list_docsets()
        assert "No docsets found" in list_result or "available" in list_result
        
        ask_result = ask("hello")
        assert "Hello! This is a mock response to your greeting" in ask_result
    
    def test_storage_and_rag_integration(self, setup_mock_storage, setup_mock_rag):
        """Test integration between storage and RAG"""
        # Setup test data
        mock_manager = setup_mock_storage
        mock_manager.create_docset("integration-test", "Integration test")
        mock_manager.add_document_to_docset(
            "integration-test",
            "Test Document",
            "This is a test document for integration testing.",
            "file"
        )
        
        # Test RAG query with the stored document
        from src.ragspace.mcp.tools import ask
        result = ask("test", "integration-test")
        
        # Should return mock RAG response
        assert "This is a test response from the mock RAG system" in result
    
    def test_error_handling_integration(self, setup_mock_storage, setup_mock_rag):
        """Test error handling across components"""
        from src.ragspace.mcp.tools import ask
        
        # Test error handling in RAG
        result = ask("error test")
        assert "❌ Mock error" in result 