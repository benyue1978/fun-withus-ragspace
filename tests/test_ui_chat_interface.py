"""
UI tests for Chat Interface component
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest
from src.ragspace.ui.handlers import process_query, clear_chat

class TestChatInterfaceUI(UIBaseTest):
    """Test Chat Interface UI functionality"""
    
    def test_process_query_basic(self, setup_mock_storage, setup_mock_rag):
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
        new_history, _ = process_query("test query", history)
        
        # Verify response from mock RAG - expect dictionary format for Gradio Chatbot
        assert len(new_history) == 2
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "test query"
        assert new_history[1]["role"] == "assistant"
        assert "This is a test response from the mock RAG system" in new_history[1]["content"]
    
    def test_process_query_global_search(self, setup_mock_storage, setup_mock_rag):
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
        new_history, _ = process_query("hello", history)
        
        # Verify response from mock RAG - expect dictionary format for Gradio Chatbot
        assert len(new_history) == 2
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "hello"
        assert new_history[1]["role"] == "assistant"
        assert "Hello! This is a mock response to your greeting" in new_history[1]["content"]
    
    def test_process_query_no_matches(self, setup_mock_storage, setup_mock_rag):
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
        
        # Verify response from mock RAG (should return default response) - expect dictionary format
        assert len(new_history) == 2
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "xyz123"
        assert new_history[1]["role"] == "assistant"
        assert "This is a mock RAG response for testing purposes" in new_history[1]["content"]
    
    def test_process_query_with_history(self, setup_mock_storage, setup_mock_rag):
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
        new_history, _ = process_query("help", history)
        
        # Verify response from mock RAG - expect dictionary format for Gradio Chatbot
        assert len(new_history) == 4
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "Previous question"
        assert new_history[1]["role"] == "assistant"
        assert new_history[1]["content"] == "Previous answer"
        assert new_history[2]["role"] == "user"
        assert new_history[2]["content"] == "help"
        assert "I'm a mock RAG system" in new_history[3]["content"]
        assert "help you with test queries" in new_history[3]["content"]
    
    def test_process_query_empty(self, setup_mock_storage, setup_mock_rag):
        """Test query processing with empty query"""
        history = []
        new_history, _ = process_query("", history)
        
        # Should return unchanged history for empty query
        assert new_history == history
    
    def test_process_query_special_characters(self, setup_mock_storage, setup_mock_rag):
        """Test query processing with special characters"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("special-test", "Special test")
        mock_manager.add_document_to_docset(
            "special-test",
            "Special Document",
            "This document contains special characters: @#$%^&*()",
            "file"
        )
        
        # Test query processing
        history = []
        new_history, _ = process_query("@#$%", history)
        
        # Verify response from mock RAG - expect dictionary format
        assert len(new_history) == 2
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "@#$%"
        assert new_history[1]["role"] == "assistant"
        assert "This is a mock RAG response for testing purposes" in new_history[1]["content"]
    
    def test_process_query_case_insensitive(self, setup_mock_storage, setup_mock_rag):
        """Test query processing with case insensitive search"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("case-test", "Case test")
        mock_manager.add_document_to_docset(
            "case-test",
            "Case Document",
            "This document tests case sensitivity with Python programming.",
            "file"
        )
        
        # Test query processing with different cases
        history = []
        new_history, _ = process_query("PYTHON", history)
        
        # Verify response from mock RAG - expect dictionary format
        assert len(new_history) == 2
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "PYTHON"
        assert new_history[1]["role"] == "assistant"
        assert "This is a mock RAG response for testing purposes" in new_history[1]["content"]
    
    def test_process_query_multiple_docsets(self, setup_mock_storage, setup_mock_rag):
        """Test query processing with multiple docsets"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("docset1", "Docset 1")
        mock_manager.create_docset("docset2", "Docset 2")
        mock_manager.add_document_to_docset(
            "docset1",
            "Doc1",
            "This is document 1 about programming.",
            "file"
        )
        mock_manager.add_document_to_docset(
            "docset2",
            "Doc2",
            "This is document 2 about programming.",
            "file"
        )
        
        # Test query processing
        history = []
        new_history, _ = process_query("programming", history)
        
        # Verify response from mock RAG - expect dictionary format
        assert len(new_history) == 2
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "programming"
        response_content = new_history[1]["content"]
        assert "This is a mock RAG response for testing purposes" in response_content
    
    def test_clear_chat(self, setup_mock_storage, setup_mock_rag):
        """Test clear chat functionality"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("clear-test", "Clear test")
        mock_manager.add_document_to_docset(
            "clear-test",
            "Clear Document",
            "This document tests clear functionality.",
            "file"
        )
        
        # Test clear chat
        history = [
            {"role": "user", "content": "Test question"},
            {"role": "assistant", "content": "Test answer"}
        ]
        new_history, _ = clear_chat()
        
        # Verify chat is cleared
        assert new_history == []
    
    def test_chat_interface_integration(self, setup_mock_storage, setup_mock_rag):
        """Test chat interface integration"""
        # Setup test data using the mock manager
        mock_manager = setup_mock_storage
        mock_manager.create_docset("integration-test", "Integration test")
        mock_manager.add_document_to_docset(
            "integration-test",
            "Integration Document",
            "This document tests integration functionality.",
            "file"
        )
        
        # Test multiple queries
        history = []
        new_history, _ = process_query("integration", history)
        
        # Verify response from mock RAG - expect dictionary format
        assert len(new_history) == 2
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "integration"
        assert "This is a mock RAG response for testing purposes" in new_history[1]["content"]
        
        # Test follow-up query
        history = new_history
        new_history, _ = process_query("follow up", history)
        
        # Verify follow-up response - expect dictionary format
        assert len(new_history) == 4
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "integration"
        assert new_history[1]["role"] == "assistant"
        assert new_history[2]["role"] == "user"
        assert new_history[2]["content"] == "follow up"
        assert "This is a mock RAG response for testing purposes" in new_history[3]["content"] 