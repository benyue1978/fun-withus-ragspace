"""
GitHub API Service for RAGSpace
Handles GitHub repository content fetching and parsing
"""

import os
import base64
import requests
import json
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self):
        """Initialize GitHub service with token from environment"""
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RAGSpace/1.0"
        }
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
            logger.info("✅ GitHub service initialized with token")
        else:
            logger.warning("⚠️ GitHub service initialized without token (limited rate)")
    
    def parse_repo_url(self, repo_url: str) -> Tuple[str, str]:
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
    
    def get_repo_files(self, owner: str, repo: str, branch: str = "main", 
                      file_types: Optional[List[str]] = None, 
                      max_size: int = 50000) -> List[Dict]:
        """Recursively get all files from repository"""
        if file_types is None:
            file_types = [".md", ".py", ".js", ".ts", ".txt", ".rst", ".adoc"]
        
        files = []
        
        def traverse_directory(path: str = ""):
            """Recursively traverse directory structure"""
            try:
                contents = self.get_repo_contents(owner, repo, path, branch)
                
                for item in contents:
                    if item["type"] == "dir":
                        # Recursively traverse subdirectories
                        traverse_directory(item["path"])
                    elif item["type"] == "file":
                        # Check file type and size
                        file_name = item["name"]
                        file_size = item.get("size", 0)
                        
                        # Skip if file is too large
                        if file_size > max_size:
                            logger.warning(f"Skipping large file: {file_name} ({file_size} bytes)")
                            continue
                        
                        # Check if file type is in our target types
                        if any(file_name.endswith(ext) for ext in file_types):
                            files.append(item)
                            
            except Exception as e:
                logger.error(f"Error traversing directory {path}: {e}")
        
        # Start traversal from root
        traverse_directory()
        return files
    
    def fetch_repo_structure(self, repo_url: str, branch: str = "main") -> Dict:
        """Fetch complete repository structure and content"""
        owner, repo = self.parse_repo_url(repo_url)
        
        logger.info(f"Fetching repository: {owner}/{repo}")
        
        # Get all files
        files = self.get_repo_files(owner, repo, branch)
        
        # Create repository root document
        repo_doc = {
            "type": "github",
            "name": f"{owner}/{repo}",
            "url": f"https://github.com/{owner}/{repo}",
            "content": f"GitHub repository: {owner}/{repo}\n\nThis repository contains {len(files)} files.",
            "metadata": {
                "repo": f"{owner}/{repo}",
                "branch": branch,
                "file_count": len(files),
                "owner": owner,
                "repository": repo
            },
            "children": []
        }
        
        # Fetch content for each file
        for file_info in files:
            try:
                file_path = file_info["path"]
                file_content = self.get_file_content(owner, repo, file_path, branch)
                
                child_doc = {
                    "type": "github_file",
                    "name": file_path,
                    "url": file_info["html_url"],
                    "content": file_content,
                    "metadata": {
                        "repo": f"{owner}/{repo}",
                        "branch": branch,
                        "path": file_path,
                        "size": file_info.get("size", 0),
                        "sha": file_info.get("sha", "")
                    }
                }
                
                repo_doc["children"].append(child_doc)
                logger.info(f"Fetched file: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to fetch file {file_info['path']}: {e}")
                continue
        
        logger.info(f"✅ Successfully fetched {len(repo_doc['children'])} files from {owner}/{repo}")
        return repo_doc
    
    def get_rate_limit_info(self) -> Dict:
        """Get current rate limit information"""
        try:
            response = requests.get(f"{self.base_url}/rate_limit", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return {"error": str(e)} 