"""
GitHub repository crawler implementation
"""

import os
import re
import base64
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import logging

from ...config.crawler_config import CrawlerConfig
from .crawler_interface import (
    CrawlerInterface, CrawlResult, CrawledItem, ContentType
)

logger = logging.getLogger(__name__)

class GitHubCrawler(CrawlerInterface):
    """GitHub repository crawler implementation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize GitHub crawler"""
        super().__init__(config)
        
        # Load configuration from environment
        github_config = CrawlerConfig.get_github_config()
        
        # GitHub API configuration
        self.token = github_config["token"]
        self.base_url = github_config["base_url"]
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": github_config["user_agent"]
        }
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
            logger.info("✅ GitHub crawler initialized with token")
        else:
            if github_config["rate_limit_warning"]:
                logger.warning("⚠️ GitHub crawler initialized without token (limited rate)")
        
        # Update configuration with environment settings
        self.config.update({
            "file_types": github_config["file_types"],
            "max_file_size": github_config["max_file_size"],
            "skip_patterns": github_config["skip_patterns"],
            "max_depth": github_config["max_depth"]
        })
    
    def can_handle(self, url: str) -> bool:
        """Check if this crawler can handle the given URL"""
        url_lower = url.lower()
        
        # Handle different URL formats
        if url_lower.startswith(("https://github.com/", "github.com/")):
            return True
        elif "/" in url and not url_lower.startswith("http"):
            # Check if it looks like owner/repo format
            parts = url.split("/")
            if len(parts) == 2 and not "." in parts[0]:
                return True
        
        return False
    
    def get_supported_url_patterns(self) -> List[str]:
        """Return list of supported URL patterns"""
        return [
            "github.com",
            "githubusercontent.com"
        ]
    
    def preprocess_url(self, url: str) -> str:
        """Normalize GitHub URL format"""
        url = url.strip()
        
        # Handle different URL formats
        if url.startswith("https://github.com/"):
            return url
        elif url.startswith("github.com/"):
            return f"https://{url}"
        elif "/" in url and not url.startswith("http"):
            return f"https://github.com/{url}"
        
        return url
    
    def parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Parse GitHub repository URL to extract owner and repo name"""
        try:
            # Handle different URL formats
            if repo_url.startswith("https://github.com/"):
                path = repo_url.replace("https://github.com/", "").rstrip("/")
            elif repo_url.startswith("github.com/"):
                path = repo_url.replace("github.com/", "").rstrip("/")
            else:
                path = repo_url.rstrip("/")
            
            # Split into owner and repo
            parts = path.split("/")
            if len(parts) != 2:
                raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
            
            owner, repo = parts
            return owner, repo
            
        except Exception as e:
            raise ValueError(f"Failed to parse GitHub URL '{repo_url}': {str(e)}")

    def get_repo_contents(self, owner: str, repo: str, path: str = "", branch: str = "main") -> List[Dict]:
        """Get contents of a GitHub repository directory"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            params = {"ref": branch}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get repo contents: {e}")
            return []

    def get_file_content(self, owner: str, repo: str, path: str, branch: str = "main") -> str:
        """Get content of a specific file from GitHub"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            params = {"ref": branch}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            content_data = response.json()
            
            # Decode content
            if content_data.get("encoding") == "base64":
                content = base64.b64decode(content_data["content"]).decode("utf-8")
                return content
            else:
                return content_data.get("content", "")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get file content: {e}")
            return ""

    def get_repo_files(self, owner: str, repo: str, branch: str = "main") -> List[Dict]:
        """Get all files from a GitHub repository"""
        files = []
        
        def traverse_directory(path: str = ""):
            """Recursively traverse repository directory"""
            try:
                contents = self.get_repo_contents(owner, repo, path, branch)
                
                for item in contents:
                    if item["type"] == "file":
                        # Check file size limit
                        if item.get("size", 0) <= self.config.get("max_file_size", 1024 * 1024):
                            files.append({
                                "name": item["name"],
                                "path": item["path"],
                                "size": item.get("size", 0),
                                "type": item["type"],
                                "url": item["url"],
                                "download_url": item.get("download_url")
                            })
                    elif item["type"] == "dir":
                        # Recursively traverse subdirectories
                        traverse_directory(item["path"])
                        
            except Exception as e:
                logger.error(f"Failed to traverse directory {path}: {e}")
        
        # Start traversal from root
        traverse_directory()
        return files

    def determine_content_type(self, file_name: str) -> ContentType:
        """Determine content type based on file extension"""
        file_lower = file_name.lower()
        
        # Code files
        if file_lower.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt')):
            return ContentType.CODE
        # Documentation files
        elif file_lower.endswith(('.md', '.txt', '.rst', '.adoc')):
            return ContentType.DOCUMENTATION
        # Configuration files
        elif file_lower.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf')):
            return ContentType.CONFIGURATION
        # Data files
        elif file_lower.endswith(('.csv', '.tsv', '.xml', '.sql')):
            return ContentType.DATA
        # Image files
        elif file_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
            return ContentType.IMAGE
        # Binary files
        elif file_lower.endswith(('.exe', '.dll', '.so', '.dylib', '.bin')):
            return ContentType.BINARY
        else:
            return ContentType.UNKNOWN

    def crawl(self, url: str, **kwargs) -> CrawlResult:
        """Crawl a GitHub repository"""
        try:
            # Preprocess URL
            processed_url = self.preprocess_url(url)
            
            # Parse repository URL
            owner, repo = self.parse_repo_url(processed_url)
            
            # Get branch from kwargs or default to main
            branch = kwargs.get("branch", "main")
            
            logger.info(f"🔄 Crawling GitHub repository: {owner}/{repo} (branch: {branch})")
            
            # Get all files from repository
            files = self.get_repo_files(owner, repo, branch)
            
            if not files:
                return CrawlResult(
                    success=False,
                    message=f"No files found in repository {owner}/{repo}",
                    items=[],
                    metadata={
                        "owner": owner,
                        "repo": repo,
                        "branch": branch,
                        "files_count": 0
                    }
                )
            
            # Process files and create crawled items
            items = []
            processed_count = 0
            skipped_count = 0
            
            for file_info in files:
                try:
                    # Get file content
                    content = self.get_file_content(owner, repo, file_info["path"], branch)
                    
                    if not content:
                        skipped_count += 1
                        continue
                    
                    # Determine content type
                    content_type = self.determine_content_type(file_info["name"])
                    
                    # Create crawled item
                    item = CrawledItem(
                        title=file_info["name"],
                        content=content,
                        url=file_info["download_url"] or file_info["url"],
                        content_type=content_type,
                        metadata={
                            "owner": owner,
                            "repo": repo,
                            "branch": branch,
                            "path": file_info["path"],
                            "size": file_info["size"],
                            "file_type": file_info["name"].split(".")[-1] if "." in file_info["name"] else None
                        }
                    )
                    
                    # Check if item should be skipped
                    if not self.should_skip_item(item):
                        items.append(item)
                        processed_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process file {file_info['path']}: {e}")
                    skipped_count += 1
                    continue
            
            logger.info(f"✅ Crawled {processed_count} files, skipped {skipped_count} files")
            
            return CrawlResult(
                success=True,
                message=f"Successfully crawled {processed_count} files from {owner}/{repo}",
                items=items,
                metadata={
                    "owner": owner,
                    "repo": repo,
                    "branch": branch,
                    "files_count": len(files),
                    "processed_count": processed_count,
                    "skipped_count": skipped_count
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to crawl GitHub repository: {e}")
            return CrawlResult(
                success=False,
                message=f"Failed to crawl GitHub repository: {str(e)}",
                items=[],
                metadata={}
            )

    def should_skip_item(self, item: CrawledItem) -> bool:
        """Check if an item should be skipped based on configuration"""
        # Check skip patterns
        skip_patterns = self.config.get("skip_patterns", [])
        for pattern in skip_patterns:
            if re.search(pattern, item.title, re.IGNORECASE):
                return True
        
        # Check file size
        max_size = self.config.get("max_file_size", 1024 * 1024)
        if hasattr(item, 'metadata') and item.metadata.get("size", 0) > max_size:
            return True
        
        # Skip binary files by default
        if item.content_type == ContentType.BINARY:
            return True
        
        return False

    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get GitHub API rate limit information"""
        try:
            response = requests.get(f"{self.base_url}/rate_limit", headers=self.headers)
            response.raise_for_status()
            
            rate_limit = response.json()
            return {
                "limit": rate_limit["resources"]["core"]["limit"],
                "remaining": rate_limit["resources"]["core"]["remaining"],
                "reset": rate_limit["resources"]["core"]["reset"],
                "used": rate_limit["resources"]["core"]["used"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return {} 