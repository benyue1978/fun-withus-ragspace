"""
Mock Crawler for Testing
Provides a mock implementation of CrawlerInterface for testing purposes
"""

import logging
from typing import List, Dict, Optional, Any
from .crawler_interface import (
    CrawlerInterface, CrawlResult, CrawledItem, ContentType
)

logger = logging.getLogger(__name__)

class MockCrawler(CrawlerInterface):
    """Mock crawler for testing purposes"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize mock crawler"""
        super().__init__(config)
        
        # Mock data for testing
        self.mock_data = {
            "https://github.com/owner/repo": {
                "name": "owner/repo",
                "type": ContentType.REPOSITORY,
                "url": "https://github.com/owner/repo",
                "content": "Mock GitHub repository: owner/repo\n\nThis repository contains 3 files.",
                "children": [
                    {
                        "name": "README.md",
                        "type": ContentType.DOCUMENT,
                        "url": "https://github.com/owner/repo/blob/main/README.md",
                        "content": "# Mock Repository\n\nThis is a mock README file for testing purposes.",
                        "metadata": {"path": "README.md", "size": 150}
                    },
                    {
                        "name": "main.py",
                        "type": ContentType.CODE,
                        "url": "https://github.com/owner/repo/blob/main/main.py",
                        "content": "def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()",
                        "metadata": {"path": "main.py", "size": 80}
                    },
                    {
                        "name": "config.json",
                        "type": ContentType.CONFIG,
                        "url": "https://github.com/owner/repo/blob/main/config.json",
                        "content": '{"name": "mock-project", "version": "1.0.0"}',
                        "metadata": {"path": "config.json", "size": 45}
                    }
                ]
            },
            "https://example.com": {
                "name": "Example Website",
                "type": ContentType.WEBSITE,
                "url": "https://example.com",
                "content": "Mock website content for testing purposes. This is a sample website with various content sections.",
                "children": [
                    {
                        "name": "about.html",
                        "type": ContentType.DOCUMENT,
                        "url": "https://example.com/about",
                        "content": "<h1>About Us</h1><p>This is a mock about page.</p>",
                        "metadata": {"path": "/about", "size": 120}
                    },
                    {
                        "name": "contact.html",
                        "type": ContentType.DOCUMENT,
                        "url": "https://example.com/contact",
                        "content": "<h1>Contact</h1><p>Email: test@example.com</p>",
                        "metadata": {"path": "/contact", "size": 100}
                    }
                ]
            }
        }
    
    def can_handle(self, url: str) -> bool:
        """Check if this crawler can handle the given URL"""
        # Handle GitHub URLs and website URLs
        url_lower = url.lower()
        if "github.com" in url_lower or "owner/repo" in url_lower:
            return True
        if url_lower.startswith(("http://", "https://")):
            return True
        return False
    
    def get_supported_url_patterns(self) -> List[str]:
        """Return list of supported URL patterns"""
        return [
            "github.com",
            "http://",
            "https://"
        ]
    
    def crawl(self, url: str, **kwargs) -> CrawlResult:
        """Mock crawling operation"""
        try:
            # Normalize URL for lookup
            lookup_url = url
            if "github.com" in url.lower() or "/" in url and not url.startswith("http"):
                if not url.startswith("https://github.com/"):
                    if url.startswith("github.com/"):
                        lookup_url = f"https://{url}"
                    else:
                        lookup_url = f"https://github.com/{url}"
            
            # Check if we have mock data for this URL
            if lookup_url not in self.mock_data:
                # Try alternative lookup keys
                if url in self.mock_data:
                    lookup_url = url
                elif f"https://github.com/{url}" in self.mock_data:
                    lookup_url = f"https://github.com/{url}"
                else:
                    return CrawlResult(
                        success=False,
                        message=f"Mock crawler: No data available for URL {url}"
                    )
            
            mock_data = self.mock_data[lookup_url]
            
            # Create root item
            root_item = CrawledItem(
                name=mock_data["name"],
                type=mock_data["type"],
                url=mock_data["url"],
                content=mock_data["content"],
                metadata={
                    "crawler": "mock",
                    "url": mock_data["url"],  # Use the full URL from mock data
                    "test": True
                },
                children=[]
            )
            
            # Add children
            for child_data in mock_data.get("children", []):
                child = CrawledItem(
                    name=child_data["name"],
                    type=child_data["type"],
                    url=child_data["url"],
                    content=child_data["content"],
                    metadata={
                        **child_data.get("metadata", {}),
                        "url": child_data["url"]  # Ensure URL is in metadata
                    }
                )
                root_item.children.append(child)
            
            logger.info(f"✅ Mock crawler: Successfully crawled {len(root_item.children)} items from {url}")
            
            return CrawlResult(
                success=True,
                message=f"Mock crawler: Successfully crawled {len(root_item.children)} items from {url}",
                root_item=root_item,
                items=root_item.children
            )
            
        except Exception as e:
            error_msg = f"Mock crawler: Failed to crawl {url}: {str(e)}"
            logger.error(error_msg)
            return CrawlResult(
                success=False,
                message=error_msg
            )
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get mock rate limit information"""
        return {
            "crawler": "mock",
            "status": "unlimited",
            "remaining": 9999,
            "limit": 10000,
            "reset_time": None
        } 