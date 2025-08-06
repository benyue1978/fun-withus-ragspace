# RAGSpace GitHub 集成功能

## 概述

RAGSpace现在支持直接从GitHub仓库抓取内容，将RAG从手动上传扩展到自动抓取。这个功能允许用户输入GitHub仓库URL，系统会自动抓取仓库中的文档和代码文件。

## 功能特性

### ✅ 核心功能
- **自动抓取**: 输入GitHub仓库URL，自动抓取所有相关文件
- **智能过滤**: 只抓取文档和代码文件（.md, .py, .js, .ts, .txt等）
- **大小限制**: 自动跳过大于50KB的文件，避免embedding失败
- **分支支持**: 支持指定分支（默认为main）
- **结构化存储**: 将仓库作为父文档，文件作为子文档存储

### ✅ 支持的文件类型
- **文档**: `.md`, `.txt`, `.rst`, `.adoc`
- **代码**: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`
- **配置**: `.json`, `.yaml`, `.yml`, `.toml`
- **其他**: `.sql`, `.sh`, `.bat`

## 技术实现

### 1. 数据结构设计

采用父子文档结构，保持向后兼容：

```json
{
  "type": "github",
  "name": "owner/repo",
  "url": "https://github.com/owner/repo",
  "content": "GitHub repository: owner/repo\n\nThis repository contains X files.",
  "metadata": {
    "repo": "owner/repo",
    "branch": "main",
    "file_count": 15,
    "owner": "owner",
    "repository": "repo"
  },
  "children": [
    {
      "type": "github_file",
      "name": "README.md",
      "url": "https://github.com/owner/repo/blob/main/README.md",
      "content": "# Project Title\n\nProject description...",
      "metadata": {
        "repo": "owner/repo",
        "branch": "main",
        "path": "README.md",
        "size": 1024,
        "sha": "abc123..."
      }
    }
  ]
}
```

### 2. GitHub API 集成

使用GitHub官方API，支持：
- **匿名访问**: 无需token即可访问public仓库
- **Token支持**: 使用token获得更高速率限制
- **递归遍历**: 自动遍历仓库目录结构
- **内容解码**: 自动解码base64编码的文件内容

### 3. 速率限制处理

| 访问方式 | 速率限制 | 建议用途 |
|----------|----------|----------|
| 匿名访问 | 60次/小时/IP | 开发测试 |
| Token访问 | 5000次/小时/token | 生产环境 |

## 使用方法

### 1. 环境配置

```bash
# 在.env文件中添加GitHub token（可选但推荐）
GITHUB_TOKEN=your-github-token
```

### 2. Web界面使用

1. 打开RAGSpace Web界面
2. 进入"📚 Knowledge Management"标签
3. 选择目标DocSet
4. 点击"🐙 Add GitHub Repo"标签
5. 输入GitHub仓库URL（支持多种格式）：
   - `https://github.com/owner/repo`
   - `github.com/owner/repo`
   - `owner/repo`
6. 可选：指定分支（默认为main）
7. 点击"Add Repository"按钮

### 3. API使用

```python
from src.ragspace.storage import docset_manager

# 添加GitHub仓库到DocSet
result = docset_manager.add_github_repo_to_docset(
    repo_url="owner/repo",
    docset_name="My Docs",
    branch="main"
)
print(result)
```

### 4. MCP工具使用

```bash
# 通过MCP工具添加GitHub仓库
mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name add_github_repo --params '{"repo_url": "owner/repo", "docset_name": "My Docs"}'
```

## 支持的URL格式

GitHub服务支持多种URL格式：

### ✅ 支持的格式
- `https://github.com/owner/repo`
- `github.com/owner/repo`
- `owner/repo`

### ❌ 不支持的格式
- `https://github.com/owner/repo/tree/main` (会自动提取为owner/repo)
- `https://github.com/owner/repo/blob/main/file.md` (会抓取整个仓库)

## 数据库迁移

### 新增字段

```sql
-- 添加children字段用于存储子文档
ALTER TABLE documents ADD COLUMN children jsonb DEFAULT '[]';

-- 添加metadata字段用于存储元数据
ALTER TABLE documents ADD COLUMN metadata jsonb DEFAULT '{}';

-- 添加索引以提高查询性能
CREATE INDEX idx_documents_children ON documents USING GIN (children);
CREATE INDEX idx_documents_metadata ON documents USING GIN (metadata);

-- 更新类型约束
ALTER TABLE documents ADD CONSTRAINT documents_type_check 
  CHECK (type IN ('file', 'url', 'github', 'website', 'github_file', 'github_readme'));
```

### 应用迁移

```bash
# 在Supabase控制台中运行迁移
supabase db push
```

## 错误处理

### 常见错误及解决方案

| 错误类型 | 原因 | 解决方案 |
|----------|------|----------|
| `Invalid GitHub URL` | URL格式不正确 | 检查URL格式，确保为owner/repo格式 |
| `Repository not found` | 仓库不存在或私有 | 确认仓库存在且为public |
| `Rate limit exceeded` | 超过API速率限制 | 添加GitHub token或等待重置 |
| `File too large` | 文件超过50KB限制 | 系统会自动跳过大文件 |
| `Branch not found` | 分支不存在 | 检查分支名称，默认为main |

### 调试信息

系统会输出详细的调试信息：
- ✅ 成功抓取的文件
- ⚠️ 跳过的文件（大小超限）
- ❌ 失败的文件及原因
- 📊 速率限制信息

## 性能优化

### 1. 文件过滤策略
- **类型过滤**: 只抓取文档和代码文件
- **大小限制**: 跳过大于50KB的文件
- **路径过滤**: 可配置忽略特定路径（如node_modules）

### 2. 缓存策略
- **内容缓存**: 避免重复抓取相同文件
- **结构缓存**: 缓存仓库目录结构
- **增量更新**: 支持增量更新已存在的仓库

### 3. 并发控制
- **请求限流**: 控制API请求频率
- **错误重试**: 自动重试失败的请求
- **超时处理**: 设置合理的请求超时时间

## 安全考虑

### 1. Token安全
- **环境变量**: Token存储在环境变量中
- **最小权限**: 只请求必要的API权限
- **定期轮换**: 建议定期更新Token

### 2. 内容安全
- **内容验证**: 验证下载的文件内容
- **大小限制**: 防止恶意大文件攻击
- **类型检查**: 只处理安全的文件类型

## 测试

### 运行测试脚本

```bash
# 测试GitHub集成功能
python test_github_integration.py
```

### 测试用例

1. **URL解析测试**: 验证各种URL格式的解析
2. **API连接测试**: 测试GitHub API连接
3. **仓库抓取测试**: 测试完整仓库抓取流程
4. **数据库集成测试**: 测试Supabase存储集成

## 未来计划

### 1. 即将实现的功能
- **私有仓库支持**: 支持私有仓库访问
- **增量更新**: 只更新变更的文件
- **Webhook支持**: 自动同步仓库更新
- **多分支支持**: 同时抓取多个分支

### 2. 性能优化
- **并行抓取**: 并发抓取多个文件
- **智能缓存**: 基于文件哈希的智能缓存
- **压缩存储**: 压缩存储大文件内容

### 3. 用户体验
- **进度显示**: 实时显示抓取进度
- **错误恢复**: 支持失败重试
- **批量操作**: 支持批量添加多个仓库

---

*最后更新: 2024年12月* 