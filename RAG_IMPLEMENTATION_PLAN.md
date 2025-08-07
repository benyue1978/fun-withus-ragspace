# RAGSpace RAG Implementation Plan

## 概述

本文档详细描述了RAGSpace项目中RAG（Retrieval-Augmented Generation）系统的实现计划，包括具体的实现步骤、代码结构、时间安排和验收标准。

## 实现阶段

### Phase 1: 核心RAG基础设施 (Week 1)

#### 1.1 数据库架构实现

**目标**: 建立向量数据库基础设施

**任务**:
- [ ] 创建chunks表
- [ ] 配置pgvector扩展
- [ ] 建立向量索引
- [ ] 添加文档状态管理

**实现步骤**:

1. **创建chunks表**
```sql
-- 在Supabase SQL Editor中执行
CREATE TABLE chunks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  docset_name TEXT NOT NULL,
  document_name TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- 创建向量索引
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 创建复合索引
CREATE INDEX idx_chunks_docset_document ON chunks(docset_name, document_name);
CREATE INDEX idx_chunks_metadata ON chunks USING GIN (metadata);
```

2. **更新documents表**
```sql
-- 添加嵌入状态字段
ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding_status TEXT 
DEFAULT 'pending' CHECK (embedding_status IN ('pending', 'processing', 'done', 'error'));

-- 添加嵌入时间字段
ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP;
```

**验收标准**:
- [ ] chunks表成功创建
- [ ] 向量索引正常工作
- [ ] 文档状态字段正确添加
- [ ] 数据库查询性能良好

#### 1.2 文本分片器实现

**目标**: 实现智能文档分片功能

**任务**:
- [ ] 实现基础文本分片器
- [ ] 实现代码分片器
- [ ] 添加分片策略选择
- [ ] 集成到现有系统

**实现步骤**:

1. **创建文本分片器模块**
```python
# src/ragspace/rag/text_splitter.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict

class RAGTextSplitter:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " "],
            length_function=len
        )
        
        self.code_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
            separators=["\nclass ", "\ndef ", "\n", " "],
            length_function=len
        )
    
    def split_text(self, content: str, doc_type: str = "text") -> List[Dict]:
        """分片文本内容"""
        if doc_type in ['github_file', 'code']:
            chunks = self.code_splitter.split_text(content)
        else:
            chunks = self.text_splitter.split_text(content)
        
        return [
            {
                "content": chunk.page_content,
                "metadata": {
                    "chunk_index": i,
                    "doc_type": doc_type,
                    "length": len(chunk.page_content)
                }
            }
            for i, chunk in enumerate(chunks)
        ]
```

2. **集成到现有系统**
```python
# src/ragspace/services/__init__.py
from .rag.text_splitter import RAGTextSplitter

# 在现有服务中使用
text_splitter = RAGTextSplitter()
chunks = text_splitter.split_text(document_content, doc_type)
```

**验收标准**:
- [ ] 文本分片器正常工作
- [ ] 代码分片器正确处理代码文件
- [ ] 分片大小和重叠设置合理
- [ ] 与现有系统集成良好

#### 1.3 嵌入工作器实现

**目标**: 实现异步文档嵌入处理

**任务**:
- [ ] 实现嵌入工作器类
- [ ] 添加异步处理支持
- [ ] 实现状态管理
- [ ] 添加错误处理

**实现步骤**:

