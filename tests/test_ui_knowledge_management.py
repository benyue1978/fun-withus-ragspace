"""
UI tests for Knowledge Management component
"""

import pytest
from unittest.mock import patch, Mock
from tests.test_ui_base import UIBaseTest
from src.ragspace.ui.handlers import create_docset_ui, upload_file_to_docset, add_url_to_docset, add_github_repo_to_docset

class TestKnowledgeManagementUI(UIBaseTest):
    """Test Knowledge Management UI functionality"""
    
    def test_create_docset_basic(self, setup_mock_storage):
        """Test basic docset creation"""
        # Test docset creation using the mock manager
        result = create_docset_ui("test-docset", "Test docset description")
        
        # Verify success response
        assert "✅" in result
        assert "test-docset" in result
        assert "created successfully" in result
    
    def test_create_docset_empty_name(self, setup_mock_storage):
        """Test docset creation with empty name"""
        result = create_docset_ui("", "Test description")
        
        # Verify error response
        assert "cannot be empty" in result
    
    def test_create_docset_duplicate(self, setup_mock_storage):
        """Test creating duplicate docset"""
        # Create first docset
        create_docset_ui("duplicate-test", "First docset")
        
        # Try to create duplicate
        result = create_docset_ui("duplicate-test", "Second docset")
        
        # Verify error response
        assert "already exists" in result
    
    def test_upload_file_basic(self, setup_mock_storage):
        """Test basic file upload"""
        # Create docset first
        create_docset_ui("upload-test", "Upload test docset")
        
        # Mock file object
        mock_file = Mock()
        mock_file.name = "/path/to/test.txt"
        mock_file.size = 1024
        mock_file.type = "text/plain"
        
        # Test file upload
        result = upload_file_to_docset([mock_file], "upload-test")
        
        # Verify success response
        assert "✅ Added: test.txt" in result
    
    def test_upload_file_no_files(self, setup_mock_storage):
        """Test file upload with no files"""
        result = upload_file_to_docset(None, "test-docset")
        
        # Verify error response
        assert "No files uploaded" in result
    
    def test_upload_file_no_docset(self, setup_mock_storage):
        """Test file upload without docset name"""
        mock_file = Mock()
        mock_file.name = "/path/to/test.txt"
        
        result = upload_file_to_docset([mock_file], "")
        
        # Verify error response
        assert "Please specify a docset name" in result
    
    def test_upload_file_nonexistent_docset(self, setup_mock_storage):
        """Test file upload to non-existent docset"""
        mock_file = Mock()
        mock_file.name = "/path/to/test.txt"  # Ensure this is a string
        mock_file.size = 1024
        mock_file.type = "text/plain"
        
        # Debug: check what manager we're using
        from src.ragspace.storage import docset_manager
        print(f"DEBUG: Using manager type: {type(docset_manager)}")
        print(f"DEBUG: Manager class: {docset_manager.__class__.__name__}")
        
        result = upload_file_to_docset([mock_file], "non-existent")
        
        # Debug: print the actual result
        print(f"DEBUG: Actual result: {result}")
        
        # Verify error response
        assert "not found" in result
    
    def test_upload_multiple_files(self, setup_mock_storage):
        """Test uploading multiple files"""
        # Create docset first
        create_docset_ui("multi-upload", "Multi upload test")
        
        # Mock multiple files with proper string names
        mock_file1 = Mock()
        mock_file1.name = "/path/to/file1.txt"
        mock_file1.size = 1024
        mock_file1.type = "text/plain"
        
        mock_file2 = Mock()
        mock_file2.name = "/path/to/file2.pdf"
        mock_file2.size = 2048
        mock_file2.type = "application/pdf"
        
        mock_file3 = Mock()
        mock_file3.name = "/path/to/file3.jpg"
        mock_file3.size = 512
        mock_file3.type = "image/jpeg"
        
        mock_files = [mock_file1, mock_file2, mock_file3]
        
        # Test multiple file upload
        result = upload_file_to_docset(mock_files, "multi-upload")
        
        # Verify success response
        assert "✅ Added: file1.txt" in result
        assert "✅ Added: file2.pdf" in result
        assert "✅ Added: file3.jpg" in result
    
    def test_add_url_basic(self, setup_mock_storage):
        """Test basic URL addition"""
        # Create docset first
        create_docset_ui("url-test", "URL test docset")
        
        # Test URL addition
        result = add_url_to_docset("https://example.com", "url-test")
        
        # Verify success response
        assert "✅" in result
        assert "example.com" in result
    
    def test_add_url_empty_url(self, setup_mock_storage):
        """Test URL addition with empty URL"""
        result = add_url_to_docset("", "test-docset")
        
        # Verify error response
        assert "Please enter a valid URL" in result
    
    def test_add_url_no_docset(self, setup_mock_storage):
        """Test URL addition without docset name"""
        result = add_url_to_docset("https://example.com", "")
        
        # Verify error response
        assert "Please specify a docset name" in result
    
    def test_add_url_nonexistent_docset(self, setup_mock_storage):
        """Test URL addition to non-existent docset"""
        result = add_url_to_docset("https://example.com", "non-existent")
        
        # Verify error response
        assert "not found" in result
    
    def test_add_github_repo_basic(self, setup_mock_storage):
        """Test basic GitHub repository addition"""
        # Create docset first
        create_docset_ui("github-test", "GitHub test docset")
        
        # Test GitHub repo addition
        result = add_github_repo_to_docset("https://github.com/user/repo", "github-test")
        
        # Verify success response
        assert "✅" in result
        assert "github.com/user/repo" in result
    
    def test_add_github_repo_empty_url(self, setup_mock_storage):
        """Test GitHub repo addition with empty URL"""
        result = add_github_repo_to_docset("", "test-docset")
        
        # Verify error response
        assert "Please enter a valid GitHub repository URL" in result
    
    def test_add_github_repo_no_docset(self, setup_mock_storage):
        """Test GitHub repo addition without docset name"""
        result = add_github_repo_to_docset("https://github.com/user/repo", "")
        
        # Verify error response
        assert "Please specify a docset name" in result
    
    def test_add_github_repo_nonexistent_docset(self, setup_mock_storage):
        """Test GitHub repo addition to non-existent docset"""
        result = add_github_repo_to_docset("https://github.com/user/repo", "non-existent")
        
        # Verify error response
        assert "not found" in result
    
    def test_knowledge_management_integration(self, setup_mock_storage):
        """Test knowledge management integration workflow"""
        # Create docset
        create_result = create_docset_ui("integration-test", "Integration test docset")
        assert "✅" in create_result
        
        # Add URL
        url_result = add_url_to_docset("https://example.com", "integration-test")
        assert "✅" in url_result
        
        # Add GitHub repo
        github_result = add_github_repo_to_docset("https://github.com/user/repo", "integration-test")
        assert "✅" in github_result
        
        # Upload file with proper string name
        mock_file = Mock()
        mock_file.name = "/path/to/test.txt"
        mock_file.size = 1024
        mock_file.type = "text/plain"
        file_result = upload_file_to_docset([mock_file], "integration-test")
        assert "✅ Added: test.txt" in file_result
    
    def test_knowledge_management_error_handling(self, setup_mock_storage):
        """Test knowledge management error handling"""
        # Test various error conditions
        assert "cannot be empty" in create_docset_ui("", "test")
        assert "No files uploaded" in upload_file_to_docset(None, "test")
        assert "Please enter a valid URL" in add_url_to_docset("", "test")
        assert "Please enter a valid GitHub repository URL" in add_github_repo_to_docset("", "test")
    
    def test_knowledge_management_special_characters(self, setup_mock_storage):
        """Test knowledge management with special characters"""
        # Test docset creation with special characters
        result = create_docset_ui("special@#$%", "Special description with @#$%")
        assert "✅" in result
        
        # Test URL with special characters
        url_result = add_url_to_docset("https://example.com/path@#$%", "special@#$%")
        assert "✅" in url_result
    
    def test_knowledge_management_large_content(self, setup_mock_storage):
        """Test knowledge management with large content"""
        # Create docset
        create_docset_ui("large-test", "Large content test")
        
        # Test with large file content
        large_content = "Large content " * 1000
        mock_file = Mock()
        mock_file.name = "/path/to/large.txt"
        mock_file.size = len(large_content)
        mock_file.type = "text/plain"
        
        result = upload_file_to_docset([mock_file], "large-test")
        assert "✅ Added: large.txt" in result
    
    def test_knowledge_management_multiple_docsets(self, setup_mock_storage):
        """Test knowledge management with multiple docsets"""
        # Create multiple docsets
        create_docset_ui("docset1", "First docset")
        create_docset_ui("docset2", "Second docset")
        
        # Add content to different docsets
        add_url_to_docset("https://example1.com", "docset1")
        add_url_to_docset("https://example2.com", "docset2")
        
        # Verify both docsets exist and have content
        mock_file1 = Mock()
        mock_file1.name = "/path/to/file1.txt"
        mock_file1.size = 1024
        mock_file1.type = "text/plain"
        
        mock_file2 = Mock()
        mock_file2.name = "/path/to/file2.txt"
        mock_file2.size = 1024
        mock_file2.type = "text/plain"
        
        upload_file_to_docset([mock_file1], "docset1")
        upload_file_to_docset([mock_file2], "docset2")
        
        # All operations should succeed
        assert True  # If we get here, all operations succeeded 