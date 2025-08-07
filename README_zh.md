# RAGSpace - AI 知识中心

[English](README.md) | [中文](README_zh.md)

🤖 构建和查询您的个人知识库，获得AI辅助。

## 🚀 快速开始

### 前置要求

1. **Supabase 项目**: 在 [supabase.com](https://supabase.com) 创建新项目
2. **环境配置**: 复制并配置环境变量

### 本地安装

1. **克隆并安装**
   ```bash
   git clone https://github.com/your-username/ragspace.git
   cd ragspace
   pip install -r requirements.txt
   ```

2. **配置环境**
   ```bash
   cp env.example .env
   # 编辑 .env 文件，填入您的 Supabase 凭据
   ```

3. **运行应用**
   ```bash
   python app.py
   ```

4. **打开浏览器**
   访问 `http://localhost:8000`

## ✨ 功能特性

- **📚 知识库管理**: 上传文件、添加网站、导入 GitHub 仓库
- **🕷️ 网络爬虫系统**: 自动从 URL 和 GitHub 仓库提取内容
- **💬 AI 聊天界面**: 用自然语言查询您的知识库
- **🔗 MCP 集成**: 连接 Cursor、Claude Desktop 和其他 LLM 客户端
- **🎨 现代界面**: 标签式界面，侧边栏布局，响应式设计
- **🗄️ Supabase 数据库**: 持久化存储，PostgreSQL 和实时功能
- **⚙️ 可配置爬虫**: 基于环境变量的所有爬虫配置
- **🚀 轻松部署**: 一键部署到 Render、Railway 或 Hugging Face Spaces

## 🎯 使用场景

### 个人知识管理
- **研究论文**: 上传和查询学术论文
- **项目文档**: 为您的项目构建知识库
- **学习笔记**: 组织学习材料和笔记
- **技术文档**: 存储和搜索技术指南

### 团队协作
- **共享知识库**: 创建团队文档中心
- **代码文档**: 导入 GitHub 仓库进行代码搜索
- **流程文档**: 存储和查询团队流程
- **会议记录**: 组织和搜索会议记录

### 社区知识分享
- **开源项目**: 为您的项目创建文档中心
- **技术社区**: 与社区分享知识
- **教育内容**: 构建学习资源集合
- **小众技术**: 记录罕见或专业的技术

## 📖 使用方法

### 1. 创建文档集
1. 进入 "📚 知识管理" 标签
2. 输入知识库的名称和描述
3. 点击 "创建文档集"

### 2. 添加内容
您可以通过三种方式添加内容：

#### 文件上传
1. 从侧边栏选择您的文档集
2. 进入 "📁 添加文件" 标签
3. 上传 PDF、TXT、MD 或其他文本文件
4. 文件将自动处理并嵌入

#### 网站内容
1. 从侧边栏选择您的文档集
2. 进入 "🌐 添加 URL" 标签
3. 输入网站 URL
4. 选择内容类型（网站、文档等）
5. 点击 "添加 URL"

#### GitHub 仓库
1. 从侧边栏选择您的文档集
2. 进入 "🐙 添加 GitHub 仓库" 标签
3. 输入仓库 URL（例如：`owner/repo` 或 `https://github.com/owner/repo`）
4. 可选择指定分支
5. 点击 "添加仓库"

### 3. 查询您的知识库
1. 进入 "💬 聊天界面" 标签
2. 从下拉菜单选择您的文档集
3. 用自然语言提问
4. 获得带有来源引用的 AI 回答

### 4. 与 MCP 客户端一起使用
连接 Cursor、Claude Desktop 或其他 LLM 客户端：

#### Cursor 集成
1. 打开 Cursor 设置 → MCP 服务器
2. 添加服务器配置：
   ```json
   {
     "name": "RAGSpace",
     "description": "查询您的知识库",
     "sse_url": "https://your-app.onrender.com/gradio_api/mcp"
   }
   ```

#### Claude Desktop 集成
1. 打开 Claude Desktop 设置 → MCP 服务器
2. 添加与上面相同的配置

## 🔧 MCP 集成

RAGSpace 包含内置的 MCP（模型上下文协议）服务器，允许 LLM 客户端访问您的知识库。

### 可用的 MCP 工具

**核心工具:**
- `list_docset` - 列出所有文档集合
- `ask` - 用自然语言查询您的知识库

### 测试 MCP 服务器

1. **安装 mcp-remote**
   ```bash
   npm install -g mcp-remote
   ```

2. **创建配置文件** `mcp_inspector_config.json`:
   ```json
   {
     "mcpServers": {
       "ragspace": {
         "command": "npx",
         "args": ["mcp-remote", "http://localhost:8000/gradio_api/mcp/"],
         "env": {}
       }
     }
   }
   ```

3. **测试连接**
   ```bash
   # 列出可用工具
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/list
   
   # 提问
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name ask --params '{"query": "What is available?", "docset": null}'
   ```

## 🚀 部署

### Render（推荐）

1. **Fork 此仓库**
2. **连接到 Render**
   - 前往 [Render 控制台](https://dashboard.render.com)
   - 点击 "New Web Service"
   - 连接您的 GitHub 仓库

3. **配置服务**
   - **名称**: `ragspace`
   - **环境**: `Python`
   - **构建命令**: `pip install -r requirements.txt`
   - **启动命令**: `python app.py`

4. **设置环境变量**
   - 从 `env.example` 添加所有必需的环境变量

5. **部署**
   - 点击 "Create Web Service"

### 其他平台

- **Railway**: 使用 `railway.json` 配置
- **Hugging Face Spaces**: 使用 Spaces 配置
- **Docker**: 使用提供的 `Dockerfile`

## ⚙️ 配置

### 环境变量

#### 必需变量
| 变量 | 描述 | 默认值 |
|------|------|--------|
| `SUPABASE_URL` | Supabase 项目 URL | (必需) |
| `SUPABASE_KEY` | Supabase API 密钥 | (必需) |
| `PORT` | 服务器端口 | `8000` |
| `DEBUG` | 调试模式 | `false` |

#### GitHub 爬虫配置
| 变量 | 描述 | 默认值 |
|------|------|--------|
| `GITHUB_TOKEN` | GitHub API 令牌 | (可选) |
| `GITHUB_FILE_TYPES` | 支持的文件类型 | `.md,.py,.js,.ts,.txt,.rst,.adoc,.json,.yaml,.yml` |
| `GITHUB_MAX_FILE_SIZE` | 最大文件大小（字节） | `50000` |
| `GITHUB_MAX_DEPTH` | 最大目录深度 | `10` |

#### 网站爬虫配置
| 变量 | 描述 | 默认值 |
|------|------|--------|
| `WEBSITE_MAX_DEPTH` | 最大爬取深度 | `3` |
| `WEBSITE_MAX_PAGES` | 最大爬取页面数 | `10` |
| `WEBSITE_TIMEOUT` | 请求超时（秒） | `10` |

## 🏗️ 开发

### 项目结构

```
fun-withus-ragspace/
├── src/
│   └── ragspace/
│       ├── config/                    # 配置管理
│       ├── models/                    # 数据模型
│       ├── services/                  # 爬虫服务
│       ├── storage/                   # 数据库管理
│       ├── ui/                        # UI 组件
│       └── mcp/                       # MCP 服务器
├── app.py              # 主应用入口点
├── tests/              # 测试文件
└── supabase/           # 数据库迁移
```

### 开发环境设置

#### 使用 Poetry（推荐）

1. **安装 Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **安装依赖**
   ```bash
   poetry install
   ```

3. **设置 Supabase CLI**
   ```bash
   ./scripts/supabase_setup.sh
   ```

4. **应用数据库迁移**
   ```bash
   supabase db push
   ```

5. **运行应用**
   ```bash
   poetry run python app.py
   ```

#### 使用 pip

1. **设置虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用**
   ```bash
   python app.py
   ```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试类别
pytest tests/test_crawler_system.py
pytest tests/test_ui_integration.py
```

## 📊 数据结构

### 数据库架构

#### 文档集表
```sql
CREATE TABLE docsets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  description text,
  created_at timestamp DEFAULT now()
);
```

#### 文档表
```sql
CREATE TABLE documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  docset_id uuid REFERENCES docsets(id) ON DELETE CASCADE,
  parent_id uuid REFERENCES documents(id) ON DELETE CASCADE,
  name text NOT NULL,
  type text CHECK (type IN ('file', 'url', 'github', 'website', 'github_file', 'github_readme', 'github_repo', 'repository', 'document', 'code', 'config', 'readme', 'documentation', 'configuration', 'data', 'image', 'binary', 'unknown')),
  url text,
  content text,
  metadata jsonb DEFAULT '{}',
  added_date timestamp DEFAULT now()
);
```

### 爬虫系统

系统包含灵活的爬虫架构：

#### 可用爬虫
- **GitHubCrawler**: 获取仓库内容和单个文件
- **WebsiteCrawler**: 从一般网站提取内容
- **MockCrawler**: 为开发提供测试数据

#### 爬虫接口
```python
class CrawlerInterface:
    def crawl(self, url: str, **kwargs) -> CrawlResult
    def can_handle(self, url: str) -> bool
    def get_supported_url_patterns(self) -> List[str]
    def get_rate_limit_info(self) -> Dict[str, Any]