1. **创建嵌入工作器**
```python
# src/ragspace/rag/embedding_worker.py
import asyncio
import logging
from typing import List, Dict
from supabase import create_client
import openai

logger = logging.getLogger(__name__)

class EmbeddingWorker:
    def __init__(self, model_name="openai"):
        self.model_name = model_name
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    async def process_document(self, doc_id: str):
        """处理单个文档的嵌入"""
        try:
            # 1. 更新状态为处理中
            self._update_status(doc_id, "processing")
            
            # 2. 获取文档内容
            document = self._get_document(doc_id)
            
            # 3. 分片文档
            text_splitter = RAGTextSplitter()
            chunks = text_splitter.split_text(
                document['content'], 
                document.get('doc_type', 'text')
            )
            
            # 4. 生成嵌入
            embeddings = await self._generate_embeddings(chunks)
            
            # 5. 存储到数据库
            self._store_chunks(document, chunks, embeddings)
            
            # 6. 更新状态为完成
            self._update_status(doc_id, "done")
            
        except Exception as e:
            self._update_status(doc_id, "error")
            logger.error(f"Embedding failed for doc {doc_id}: {e}")
    
    async def _generate_embeddings(self, chunks: List[Dict]) -> List[List[float]]:
        """生成文本嵌入"""
        texts = [chunk['content'] for chunk in chunks]
        
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        
        return [embedding.embedding for embedding in response.data]
    
    def _store_chunks(self, document: Dict, chunks: List[Dict], embeddings: List[List[float]]):
        """存储分片和嵌入到数据库"""
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_data = {
                "docset_name": document['docset_name'],
                "document_name": document['title'],
                "chunk_index": i,
                "content": chunk['content'],
                "embedding": embedding,
                "metadata": {
                    **chunk['metadata'],
                    "source_type": document.get('source_type', 'file'),
                    "url": document.get('url', ''),
                    "file_path": document.get('file_path', ''),
                    "language": document.get('language', ''),
                    "repo": document.get('repo', ''),
                    "commit_id": document.get('commit_id', '')
                }
            }
            
            self.supabase.table("chunks").insert(chunk_data).execute()
    
    def _update_status(self, doc_id: str, status: str):
        """更新文档嵌入状态"""
        self.supabase.table("documents").update({
            "embedding_status": status,
            "embedding_updated_at": datetime.now().isoformat()
        }).eq("id", doc_id).execute()
    
    def _get_document(self, doc_id: str) -> Dict:
        """获取文档内容"""
        response = self.supabase.table("documents").select("*").eq("id", doc_id).execute()
        return response.data[0] if response.data else None
```

2. **添加批量处理功能**
```python
async def batch_process(self, docset_name: str = None):
    """批量处理待嵌入的文档"""
    query = self.supabase.table("documents").select("id").eq("embedding_status", "pending")
    
    if docset_name:
        query = query.eq("docset_name", docset_name)
    
    response = query.execute()
    pending_docs = response.data
    
    for doc in pending_docs:
        await self.process_document(doc['id'])
        await asyncio.sleep(1)  # 避免API限制
```

**验收标准**:
- [ ] 嵌入工作器正常工作
- [ ] 异步处理支持良好
- [ ] 状态管理正确
- [ ] 错误处理完善

### Phase 2: 检索系统实现 (Week 2)

#### 2.1 向量检索实现

**目标**: 实现高效的向量相似度搜索

**任务**:
- [ ] 实现向量检索功能
- [ ] 添加DocSet过滤
- [ ] 优化查询性能
- [ ] 添加结果缓存

**实现步骤**:

