# RAGSpace API 端点文档

## 概述

RAGSpace提供多种API接口，包括Web界面API、MCP工具API和REST API。本文档详细描述了所有可用的API端点。

## API 基础信息

- **基础URL**: `http://localhost:8000`
- **协议**: HTTP/HTTPS
- **认证**: 目前为公开访问（未来将支持JWT认证）
- **数据格式**: JSON

## 1. Web界面API (Gradio)

### 1.1 知识管理端点

#### 创建文档集合
- **端点**: `/gradio_api/create_docset_ui`
- **方法**: POST
- **参数**:
  - `name` (string): 文档集合名称
  - `description` (string): 文档集合描述
- **返回**: 操作结果字符串
- **示例**:
```python
# 通过Gradio界面调用
create_docset_ui("My Docs", "My documentation collection")
```

#### 上传文件到文档集合
- **端点**: `/gradio_api/upload_file_to_docset`
- **方法**: POST
- **参数**:
  - `files` (list): 文件列表
  - `docset_name` (string): 目标文档集合名称
- **返回**: 上传结果字符串
- **示例**:
```python
# 通过Gradio界面调用
upload_file_to_docset([file1, file2], "My Docs")
```

#### 添加网站到文档集合
- **端点**: `/gradio_api/add_url_to_docset`
- **方法**: POST
- **参数**:
  - `url` (string): 网站URL
  - `docset_name` (string): 目标文档集合名称
  - `website_type` (string): 网站类型（默认"website"）
- **返回**: 操作结果字符串
- **示例**:
```python
# 通过Gradio界面调用
add_url_to_docset("https://example.com", "My Docs", "website")
```

#### 添加GitHub仓库到文档集合
- **端点**: `/gradio_api/add_github_repo_to_docset`
- **方法**: POST
- **参数**:
  - `repo_url` (string): GitHub仓库URL
  - `docset_name` (string): 目标文档集合名称
- **返回**: 操作结果字符串
- **示例**:
```python
# 通过Gradio界面调用
add_github_repo_to_docset("owner/repo", "My Docs")
```

### 1.2 聊天端点

#### 处理查询
- **端点**: `/gradio_api/process_query`
- **方法**: POST
- **参数**:
  - `query` (string): 查询文本
  - `history` (list): 聊天历史
  - `docset_name` (string, optional): 文档集合名称
- **返回**: (更新后的历史, 清空的输入框)
- **示例**:
```python
# 通过Gradio界面调用
process_query("What documents do I have?", [], "My Docs")
```

#### 清空聊天历史
- **端点**: `/gradio_api/clear_chat`
- **方法**: POST
- **参数**: 无
- **返回**: (空历史, 空输入框)
- **示例**:
```python
# 通过Gradio界面调用
clear_chat()
```

## 2. MCP工具API

### 2.1 list_docset
- **端点**: `/gradio_api/list_docset`
- **方法**: POST
- **参数**: 无
- **返回**: 文档集合列表字符串
- **MCP工具名称**: `list_docset`
- **示例**:
```bash
# 使用mcp-inspector
mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/list

# 返回示例
Available DocSets:
- My Docs: My documentation collection
- Python Docs: Python documentation
```

### 2.2 ask
- **端点**: `/gradio_api/ask`
- **方法**: POST
- **参数**:
  - `query` (string): 查询文本
  - `docset` (string, optional): 文档集合名称
- **返回**: 查询结果字符串
- **MCP工具名称**: `ask`
- **示例**:
```bash
# 使用mcp-inspector
mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name ask --params '{"query": "What documents do I have?", "docset": null}'

# 返回示例
Found 3 relevant documents:

📄 [My Docs] README
Type: file
This is my README content...

📄 [My Docs] Documentation
Type: url
URL: https://example.com/docs
Documentation content...
```

## 3. 存储管理API

### 3.1 SupabaseDocsetManager 方法

#### 创建文档集合（存储管理）
```python
def create_docset(self, name: str, description: str = "") -> str
```
- **功能**: 创建新的文档集合
- **参数**:
  - `name` (string): 文档集合名称
  - `description` (string): 文档集合描述
- **返回**: 操作结果字符串
- **示例**:
```python
from src.ragspace.storage import docset_manager
result = docset_manager.create_docset("My Docs", "My documentation collection")
print(result)  # "✅ DocSet 'My Docs' created successfully."
```

#### 列出文档集合
```python
def list_docsets(self) -> str
```
- **功能**: 列出所有文档集合
- **返回**: 格式化的文档集合列表字符串
- **示例**:
```python
result = docset_manager.list_docsets()
print(result)
# 输出:
# 📚 Available DocSets:
# 
# 📁 My Docs
#    Description: My documentation collection
#    Documents: 5
#    Created: 2024-12-01 10:00:00
```

#### 获取文档集合
```python
def get_docset_by_name(self, name: str) -> Optional[Dict]
```
- **功能**: 根据名称获取文档集合
- **参数**:
  - `name` (string): 文档集合名称
- **返回**: 文档集合字典或None
- **示例**:
```python
docset = docset_manager.get_docset_by_name("My Docs")
if docset:
    print(f"Found docset: {docset['name']}")
```

