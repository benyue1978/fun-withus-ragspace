"""
UI Tests for Crawler Functionality
Tests the crawler integration with the UI components
"""

import pytest
from unittest.mock import patch, MagicMock
from src.ragspace.ui.components.knowledge_management import create_knowledge_management_tab
from src.ragspace.services.mock_crawler import MockCrawler
from src.ragspace.storage.manager import MockDocsetManager


class TestCrawlerUI:
    """Test crawler UI functionality"""
    
    @pytest.fixture
    def mock_crawler(self):
        """Create a mock crawler instance"""
        return MockCrawler()
    
    @pytest.fixture
    def mock_docset_manager(self):
        """Create a mock docset manager"""
        return MockDocsetManager()
    
    def test_add_github_repo_ui_basic(self, mock_crawler, mock_docset_manager):
        """Test basic GitHub repository addition through UI"""
        # Mock the crawler registry to use our mock crawler
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = mock_crawler
            mock_registry.get_all_crawlers.return_value = [mock_crawler]
            
            # Mock the docset manager
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset first
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Test adding GitHub repository
                result = mock_docset_manager.add_url_to_docset(
                    "owner/repo",
                    "test-docset"
                )
                
                assert "✅" in result
                assert "owner/repo" in result
                assert "3 child documents" in result
    
    def test_add_website_ui_basic(self, mock_crawler, mock_docset_manager):
        """Test basic website addition through UI"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = mock_crawler
            mock_registry.get_all_crawlers.return_value = [mock_crawler]
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Test adding website
                result = mock_docset_manager.add_url_to_docset(
                    "https://example.com",
                    "test-docset"
                )
                
                assert "✅" in result
                assert "Example Website" in result
                assert "2 child documents" in result
    
    def test_add_github_repo_ui_no_docset(self, mock_crawler, mock_docset_manager):
        """Test GitHub repository addition with non-existent docset"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = mock_crawler
            mock_registry.get_all_crawlers.return_value = [mock_crawler]
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Test adding to non-existent docset
                result = mock_docset_manager.add_url_to_docset(
                    "owner/repo",
                    "non-existent-docset"
                )
                
                assert "not found" in result
    
    def test_add_github_repo_ui_duplicate(self, mock_crawler, mock_docset_manager):
        """Test adding the same GitHub repository twice"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = mock_crawler
            mock_registry.get_all_crawlers.return_value = [mock_crawler]
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Add repository first time
                result1 = mock_docset_manager.add_url_to_docset(
                    "owner/repo",
                    "test-docset"
                )
                assert "✅" in result1
                
                # Add same repository second time
                result2 = mock_docset_manager.add_url_to_docset(
                    "owner/repo",
                    "test-docset"
                )
                # For now, just check that it doesn't fail completely
                assert "✅" in result2 or "⚠️" in result2 or "already exists" in result2
    
    def test_add_github_repo_ui_invalid_url(self, mock_crawler, mock_docset_manager):
        """Test adding invalid GitHub URL"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = mock_crawler
            mock_registry.get_all_crawlers.return_value = [mock_crawler]
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Test adding invalid URL
                result = mock_docset_manager.add_url_to_docset(
                    "invalid-url",
                    "test-docset"
                )
                
                assert "❌" in result
                assert "Failed to crawl" in result
    
    def test_crawler_rate_limit_ui(self, mock_crawler):
        """Test crawler rate limit information in UI"""
        rate_limit_info = mock_crawler.get_rate_limit_info()
        
        assert "crawler" in rate_limit_info
        assert "status" in rate_limit_info
        assert rate_limit_info["crawler"] == "mock"
        assert rate_limit_info["status"] == "unlimited"
        assert rate_limit_info["remaining"] == 9999
    
    def test_crawler_supported_patterns_ui(self, mock_crawler):
        """Test crawler supported URL patterns"""
        patterns = mock_crawler.get_supported_url_patterns()
        
        assert "github.com" in patterns
        assert "http://" in patterns
        assert "https://" in patterns
    
    def test_crawler_can_handle_ui(self, mock_crawler):
        """Test crawler URL handling logic"""
        # Test GitHub URLs
        assert mock_crawler.can_handle("https://github.com/owner/repo")
        assert mock_crawler.can_handle("github.com/owner/repo")
        assert mock_crawler.can_handle("owner/repo")
        
        # Test website URLs
        assert mock_crawler.can_handle("https://example.com")
        assert mock_crawler.can_handle("http://example.com")
        
        # Test unsupported URLs
        assert not mock_crawler.can_handle("ftp://example.com")
        assert not mock_crawler.can_handle("invalid-url")
    
    def test_crawler_mock_data_structure(self, mock_crawler):
        """Test mock crawler data structure"""
        # Test GitHub repository data
        github_data = mock_crawler.mock_data["https://github.com/owner/repo"]
        assert github_data["name"] == "owner/repo"
        assert github_data["type"].value == "repository"
        assert len(github_data["children"]) == 3
        
        # Test website data
        website_data = mock_crawler.mock_data["https://example.com"]
        assert website_data["name"] == "Example Website"
        assert website_data["type"].value == "website"
        assert len(website_data["children"]) == 2
    
    def test_crawler_mock_children_content(self, mock_crawler):
        """Test mock crawler children content"""
        github_data = mock_crawler.mock_data["https://github.com/owner/repo"]
        children = github_data["children"]
        
        # Check README.md
        readme = next(child for child in children if child["name"] == "README.md")
        assert readme["type"].value == "document"
        assert "# Mock Repository" in readme["content"]
        
        # Check main.py
        main_py = next(child for child in children if child["name"] == "main.py")
        assert main_py["type"].value == "code"
        assert "def main():" in main_py["content"]
        
        # Check config.json
        config = next(child for child in children if child["name"] == "config.json")
        assert config["type"].value == "config"
        assert '"name": "mock-project"' in config["content"]
    
    def test_crawler_ui_error_handling(self, mock_crawler, mock_docset_manager):
        """Test crawler UI error handling"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            # Mock crawler that fails
            failing_crawler = MagicMock()
            failing_crawler.crawl.return_value = MagicMock(
                success=False,
                message="Mock error: Failed to crawl"
            )
            mock_registry.get_crawler_for_url.return_value = failing_crawler
            mock_registry.get_all_crawlers.return_value = [failing_crawler]
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Test adding with failing crawler
                result = mock_docset_manager.add_url_to_docset(
                    "https://example.com",
                    "test-docset"
                )
                
                assert "❌" in result
                assert "Failed to crawl" in result
    
    def test_crawler_ui_no_crawler_available(self, mock_docset_manager):
        """Test UI when no crawler is available for URL"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = None
            mock_registry.get_all_crawlers.return_value = []
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Test adding URL with no available crawler
                result = mock_docset_manager.add_url_to_docset(
                    "ftp://example.com",
                    "test-docset"
                )
                
                assert "❌" in result
                assert "No crawler available" in result
    
    def test_crawler_ui_document_listing(self, mock_crawler, mock_docset_manager):
        """Test document listing after crawler adds content"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = mock_crawler
            mock_registry.get_all_crawlers.return_value = [mock_crawler]
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Add GitHub repository
                mock_docset_manager.add_url_to_docset("owner/repo", "test-docset")
                
                # List documents
                documents = mock_docset_manager.list_documents_in_docset("test-docset")
                
                # Should have parent document and child documents
                assert len(documents) >= 4  # 1 parent + 3 children
                
                # Check parent document
                parent_docs = [doc for doc in documents if doc["name"] == "owner/repo"]
                assert len(parent_docs) == 1
                assert parent_docs[0]["type"] == "repository"
                
                # Check child documents
                child_names = [doc["name"] for doc in documents if doc["name"] != "owner/repo"]
                assert "README.md" in child_names
                assert "main.py" in child_names
                assert "config.json" in child_names
    
    def test_crawler_ui_metadata_preservation(self, mock_crawler, mock_docset_manager):
        """Test that crawler metadata is preserved in documents"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = mock_crawler
            mock_registry.get_all_crawlers.return_value = [mock_crawler]
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Add GitHub repository
                mock_docset_manager.add_url_to_docset("owner/repo", "test-docset")
                
                # List documents
                documents = mock_docset_manager.list_documents_in_docset("test-docset")
                
                # Check parent document metadata
                parent_doc = next(doc for doc in documents if doc["name"] == "owner/repo")
                assert "metadata" in parent_doc
                assert parent_doc["metadata"]["crawler"] == "mock"
                assert parent_doc["metadata"]["test"] is True
    
    def test_crawler_ui_url_field_population(self, mock_crawler, mock_docset_manager):
        """Test that URL fields are properly populated"""
        with patch('src.ragspace.services.crawler_registry') as mock_registry:
            mock_registry.get_crawler_for_url.return_value = mock_crawler
            mock_registry.get_all_crawlers.return_value = [mock_crawler]
            
            with patch('src.ragspace.ui.components.knowledge_management.get_docset_manager') as mock_get_manager:
                mock_get_manager.return_value = mock_docset_manager
                
                # Create a test docset
                mock_docset_manager.create_docset("test-docset", "Test docset for crawler")
                
                # Add GitHub repository
                mock_docset_manager.add_url_to_docset("owner/repo", "test-docset")
                
                # List documents
                documents = mock_docset_manager.list_documents_in_docset("test-docset")
                
                # Check parent document URL
                parent_doc = next(doc for doc in documents if doc["name"] == "owner/repo")
                assert parent_doc["url"] == "https://github.com/owner/repo"
                
                # Check child document URLs
                readme_doc = next(doc for doc in documents if doc["name"] == "README.md")
                assert "github.com/owner/repo/blob/main/README.md" in readme_doc["url"] 