1. **创建检索器类**
```python
# src/ragspace/rag/retriever.py
import numpy as np
from typing import List, Dict, Optional
from supabase import create_client
import openai

class RAGRetriever:
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    def retrieve_chunks(self, query: str, docsets: List[str] = None, top_k: int = 5) -> List[Dict]:
        """向量相似度检索"""
        # 1. 生成查询嵌入
        query_embedding = self._generate_query_embedding(query)
        
        # 2. 构建查询
        query_builder = self.supabase.table("chunks").select("*")
        
        if docsets and "all" not in docsets:
            query_builder = query_builder.in_("docset_name", docsets)
        
        # 3. 向量相似度搜索
        results = query_builder.order(
            f"embedding <-> '{query_embedding}'"
        ).limit(top_k).execute()
        
        return results.data
    
    def _generate_query_embedding(self, query: str) -> List[float]:
        """生成查询嵌入"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        return response.data[0].embedding
    
    def hybrid_retrieve(self, query: str, docsets: List[str] = None, 
                       top_k: int = 5, use_rerank: bool = True) -> List[Dict]:
        """混合检索策略"""
        # 1. 向量检索获取候选
        candidates = self.retrieve_chunks(query, docsets, top_k * 2)
        
        if not use_rerank:
            return candidates[:top_k]
        
        # 2. GPT重排序
        return self._gpt_rerank(query, candidates, top_k)
    
    def _gpt_rerank(self, query: str, chunks: List[Dict], top_k: int = 3) -> List[Dict]:
        """使用GPT进行重排序"""
        if not chunks:
            return []
        
        # 构建重排序提示
        prompt = self._build_rerank_prompt(query, chunks)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        try:
            ranking = json.loads(response.choices[0].message.content)
            return [chunks[i] for i in ranking[:top_k] if i < len(chunks)]
        except (json.JSONDecodeError, IndexError):
            # 如果重排序失败，返回原始结果
            return chunks[:top_k]
    
    def _build_rerank_prompt(self, query: str, chunks: List[Dict]) -> str:
        """构建重排序提示"""
        snippets_text = "\n".join([
            f"{i+1}. {chunk['content'][:200]}..." 
            for i, chunk in enumerate(chunks)
        ])
        
        return f"""
        You are an expert technical assistant.
        
        Given the following user question and a list of code/document snippets retrieved from a knowledge base, rank the snippets by how relevant they are to answering the question.
        
        Question: {query}
        
        Snippets:
        {snippets_text}
        
        Return the ranking as a JSON list of indices sorted from most to least relevant. Do not explain.
        Example: [2, 1, 3]
        """
```

2. **添加缓存机制**
```python
import redis
import hashlib
import json

class CachedRetriever(RAGRetriever):
    def __init__(self):
        super().__init__()
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0
        )
    
    def retrieve_chunks(self, query: str, docsets: List[str] = None, top_k: int = 5) -> List[Dict]:
        """带缓存的向量检索"""
        # 生成缓存键
        cache_key = self._generate_cache_key(query, docsets, top_k)
        
        # 尝试从缓存获取
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # 执行检索
        result = super().retrieve_chunks(query, docsets, top_k)
        
        # 缓存结果（5分钟过期）
        self.redis_client.setex(cache_key, 300, json.dumps(result))
        
        return result
    
    def _generate_cache_key(self, query: str, docsets: List[str], top_k: int) -> str:
        """生成缓存键"""
        key_data = {
            "query": query,
            "docsets": sorted(docsets or []),
            "top_k": top_k
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"rag_retrieval:{hashlib.md5(key_string.encode()).hexdigest()}"
```

**验收标准**:
- [ ] 向量检索功能正常
- [ ] DocSet过滤正确工作
- [ ] 查询性能良好（< 1秒）
- [ ] 缓存机制有效

#### 2.2 上下文组装实现

**目标**: 实现智能上下文组装功能

**任务**:
- [ ] 实现上下文组装器
- [ ] 添加源信息管理
- [ ] 优化上下文长度
- [ ] 添加上下文质量评估

**实现步骤**:

