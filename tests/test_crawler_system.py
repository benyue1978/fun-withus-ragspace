"""
Test crawler system functionality
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import re

from src.ragspace.services.crawler import (
    CrawlerInterface,
    CrawlResult,
    CrawledItem,
    ContentType,
    CrawlerRegistry,
    GitHubCrawler,
    WebsiteCrawler
)


class TestCrawlerInterface:
    """Test the abstract crawler interface"""
    
    def test_crawler_interface_initialization(self):
        """Test crawler interface initialization"""
        # Create a real crawler instance to test
        crawler = GitHubCrawler()
        assert hasattr(crawler, 'config')
        assert hasattr(crawler, 'logger')
    
    def test_content_type_enum(self):
        """Test ContentType enum values"""
        assert ContentType.FILE.value == "file"
        assert ContentType.DOCUMENT.value == "document"
        assert ContentType.CODE.value == "code"
        assert ContentType.CONFIG.value == "config"
        assert ContentType.README.value == "readme"
        assert ContentType.WEBSITE.value == "website"
        assert ContentType.REPOSITORY.value == "repository"


class TestCrawledItem:
    """Test CrawledItem dataclass"""
    
    def test_crawled_item_creation(self):
        """Test CrawledItem creation"""
        item = CrawledItem(
            title="Test Document",
            content="This is test content",
            content_type=ContentType.DOCUMENTATION,
            url="https://example.com",
            metadata={"test": "data"}
        )
        
        assert item.title == "Test Document"
        assert item.content == "This is test content"
        assert item.content_type == ContentType.DOCUMENTATION
        assert item.url == "https://example.com"
        assert item.metadata["test"] == "data"
    
    def test_crawled_item_with_children(self):
        """Test CrawledItem with children"""
        child = CrawledItem(
            title="Child Document",
            content="Child content",
            content_type=ContentType.CODE,
            url="https://example.com/child"
        )
        
        parent = CrawledItem(
            title="Parent Document",
            content="Parent content",
            content_type=ContentType.REPOSITORY,
            children=[child]
        )
        
        assert parent.children is not None
        assert len(parent.children) == 1
        assert parent.children[0].title == "Child Document"


class TestCrawlResult:
    """Test CrawlResult dataclass"""
    
    def test_successful_crawl_result(self):
        """Test successful CrawlResult creation"""
        item = CrawledItem(
            title="Test Document",
            content="Test content",
            content_type=ContentType.DOCUMENTATION
        )
        
        result = CrawlResult(
            success=True,
            message="Successfully crawled",
            items=[item],
            metadata={"crawled_count": 1}
        )
        
        assert result.success is True
        assert result.message == "Successfully crawled"
        assert len(result.items) == 1
        assert result.items[0].title == "Test Document"
        assert result.metadata["crawled_count"] == 1
    
    def test_failed_crawl_result(self):
        """Test failed CrawlResult creation"""
        result = CrawlResult(
            success=False,
            message="Failed to crawl",
            items=[],
            metadata={"error": "test error"}
        )
        
        assert result.success is False
        assert result.message == "Failed to crawl"
        assert result.items == []
        assert result.metadata["error"] == "test error"


class TestCrawlerRegistry:
    """Test CrawlerRegistry functionality"""
    
    def test_crawler_registry_initialization(self):
        """Test crawler registry initialization"""
        registry = CrawlerRegistry()
        assert len(registry.crawlers) == 0
    
    def test_register_crawler(self):
        """Test registering a crawler"""
        registry = CrawlerRegistry()
        crawler = Mock(spec=CrawlerInterface)
        crawler.__class__.__name__ = "MockCrawler"
        
        registry.register(crawler)
        assert len(registry.crawlers) == 1
        assert registry.crawlers[0] == crawler
    
    def test_get_crawler_for_url(self):
        """Test getting appropriate crawler for URL"""
        registry = CrawlerRegistry()
        
        # Mock crawler that can handle GitHub URLs
        github_crawler = Mock(spec=CrawlerInterface)
        github_crawler.can_handle.return_value = True
        
        # Mock crawler that can't handle the URL
        other_crawler = Mock(spec=CrawlerInterface)
        other_crawler.can_handle.return_value = False
        
        registry.register(github_crawler)
        registry.register(other_crawler)
        
        result = registry.get_crawler_for_url("https://github.com/owner/repo")
        assert result == github_crawler
    
    def test_get_crawler_for_url_no_match(self):
        """Test getting crawler when no crawler can handle URL"""
        registry = CrawlerRegistry()
        
        crawler = Mock(spec=CrawlerInterface)
        crawler.can_handle.return_value = False
        registry.register(crawler)
        
        result = registry.get_crawler_for_url("https://unknown.com")
        assert result is None
    
    def test_get_all_crawlers(self):
        """Test getting all registered crawlers"""
        registry = CrawlerRegistry()
        
        crawler1 = Mock(spec=CrawlerInterface)
        crawler2 = Mock(spec=CrawlerInterface)
        
        registry.register(crawler1)
        registry.register(crawler2)
        
        all_crawlers = registry.get_all_crawlers()
        assert len(all_crawlers) == 2
        assert crawler1 in all_crawlers
        assert crawler2 in all_crawlers


class TestGitHubCrawler:
    """Test GitHub crawler functionality"""
    
    @pytest.fixture
    def github_crawler(self):
        """Create a GitHub crawler instance"""
        return GitHubCrawler()
    
    def test_github_crawler_initialization(self):
        """Test GitHub crawler initialization"""
        crawler = GitHubCrawler()
        assert crawler.base_url == "https://api.github.com"
        assert "Accept" in crawler.headers
        assert "User-Agent" in crawler.headers
    
    def test_can_handle_github_urls(self):
        """Test URL handling for GitHub URLs"""
        crawler = GitHubCrawler()
        
        # Test various GitHub URL formats
        assert crawler.can_handle("https://github.com/owner/repo")
        assert crawler.can_handle("github.com/owner/repo")
        assert crawler.can_handle("owner/repo")
        assert not crawler.can_handle("https://example.com")
        assert not crawler.can_handle("not-a-url")
    
    def test_preprocess_url(self):
        """Test URL preprocessing"""
        crawler = GitHubCrawler()
        
        assert crawler.preprocess_url("https://github.com/owner/repo") == "https://github.com/owner/repo"
        assert crawler.preprocess_url("github.com/owner/repo") == "https://github.com/owner/repo"
        assert crawler.preprocess_url("owner/repo") == "https://github.com/owner/repo"
    
    def test_parse_repo_url(self):
        """Test repository URL parsing"""
        crawler = GitHubCrawler()
        
        owner, repo = crawler.parse_repo_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"
        
        owner, repo = crawler.parse_repo_url("owner/repo")
        assert owner == "owner"
        assert repo == "repo"
    
    def test_parse_repo_url_invalid(self):
        """Test invalid repository URL parsing"""
        crawler = GitHubCrawler()
        
        with pytest.raises(ValueError):
            crawler.parse_repo_url("invalid-url")
        
        with pytest.raises(ValueError):
            crawler.parse_repo_url("https://github.com/owner")
    
    def test_determine_content_type(self):
        """Test content type determination"""
        crawler = GitHubCrawler()
        
        # Test different file types
        assert crawler.determine_content_type("README.md") == ContentType.DOCUMENTATION
        assert crawler.determine_content_type("main.py") == ContentType.CODE
        assert crawler.determine_content_type("config.json") == ContentType.CONFIGURATION
        assert crawler.determine_content_type("data.csv") == ContentType.DATA
        assert crawler.determine_content_type("image.png") == ContentType.IMAGE
        assert crawler.determine_content_type("unknown.xyz") == ContentType.UNKNOWN
    
    @patch('src.ragspace.services.crawler.github_crawler.requests.get')
    def test_get_rate_limit_info(self, mock_get):
        """Test rate limit info retrieval"""
        crawler = GitHubCrawler()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "resources": {
                "core": {
                    "limit": 5000,
                    "remaining": 4999,
                    "reset": 1234567890,
                    "used": 1
                }
            }
        }
        mock_get.return_value = mock_response
        
        result = crawler.get_rate_limit_info()
        assert "limit" in result
        assert "remaining" in result
        assert "reset" in result
        assert "used" in result
        assert result["limit"] == 5000
        assert result["remaining"] == 4999
    
    @patch('src.ragspace.services.crawler.github_crawler.requests.get')
    def test_get_rate_limit_info_error(self, mock_get):
        """Test rate limit info error handling"""
        crawler = GitHubCrawler()
        
        # Mock failed response
        mock_get.side_effect = Exception("Network error")
        
        result = crawler.get_rate_limit_info()
        assert result == {}  # Should return empty dict on error
    
    def test_convert_wildcard_to_regex(self):
        """Test wildcard pattern conversion to regex"""
        crawler = GitHubCrawler()
        
        # Test various wildcard patterns
        test_cases = [
            ("*.pyc", r".*\.pyc"),
            ("*.log", r".*\.log"),
            ("*.py", r".*\.py"),
            ("node_modules", "node_modules"),
            (".git", r"\.git"),
            ("__pycache__", r"__pycache__"),
            ("*.txt", r".*\.txt"),
            ("test?.py", r"test.\.py"),
        ]
        
        for wildcard, expected_regex in test_cases:
            result = crawler._convert_wildcard_to_regex(wildcard)
            assert result == expected_regex, f"Failed for {wildcard}: expected {expected_regex}, got {result}"
    
    def test_should_skip_item_with_wildcards(self):
        """Test should_skip_item with wildcard patterns"""
        crawler = GitHubCrawler()
        
        # Test items that should be skipped
        skip_items = [
            ("test.pyc", ["*.pyc"]),
            ("app.log", ["*.log"]),
            ("node_modules", ["node_modules"]),
            ("__pycache__", ["__pycache__"]),
            ("test.py", ["*.py"]),
        ]
        
        for item_name, patterns in skip_items:
            item = CrawledItem(
                title=item_name,
                content="test content",
                content_type=ContentType.CODE
            )
            
            # Temporarily set config for testing
            original_config = crawler.config
            crawler.config = {"skip_patterns": patterns}
            
            try:
                result = crawler.should_skip_item(item)
                assert result is True, f"Item {item_name} should be skipped with patterns {patterns}"
            finally:
                crawler.config = original_config
    
    def test_should_skip_item_with_invalid_regex(self):
        """Test should_skip_item handles invalid regex patterns gracefully"""
        crawler = GitHubCrawler()
        
        item = CrawledItem(
            title="test.py",
            content="test content",
            content_type=ContentType.CODE,
            metadata={}  # Add empty metadata to avoid None error
        )
        
        # Test with invalid regex pattern
        crawler.config = {"skip_patterns": ["[invalid-regex"]}
        
        # Should not raise an exception, should handle gracefully
        result = crawler.should_skip_item(item)
        # Should return False since the pattern is invalid
        assert result is False
    
    def test_wildcard_patterns_should_not_cause_regex_error(self):
        """Test that wildcard patterns like *.pyc don't cause regex errors"""
        crawler = GitHubCrawler()
        
        item = CrawledItem(
            title="test.pyc",
            content="test content",
            content_type=ContentType.CODE,
            metadata={}
        )
        
        # Test with wildcard patterns that used to cause regex errors
        wildcard_patterns = ["*.pyc", "*.log", "*.py", "test?.py"]
        
        for pattern in wildcard_patterns:
            crawler.config = {"skip_patterns": [pattern]}
            
            # This should not raise a regex error
            try:
                result = crawler.should_skip_item(item)
                # Should handle gracefully without exceptions
                assert isinstance(result, bool)
            except re.error as e:
                pytest.fail(f"Wildcard pattern '{pattern}' caused regex error: {e}")
            except Exception as e:
                pytest.fail(f"Wildcard pattern '{pattern}' caused unexpected error: {e}")
    
    @patch('src.ragspace.services.crawler.github_crawler.requests.get')
    def test_different_repos_same_filename_no_conflict(self, mock_get):
        """Test that documents from different repositories with same filename don't conflict"""
        crawler = GitHubCrawler()
        
        # Mock GitHub API responses for two different repositories
        mock_responses = [
            # First repo: owner1/repo1
            Mock(
                status_code=200,
                json=lambda: [
                    {
                        "name": "README.md",
                        "path": "README.md",
                        "type": "file",
                        "download_url": "https://raw.githubusercontent.com/owner1/repo1/main/README.md",
                        "url": "https://api.github.com/repos/owner1/repo1/contents/README.md",
                        "size": 100
                    }
                ]
            ),
            # File content for first repo
            Mock(
                status_code=200,
                text="Content from owner1/repo1 README"
            ),
            # Second repo: owner2/repo2  
            Mock(
                status_code=200,
                json=lambda: [
                    {
                        "name": "README.md",
                        "path": "README.md",
                        "type": "file",
                        "download_url": "https://raw.githubusercontent.com/owner2/repo2/main/README.md",
                        "url": "https://api.github.com/repos/owner2/repo2/contents/README.md",
                        "size": 100
                    }
                ]
            ),
            # File content for second repo
            Mock(
                status_code=200,
                text="Content from owner2/repo2 README"
            )
        ]
        
        mock_get.side_effect = mock_responses
        
        # Crawl first repository
        result1 = crawler.crawl("owner1/repo1")
        assert result1.success is True
        assert len(result1.items) == 1
        assert result1.items[0].title == "owner1/repo1/README.md"
        
        # Crawl second repository
        result2 = crawler.crawl("owner2/repo2")
        assert result2.success is True
        assert len(result2.items) == 1
        assert result2.items[0].title == "owner2/repo2/README.md"
        
        # Verify that the titles are different even though both files are named README.md
        assert result1.items[0].title != result2.items[0].title
        assert result1.items[0].title == "owner1/repo1/README.md"
        assert result2.items[0].title == "owner2/repo2/README.md"


