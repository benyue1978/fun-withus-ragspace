"""
UI tests for Chat Interface component
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest
from src.ragspace.ui.handlers import process_query, clear_chat

class TestChatInterfaceUI(UIBaseTest):
    """Test Chat Interface UI functionality"""
    
    def test_process_query_basic(self, setup_mock_storage):
        """Test basic query processing"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("chat-test", "Chat test")
        mock_manager.add_document_to_docset(
            "chat-test",
            "Chat Document",
            "This document contains information about chat functionality.",
            "file"
        )
        
        # Test query processing
        history = []
        new_history, _ = process_query("chat", history)
        
        # Verify response
        assert len(new_history) == 2
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "chat"
        assert new_history[1]["role"] == "assistant"
        assert "Chat Document" in new_history[1]["content"] or "chat" in new_history[1]["content"].lower()
    
    def test_process_query_global_search(self, setup_mock_storage):
        """Test query processing with global search"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("global-test", "Global test")
        mock_manager.add_document_to_docset(
            "global-test",
            "Global Document",
            "This document contains global information.",
            "file"
        )
        
        # Test query processing
        history = []
        new_history, _ = process_query("global", history)
        
        # Verify response
        assert len(new_history) == 2
        assert "Global Document" in new_history[1]["content"] or "global" in new_history[1]["content"].lower()
    
    def test_process_query_no_matches(self, setup_mock_storage):
        """Test query processing with no matches"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("no-match", "No match test")
        mock_manager.add_document_to_docset(
            "no-match",
            "No Match Document",
            "This document has no relevant content.",
            "file"
        )
        
        # Test query processing
        history = []
        new_history, _ = process_query("xyz123", history)
        
        # Verify response
        assert len(new_history) == 2
        assert "No documents found" in new_history[1]["content"] or "not found" in new_history[1]["content"]
    
    def test_process_query_with_history(self, setup_mock_storage):
        """Test query processing with existing history"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("history-test", "History test")
        mock_manager.add_document_to_docset(
            "history-test",
            "History Document",
            "This document contains historical information.",
            "file"
        )
        
        # Test query processing with existing history
        history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]
        new_history, _ = process_query("history", history)
        
        # Verify response
        assert len(new_history) == 4
        assert new_history[0]["content"] == "Previous question"
        assert new_history[1]["content"] == "Previous answer"
        assert new_history[2]["content"] == "history"
        assert "History Document" in new_history[3]["content"] or "history" in new_history[3]["content"].lower()
    
    def test_process_query_empty(self, setup_mock_storage):
        """Test query processing with empty query"""
        history = []
        new_history, _ = process_query("", history)
        
        # Verify empty query doesn't change history
        assert new_history == history
    
    def test_process_query_special_characters(self, setup_mock_storage):
        """Test query processing with special characters"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("special-test", "Special test")
        mock_manager.add_document_to_docset(
            "special-test",
            "Special Document",
            "This document contains special chars: @#$%^&*()",
            "file"
        )
        
        # Test query processing with special characters
        history = []
        new_history, _ = process_query("@#$%", history)
        
        # Verify response
        assert len(new_history) == 2
        assert "Special Document" in new_history[1]["content"] or "special" in new_history[1]["content"].lower()
    
    def test_process_query_case_insensitive(self, setup_mock_storage):
        """Test that query processing is case insensitive"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("case-test", "Case test")
        mock_manager.add_document_to_docset(
            "case-test",
            "Case Document",
            "This document contains PYTHON programming language.",
            "file"
        )
        
        # Test case insensitive query
        history = []
        new_history, _ = process_query("python", history)
        
        # Verify response (should match despite case difference)
        assert len(new_history) == 2
        assert "Case Document" in new_history[1]["content"] or "python" in new_history[1]["content"].lower()
    
    def test_process_query_multiple_docsets(self, setup_mock_storage):
        """Test query processing across multiple docsets"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("docset1", "First docset")
        mock_manager.create_docset("docset2", "Second docset")
        
        mock_manager.add_document_to_docset(
            "docset1", "Doc1", "Content about Python programming", "file"
        )
        mock_manager.add_document_to_docset(
            "docset2", "Doc2", "Content about JavaScript programming", "file"
        )
        
        # Test query processing
        history = []
        new_history, _ = process_query("programming", history)
        
        # Verify response contains content from multiple docsets
        assert len(new_history) == 2
        response_content = new_history[1]["content"]
        assert "Doc1" in response_content or "Doc2" in response_content or "programming" in response_content.lower()
    
    def test_clear_chat(self, setup_mock_storage):
        """Test clearing chat history"""
        # Setup some history
        history = [
            {"role": "user", "content": "Test question"},
            {"role": "assistant", "content": "Test answer"}
        ]
        
        # Test clearing chat
        new_history, _ = clear_chat()
        
        # Verify history is cleared
        assert new_history == []
    
    def test_chat_interface_integration(self, setup_mock_storage):
        """Test chat interface integration with multiple queries"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("integration-test", "Integration test")
        mock_manager.add_document_to_docset(
            "integration-test",
            "Integration Document",
            "This document contains integration information.",
            "file"
        )
        
        # Test multiple queries
        history = []
        
        # First query
        history, _ = process_query("integration", history)
        assert len(history) == 2
        assert "Integration Document" in history[1]["content"] or "integration" in history[1]["content"].lower()
        
        # Second query
        history, _ = process_query("information", history)
        assert len(history) == 4
        assert "Integration Document" in history[3]["content"] or "information" in history[3]["content"].lower()
        
        # Clear chat
        history, _ = clear_chat()
        assert history == [] 