```

## 🔄 开发阶段

### 第一阶段：基础 ✅
- [x] 基础 Gradio 界面
- [x] MCP 服务器集成
- [x] 部署配置
- [x] 文件上传界面

### 第二阶段：数据摄取 ✅
- [x] GitHub 仓库爬虫
- [x] 网络爬取功能
- [x] 文档处理管道
- [x] 配置管理系统

### 第三阶段：RAG 实现 ✅
- [x] 向量数据库集成
- [x] 语义搜索功能
- [x] LLM 集成响应
- [x] 上下文检索和生成

### 第四阶段：RAG-UI 集成 ✅
- [x] 知识管理与 RAG 集成
- [x] 聊天界面与 RAG 增强
- [x] MCP 工具与 RAG 集成
- [x] UI 反馈和状态管理

### 第五阶段：高级功能 📋
- [ ] 多用户认证
- [ ] 知识库管理
- [ ] 社区分享功能
- [ ] 高级分析

## 🤝 贡献

1. **Fork 仓库**
2. **创建功能分支**: `git checkout -b feature/amazing-feature`
3. **提交更改**: `git commit -m 'Add amazing feature'`
4. **推送到分支**: `git push origin feature/amazing-feature`
5. **打开 Pull Request**

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 🆘 支持

- **GitHub Issues**: [报告错误或请求功能](https://github.com/your-username/ragspace/issues)
- **Discussions**: [加入社区](https://github.com/your-username/ragspace/discussions)
- **Documentation**: [完整文档](https://github.com/your-username/ragspace/wiki)

## 🗺️ 路线图

- [ ] **多用户支持**: 团队协作和分享
- [ ] **高级分析**: 使用洞察和性能指标
- [ ] **API 市场**: 第三方集成和插件
- [ ] **移动支持**: 移动优化界面
- [ ] **高级搜索**: 多模态搜索功能

---

使用 [Gradio](https://gradio.app) 和 [MCP](https://modelcontextprotocol.io) 构建 ❤️
