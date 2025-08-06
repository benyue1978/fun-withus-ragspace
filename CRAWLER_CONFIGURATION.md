# RAGSpace Crawler Configuration Guide

## 概述

RAGSpace的爬虫系统采用模块化设计，支持多种内容源的自动抓取。所有配置都通过环境变量管理，提供了灵活的配置选项。

## 配置系统架构

### 1. 配置管理类

**位置**: `src/ragspace/config/crawler_config.py`

```python
class CrawlerConfig:
    @staticmethod
    def get_github_config() -> Dict[str, Any]
    @staticmethod
    def get_website_config() -> Dict[str, Any]
    @staticmethod
    def get_global_config() -> Dict[str, Any]
    @staticmethod
    def get_mock_config() -> Dict[str, Any]
    @staticmethod
    def validate_config() -> List[str]
    @staticmethod
    def get_config_summary() -> Dict[str, Any]
```

### 2. 爬虫接口

**位置**: `src/ragspace/services/crawler_interface.py`

```python
class CrawlerInterface:
    def crawl(self, url: str, **kwargs) -> CrawlResult
    def can_handle(self, url: str) -> bool
    def get_supported_url_patterns(self) -> List[str]
    def get_rate_limit_info(self) -> Dict[str, Any]
```

### 3. 爬虫注册表

**位置**: `src/ragspace/services/crawler_interface.py`

```python
class CrawlerRegistry:
    def register(self, crawler: CrawlerInterface)
    def get_crawler_for_url(self, url: str) -> Optional[CrawlerInterface]
    def get_all_crawlers(self) -> List[CrawlerInterface]
```

## 环境变量配置

### GitHub 爬虫配置

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `GITHUB_TOKEN` | GitHub API 令牌 | (无) | `ghp_xxxxxxxxxxxx` |
| `GITHUB_API_URL` | GitHub API 基础URL | `https://api.github.com` | `https://api.github.com` |
| `GITHUB_USER_AGENT` | 用户代理字符串 | `RAGSpace/1.0` | `MyApp/1.0` |
| `GITHUB_FILE_TYPES` | 支持的文件类型 | `.md,.py,.js,.ts,.txt,.rst,.adoc,.json,.yaml,.yml` | `.md,.py,.js` |
| `GITHUB_MAX_FILE_SIZE` | 最大文件大小(字节) | `50000` | `100000` |
| `GITHUB_SKIP_PATTERNS` | 跳过的模式 | `node_modules,.git,__pycache__,.DS_Store,*.pyc` | `test,temp` |
| `GITHUB_MAX_DEPTH` | 最大目录深度 | `10` | `5` |
| `GITHUB_RATE_LIMIT_WARNING` | 显示速率限制警告 | `true` | `false` |

### 网站爬虫配置

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `WEBSITE_MAX_DEPTH` | 最大爬取深度 | `3` | `5` |
| `WEBSITE_MAX_PAGES` | 最大页面数量 | `10` | `20` |
| `WEBSITE_SKIP_PATTERNS` | 跳过的URL模式 | `#,javascript:,mailto:,tel:,data:` | `#,javascript:` |
| `WEBSITE_CONTENT_SELECTORS` | 内容CSS选择器 | `main,article,.content,#content,.post,.entry` | `main,article` |
| `WEBSITE_TITLE_SELECTORS` | 标题CSS选择器 | `h1,title,.title,.headline` | `h1,title` |
| `WEBSITE_USER_AGENT` | 用户代理字符串 | `RAGSpace/1.0` | `MyApp/1.0` |
| `WEBSITE_TIMEOUT` | 请求超时(秒) | `10` | `15` |
| `WEBSITE_MAX_CONTENT_SIZE` | 最大内容大小(字节) | `50000` | `100000` |

### 全局爬虫配置

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `CRAWLER_ENABLE_LOGGING` | 启用爬虫日志 | `true` | `false` |
| `CRAWLER_LOG_LEVEL` | 日志级别 | `INFO` | `DEBUG` |
| `CRAWLER_DEFAULT_TIMEOUT` | 默认超时(秒) | `30` | `60` |
| `CRAWLER_RETRY_ATTEMPTS` | 重试次数 | `3` | `5` |
| `CRAWLER_RETRY_DELAY` | 重试延迟(秒) | `1` | `2` |

### Mock爬虫配置

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `CRAWLER_ENABLE_MOCK` | 启用Mock爬虫 | `false` | `true` |
| `CRAWLER_MOCK_DATA_PATH` | Mock数据路径 | (空) | `/path/to/mock/data` |
| `CRAWLER_MOCK_DELAY` | Mock响应延迟(秒) | `0.1` | `0.5` |

## 配置示例

### 1. 基础配置 (.env)

```bash
# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# GitHub配置
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_MAX_DEPTH=5
GITHUB_MAX_FILE_SIZE=100000

# 网站配置
WEBSITE_MAX_DEPTH=2
WEBSITE_MAX_PAGES=5
WEBSITE_TIMEOUT=15

# 全局配置
CRAWLER_ENABLE_LOGGING=true
CRAWLER_LOG_LEVEL=INFO
```

### 2. 开发环境配置

```bash
# 开发环境 - 更详细的日志
CRAWLER_ENABLE_LOGGING=true
CRAWLER_LOG_LEVEL=DEBUG
GITHUB_RATE_LIMIT_WARNING=true

# 较小的限制以避免过载
GITHUB_MAX_DEPTH=3
WEBSITE_MAX_DEPTH=2
WEBSITE_MAX_PAGES=5
```

### 3. 生产环境配置

