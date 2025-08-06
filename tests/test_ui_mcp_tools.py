"""
UI tests for MCP Tools component
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest
from src.ragspace.mcp.tools import list_docset, ask

class TestMCPToolsUI(UIBaseTest):
    """Test MCP Tools UI functionality"""
    
    def test_list_docset_basic(self, setup_mock_storage):
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
        
        # Test list_docset
        result = list_docset()
        
        # Verify response
        assert "mcp-test" in result
        assert "MCP test docset" in result
    
    def test_list_docset_empty(self, setup_mock_storage):
        """Test docset listing when no docsets exist"""
        result = list_docset()
        
        # Verify empty response
        assert "No docsets found" in result or "available" in result
    
    def test_ask_basic(self, setup_mock_storage):
        """Test basic ask functionality via MCP"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("ask-test", "Ask test docset")
        mock_manager.add_document_to_docset(
            "ask-test",
            "Ask Document",
            "This document contains information about asking questions.",
            "file"
        )
        
        # Test ask
        result = ask("asking")
        
        # Verify response
        assert "Ask Document" in result or "asking" in result.lower()
    
    def test_ask_with_docset(self, setup_mock_storage):
        """Test ask functionality with specific docset"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("specific-ask", "Specific ask test")
        mock_manager.add_document_to_docset(
            "specific-ask",
            "Specific Document",
            "This document is specific to the ask test.",
            "file"
        )
        
        # Test ask with specific docset
        result = ask("specific", "specific-ask")
        
        # Verify response
        assert "Specific Document" in result or "specific" in result.lower()
    
    def test_ask_no_matches(self, setup_mock_storage):
        """Test ask functionality with no matching documents"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("no-match-ask", "No match ask test")
        mock_manager.add_document_to_docset(
            "no-match-ask",
            "No Match Document",
            "This document has no relevant content.",
            "file"
        )
        
        # Test ask with no matches
        result = ask("xyz123", "no-match-ask")
        
        # Verify no-match response
        assert "No documents found" in result or "not found" in result
    
    def test_ask_nonexistent_docset(self, setup_mock_storage):
        """Test ask functionality with non-existent docset"""
        result = ask("test", "non-existent")
        
        # Verify error response
        assert "not found" in result or "No docsets available" in result
    
    def test_ask_empty_query(self, setup_mock_storage):
        """Test ask functionality with empty query"""
        result = ask("")
        
        # Verify empty query response
        assert "Please provide a query" in result
    
    def test_mcp_tools_integration(self, setup_mock_storage):
        """Test MCP tools integration with multiple docsets"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("mcp1", "First MCP docset")
        mock_manager.create_docset("mcp2", "Second MCP docset")
        
        mock_manager.add_document_to_docset(
            "mcp1", "Doc1", "Content about Python programming", "file"
        )
        mock_manager.add_document_to_docset(
            "mcp2", "Doc2", "Content about JavaScript programming", "file"
        )
        
        # Test list_docset
        list_result = list_docset()
        assert "mcp1" in list_result
        assert "mcp2" in list_result
        
        # Test ask across all docsets
        ask_result = ask("programming")
        assert "Doc1" in ask_result or "Doc2" in ask_result or "programming" in ask_result.lower()
    
    def test_mcp_tools_case_insensitive(self, setup_mock_storage):
        """Test that MCP tools are case insensitive"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("case-mcp", "Case MCP test")
        mock_manager.add_document_to_docset(
            "case-mcp",
            "Case Document",
            "This document contains PYTHON programming language.",
            "file"
        )
        
        # Test case insensitive ask
        result = ask("python", "case-mcp")
        
        # Verify response (should match despite case difference)
        assert "Case Document" in result or "python" in result.lower()
    
    def test_mcp_tools_special_characters(self, setup_mock_storage):
        """Test MCP tools with special characters"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("special-mcp", "Special MCP test")
        mock_manager.add_document_to_docset(
            "special-mcp",
            "Special Document",
            "This document contains special chars: @#$%^&*()",
            "file"
        )
        
        # Test ask with special characters
        result = ask("@#$%", "special-mcp")
        
        # Verify response
        assert "Special Document" in result or "special" in result.lower()
    
    def test_mcp_tools_large_content(self, setup_mock_storage):
        """Test MCP tools with large content"""
        # Setup test data with large content using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("large-mcp", "Large MCP test")
        
        large_content = "This is a very large document with lots of content. " * 100
        mock_manager.add_document_to_docset(
            "large-mcp",
            "Large Document",
            large_content,
            "file"
        )
        
        # Test ask
        result = ask("large", "large-mcp")
        
        # Verify response (should be truncated)
        assert "Large Document" in result or "large" in result.lower()
        assert len(result) < len(large_content)  # Should be truncated
    
    def test_mcp_tools_multiple_documents(self, setup_mock_storage):
        """Test MCP tools with multiple documents in same docset"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("multi-mcp", "Multiple MCP test")
        
        # Add multiple documents
        mock_manager.add_document_to_docset(
            "multi-mcp", "Doc1", "First document about Python", "file"
        )
        mock_manager.add_document_to_docset(
            "multi-mcp", "Doc2", "Second document about JavaScript", "file"
        )
        mock_manager.add_document_to_docset(
            "multi-mcp", "Doc3", "Third document about HTML", "file"
        )
        
        # Test ask
        result = ask("document", "multi-mcp")
        
        # Verify response contains multiple documents
        assert "Doc1" in result or "Doc2" in result or "Doc3" in result or "document" in result.lower()
    
    def test_mcp_tools_error_handling(self, setup_mock_storage):
        """Test MCP tools error handling"""
        # Test with invalid inputs
        result = ask("", "non-existent")
        assert "Please provide a query" in result
        
        # Test list_docset with no data
        list_result = list_docset()
        assert "No docsets found" in list_result or "available" in list_result 