1. **创建上下文组装器**
```python
# src/ragspace/rag/context_assembler.py
from typing import List, Dict
import re

class ContextAssembler:
    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
    
    def assemble_context(self, chunks: List[Dict]) -> str:
        """组装上下文"""
        context_parts = []
        current_length = 0
        
        for chunk in chunks:
            # 构建源信息
            source_info = self._build_source_info(chunk)
            
            # 构建内容
            content = chunk['content']
            
            # 检查长度限制
            part_length = len(source_info) + len(content) + 10  # 额外空间
            if current_length + part_length > self.max_context_length:
                break
            
            # 添加到上下文
            context_parts.append(f"{source_info}\n{content}\n")
            current_length += part_length
        
        return "\n".join(context_parts)
    
    def _build_source_info(self, chunk: Dict) -> str:
        """构建源信息"""
        metadata = chunk.get('metadata', {})
        
        source_parts = []
        
        # 文档名称
        if 'document_name' in metadata:
            source_parts.append(f"Document: {metadata['document_name']}")
        
        # 文件路径
        if 'file_path' in metadata:
            source_parts.append(f"File: {metadata['file_path']}")
        
        # 行号信息
        if 'start_line' in metadata and 'end_line' in metadata:
            source_parts.append(f"Lines: {metadata['start_line']}-{metadata['end_line']}")
        
        # 仓库信息
        if 'repo' in metadata:
            source_parts.append(f"Repository: {metadata['repo']}")
        
        # 语言信息
        if 'language' in metadata:
            source_parts.append(f"Language: {metadata['language']}")
        
        if source_parts:
            return f"Source: {' | '.join(source_parts)}"
        else:
            return "Source: Unknown"
    
    def evaluate_context_quality(self, chunks: List[Dict]) -> Dict:
        """评估上下文质量"""
        if not chunks:
            return {"score": 0, "issues": ["No chunks provided"]}
        
        issues = []
        score = 100
        
        # 检查多样性
        unique_docs = len(set(chunk.get('metadata', {}).get('document_name', '') for chunk in chunks))
        if unique_docs < 2:
            issues.append("Limited document diversity")
            score -= 20
        
        # 检查内容长度
        total_length = sum(len(chunk['content']) for chunk in chunks)
        if total_length < 500:
            issues.append("Context too short")
            score -= 15
        elif total_length > self.max_context_length:
            issues.append("Context too long")
            score -= 10
        
        # 检查相关性（基于chunk顺序）
        if len(chunks) > 1:
            # 简单的相关性检查：相邻chunk来自同一文档
            consecutive_same_doc = 0
            for i in range(len(chunks) - 1):
                doc1 = chunks[i].get('metadata', {}).get('document_name', '')
                doc2 = chunks[i+1].get('metadata', {}).get('document_name', '')
                if doc1 == doc2:
                    consecutive_same_doc += 1
            
            if consecutive_same_doc > len(chunks) * 0.7:
                issues.append("Low content diversity")
                score -= 15
        
        return {
            "score": max(0, score),
            "issues": issues,
            "total_chunks": len(chunks),
            "total_length": total_length,
            "unique_documents": unique_docs
        }
```

**验收标准**:
- [ ] 上下文组装功能正常
- [ ] 源信息管理正确
- [ ] 长度限制有效
- [ ] 质量评估准确

### Phase 3: 响应生成系统 (Week 3)

#### 3.1 LLM响应生成实现

**目标**: 实现基于上下文的LLM响应生成

**任务**:
- [ ] 实现LLM响应生成器
- [ ] 添加流式响应支持
- [ ] 实现对话历史管理
- [ ] 添加响应质量评估

**实现步骤**:

