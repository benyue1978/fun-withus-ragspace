"""
Crawler Configuration Management
Centralized configuration for all crawlers using environment variables
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CrawlerConfig:
    """Centralized crawler configuration"""
    
    @staticmethod
    def get_github_config() -> Dict[str, Any]:
        """Get GitHub crawler configuration from environment variables"""
        return {
            "token": os.getenv("GITHUB_TOKEN"),
            "base_url": os.getenv("GITHUB_API_URL", "https://api.github.com"),
            "user_agent": os.getenv("GITHUB_USER_AGENT", "RAGSpace/1.0"),
            "file_types": _parse_list_env("GITHUB_FILE_TYPES", [
                ".md", ".py", ".js", ".ts", ".txt", ".rst", ".adoc", ".json", ".yaml", ".yml"
            ]),
            "max_file_size": int(os.getenv("GITHUB_MAX_FILE_SIZE", "50000")),
            "skip_patterns": _parse_list_env("GITHUB_SKIP_PATTERNS", [
                "node_modules", ".git", "__pycache__", ".DS_Store", "*.pyc"
            ]),
            "max_depth": int(os.getenv("GITHUB_MAX_DEPTH", "10")),
            "rate_limit_warning": os.getenv("GITHUB_RATE_LIMIT_WARNING", "true").lower() == "true"
        }
    
    @staticmethod
    def get_website_config() -> Dict[str, Any]:
        """Get website crawler configuration from environment variables"""
        return {
            "max_depth": int(os.getenv("WEBSITE_MAX_DEPTH", "3")),
            "max_pages": int(os.getenv("WEBSITE_MAX_PAGES", "10")),
            "skip_patterns": _parse_list_env("WEBSITE_SKIP_PATTERNS", [
                "#", "javascript:", "mailto:", "tel:", "data:"
            ]),
            "content_selectors": _parse_list_env("WEBSITE_CONTENT_SELECTORS", [
                "main", "article", ".content", "#content", ".post", ".entry"
            ]),
            "title_selectors": _parse_list_env("WEBSITE_TITLE_SELECTORS", [
                "h1", "title", ".title", ".headline"
            ]),
            "user_agent": os.getenv("WEBSITE_USER_AGENT", "RAGSpace/1.0"),
            "timeout": int(os.getenv("WEBSITE_TIMEOUT", "10")),
            "max_content_size": int(os.getenv("WEBSITE_MAX_CONTENT_SIZE", "50000"))
        }
    
    @staticmethod
    def get_global_config() -> Dict[str, Any]:
        """Get global crawler configuration"""
        return {
            "enable_logging": os.getenv("CRAWLER_ENABLE_LOGGING", "true").lower() == "true",
            "log_level": os.getenv("CRAWLER_LOG_LEVEL", "INFO"),
            "default_timeout": int(os.getenv("CRAWLER_DEFAULT_TIMEOUT", "30")),
            "retry_attempts": int(os.getenv("CRAWLER_RETRY_ATTEMPTS", "3")),
            "retry_delay": int(os.getenv("CRAWLER_RETRY_DELAY", "1"))
        }
    
    @staticmethod
    def get_mock_config() -> Dict[str, Any]:
        """Get mock crawler configuration for testing"""
        return {
            "enable_mock": os.getenv("CRAWLER_ENABLE_MOCK", "false").lower() == "true",
            "mock_data_path": os.getenv("CRAWLER_MOCK_DATA_PATH", ""),
            "mock_response_delay": float(os.getenv("CRAWLER_MOCK_DELAY", "0.1"))
        }
    
    @staticmethod
    def validate_config() -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Check GitHub configuration
        github_config = CrawlerConfig.get_github_config()
        if github_config["max_file_size"] <= 0:
            issues.append("GITHUB_MAX_FILE_SIZE must be positive")
        if github_config["max_depth"] <= 0:
            issues.append("GITHUB_MAX_DEPTH must be positive")
        
        # Check website configuration
        website_config = CrawlerConfig.get_website_config()
        if website_config["max_depth"] <= 0:
            issues.append("WEBSITE_MAX_DEPTH must be positive")
        if website_config["max_pages"] <= 0:
            issues.append("WEBSITE_MAX_PAGES must be positive")
        if website_config["timeout"] <= 0:
            issues.append("WEBSITE_TIMEOUT must be positive")
        
        return issues
    
    @staticmethod
    def get_config_summary() -> Dict[str, Any]:
        """Get a summary of all crawler configurations"""
        return {
            "github": {
                "has_token": bool(CrawlerConfig.get_github_config()["token"]),
                "max_file_size": CrawlerConfig.get_github_config()["max_file_size"],
                "max_depth": CrawlerConfig.get_github_config()["max_depth"],
                "file_types": len(CrawlerConfig.get_github_config()["file_types"])
            },
            "website": {
                "max_depth": CrawlerConfig.get_website_config()["max_depth"],
                "max_pages": CrawlerConfig.get_website_config()["max_pages"],
                "timeout": CrawlerConfig.get_website_config()["timeout"]
            },
            "global": {
                "enable_logging": CrawlerConfig.get_global_config()["enable_logging"],
                "log_level": CrawlerConfig.get_global_config()["log_level"]
            }
        }


def _parse_list_env(env_var: str, default: List[str]) -> List[str]:
    """Parse environment variable as comma-separated list"""
    value = os.getenv(env_var)
    if value:
        return [item.strip() for item in value.split(",") if item.strip()]
    return default


def _parse_int_env(env_var: str, default: int) -> int:
    """Parse environment variable as integer"""
    value = os.getenv(env_var)
    if value:
        try:
            return int(value)
        except ValueError:
            return default
    return default


def _parse_bool_env(env_var: str, default: bool) -> bool:
    """Parse environment variable as boolean"""
    value = os.getenv(env_var)
    if value:
        return value.lower() in ("true", "1", "yes", "on")
    return default 