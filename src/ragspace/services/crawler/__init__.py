"""
Crawler Services Module

This module contains all crawler-related services for RAGSpace.
"""

from .crawler_interface import CrawlerInterface, CrawlResult, CrawledItem, ContentType, CrawlerRegistry, crawler_registry
from .github_crawler import GitHubCrawler
from .website_crawler import WebsiteCrawler
from .mock_crawler import MockCrawler
from .github_service import GitHubService

# Register default crawlers
def register_default_crawlers():
    """Register default crawlers with proper environment variable loading"""
    if not crawler_registry.crawlers:  # Only register if not already registered
        crawler_registry.register(GitHubCrawler())
        crawler_registry.register(WebsiteCrawler())

__all__ = [
    'CrawlerInterface',
    'CrawlResult', 
    'CrawledItem',
    'ContentType',
    'CrawlerRegistry',
    'crawler_registry',
    'GitHubCrawler',
    'WebsiteCrawler',
    'MockCrawler',
    'GitHubService',
    'register_default_crawlers'
]