```bash
# 生产环境 - 更严格的限制
GITHUB_MAX_DEPTH=10
GITHUB_MAX_FILE_SIZE=50000
WEBSITE_MAX_DEPTH=3
WEBSITE_MAX_PAGES=10

# 更长的超时
WEBSITE_TIMEOUT=30
CRAWLER_DEFAULT_TIMEOUT=60
```

## 爬虫类型

### 1. GitHub爬虫 (GitHubCrawler)

**功能**: 抓取GitHub仓库内容和文件

**支持的操作**:
- 解析GitHub URL格式
- 递归获取仓库文件
- 获取文件内容
- 处理速率限制

**URL格式支持**:
- `https://github.com/owner/repo`
- `github.com/owner/repo`
- `owner/repo`

**配置示例**:
```python
# 获取GitHub配置
config = CrawlerConfig.get_github_config()
print(f"Token: {config['token']}")
print(f"Max depth: {config['max_depth']}")
print(f"File types: {config['file_types']}")
```

### 2. 网站爬虫 (WebsiteCrawler)

**功能**: 抓取一般网站内容

**支持的操作**:
- 提取网页文本内容
- 查找页面链接
- 递归爬取
- 内容过滤

**配置示例**:
```python
# 获取网站配置
config = CrawlerConfig.get_website_config()
print(f"Max depth: {config['max_depth']}")
print(f"Content selectors: {config['content_selectors']}")
print(f"Timeout: {config['timeout']}")
```

### 3. Mock爬虫 (MockCrawler)

**功能**: 提供测试数据

**用途**:
- 单元测试
- 集成测试
- 开发环境模拟

**配置示例**:
```python
# 获取Mock配置
config = CrawlerConfig.get_mock_config()
print(f"Enable mock: {config['enable_mock']}")
print(f"Response delay: {config['mock_response_delay']}")
```

## 配置验证

### 1. 验证配置

```python
from src.ragspace.config import CrawlerConfig

# 验证配置
issues = CrawlerConfig.validate_config()
if issues:
    print("配置问题:")
    for issue in issues:
        print(f"- {issue}")
else:
    print("配置验证通过")
```

### 2. 获取配置摘要

```python
# 获取配置摘要
summary = CrawlerConfig.get_config_summary()
print("GitHub配置:")
print(f"- 有令牌: {summary['github']['has_token']}")
print(f"- 最大文件大小: {summary['github']['max_file_size']}")
print(f"- 最大深度: {summary['github']['max_depth']}")

print("网站配置:")
print(f"- 最大深度: {summary['website']['max_depth']}")
print(f"- 最大页面数: {summary['website']['max_pages']}")
```

## 使用示例

### 1. 基本使用

```python
from src.ragspace.services import crawler_registry
from src.ragspace.config import CrawlerConfig

# 获取适合的爬虫
url = "https://github.com/owner/repo"
crawler = crawler_registry.get_crawler_for_url(url)

if crawler:
    # 爬取内容
    result = crawler.crawl(url)
    if result.success:
        print(f"成功爬取: {result.root_item.name}")
        print(f"子项目数量: {len(result.root_item.children)}")
    else:
        print(f"爬取失败: {result.message}")
else:
    print("没有找到适合的爬虫")
```

### 2. 配置检查

```python
# 检查GitHub配置
github_config = CrawlerConfig.get_github_config()
if not github_config['token']:
    print("警告: 未设置GitHub令牌，将使用受限的API访问")

# 检查网站配置
website_config = CrawlerConfig.get_website_config()
print(f"网站爬虫超时: {website_config['timeout']}秒")
print(f"最大深度: {website_config['max_depth']}")
```

### 3. 错误处理

```python
try:
    # 验证配置
    issues = CrawlerConfig.validate_config()
    if issues:
        raise ValueError(f"配置错误: {', '.join(issues)}")
    
    # 使用爬虫
    crawler = crawler_registry.get_crawler_for_url(url)
    result = crawler.crawl(url)
    
except ValueError as e:
    print(f"配置错误: {e}")
except Exception as e:
    print(f"爬取错误: {e}")
```

## 测试

### 1. 运行配置测试

```bash
# 运行配置测试
poetry run pytest tests/test_crawler_config.py -v

# 运行特定测试
poetry run pytest tests/test_crawler_config.py::TestCrawlerConfig::test_github_config_defaults -v
```

### 2. 运行爬虫测试

```bash
# 运行爬虫系统测试
poetry run pytest tests/test_crawler_system.py -v

# 运行UI集成测试
poetry run pytest tests/test_ui_crawler.py -v
```

## 故障排除

### 1. 常见问题

**问题**: GitHub API速率限制
```
解决方案: 设置GITHUB_TOKEN环境变量
```

**问题**: 网站爬取超时
```
解决方案: 增加WEBSITE_TIMEOUT值
```

**问题**: 文件大小限制
```
解决方案: 调整GITHUB_MAX_FILE_SIZE或WEBSITE_MAX_CONTENT_SIZE
```

### 2. 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查爬虫注册
print("已注册的爬虫:")
for crawler in crawler_registry.get_all_crawlers():
    print(f"- {crawler.__class__.__name__}")

# 检查配置
summary = CrawlerConfig.get_config_summary()
print("配置摘要:", summary)
```

## 最佳实践

### 1. 环境变量管理

- 使用`.env`文件管理本地配置
- 在生产环境中使用环境变量
- 定期更新配置文档

### 2. 性能优化

- 根据需求调整爬取深度和页面数量
- 合理设置超时时间
- 监控API使用情况

### 3. 安全考虑

- 不要在代码中硬编码令牌
- 定期轮换API令牌
- 限制爬取频率

### 4. 监控和日志

- 启用爬虫日志记录
- 监控错误率和成功率
- 设置告警机制

---

*最后更新: 2024年12月* 