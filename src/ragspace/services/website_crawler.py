"""
Website Crawler Implementation
Implements the CrawlerInterface for general websites
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Any
import logging
import re

from .crawler_interface import (
    CrawlerInterface, CrawlResult, CrawledItem, ContentType
)

logger = logging.getLogger(__name__)

class WebsiteCrawler(CrawlerInterface):
    """General website crawler implementation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize website crawler"""
        super().__init__(config)
        
        # Default configuration
        self.config.setdefault("max_depth", 2)
        self.config.setdefault("max_pages", 10)
        self.config.setdefault("skip_patterns", ["#", "javascript:", "mailto:"])
        self.config.setdefault("content_selectors", ["main", "article", ".content", "#content"])
        self.config.setdefault("title_selectors", ["h1", "title"])
        self.config.setdefault("user_agent", "RAGSpace/1.0")
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.config["user_agent"]
        })
    
    def can_handle(self, url: str) -> bool:
        """Check if this crawler can handle the given URL"""
        url_lower = url.lower()
        
        # Skip GitHub URLs (handled by GitHub crawler)
        if "github.com" in url_lower:
            return False
        
        # Handle HTTP/HTTPS URLs
        return url_lower.startswith(("http://", "https://"))
    
    def get_supported_url_patterns(self) -> List[str]:
        """Return list of supported URL patterns"""
        return [
            "http://",
            "https://"
        ]
    
    def preprocess_url(self, url: str) -> str:
        """Normalize URL format"""
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        return url
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract text content from BeautifulSoup object"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content area
        content = None
        for selector in self.config["content_selectors"]:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            content = soup.find("body")
        
        if not content:
            return ""
        
        # Extract text
        text = content.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract title from page"""
        # Try title selectors
        for selector in self.config["title_selectors"]:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title:
                    return title
        
        # Fallback to URL
        parsed_url = urlparse(url)
        return f"Page from {parsed_url.netloc}"
    
    def get_page_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get information about a single page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = self.extract_title(soup, url)
            content = self.extract_text_content(soup)
            
            return {
                "url": url,
                "title": title,
                "content": self.postprocess_content(content),
                "status_code": response.status_code,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch page {url}: {e}")
            return None
    
    def find_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find all links on the page"""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip patterns
            if any(pattern in href.lower() for pattern in self.config["skip_patterns"]):
                continue
            
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Only include links from same domain
            if urlparse(absolute_url).netloc == base_domain:
                links.append(absolute_url)
        
        return list(set(links))  # Remove duplicates
    
    def determine_content_type(self, url: str, title: str) -> ContentType:
        """Determine content type based on URL and title"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Check for documentation indicators
        if any(word in title_lower for word in ["documentation", "docs", "guide", "manual"]):
            return ContentType.DOCUMENT
        
        # Check for blog/article indicators
        if any(word in title_lower for word in ["blog", "article", "post", "news"]):
            return ContentType.DOCUMENT
        
        # Check for API documentation
        if any(word in url_lower for word in ["api", "reference", "docs"]):
            return ContentType.DOCUMENT
        
        # Default to website
        return ContentType.WEBSITE
    
    def crawl(self, url: str, **kwargs) -> CrawlResult:
        """Crawl website and return structured content"""
        try:
            # Preprocess URL
            url = self.preprocess_url(url)
            max_depth = kwargs.get("max_depth", self.config["max_depth"])
            max_pages = kwargs.get("max_pages", self.config["max_pages"])
            
            logger.info(f"🔍 Crawling website: {url}")
            
            # Get initial page
            page_info = self.get_page_info(url)
            if not page_info:
                return CrawlResult(
                    success=False,
                    message=f"Failed to fetch initial page: {url}",
                    errors=[f"Could not fetch {url}"]
                )
            
            # Create root item
            root_item = CrawledItem(
                name=page_info["title"],
                type=ContentType.WEBSITE,
                url=url,
                content=page_info["content"],
                metadata={
                    "domain": urlparse(url).netloc,
                    "status_code": page_info["status_code"],
                    "content_length": page_info["content_length"],
                    "crawler": "website"
                },
                children=[]
            )
            
            # Crawl additional pages if depth > 1
            if max_depth > 1:
                try:
                    response = self.session.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = self.find_links(soup, url)
                    
                    # Limit number of pages to crawl
                    links = links[:max_pages - 1]  # -1 for root page
                    
                    for link in links:
                        child_info = self.get_page_info(link)
                        if child_info:
                            content_type = self.determine_content_type(link, child_info["title"])
                            
                            child_item = CrawledItem(
                                name=child_info["title"],
                                type=content_type,
                                url=link,
                                content=child_info["content"],
                                metadata={
                                    "domain": urlparse(link).netloc,
                                    "status_code": child_info["status_code"],
                                    "content_length": child_info["content_length"],
                                    "crawler": "website"
                                }
                            )
                            
                            if not self.should_skip_item(child_item):
                                root_item.children.append(child_item)
                                logger.info(f"✅ Fetched page: {child_info['title']}")
                            
                except Exception as e:
                    logger.warning(f"Failed to crawl additional pages: {e}")
            
            logger.info(f"✅ Successfully crawled {len(root_item.children) + 1} pages from {url}")
            
            return CrawlResult(
                success=True,
                message=f"Successfully crawled {len(root_item.children) + 1} pages from {url}",
                root_item=root_item,
                total_items=len(root_item.children) + 1
            )
            
        except Exception as e:
            error_msg = f"Failed to crawl website: {str(e)}"
            logger.error(error_msg)
            return CrawlResult(
                success=False,
                message=error_msg,
                errors=[error_msg]
            )
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information for this crawler"""
        return {
            "crawler": "website",
            "status": "no_rate_limit",
            "max_pages": self.config["max_pages"],
            "max_depth": self.config["max_depth"]
        } 