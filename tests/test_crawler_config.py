"""
Tests for Crawler Configuration System
"""

import pytest
import os
from unittest.mock import patch
from src.ragspace.config import CrawlerConfig


class TestCrawlerConfig:
    """Test crawler configuration functionality"""
    
    def test_github_config_defaults(self):
        """Test GitHub configuration with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = CrawlerConfig.get_github_config()
            
            assert config["token"] is None
            assert config["base_url"] == "https://api.github.com"
            assert config["user_agent"] == "RAGSpace/1.0"
            assert ".md" in config["file_types"]
            assert ".py" in config["file_types"]
            assert config["max_file_size"] == 50000
            assert "node_modules" in config["skip_patterns"]
            assert config["max_depth"] == 10
            assert config["rate_limit_warning"] is True
    
    def test_github_config_with_env(self):
        """Test GitHub configuration with environment variables"""
        with patch.dict(os.environ, {
            "GITHUB_TOKEN": "test-token",
            "GITHUB_API_URL": "https://api.github.com/v3",
            "GITHUB_USER_AGENT": "TestAgent/1.0",
            "GITHUB_FILE_TYPES": ".md,.txt,.py",
            "GITHUB_MAX_FILE_SIZE": "100000",
            "GITHUB_SKIP_PATTERNS": "test,skip",
            "GITHUB_MAX_DEPTH": "5",
            "GITHUB_RATE_LIMIT_WARNING": "false"
        }, clear=True):
            config = CrawlerConfig.get_github_config()
            
            assert config["token"] == "test-token"
            assert config["base_url"] == "https://api.github.com/v3"
            assert config["user_agent"] == "TestAgent/1.0"
            assert config["file_types"] == [".md", ".txt", ".py"]
            assert config["max_file_size"] == 100000
            assert config["skip_patterns"] == ["test", "skip"]
            assert config["max_depth"] == 5
            assert config["rate_limit_warning"] is False
    
    def test_website_config_defaults(self):
        """Test website configuration with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = CrawlerConfig.get_website_config()
            
            assert config["max_depth"] == 3
            assert config["max_pages"] == 10
            assert "#" in config["skip_patterns"]
            assert "main" in config["content_selectors"]
            assert "h1" in config["title_selectors"]
            assert config["user_agent"] == "RAGSpace/1.0"
            assert config["timeout"] == 10
            assert config["max_content_size"] == 50000
    
    def test_website_config_with_env(self):
        """Test website configuration with environment variables"""
        with patch.dict(os.environ, {
            "WEBSITE_MAX_DEPTH": "3",
            "WEBSITE_MAX_PAGES": "20",
            "WEBSITE_SKIP_PATTERNS": "test,skip",
            "WEBSITE_CONTENT_SELECTORS": "main,article",
            "WEBSITE_TITLE_SELECTORS": "h1,title",
            "WEBSITE_USER_AGENT": "TestAgent/1.0",
            "WEBSITE_TIMEOUT": "15",
            "WEBSITE_MAX_CONTENT_SIZE": "100000"
        }, clear=True):
            config = CrawlerConfig.get_website_config()
            
            assert config["max_depth"] == 3
            assert config["max_pages"] == 20
            assert config["skip_patterns"] == ["test", "skip"]
            assert config["content_selectors"] == ["main", "article"]
            assert config["title_selectors"] == ["h1", "title"]
            assert config["user_agent"] == "TestAgent/1.0"
            assert config["timeout"] == 15
            assert config["max_content_size"] == 100000
    
    def test_global_config_defaults(self):
        """Test global configuration with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = CrawlerConfig.get_global_config()
            
            assert config["enable_logging"] is True
            assert config["log_level"] == "INFO"
            assert config["default_timeout"] == 30
            assert config["retry_attempts"] == 3
            assert config["retry_delay"] == 1
    
    def test_mock_config_defaults(self):
        """Test mock configuration with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = CrawlerConfig.get_mock_config()
            
            assert config["enable_mock"] is False
            assert config["mock_data_path"] == ""
            assert config["mock_response_delay"] == 0.1
    
    def test_config_validation_valid(self):
        """Test configuration validation with valid values"""
        with patch.dict(os.environ, {
            "GITHUB_MAX_FILE_SIZE": "1000",
            "GITHUB_MAX_DEPTH": "2",
            "WEBSITE_MAX_DEPTH": "3",
            "WEBSITE_MAX_PAGES": "5",
            "WEBSITE_TIMEOUT": "10"
        }, clear=True):
            issues = CrawlerConfig.validate_config()
            assert len(issues) == 0
    
    def test_config_validation_invalid(self):
        """Test configuration validation with invalid values"""
        with patch.dict(os.environ, {
            "GITHUB_MAX_FILE_SIZE": "-1",
            "GITHUB_MAX_DEPTH": "0",
            "WEBSITE_MAX_DEPTH": "-5",
            "WEBSITE_MAX_PAGES": "0",
            "WEBSITE_TIMEOUT": "-10"
        }, clear=True):
            issues = CrawlerConfig.validate_config()
            assert len(issues) > 0
            assert "GITHUB_MAX_FILE_SIZE must be positive" in issues
            assert "GITHUB_MAX_DEPTH must be positive" in issues
            assert "WEBSITE_MAX_DEPTH must be positive" in issues
            assert "WEBSITE_MAX_PAGES must be positive" in issues
            assert "WEBSITE_TIMEOUT must be positive" in issues
    
    def test_config_summary(self):
        """Test configuration summary"""
        with patch.dict(os.environ, {
            "GITHUB_TOKEN": "test-token",
            "GITHUB_MAX_FILE_SIZE": "1000",
            "GITHUB_MAX_DEPTH": "2",
            "WEBSITE_MAX_DEPTH": "3",
            "WEBSITE_MAX_PAGES": "5",
            "WEBSITE_TIMEOUT": "10"
        }, clear=True):
            summary = CrawlerConfig.get_config_summary()
            
            assert "github" in summary
            assert "website" in summary
            assert "global" in summary
            
            assert summary["github"]["has_token"] is True
            assert summary["github"]["max_file_size"] == 1000
            assert summary["github"]["max_depth"] == 2
            assert summary["github"]["file_types"] > 0
            
            assert summary["website"]["max_depth"] == 3
            assert summary["website"]["max_pages"] == 5
            assert summary["website"]["timeout"] == 10
            
            assert summary["global"]["enable_logging"] is True
            assert summary["global"]["log_level"] == "INFO"
    
    def test_parse_list_env(self):
        """Test parsing list environment variables"""
        with patch.dict(os.environ, {
            "TEST_LIST": "item1,item2,item3"
        }, clear=True):
            from src.ragspace.config.crawler_config import _parse_list_env
            result = _parse_list_env("TEST_LIST", ["default"])
            assert result == ["item1", "item2", "item3"]
    
    def test_parse_list_env_empty(self):
        """Test parsing empty list environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            from src.ragspace.config.crawler_config import _parse_list_env
            result = _parse_list_env("TEST_LIST", ["default"])
            assert result == ["default"]
    
    def test_parse_int_env(self):
        """Test parsing integer environment variables"""
        with patch.dict(os.environ, {
            "TEST_INT": "42"
        }, clear=True):
            from src.ragspace.config.crawler_config import _parse_int_env
            result = _parse_int_env("TEST_INT", 10)
            assert result == 42
    
    def test_parse_int_env_invalid(self):
        """Test parsing invalid integer environment variable"""
        with patch.dict(os.environ, {
            "TEST_INT": "invalid"
        }, clear=True):
            from src.ragspace.config.crawler_config import _parse_int_env
            result = _parse_int_env("TEST_INT", 10)
            assert result == 10
    
    def test_parse_bool_env(self):
        """Test parsing boolean environment variables"""
        test_cases = [
            ("true", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("", False)
        ]
        
        for value, expected in test_cases:
            with patch.dict(os.environ, {"TEST_BOOL": value}, clear=True):
                from src.ragspace.config.crawler_config import _parse_bool_env
                result = _parse_bool_env("TEST_BOOL", False)
                assert result == expected 