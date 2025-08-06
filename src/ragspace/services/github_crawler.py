"""
GitHub Crawler Implementation
Implements the CrawlerInterface for GitHub repositories
"""

import os
import base64
import requests
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse
import logging

from ..config import CrawlerConfig
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
        """Get repository contents at specified path"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict):
                # Single file
                return [data]
            else:
                # Directory listing
                return data
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch GitHub contents: {e}")
            raise Exception(f"GitHub API error: {str(e)}")
    
    def get_file_content(self, owner: str, repo: str, path: str, branch: str = "main") -> str:
        """Get file content from GitHub repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("type") != "file":
                raise ValueError(f"Path {path} is not a file")
            
            # Decode base64 content
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch file content: {e}")
            raise Exception(f"GitHub API error: {str(e)}")
    
    def get_repo_files(self, owner: str, repo: str, branch: str = "main") -> List[Dict]:
        """Recursively get all files from repository"""
        files = []
        
        def traverse_directory(path: str = ""):
            """Recursively traverse directory structure"""
            try:
                contents = self.get_repo_contents(owner, repo, path, branch)
                
                for item in contents:
                    if item["type"] == "dir":
                        # Check if directory should be skipped
                        dir_name = item["name"]
                        if any(pattern in dir_name.lower() for pattern in self.config["skip_patterns"]):
                            logger.info(f"Skipping directory: {dir_name}")
                            continue
                        
                        # Recursively traverse subdirectories
                        traverse_directory(item["path"])
                    elif item["type"] == "file":
                        # Check file type and size
                        file_name = item["name"]
                        file_size = item.get("size", 0)
                        
                        # Skip if file is too large
                        if file_size > self.config["max_file_size"]:
                            logger.warning(f"Skipping large file: {file_name} ({file_size} bytes)")
                            continue
                        
                        # Check if file type is in our target types
                        if any(file_name.endswith(ext) for ext in self.config["file_types"]):
                            files.append(item)
                            
            except Exception as e:
                logger.error(f"Error traversing directory {path}: {e}")
        
        # Start traversal from root
        traverse_directory()
        return files
    
    def determine_content_type(self, file_name: str) -> ContentType:
        """Determine content type based on file name"""
        file_lower = file_name.lower()
        
        if file_lower.endswith(('.md', '.txt', '.rst', '.adoc')):
            return ContentType.DOCUMENT
        elif file_lower.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c')):
            return ContentType.CODE
        elif file_lower.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')):
            return ContentType.CONFIG
        elif file_lower in ('readme.md', 'readme.txt'):
            return ContentType.README
        else:
            return ContentType.FILE
    
    def crawl(self, url: str, **kwargs) -> CrawlResult:
        """Crawl GitHub repository and return structured content"""
        try:
            # Preprocess URL
            url = self.preprocess_url(url)
            
            # Parse repository URL
            owner, repo = self.parse_repo_url(url)
            branch = kwargs.get("branch", "main")
            
            logger.info(f"🔍 Crawling GitHub repository: {owner}/{repo}")
            
            # Get all files
            files = self.get_repo_files(owner, repo, branch)
            
            # Create repository root item
            root_item = CrawledItem(
                name=f"{owner}/{repo}",
                type=ContentType.REPOSITORY,
                url=f"https://github.com/{owner}/{repo}",
                content=f"GitHub repository: {owner}/{repo}\n\nThis repository contains {len(files)} files.",
                metadata={
                    "repo": f"{owner}/{repo}",
                    "branch": branch,
                    "file_count": len(files),
                    "owner": owner,
                    "repository": repo,
                    "crawler": "github"
                },
                children=[]
            )
            
            # Fetch content for each file
            errors = []
            for file_info in files:
                try:
                    file_path = file_info["path"]
                    file_content = self.get_file_content(owner, repo, file_path, branch)
                    
                    # Determine content type
                    content_type = self.determine_content_type(file_path)
                    
                    child_item = CrawledItem(
                        name=file_path,
                        type=content_type,
                        url=file_info["html_url"],
                        content=file_content,
                        metadata={
                            "repo": f"{owner}/{repo}",
                            "branch": branch,
                            "path": file_path,
                            "size": file_info.get("size", 0),
                            "sha": file_info.get("sha", ""),
                            "crawler": "github",
                            "url": file_info["html_url"]
                        }
                    )
                    
                    # Check if item should be skipped
                    if not self.should_skip_item(child_item):
                        root_item.children.append(child_item)
                        logger.info(f"✅ Fetched file: {file_path}")
                    else:
                        logger.info(f"⏭️ Skipped file: {file_path}")
                        
                except Exception as e:
                    error_msg = f"Failed to fetch file {file_info['path']}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue
            
            logger.info(f"✅ Successfully crawled {len(root_item.children)} files from {owner}/{repo}")
            
            return CrawlResult(
                success=True,
                message=f"Successfully crawled {len(root_item.children)} files from {owner}/{repo}",
                root_item=root_item,
                items=root_item.children
            )
            
        except Exception as e:
            error_msg = f"Failed to crawl GitHub repository: {str(e)}"
            logger.error(error_msg)
            return CrawlResult(
                success=False,
                message=error_msg
            )
    
    def should_skip_item(self, item: CrawledItem) -> bool:
        """Check if an item should be skipped based on configuration"""
        # Skip if content is too large
        if len(item.content) > self.config.get("max_file_size", 50000):
            return True
        
        # Skip if name matches skip patterns
        for pattern in self.config.get("skip_patterns", []):
            if pattern in item.name:
                return True
        
        return False
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get GitHub API rate limit information"""
        try:
            response = requests.get(f"{self.base_url}/rate_limit", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return {"error": str(e)} 