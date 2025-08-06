"""
Base UI testing configuration for RAGSpace
"""

import pytest
import gradio as gr
from unittest.mock import Mock, patch
from src.ragspace.storage import StorageInterface, MockDocsetManager
from src.ragspace.ui.components.knowledge_management import create_knowledge_management_tab
from src.ragspace.ui.components.chat_interface import create_chat_interface_tab
from src.ragspace.ui.components.mcp_tools import create_mcp_tools_tab

class MockFile:
    """Mock file object for testing file uploads"""
    def __init__(self, name, size=1024, content_type="text/plain"):
        self.name = name
        self.size = size
        self.type = content_type

class UIBaseTest:
    """Base class for UI tests with common setup"""
    
    @pytest.fixture(autouse=True)
    def setup_mock_storage(self):
        """Setup mock storage for all UI tests"""
        # Use mock storage for testing
        from src.ragspace.storage import use_mock, MockDocsetManager
        use_mock()  # Switch to mock storage
        
        # Get the mock manager instance
        from src.ragspace.storage import docset_manager
        mock_manager = docset_manager
        
        # Also patch the module-level docset_manager to ensure consistency
        import src.ragspace.storage
        src.ragspace.storage.docset_manager = mock_manager
        
        yield mock_manager
    
    def create_mock_gradio_app(self):
        """Create a mock Gradio app for testing"""
        with gr.Blocks() as demo:
            with gr.Tabs():
                create_knowledge_management_tab()
                create_chat_interface_tab()
                create_mcp_tools_tab()
        return demo
    
    def mock_file_upload(self, filename="test.txt", content="Test content"):
        """Create a mock file upload"""
        return MockFile(filename, len(content))
    
    def mock_gradio_event(self, fn, *args, **kwargs):
        """Mock a Gradio event call"""
        return fn(*args, **kwargs)
    
    def assert_success_message(self, result, expected_keywords):
        """Assert that result contains success keywords"""
        assert any(keyword in result for keyword in expected_keywords), f"Expected success keywords in: {result}"
    
    def assert_error_message(self, result, expected_keywords):
        """Assert that result contains error keywords"""
        assert any(keyword in result for keyword in expected_keywords), f"Expected error keywords in: {result}" 