1. **创建LLM响应生成器**
```python
# src/ragspace/rag/response_generator.py
import openai
from typing import List, Dict, Generator
import json

class RAGResponseGenerator:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    def generate_response(self, query: str, context: str, 
                         conversation_history: List[Dict] = None) -> str:
        """生成响应"""
        messages = self._build_messages(query, context, conversation_history)
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def generate_streaming_response(self, query: str, context: str,
                                  conversation_history: List[Dict] = None) -> Generator[str, None, None]:
        """生成流式响应"""
        messages = self._build_messages(query, context, conversation_history)
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _build_messages(self, query: str, context: str, 
                       conversation_history: List[Dict] = None) -> List[Dict]:
        """构建消息列表"""
        system_prompt = self._get_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话历史
        if conversation_history:
            for msg in conversation_history[-6:]:  # 保留最近6条消息
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # 添加当前查询和上下文
        user_prompt = self._build_user_prompt(query, context)
        messages.append({"role": "user", "content": user_prompt})
        
        return messages
    
    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """You are a helpful AI assistant with access to a knowledge base.

Your role is to:
1. Answer questions based on the provided context
2. Always cite your sources when possible
3. Be accurate and helpful
4. If the context doesn't contain enough information, say so
5. Provide clear and concise answers

When citing sources, use the format: [Document Name, Lines X-Y]"""
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """构建用户提示"""
        return f"""Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If you cite information from the context, please mention the source."""
    
    def evaluate_response_quality(self, response: str, query: str, context: str) -> Dict:
        """评估响应质量"""
        issues = []
        score = 100
        
        # 检查响应长度
        if len(response) < 50:
            issues.append("Response too short")
            score -= 20
        elif len(response) > 2000:
            issues.append("Response too long")
            score -= 10
        
        # 检查是否包含源引用
        if "[" in response and "]" in response:
            score += 10
        else:
            issues.append("No source citations")
            score -= 15
        
        # 检查是否回答了问题
        if not any(word in response.lower() for word in query.lower().split()):
            issues.append("Response may not address the question")
            score -= 20
        
        # 检查是否承认信息不足
        if "don't have enough information" in response.lower() or "context doesn't contain" in response.lower():
            score += 5  # 诚实回答加分
        
        return {
            "score": max(0, score),
            "issues": issues,
            "length": len(response),
            "has_citations": "[" in response and "]" in response,
            "addresses_question": any(word in response.lower() for word in query.lower().split())
        }
```

2. **添加对话历史管理**
```python
# src/ragspace/rag/conversation_manager.py
from typing import List, Dict
import json
from datetime import datetime

class ConversationManager:
    def __init__(self, max_history_length: int = 10):
        self.max_history_length = max_history_length
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   metadata: Dict = None) -> Dict:
        """添加消息到对话历史"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # 存储到数据库
        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }).execute()
        
        return message
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """获取对话历史"""
        response = supabase.table("messages").select("*").eq(
            "conversation_id", conversation_id
        ).order("created_at").execute()
        
        return response.data
    
    def create_conversation(self, user_id: str, title: str = None) -> str:
        """创建新对话"""
        response = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }).execute()
        
        return response.data[0]["id"]
    
    def update_conversation_title(self, conversation_id: str, title: str):
        """更新对话标题"""
        supabase.table("conversations").update({
            "title": title
        }).eq("id", conversation_id).execute()
```

**验收标准**:
- [ ] LLM响应生成功能正常
- [ ] 流式响应支持良好
- [ ] 对话历史管理正确
- [ ] 响应质量评估准确

### Phase 4: UI集成 (Week 4)

#### 4.1 RAG聊天界面增强

**目标**: 将RAG功能集成到现有聊天界面

**任务**:
- [ ] 增强现有聊天界面
- [ ] 添加DocSet选择器
- [ ] 实现检索结果显示
- [ ] 添加嵌入状态显示

**实现步骤**:

1. **增强聊天界面组件**
```python
# src/ragspace/ui/components/rag_chat.py
import gradio as gr
from typing import List, Dict
from ..rag.retriever import RAGRetriever
from ..rag.response_generator import RAGResponseGenerator
from ..rag.context_assembler import ContextAssembler

class RAGChatInterface:
    def __init__(self):
        self.retriever = RAGRetriever()
        self.response_generator = RAGResponseGenerator()
        self.context_assembler = ContextAssembler()
    
    def create_interface(self):
        """创建RAG增强的聊天界面"""
        with gr.Blocks() as interface:
            gr.Markdown("# 🤖 RAGSpace - AI Knowledge Hub")
            
            with gr.Row():
                with gr.Column(scale=3):
                    # DocSet选择器
                    docset_selector = gr.CheckboxGroup(
                        choices=self._get_docsets_list(),
                        label="选择文档集合",
                        value=["all"],
                        interactive=True
                    )
                    
                    # 聊天历史
                    chatbot = gr.Chatbot(
                        height=400,
                        show_label=False
                    )
                    
                    # 查询输入
                    msg = gr.Textbox(
                        label="输入问题",
                        placeholder="请输入您的问题...",
                        lines=2
                    )
                    
                    with gr.Row():
                        submit = gr.Button("发送", variant="primary")
                        clear = gr.Button("清除")
                    
                    # 检索结果显示
                    retrieval_results = gr.Markdown(
                        label="检索结果",
                        visible=False
                    )
                
                with gr.Column(scale=1):
                    # 嵌入状态
                    embedding_status = gr.Dataframe(
                        headers=["文档", "状态", "更新时间"],
                        datatype=["str", "str", "str"],
                        col_count=(3, "fixed"),
                        interactive=False,
                        label="嵌入状态"
                    )
                    
                    # 刷新按钮
                    refresh_btn = gr.Button("刷新状态")
                    
                    # 手动触发嵌入
                    trigger_embedding_btn = gr.Button("手动触发嵌入")
            
            # 事件处理
            submit.click(
                self._process_rag_query,
                inputs=[msg, chatbot, docset_selector],
                outputs=[chatbot, msg, retrieval_results]
            )
            
            clear.click(
                lambda: ([], "", gr.Markdown(visible=False)),
                outputs=[chatbot, msg, retrieval_results]
            )
            
            refresh_btn.click(
                self._update_embedding_status,
                outputs=embedding_status
            )
            
            trigger_embedding_btn.click(
                self._trigger_embedding_process,
                outputs=embedding_status
            )
        
        return interface
    
    def _process_rag_query(self, message: str, history: List[List[str]], 
                          docsets: List[str]) -> tuple:
        """处理RAG查询"""
        if not message.strip():
            return history, "", gr.Markdown(visible=False)
        
        try:
            # 1. 检索相关chunks
            chunks = self.retriever.hybrid_retrieve(message, docsets)
            
            # 2. 组装上下文
            context = self.context_assembler.assemble_context(chunks)
            
            # 3. 生成响应
            response = self.response_generator.generate_response(message, context)
            
            # 4. 构建检索结果显示
            retrieval_display = self._build_retrieval_display(chunks)
            
            # 5. 更新聊天历史
            history.append([message, response])
            
            return history, "", gr.Markdown(retrieval_display, visible=True)
            
        except Exception as e:
            error_response = f"抱歉，处理您的问题时出现了错误: {str(e)}"
            history.append([message, error_response])
            return history, "", gr.Markdown(visible=False)
    
    def _build_retrieval_display(self, chunks: List[Dict]) -> str:
        """构建检索结果显示"""
        if not chunks:
            return "未找到相关文档。"
        
        display_parts = ["## 📚 检索到的相关文档"]
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            
            # 构建源信息
            source_info = []
            if 'document_name' in metadata:
                source_info.append(f"**文档**: {metadata['document_name']}")
            if 'file_path' in metadata:
                source_info.append(f"**文件**: {metadata['file_path']}")
            if 'start_line' in metadata and 'end_line' in metadata:
                source_info.append(f"**行号**: {metadata['start_line']}-{metadata['end_line']}")
            
            source_text = " | ".join(source_info) if source_info else "未知来源"
            
            # 构建内容预览
            content_preview = chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content']
            
            display_parts.append(f"""
            ### 结果 {i}
            
            {source_text}
            
            ```
            {content_preview}
            ```
            
            ---
            """)
        
        return "\n".join(display_parts)
    
    def _get_docsets_list(self) -> List[str]:
        """获取DocSet列表"""
        # 从数据库获取DocSet列表
        response = supabase.table("docsets").select("name").execute()
        return ["all"] + [docset["name"] for docset in response.data]
    
    def _update_embedding_status(self) -> List[List[str]]:
        """更新嵌入状态"""
        response = supabase.table("documents").select(
            "title, embedding_status, embedding_updated_at"
        ).execute()
        
        status_data = []
        for doc in response.data:
            status_text = {
                'pending': '🟡 等待处理',
                'processing': '⏳ 处理中...',
                'done': '✅ 已完成',
                'error': '❌ 处理失败'
            }.get(doc['embedding_status'], '❓ 未知状态')
            
            status_data.append([
                doc['title'],
                status_text,
                doc.get('embedding_updated_at', 'N/A')
            ])
        
        return status_data
    
    def _trigger_embedding_process(self) -> List[List[str]]:
        """手动触发嵌入处理"""
        # 这里可以调用嵌入工作器
        # 暂时返回更新后的状态
        return self._update_embedding_status()
```