class TestWebsiteCrawler:
    """Test Website crawler functionality"""
    
    @pytest.fixture
    def website_crawler(self):
        """Create a website crawler instance"""
        return WebsiteCrawler()
    
    def test_website_crawler_initialization(self):
        """Test website crawler initialization"""
        crawler = WebsiteCrawler()
        assert crawler.config is not None
        assert "max_depth" in crawler.config
    
    def test_can_handle_website_urls(self):
        """Test URL handling for website URLs"""
        crawler = WebsiteCrawler()
        
        assert crawler.can_handle("https://example.com")
        assert crawler.can_handle("http://example.com")
        assert crawler.can_handle("https://www.example.com/path")
        assert not crawler.can_handle("github.com/owner/repo")
        assert not crawler.can_handle("not-a-url")
    
    def test_get_supported_url_patterns(self):
        """Test supported URL patterns"""
        crawler = WebsiteCrawler()
        patterns = crawler.get_supported_url_patterns()
        
        assert "http://" in patterns
        assert "https://" in patterns
    
    def test_should_skip_item(self):
        """Test should_skip_item functionality"""
        crawler = WebsiteCrawler()
        
        # Test normal item (should not skip)
        normal_item = CrawledItem(
            title="normal.html",
            content="Normal content",
            content_type=ContentType.WEBSITE
        )
        assert not crawler.should_skip_item(normal_item)
        
        # Test large item (should skip) - create content larger than 50000 chars
        large_content = "Large content " * 4000  # 15 * 4000 = 60000 chars
        large_item = CrawledItem(
            title="large.html",
            content=large_content,
            content_type=ContentType.WEBSITE
        )
        assert crawler.should_skip_item(large_item)
    
    def test_get_rate_limit_info(self):
        """Test rate limit info for website crawler"""
        crawler = WebsiteCrawler()
        result = crawler.get_rate_limit_info()
        
        assert "crawler" in result
        assert "status" in result
        assert "max_pages" in result
        assert "max_depth" in result
        assert result["crawler"] == "website"
        assert result["status"] == "no_rate_limit"


