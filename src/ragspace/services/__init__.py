"""
Services package for RAGSpace
"""

from .github_service import GitHubService

# Import crawler system components
from .crawler_interface import CrawlerInterface, CrawlResult, CrawledItem, ContentType, CrawlerRegistry, crawler_registry
from .github_crawler import GitHubCrawler
from .website_crawler import WebsiteCrawler
from .mock_crawler import MockCrawler

# Import RAG system components
from .text_splitter import RAGTextSplitter, ChunkConfig
from .embedding_worker import EmbeddingWorker
from .rag_retriever import RAGRetriever
from .rag_response_generator import RAGResponseGenerator
from .rag_manager import RAGManager

# Register default crawlers
# Note: Crawlers are registered lazily to ensure environment variables are loaded
def register_default_crawlers():
    """Register default crawlers with proper environment variable loading"""
    if not crawler_registry.crawlers:  # Only register if not already registered
        crawler_registry.register(GitHubCrawler())
        crawler_registry.register(WebsiteCrawler())

__all__ = [
    "GitHubService",
    "CrawlerInterface",
    "CrawlResult", 
    "CrawledItem",
    "ContentType",
    "CrawlerRegistry",
    "crawler_registry",
    "GitHubCrawler",
    "WebsiteCrawler",
    "MockCrawler",
    "register_default_crawlers",
    # RAG Components
    "RAGTextSplitter",
    "ChunkConfig",
    "EmbeddingWorker",
    "RAGRetriever",
    "RAGResponseGenerator",
    "RAGManager"
] 