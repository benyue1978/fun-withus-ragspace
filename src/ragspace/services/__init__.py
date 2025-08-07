"""
Services Module

This module contains all services for RAGSpace, organized by functionality.
"""

# Import crawler services
from .crawler import (
    CrawlerInterface,
    CrawlResult,
    CrawledItem, 
    ContentType,
    CrawlerRegistry,
    crawler_registry,
    GitHubCrawler,
    WebsiteCrawler,
    MockCrawler,
    GitHubService,
    register_default_crawlers
)

# Import RAG services
from .rag import (
    RAGManager,
    RAGRetriever,
    RAGResponseGenerator,
    EmbeddingWorker,
    RAGTextSplitter
)

__all__ = [
    # Crawler services
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
    'register_default_crawlers',
    
    # RAG services
    'RAGManager',
    'RAGRetriever',
    'RAGResponseGenerator',
    'EmbeddingWorker',
    'RAGTextSplitter'
] 