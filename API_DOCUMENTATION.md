# RAGSpace - 数据结构和API文档

## 项目概述

RAGSpace是一个基于AI的知识管理系统，支持文档集合管理、智能查询和MCP（Model Context Protocol）集成。项目使用Supabase作为后端数据库，Gradio作为Web界面。

## 技术栈

- **后端**: Python + FastAPI/Gradio
- **数据库**: Supabase (PostgreSQL + pgvector)
- **前端**: Gradio Web界面
- **协议**: MCP (Model Context Protocol)
- **部署**: Docker + Render/Railway

## 数据库结构

### 1. 文档集合表 (docsets)

```sql
CREATE TABLE docsets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  description text,
  created_at timestamp DEFAULT now()
);
```

**字段说明**:
- `id`: 主键，UUID格式
- `name`: 文档集合名称，唯一
- `description`: 文档集合描述
- `created_at`: 创建时间

### 2. 文档表 (documents)

```sql
CREATE TABLE documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  docset_id uuid REFERENCES docsets(id) ON DELETE CASCADE,
  parent_id uuid REFERENCES documents(id) ON DELETE CASCADE,
  name text NOT NULL,
  type text CHECK (type IN ('file', 'url', 'github', 'website', 'github_file', 'github_readme', 'github_repo', 'repository', 'document', 'code', 'config', 'readme')),
  url text,
  content text,
  metadata jsonb DEFAULT '{}',
  added_date timestamp DEFAULT now()
);
```

**字段说明**:
- `id`: 主键，UUID格式
- `docset_id`: 外键，关联到docsets表
- `parent_id`: 外键，支持父子文档关系（自引用）
- `name`: 文档名称
- `type`: 文档类型，支持多种爬虫类型
- `url`: 文档来源URL（可选）
- `content`: 文档内容
- `metadata`: 元数据，存储爬虫相关信息
- `added_date`: 添加时间

**支持的文档类型**:
- `file` - 上传的文件
- `url` - URL链接
- `github` - GitHub相关（已弃用）
- `website` - 网站内容
- `github_file` - GitHub文件
- `github_readme` - GitHub README
- `github_repo` - GitHub仓库
- `repository` - 仓库类型
- `document` - 文档类型
- `code` - 代码类型
- `config` - 配置类型
- `readme` - README类型

### 3. 索引

```sql
CREATE INDEX idx_documents_docset_id ON documents(docset_id);
CREATE INDEX idx_documents_parent_id ON documents(parent_id);
CREATE INDEX idx_documents_type ON documents(type);
CREATE INDEX idx_documents_added_date ON documents(added_date);
CREATE INDEX idx_documents_metadata ON documents USING GIN (metadata);
```

## 数据模型

### 1. Document 模型

**位置**: `src/ragspace/models/document.py`

```python
class Document:
    def __init__(self, title: str, content: str, doc_type: str = "file", metadata: Optional[Dict[str, Any]] = None):
        self.title = title
        self.content = content
        self.doc_type = doc_type  # 支持多种爬虫类型
        self.metadata = metadata or {}
        self.id = None
        self.parent_id = None  # 支持父子关系
```

**属性**:
- `title`: 文档标题
- `content`: 文档内容
- `doc_type`: 文档类型
- `metadata`: 元数据字典
- `id`: 文档ID
- `parent_id`: 父文档ID（支持父子关系）

### 2. 爬虫系统模型

#### CrawlerInterface
**位置**: `src/ragspace/services/crawler_interface.py`

```python
class CrawlerInterface:
    def crawl(self, url: str, **kwargs) -> CrawlResult
    def can_handle(self, url: str) -> bool
    def get_supported_url_patterns(self) -> List[str]
    def get_rate_limit_info(self) -> Dict[str, Any]
    def should_skip_item(self, item: CrawledItem) -> bool
```

#### CrawledItem
```python
@dataclass
class CrawledItem:
    name: str
    type: ContentType
    url: str
    content: str
    metadata: Dict[str, Any]
    children: List['CrawledItem']
```

#### CrawlResult
```python
@dataclass
class CrawlResult:
    success: bool
    message: str
    root_item: Optional[CrawledItem]
    total_items: int
    errors: List[str]
```

#### ContentType
```python
class ContentType(Enum):
    REPOSITORY = "repository"
    DOCUMENT = "document"
    CODE = "code"
    CONFIG = "config"
    README = "readme"
```

### 2. DocSet 模型

**位置**: `src/ragspace/models/docset.py`

```python
class DocSet:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.documents: List[Document] = []
        self.metadata = {
            "created_at": time.time(),
            "updated_at": time.time()
        }
```