2. **集成到主应用**
```python
# src/ragspace/ui/components/__init__.py
from .rag_chat import RAGChatInterface

def create_rag_chat_tab():
    """创建RAG聊天标签页"""
    rag_interface = RAGChatInterface()
    return rag_interface.create_interface()
```

**验收标准**:
- [ ] RAG聊天界面正常工作
- [ ] DocSet选择器功能正确
- [ ] 检索结果显示清晰
- [ ] 嵌入状态显示准确

### Phase 5: 测试和优化 (Week 5)

#### 5.1 全面测试

**目标**: 确保RAG系统稳定可靠

**任务**:
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能测试
- [ ] 用户验收测试

**测试计划**:

1. **单元测试**
```python
# tests/test_rag_system.py
import pytest
from src.ragspace.rag.text_splitter import RAGTextSplitter
from src.ragspace.rag.retriever import RAGRetriever
from src.ragspace.rag.response_generator import RAGResponseGenerator

class TestRAGSystem:
    def test_text_splitter(self):
        """测试文本分片器"""
        splitter = RAGTextSplitter()
        
        # 测试文本分片
        text = "This is a test document. It has multiple sentences. Each sentence should be properly split."
        chunks = splitter.split_text(text, "text")
        
        assert len(chunks) > 0
        assert all("content" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    
    def test_retriever(self):
        """测试检索器"""
        retriever = RAGRetriever()
        
        # 测试向量检索
        query = "How to use the API?"
        results = retriever.retrieve_chunks(query, top_k=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
    
    def test_response_generator(self):
        """测试响应生成器"""
        generator = RAGResponseGenerator()
        
        # 测试响应生成
        query = "What is this about?"
        context = "This is a test context about API usage."
        
        response = generator.generate_response(query, context)
        
        assert isinstance(response, str)
        assert len(response) > 0
```

2. **集成测试**
```python
# tests/test_rag_integration.py
class TestRAGIntegration:
    def test_end_to_end_rag_flow(self):
        """测试端到端RAG流程"""
        # 1. 准备测试数据
        test_document = {
            "title": "Test Document",
            "content": "This is a test document about API usage.",
            "docset_name": "test_docset"
        }
        
        # 2. 添加文档到数据库
        doc_id = self._add_test_document(test_document)
        
        # 3. 触发嵌入处理
        self._trigger_embedding(doc_id)
        
        # 4. 执行查询
        query = "How to use the API?"
        response = self._execute_rag_query(query, ["test_docset"])
        
        # 5. 验证结果
        assert response is not None
        assert len(response) > 0
```

3. **性能测试**
```python
# tests/test_rag_performance.py
import time

class TestRAGPerformance:
    def test_retrieval_performance(self):
        """测试检索性能"""
        retriever = RAGRetriever()
        
        start_time = time.time()
        results = retriever.retrieve_chunks("test query", top_k=5)
        end_time = time.time()
        
        # 检索时间应该在1秒以内
        assert end_time - start_time < 1.0
        assert len(results) <= 5
    
    def test_response_generation_performance(self):
        """测试响应生成性能"""
        generator = RAGResponseGenerator()
        
        start_time = time.time()
        response = generator.generate_response("test query", "test context")
        end_time = time.time()
        
        # 响应生成时间应该在5秒以内
        assert end_time - start_time < 5.0
        assert len(response) > 0
```

#### 5.2 性能优化

**目标**: 优化RAG系统性能