#### 添加文档到文档集合
```python
def add_document_to_docset(self, docset_name: str, title: str, content: str, 
                          doc_type: str = "file", metadata: Optional[Dict] = None) -> str
```
- **功能**: 添加文档到指定文档集合
- **参数**:
  - `docset_name` (string): 目标文档集合名称
  - `title` (string): 文档标题
  - `content` (string): 文档内容
  - `doc_type` (string): 文档类型（file/url/github/website）
  - `metadata` (dict, optional): 元数据
- **返回**: 操作结果字符串
- **示例**:
```python
result = docset_manager.add_document_to_docset(
    "My Docs", 
    "README", 
    "This is my README content", 
    "file",
    {"url": "https://github.com/owner/repo"}
)
```

#### 列出文档集合中的文档
```python
def list_documents_in_docset(self, docset_name: str) -> str
```
- **功能**: 列出指定文档集合中的所有文档
- **参数**:
  - `docset_name` (string): 文档集合名称
- **返回**: 格式化的文档列表字符串
- **示例**:
```python
result = docset_manager.list_documents_in_docset("My Docs")
print(result)
# 输出:
# 📚 Documents in DocSet 'My Docs':
# 
# 1. README
#    Type: file
#    ID: 123e4567-e89b-12d3-a456-426614174000
#    Added: 2024-12-01 10:00:00
```

#### 查询知识库
```python
def query_knowledge_base(self, query: str, docset_name: Optional[str] = None) -> str
```
- **功能**: 在知识库中搜索相关内容
- **参数**:
  - `query` (string): 查询文本
  - `docset_name` (string, optional): 限制搜索的文档集合名称
- **返回**: 查询结果字符串
- **示例**:
```python
result = docset_manager.query_knowledge_base("What is RAG?", "My Docs")
print(result)
# 输出:
# Found 2 relevant documents:
# 
# 📄 [My Docs] README
# Type: file
# This is my README content about RAG...
```

#### 获取文档集合字典
```python
def get_docsets_dict(self) -> Dict[str, Dict]
```
- **功能**: 获取所有文档集合的字典表示
- **返回**: 文档集合字典
- **示例**:
```python
docsets = docset_manager.get_docsets_dict()
for name, docset in docsets.items():
    print(f"{name}: {docset['description']}")
```

## 4. 错误响应格式

### 4.1 成功响应
```
✅ Operation completed successfully.
```

### 4.2 错误响应
```
❌ Error: [错误描述]
```

### 4.3 常见错误类型

1. **文档集合不存在**
```
DocSet 'My Docs' not found. Please create it first.
```

1. **文档集合已存在**
   ```
   DocSet 'My Docs' already exists.
   ```

2. **Supabase连接错误**
   ```
   ❌ Error creating docset: [连接错误详情]
   ```

3. **参数验证错误**
   ```
   Please provide a query.
   Please specify a docset name.
   ```

## 5. 使用示例

### 5.1 Python客户端示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 创建文档集合
def create_docset(name, description):
    response = requests.post(f"{BASE_URL}/gradio_api/create_docset_ui", 
                           data={"name": name, "description": description})
    return response.text

# 查询知识库
def query_knowledge(query, docset=None):
    data = {"query": query}
    if docset:
        data["docset"] = docset
    response = requests.post(f"{BASE_URL}/gradio_api/ask", data=data)
    return response.text

# 使用示例
create_docset("My Docs", "My documentation collection")
result = query_knowledge("What is RAG?", "My Docs")
print(result)
```

### 5.2 cURL示例

```bash
# 创建文档集合
curl -X POST "http://localhost:8000/gradio_api/create_docset_ui" \
     -d "name=My Docs" \
     -d "description=My documentation collection"

# 查询知识库
curl -X POST "http://localhost:8000/gradio_api/ask" \
     -d "query=What is RAG?" \
     -d "docset=My Docs"
```

### 5.3 JavaScript示例

```javascript
// 创建文档集合
async function createDocset(name, description) {
    const response = await fetch('http://localhost:8000/gradio_api/create_docset_ui', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}`
    });
    return await response.text();
}

// 查询知识库
async function queryKnowledge(query, docset = null) {
    const data = new URLSearchParams();
    data.append('query', query);
    if (docset) {
        data.append('docset', docset);
    }
    
    const response = await fetch('http://localhost:8000/gradio_api/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: data
    });
    return await response.text();
}

// 使用示例
createDocset("My Docs", "My documentation collection")
    .then(result => console.log(result));

queryKnowledge("What is RAG?", "My Docs")
    .then(result => console.log(result));
```

## 6. 限制和注意事项

### 6.1 当前限制
- 文档内容大小限制：取决于Supabase配置
- 并发请求限制：取决于服务器配置
- 文件上传限制：取决于Gradio配置

### 6.2 安全注意事项
- 目前为公开访问，生产环境需要添加认证
- 输入验证需要加强
- SQL注入防护需要完善

### 6.3 性能考虑
- 大量文档查询可能需要优化
- 向量搜索功能待实现
- 缓存机制待添加

## 7. 未来计划

### 7.1 即将添加的端点
- 用户认证端点
- 文档删除端点
- 文档更新端点
- 批量操作端点

### 7.2 计划的功能
- RESTful API标准化
- OpenAPI文档自动生成
- 速率限制
- 请求日志记录

---

*最后更新: 2024年12月* 