**方法**:
- `add_document(doc)`: 添加文档
- `get_document_by_id(doc_id)`: 根据ID获取文档
- `search_documents(query)`: 搜索文档

## API接口

### 1. Web界面API (Gradio)

#### 知识管理接口

### 创建文档集合
```python
def create_docset_ui(name: str, description: str) -> str
```
- **输入**: 名称和描述
- **输出**: 操作结果字符串
- **功能**: 创建新的文档集合

### 上传文件
```python
def upload_file_to_docset(files, docset_name: str) -> str
```
- **输入**: 文件列表和目标文档集合名称
- **输出**: 上传结果字符串
- **功能**: 将文件上传到指定文档集合

### 添加网站
```python
def add_url_to_docset(url: str, docset_name: str, website_type: str = "website") -> str
```
- **输入**: URL、文档集合名称、网站类型
- **输出**: 操作结果字符串
- **功能**: 添加网站内容到文档集合

### 添加GitHub仓库
```python
def add_github_repo_to_docset(repo_url: str, docset_name: str) -> str
```
- **输入**: GitHub仓库URL和文档集合名称
- **输出**: 操作结果字符串
- **功能**: 添加GitHub仓库内容到文档集合

#### 聊天接口

### 处理查询
```python
def process_query(query: str, history, docset_name: str = None) -> tuple
```
- **输入**: 查询文本、聊天历史、文档集合名称
- **输出**: (更新后的历史, 清空的输入框)
- **功能**: 处理用户查询并返回AI响应

### 清空聊天
```python
def clear_chat() -> tuple
```
- **输入**: 无
- **输出**: (空历史, 空输入框)
- **功能**: 清空聊天历史

### 2. MCP工具API

#### list_docset
```python
def list_docset() -> str
```
- **功能**: 列出所有文档集合
- **返回**: 文档集合列表字符串
- **MCP端点**: `/gradio_api/list_docset`

#### ask
```python
def ask(query: str, docset: str = None) -> str
```
- **功能**: 查询知识库
- **参数**: 
  - `query`: 查询文本
  - `docset`: 可选的文档集合名称
- **返回**: 查询结果字符串
- **MCP端点**: `/gradio_api/ask`

### 3. 存储管理API

#### SupabaseDocsetManager

### 初始化
```python
def __init__(self):
    # 从环境变量获取Supabase配置
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    self.supabase: Client = create_client(supabase_url, supabase_key)
    # 注册默认爬虫
    register_default_crawlers()
```

**核心方法**:

- **创建文档集合**
```python
def create_docset(self, name: str, description: str = "") -> str
```

- **列出文档集合**
```python
def list_docsets(self) -> str
```

- **获取文档集合**
```python
def get_docset_by_name(self, name: str) -> Optional[Dict]
```

- **添加文档**
```python
def add_document_to_docset(self, docset_name: str, title: str, content: str, 
                          doc_type: str = "file", metadata: Optional[Dict] = None, 
                          parent_id: Optional[str] = None) -> str
```

- **列出文档**
```python
def list_documents_in_docset(self, docset_name: str) -> List[Dict]
```

- **查询知识库**
```python
def query_knowledge_base(self, query: str, docset_name: Optional[str] = None) -> str
```

- **获取文档集合字典**
```python
def get_docsets_dict(self) -> Dict[str, Dict]
```

- **添加URL内容**
```python
def add_url_to_docset(self, url: str, docset_name: str, **kwargs) -> str
```

- **添加GitHub仓库**
```python
def add_github_repo_to_docset(self, repo_url: str, docset_name: str, branch: str = "main") -> str
```

- **获取文档及其子文档**
```python
def get_document_with_children(self, docset_name: str, document_name: str) -> Optional[Dict]
```

- **获取子文档**
```python
def get_child_documents(self, parent_id: str) -> List[Dict]
```

- **获取爬虫速率限制信息**
```python
def get_crawler_rate_limit(self, url: str) -> Dict[str, Any]
```

## 环境配置

### 必需的环境变量

```bash
# Supabase配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# 可选配置
GRADIO_SERVER_PORT=8000
GRADIO_SERVER_NAME=0.0.0.0
```

### 环境变量文件

**位置**: `env.example`
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Gradio Configuration
GRADIO_SERVER_PORT=8000
GRADIO_SERVER_NAME=0.0.0.0
```

## 部署配置

### Docker配置

**位置**: `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "app.py"]
```

### Render配置

**位置**: `render.yaml`
```yaml
services:
  - type: web
    name: ragspace
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
```

## 数据库迁移

### 初始化迁移

**位置**: `supabase/migrations/20241201000000_create_ragspace_schema.sql`

```sql
-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建文档集合表
CREATE TABLE IF NOT EXISTS docsets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  description text,
  created_at timestamp DEFAULT now()
);

