"""
Tests for the crawler system
"""

import pytest
from unittest.mock import Mock, patch
from src.ragspace.services.crawler_interface import (
    CrawlerInterface, CrawlResult, CrawledItem, ContentType, CrawlerRegistry
)
from src.ragspace.services.github_crawler import GitHubCrawler
from src.ragspace.services.website_crawler import WebsiteCrawler


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
        """Test creating a CrawledItem"""
        item = CrawledItem(
            name="test.txt",
            content="Test content",
            type=ContentType.FILE,
            url="https://example.com/test.txt",
            metadata={"size": 100}
        )
        
        assert item.name == "test.txt"
        assert item.content == "Test content"
        assert item.type == ContentType.FILE
        assert item.url == "https://example.com/test.txt"
        assert item.metadata["size"] == 100
        assert item.children is None
    
    def test_crawled_item_with_children(self):
        """Test CrawledItem with children"""
        child = CrawledItem(
            name="child.txt",
            content="Child content",
            type=ContentType.FILE
        )
        
        parent = CrawledItem(
            name="parent",
            content="Parent content",
            type=ContentType.REPOSITORY,
            children=[child]
        )
        
        assert len(parent.children) == 1
        assert parent.children[0].name == "child.txt"


class TestCrawlResult:
    """Test CrawlResult dataclass"""
    
    def test_successful_crawl_result(self):
        """Test successful CrawlResult"""
        item = CrawledItem(
            name="test.txt",
            content="Test content",
            type=ContentType.FILE
        )
        
        result = CrawlResult(
            success=True,
            message="Successfully crawled",
            root_item=item,
            items=[item]
        )
        
        assert result.success is True
        assert result.message == "Successfully crawled"
        assert result.root_item == item
        assert result.items == [item]
    
    def test_failed_crawl_result(self):
        """Test failed CrawlResult"""
        result = CrawlResult(
            success=False,
            message="Failed to crawl"
        )
        
        assert result.success is False
        assert result.message == "Failed to crawl"
        assert result.root_item is None
        assert result.items is None


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
        
        assert crawler.determine_content_type("README.md") == ContentType.DOCUMENT
        assert crawler.determine_content_type("main.py") == ContentType.CODE
        assert crawler.determine_content_type("config.json") == ContentType.CONFIG
        assert crawler.determine_content_type("document.txt") == ContentType.DOCUMENT
        assert crawler.determine_content_type("unknown.xyz") == ContentType.FILE
    
    @patch('src.ragspace.services.github_crawler.requests.get')
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
                    "reset": 1234567890
                }
            }
        }
        mock_get.return_value = mock_response
        
        result = crawler.get_rate_limit_info()
        assert "resources" in result
        assert result["resources"]["core"]["limit"] == 5000
    
    @patch('src.ragspace.services.github_crawler.requests.get')
    def test_get_rate_limit_info_error(self, mock_get):
        """Test rate limit info error handling"""
        crawler = GitHubCrawler()
        
        # Mock failed response
        mock_get.side_effect = Exception("Network error")
        
        result = crawler.get_rate_limit_info()
        assert "error" in result
        assert "Network error" in result["error"]


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
        """Test item skipping logic"""
        crawler = WebsiteCrawler()
        
        # Test large content
        large_item = CrawledItem(
            name="large.txt",
            content="x" * 100000,  # 100KB
            type=ContentType.DOCUMENT
        )
        assert crawler.should_skip_item(large_item)
        
        # Test normal content
        normal_item = CrawledItem(
            name="normal.txt",
            content="Normal content",
            type=ContentType.DOCUMENT
        )
        assert not crawler.should_skip_item(normal_item)
    
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