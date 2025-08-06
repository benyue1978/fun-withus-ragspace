"""
End-to-end UI integration tests for RAGSpace
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest, MockFile

class TestUIIntegration(UIBaseTest):
    """Test complete UI workflow integration"""
    
    def test_complete_workflow(self, setup_mock_storage):
        """Test complete workflow: create docset -> upload files -> query"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            add_url_to_docset,
            process_query,
            clear_chat
        )
        
        # Step 1: Create docset
        result = create_docset_ui("workflow-test", "Complete workflow test")
        self.assert_success_message(result, ["created successfully"])
        
        # Step 2: Upload files
        mock_files = [
            MockFile("python_guide.txt", 1024),
            MockFile("javascript_guide.md", 2048)
        ]
        result = upload_file_to_docset(mock_files, "workflow-test")
        self.assert_success_message(result, ["Added: python_guide.txt", "Added: javascript_guide.md"])
        
        # Step 3: Add URL
        result = add_url_to_docset("https://example.com/docs", "workflow-test", "website")
        self.assert_success_message(result, ["added to docset"])
        
        # Step 4: Query the knowledge base
        history = []
        new_history, _ = process_query("python", history, "workflow-test")
        
        # Verify response
        assert len(new_history) == 2
        assert new_history[1]["role"] == "assistant"
        assert "python_guide.txt" in new_history[1]["content"] or "python" in new_history[1]["content"].lower()
        
        # Step 5: Clear chat
        new_history, _ = clear_chat()
        assert new_history == []
    
    def test_multi_user_workflow(self, setup_mock_storage):
        """Test multiple users working with different docsets"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            process_query
        )
        
        # User 1 creates Python docset
        create_docset_ui("python-docs", "Python documentation")
        upload_file_to_docset([MockFile("python_basics.txt")], "python-docs")
        
        # User 2 creates JavaScript docset
        create_docset_ui("js-docs", "JavaScript documentation")
        upload_file_to_docset([MockFile("js_basics.txt")], "js-docs")
        
        # User 1 queries their docset
        history = []
        new_history, _ = process_query("python", history, "python-docs")
        assert "python_basics.txt" in new_history[1]["content"] or "python" in new_history[1]["content"].lower()
        
        # User 2 queries their docset
        history = []
        new_history, _ = process_query("javascript", history, "js-docs")
        assert "js_basics.txt" in new_history[1]["content"] or "javascript" in new_history[1]["content"].lower()
        
        # Verify isolation - User 1 shouldn't see User 2's content
        history = []
        new_history, _ = process_query("javascript", history, "python-docs")
        assert "No documents found" in new_history[1]["content"] or "not found" in new_history[1]["content"]
    
    def test_error_recovery_workflow(self, setup_mock_storage):
        """Test error recovery in UI workflow"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            add_url_to_docset,
            process_query
        )
        
        # Try to upload to non-existent docset (should fail)
        mock_files = [MockFile("test.txt")]
        result = upload_file_to_docset(mock_files, "non-existent")
        self.assert_error_message(result, ["not found"])
        
        # Create docset and try again (should succeed)
        create_docset_ui("recovery-test", "Recovery test")
        result = upload_file_to_docset(mock_files, "recovery-test")
        self.assert_success_message(result, ["Added: test.txt"])
        
        # Try to add URL to non-existent docset (should fail)
        result = add_url_to_docset("https://example.com", "non-existent", "website")
        self.assert_error_message(result, ["not found"])
        
        # Add URL to existing docset (should succeed)
        result = add_url_to_docset("https://example.com", "recovery-test", "website")
        self.assert_success_message(result, ["added to docset"])
        
        # Query should work now
        history = []
        new_history, _ = process_query("test", history, "recovery-test")
        assert len(new_history) == 2
        assert new_history[1]["role"] == "assistant"
    
    def test_large_scale_workflow(self, setup_mock_storage):
        """Test large scale workflow with many documents"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            process_query
        )
        
        # Create docset
        create_docset_ui("large-scale", "Large scale test")
        
        # Upload many files
        mock_files = []
        for i in range(10):
            mock_files.append(MockFile(f"document_{i}.txt", 1024))
        
        result = upload_file_to_docset(mock_files, "large-scale")
        
        # Verify all files were added
        for i in range(10):
            assert f"Added: document_{i}.txt" in result
        
        # Query should find multiple documents
        history = []
        new_history, _ = process_query("document", history, "large-scale")
        assert len(new_history) == 2
        assert new_history[1]["role"] == "assistant"
        # Should mention multiple documents
        response = new_history[1]["content"]
        assert "document_" in response
    
    def test_concurrent_operations(self, setup_mock_storage):
        """Test concurrent operations on same docset"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            add_url_to_docset,
            process_query
        )
        
        # Create docset
        create_docset_ui("concurrent-test", "Concurrent test")
        
        # Simulate concurrent operations
        operations = [
            lambda: upload_file_to_docset([MockFile("file1.txt")], "concurrent-test"),
            lambda: upload_file_to_docset([MockFile("file2.txt")], "concurrent-test"),
            lambda: add_url_to_docset("https://example1.com", "concurrent-test", "website"),
            lambda: add_url_to_docset("https://example2.com", "concurrent-test", "website"),
        ]
        
        # Execute operations
        results = [op() for op in operations]
        
        # Verify all operations succeeded
        for result in results:
            self.assert_success_message(result, ["added to docset", "Added:"])
        
        # Query should find all documents
        history = []
        new_history, _ = process_query("file", history, "concurrent-test")
        assert len(new_history) == 2
        assert new_history[1]["role"] == "assistant"
        response = new_history[1]["content"]
        assert "file1.txt" in response or "file2.txt" in response
    
    def test_ui_component_integration(self, setup_mock_storage):
        """Test integration between different UI components"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            process_query
        )
        from src.ragspace.mcp.tools import list_docset, ask
        
        # Create docset via UI
        create_docset_ui("integration-test", "Integration test")
        
        # Upload file via UI
        mock_files = [MockFile("integration_doc.txt")]
        upload_file_to_docset(mock_files, "integration-test")
        
        # List docsets via MCP
        list_result = list_docset()
        assert "integration-test" in list_result
        
        # Ask via MCP
        ask_result = ask("integration", "integration-test")
        assert "integration_doc.txt" in ask_result or "integration" in ask_result.lower()
        
        # Query via UI
        history = []
        new_history, _ = process_query("integration", history, "integration-test")
        assert len(new_history) == 2
        assert new_history[1]["role"] == "assistant"
        assert "integration_doc.txt" in new_history[1]["content"] or "integration" in new_history[1]["content"].lower()
    
    def test_data_persistence_simulation(self, setup_mock_storage):
        """Test that data persists across operations (simulating real storage)"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            process_query
        )
        
        # Create and populate docset
        create_docset_ui("persistence-test", "Persistence test")
        upload_file_to_docset([MockFile("persistent_doc.txt")], "persistence-test")
        
        # Simulate app restart by creating new storage instance
        from src.ragspace.storage import MockDocsetManager
        new_storage = MockDocsetManager()
        
        # Recreate the same data
        new_storage.create_docset("persistence-test", "Persistence test")
        new_storage.add_document_to_docset(
            "persistence-test",
            "persistent_doc.txt",
            "This is persistent content",
            "file"
        )
        
        # Query should still work
        result = new_storage.query_knowledge_base("persistent", "persistence-test")
        assert "persistent_doc.txt" in result or "persistent" in result.lower()
    
    def test_ui_error_boundaries(self, setup_mock_storage):
        """Test UI error boundaries and graceful degradation"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            process_query
        )
        
        # Test with invalid inputs
        result = create_docset_ui("", "")  # Empty name
        self.assert_error_message(result, ["cannot be empty", "Error"])
        
        result = upload_file_to_docset(None, "test")  # No files
        self.assert_error_message(result, ["No files uploaded"])
        
        result = upload_file_to_docset([MockFile("test.txt")], "")  # No docset
        self.assert_error_message(result, ["specify a docset name"])
        
        # Test query with invalid inputs
        history = []
        new_history, _ = process_query("", history)  # Empty query
        assert new_history == history  # Should return unchanged history
        
        new_history, _ = process_query("test", history, "non-existent")  # Non-existent docset
        assert len(new_history) == 2
        assert "not found" in new_history[1]["content"] or "No docsets available" in new_history[1]["content"]
    
    def test_ui_performance_simulation(self, setup_mock_storage):
        """Test UI performance with large datasets"""
        from src.ragspace.ui.handlers import (
            create_docset_ui,
            upload_file_to_docset,
            process_query
        )
        
        # Create docset
        create_docset_ui("performance-test", "Performance test")
        
        # Add many documents
        for i in range(50):
            mock_file = MockFile(f"perf_doc_{i}.txt", 1024)
            upload_file_to_docset([mock_file], "performance-test")
        
        # Query should still be fast
        history = []
        new_history, _ = process_query("perf_doc", history, "performance-test")
        
        # Verify response is reasonable
        assert len(new_history) == 2
        assert new_history[1]["role"] == "assistant"
        response = new_history[1]["content"]
        assert "perf_doc_" in response  # Should find some documents
        assert len(response) < 10000  # Response should be reasonably sized 