-- 创建文档表
CREATE TABLE IF NOT EXISTS documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  docset_id uuid REFERENCES docsets(id) ON DELETE CASCADE,
  name text,
  type text CHECK (type IN ('file', 'url', 'github', 'website')),
  url text,
  content text,
  added_date timestamp DEFAULT now()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_documents_docset_id ON documents(docset_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(type);
CREATE INDEX IF NOT EXISTS idx_documents_added_date ON documents(added_date);

-- 启用行级安全策略
ALTER TABLE docsets ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 创建访问策略
CREATE POLICY "Allow public read access to docsets" ON docsets
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to docsets" ON docsets
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to documents" ON documents
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to documents" ON documents
  FOR INSERT WITH CHECK (true);
```

## 项目结构

```
fun-withus-ragspace/
├── src/ragspace/
│   ├── config/           # 配置管理
│   │   ├── __init__.py
│   │   └── crawler_config.py  # 爬虫配置系统
│   ├── models/           # 数据模型
│   │   ├── document.py   # 文档模型
│   │   └── docset.py     # 文档集合模型
│   ├── services/         # 爬虫服务
│   │   ├── __init__.py
│   │   ├── crawler_interface.py  # 爬虫接口定义
│   │   ├── github_crawler.py     # GitHub爬虫实现
│   │   ├── website_crawler.py    # 网站爬虫实现
│   │   └── mock_crawler.py       # Mock爬虫实现
│   ├── storage/          # 存储管理
│   │   ├── manager.py    # 内存存储管理器
│   │   └── supabase_manager.py  # Supabase存储管理器
│   ├── ui/               # 用户界面
│   │   ├── handlers.py   # 事件处理器
│   │   └── components/   # UI组件
│   │       ├── knowledge_management.py
│   │       ├── chat_interface.py
│   │       └── mcp_tools.py
│   └── mcp/              # MCP协议
│       └── tools.py      # MCP工具定义
├── supabase/             # 数据库配置
│   ├── config.toml       # Supabase配置
│   ├── migrations/       # 数据库迁移
│   └── seed.sql          # 种子数据
├── tests/                # 测试文件
├── app.py               # 主应用入口
├── dev.py               # 开发服务器
├── pyproject.toml       # Poetry配置
├── requirements.txt      # 依赖列表
├── Dockerfile           # Docker配置
└── render.yaml          # Render部署配置
```

## 使用示例

### 1. 启动应用

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export SUPABASE_URL=your_supabase_url
export SUPABASE_KEY=your_supabase_key

# 启动应用
python app.py
```

### 2. 使用MCP工具

```bash
# 使用mcp-inspector测试
mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/list

# 查询知识库
mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name ask --params '{"query": "What documents do I have?", "docset": null}'
```

### 3. 数据库操作

```python
from src.ragspace.storage import docset_manager

# 创建文档集合
result = docset_manager.create_docset("My Docs", "My documentation collection")

# 添加文档
result = docset_manager.add_document_to_docset("My Docs", "README", "This is my README content", "file")

# 查询知识库
result = docset_manager.query_knowledge_base("What is in my docs?", "My Docs")
```

### 4. 爬虫系统使用

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

# 检查配置
github_config = CrawlerConfig.get_github_config()
if not github_config['token']:
    print("警告: 未设置GitHub令牌")

# 添加GitHub仓库
result = docset_manager.add_github_repo_to_docset("owner/repo", "my-docset")

# 添加网站内容
result = docset_manager.add_url_to_docset("https://example.com", "my-docset")
```

## 错误处理

### 常见错误

1. **Supabase连接错误**
   - 检查环境变量SUPABASE_URL和SUPABASE_KEY
   - 确认网络连接正常

2. **数据库表不存在**
   - 运行数据库迁移脚本
   - 检查Supabase项目配置

3. **MCP工具调用失败**
   - 确认应用正在运行
   - 检查端口8000是否可用

### 调试信息

应用会输出详细的调试信息：
- ✅ 成功操作
- ❌ 错误操作
- INFO: 信息日志

## 扩展计划

### 即将实现的功能

1. **向量搜索**: 集成pgvector进行语义搜索
2. **用户认证**: 多用户支持和权限管理
3. **文件处理**: 支持更多文件格式（PDF、DOCX等）
4. **实时同步**: WebSocket实时更新
5. **API文档**: 自动生成OpenAPI文档

### 技术改进

1. **性能优化**: 查询缓存和索引优化
2. **安全增强**: 输入验证和SQL注入防护
3. **监控告警**: 应用性能监控
4. **容器化**: 完整的Docker Compose配置

---

*最后更新: 2024年12月* 