class TestCrawlerIntegration:
    """Integration tests for crawler system"""
    
    def test_crawler_registry_with_real_crawlers(self):
        """Test crawler registry with actual crawler implementations"""
        from src.ragspace.services import crawler_registry, register_default_crawlers
        
        # Register default crawlers
        register_default_crawlers()
        
        # Test GitHub crawler registration
        github_crawler = crawler_registry.get_crawler_for_url("https://github.com/owner/repo")
        assert github_crawler is not None
        assert isinstance(github_crawler, GitHubCrawler)
        
        # Test website crawler registration
        website_crawler = crawler_registry.get_crawler_for_url("https://example.com")
        assert website_crawler is not None
        assert isinstance(website_crawler, WebsiteCrawler)
        
        # Test unknown URL
        unknown_crawler = crawler_registry.get_crawler_for_url("ftp://example.com")
        assert unknown_crawler is None
    
    def test_crawler_configuration(self):
        """Test crawler configuration"""
        config = {
            "max_depth": 2,
            "file_types": [".md", ".txt"],
            "skip_patterns": ["node_modules"]
        }
        
        github_crawler = GitHubCrawler(config)
        assert github_crawler.config["max_depth"] == 10
        assert ".md" in github_crawler.config["file_types"]
        assert "node_modules" in github_crawler.config["skip_patterns"]
    
    def test_crawler_error_handling(self):
        """Test crawler error handling"""
        crawler = GitHubCrawler()
        
        # Test with invalid URL
        result = crawler.crawl("invalid-url")
        assert result.success is False
        assert "Failed to crawl" in result.message 