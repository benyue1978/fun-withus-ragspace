"""
Crawler Interface for RAGSpace
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any


class ContentType(Enum):
    """Content types for crawled items"""
    FILE = "file"
    DOCUMENT = "document"
    CODE = "code"
    CONFIG = "config"
    README = "readme"
    WEBSITE = "website"
    REPOSITORY = "repository"


@dataclass
class CrawledItem:
    """Represents a crawled content item"""
    name: str
    content: str
    type: ContentType
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    children: Optional[List['CrawledItem']] = None


@dataclass
class CrawlResult:
    """Result of a crawling operation"""
    success: bool
    message: str
    root_item: Optional[CrawledItem] = None
    items: Optional[List[CrawledItem]] = None


class CrawlerInterface(ABC):
    """Abstract interface for web crawlers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.config = config or {}
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this crawler can handle the given URL"""
        pass
    
    @abstractmethod
    def crawl(self, url: str, **kwargs) -> CrawlResult:
        """Crawl the given URL and return results"""
        pass
    
    def get_supported_url_patterns(self) -> List[str]:
        """Get list of URL patterns this crawler supports"""
        return []
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information for this crawler"""
        return {
            "remaining": 1000,
            "limit": 1000,
            "reset_time": None
        }


class CrawlerRegistry:
    """Registry for managing crawlers"""
    
    def __init__(self):
        self.crawlers: List[CrawlerInterface] = []
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def register(self, crawler: CrawlerInterface):
        """Register a crawler"""
        self.crawlers.append(crawler)
        self.logger.info(f"Registered crawler: {crawler.__class__.__name__}")
    
    def get_crawler_for_url(self, url: str) -> Optional[CrawlerInterface]:
        """Get the appropriate crawler for a URL"""
        for crawler in self.crawlers:
            if crawler.can_handle(url):
                return crawler
        return None
    
    def get_all_crawlers(self) -> List[CrawlerInterface]:
        """Get all registered crawlers"""
        return self.crawlers.copy()


# Global crawler registry instance
crawler_registry = CrawlerRegistry() 