**任务**:
- [ ] 数据库查询优化
- [ ] 缓存策略优化
- [ ] 并发处理优化
- [ ] 内存使用优化

**优化策略**:

1. **数据库查询优化**
```sql
-- 优化向量索引
CREATE INDEX CONCURRENTLY ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 添加复合索引
CREATE INDEX CONCURRENTLY idx_chunks_docset_status ON chunks(docset_name, embedding_status);

-- 添加部分索引（只索引已嵌入的chunks）
CREATE INDEX CONCURRENTLY idx_chunks_embedded ON chunks(embedding) 
WHERE embedding IS NOT NULL;
```

2. **缓存策略优化**
```python
# 多级缓存策略
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # 内存缓存
        self.l2_cache = redis.Redis()  # Redis缓存
    
    def get(self, key: str):
        # L1缓存查找
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2缓存查找
        value = self.l2_cache.get(key)
        if value:
            # 更新L1缓存
            self.l1_cache[key] = value
            return value
        
        return None
    
    def set(self, key: str, value: str, ttl: int = 300):
        # 设置L1缓存
        self.l1_cache[key] = value
        
        # 设置L2缓存
        self.l2_cache.setex(key, ttl, value)
```

3. **并发处理优化**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncRAGProcessor:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_multiple_queries(self, queries: List[str]) -> List[str]:
        """并发处理多个查询"""
        loop = asyncio.get_event_loop()
        
        # 并发执行查询
        tasks = [
            loop.run_in_executor(self.executor, self._process_single_query, query)
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks)
        return results
    
    def _process_single_query(self, query: str) -> str:
        """处理单个查询"""
        retriever = RAGRetriever()
        response_generator = RAGResponseGenerator()
        
        chunks = retriever.retrieve_chunks(query)
        context = ContextAssembler().assemble_context(chunks)
        response = response_generator.generate_response(query, context)
        
        return response
```

## 验收标准

### Phase 1 验收标准
- [ ] chunks表成功创建并正常工作
- [ ] 文本分片器正确处理各种文档类型
- [ ] 嵌入工作器能够异步处理文档
- [ ] 状态管理系统正确跟踪处理状态

### Phase 2 验收标准
- [ ] 向量检索功能正常，响应时间 < 1秒
- [ ] GPT重排序功能正确工作
- [ ] 混合检索策略有效
- [ ] 缓存机制显著提升性能

### Phase 3 验收标准
- [ ] LLM响应生成功能正常
- [ ] 流式响应支持良好
- [ ] 对话历史管理正确
- [ ] 响应质量评估准确

### Phase 4 验收标准
- [ ] RAG聊天界面集成成功
- [ ] DocSet选择器功能正确
- [ ] 检索结果显示清晰
- [ ] 嵌入状态显示准确

### Phase 5 验收标准
- [ ] 所有测试通过
- [ ] 性能指标达到要求
- [ ] 系统稳定可靠
- [ ] 用户体验良好

## 风险评估和缓解策略

### 技术风险

1. **OpenAI API限制**
   - **风险**: API调用限制和成本控制
   - **缓解**: 实现缓存机制，添加成本监控

2. **向量数据库性能**
   - **风险**: 大规模数据下的查询性能
   - **缓解**: 优化索引，实现分页查询

3. **并发处理复杂性**
   - **风险**: 异步处理的复杂性
   - **缓解**: 使用成熟的异步框架，充分测试

### 业务风险

1. **用户体验**
   - **风险**: RAG系统响应时间过长
   - **缓解**: 实现流式响应，优化缓存策略

2. **数据质量**
   - **风险**: 检索结果不准确
   - **缓解**: 实现多级检索策略，添加质量评估

## 总结

本RAG实现计划提供了详细的实施步骤和技术方案，确保RAGSpace项目能够成功实现高质量的文档检索和问答功能。通过分阶段实施和严格的验收标准，可以确保系统的稳定性和可靠性。

---

*实现计划版本: 1.0*  
*更新时间: 2025-08-07*
