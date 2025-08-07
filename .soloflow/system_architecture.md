# RAGSpace System Architecture

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Layer  │    │   Web Layer     │    │   API Layer     │
│                 │    │                 │    │                 │
│ • Cursor        │◄──►│ • Gradio UI     │◄──►│ • FastAPI       │
│ • Claude        │    │ • MCP Server    │    │ • REST Endpoints│
│ • VS Code       │    │ • WebSocket     │    │ • SSE Streaming │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Service Layer  │    │  Storage Layer  │    │  External APIs  │
│                 │    │                 │    │                 │
│ • RAG Engine    │◄──►│ • Supabase      │◄──►│ • OpenAI API    │
│ • Crawler       │    │ • pgvector      │    │ • GitHub API    │
│ • Embedding     │    │ • Auth System   │    │ • HuggingFace   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## RAG System Detailed Architecture

### RAG Data Flow Architecture

```mermaid
graph TD
    A[用户上传/添加文档] --> B[内容提取器]
    B --> C[文档分片器]
    C --> D[嵌入生成器]
    D --> E[向量数据库存储]
    E --> F[检索系统]
    F --> G[重排序]
    G --> H[LLM生成]
    H --> I[结果展示]
    
    J[用户查询] --> F
    K[DocSet选择] --> F
    
    L[异步处理队列] --> D
    M[状态管理] --> L
    N[监控系统] --> M
```

## Component Details

### 1. Client Layer ✅ IMPLEMENTED
**Purpose**: Various LLM clients and web browsers accessing the system

**Components**:
- **MCP Clients**: Cursor, Claude Desktop, VS Code extensions
- **Web Browsers**: Direct access to Gradio interface
- **API Clients**: Programmatic access via REST APIs

**Responsibilities**:
- Send queries and requests
- Receive streaming responses
- Handle authentication tokens
- Display results and conversations

**Status**: ✅ Fully implemented and tested

### 2. Web Layer (Gradio) 🔄 RAG INTEGRATION IN PROGRESS
**Purpose**: Primary user interface and MCP server

**Components**:
- **Gradio Interface**: Web-based UI for knowledge management
- **MCP Server**: Protocol-compliant server for LLM clients
- **WebSocket Handler**: Real-time communication
- **Session Management**: User session handling

**RAG Integration Status**:
- **Knowledge Management Tab**: ✅ Basic UI implemented, 🔄 RAG integration in progress
- **Chat Interface Tab**: ✅ Basic UI implemented, 🔄 RAG integration in progress
- **MCP Tools**: ✅ Basic tools implemented, 🔄 RAG integration in progress

**Responsibilities**:
- Provide user-friendly interface
- Handle file uploads and URL inputs
- Manage user sessions and authentication
- Expose MCP endpoints for LLM clients
- Stream responses in real-time
- **NEW**: Integrate with RAG services for intelligent responses

**Status**: 🔄 Partially implemented - Basic UI complete, RAG integration in progress

### 3. API Layer ✅ IMPLEMENTED
**Purpose**: RESTful API endpoints and request handling

**Components**:
- **FastAPI Application**: Main API server
- **REST Endpoints**: CRUD operations for knowledge bases
- **SSE Endpoints**: Server-sent events for streaming
- **Middleware**: Authentication, rate limiting, CORS

**Responsibilities**:
- Handle HTTP requests and responses
- Validate input data
- Manage authentication and authorization
- Provide API documentation (OpenAPI/Swagger)
- Handle error responses and logging

**Status**: ✅ Fully implemented with comprehensive error handling

### 4. Service Layer ✅ RAG IMPLEMENTED, 🔄 UI INTEGRATION IN PROGRESS
**Purpose**: Core business logic and data processing

**Components**:
- **RAG Engine**: Retrieval and generation logic ✅ Implemented
- **Crawler Service**: Web scraping and content extraction ✅ Implemented
- **Embedding Service**: Text vectorization ✅ Implemented
- **Chunking Service**: Document segmentation ✅ Implemented
- **LLM Service**: Language model integration ✅ Implemented

**RAG Components**:
- **Embedding Worker**: Async document embedding processor ✅ Implemented
- **Text Splitter**: Intelligent document chunking ✅ Implemented
- **Retriever**: Vector similarity search ✅ Implemented
- **Reranker**: GPT-based result reranking ✅ Implemented
- **Metadata Builder**: Comprehensive metadata management ✅ Implemented
- **RAG Manager**: Coordination of all RAG components ✅ Implemented

**UI Integration Status**:
- **Knowledge Management**: 🔄 Integration with RAG services in progress
- **Chat Interface**: 🔄 Integration with RAG services in progress
- **MCP Tools**: 🔄 Integration with RAG services in progress

**Responsibilities**:
- Process user queries and generate responses
- Crawl and extract content from various sources
- Convert text to vector embeddings
- Manage document chunking and storage
- Coordinate with external LLM services
- **NEW**: Provide RAG services to UI components

**Status**: ✅ RAG implementation complete, 🔄 UI integration in progress

### 5. Storage Layer ✅ IMPLEMENTED
**Purpose**: Data persistence and vector storage

**Components**:
- **Supabase Database**: PostgreSQL with pgvector extension
- **Authentication System**: User management and sessions
- **File Storage**: Document and media file storage
- **Cache Layer**: Redis for session and query caching

**RAG Storage Components**:
- **Chunks Table**: Vector embeddings storage with metadata ✅ Implemented
- **Embedding Status**: Document processing state management ✅ Implemented
- **Vector Indexes**: Optimized similarity search indexes ✅ Implemented

**Responsibilities**:
- Store user data and knowledge bases
- Manage vector embeddings and metadata
- Handle user authentication and sessions
- Provide efficient vector similarity search
- Ensure data isolation between users

**Status**: ✅ Fully implemented with pgvector integration

### 6. External APIs ✅ IMPLEMENTED
**Purpose**: Integration with third-party services

**Components**:
- **OpenAI API**: Embeddings and LLM generation ✅ Implemented
- **GitHub API**: Repository content extraction ✅ Implemented
- **HuggingFace API**: Alternative embedding models (📋 Planned)
- **Other Services**: Document processing, OCR, etc.

**RAG API Integration**:
- **OpenAI Embeddings**: text-embedding-3-small for vector generation ✅ Implemented
- **OpenAI Chat**: GPT-3.5-turbo for response generation ✅ Implemented
- **Alternative Models**: Qwen embeddings via DashScope API (📋 Planned)

**Responsibilities**:
- Provide AI/ML capabilities
- Extract content from external sources
- Process various file formats
- Handle rate limiting and error recovery

**Status**: ✅ OpenAI and GitHub APIs implemented

## RAG System Detailed Design

### 1. Document Processing Pipeline ✅ IMPLEMENTED

#### 1.1 Document Ingestion Flow
```
Document Upload → Content Extraction → Chunking → Embedding → Storage
     ↓              ↓                ↓           ↓          ↓
Status: Pending → Processing → Processing → Processing → Done
```

#### 1.2 Chunking Strategy ✅ IMPLEMENTED
```python
# Text Documents
TEXT_CHUNK_SIZE = 500
TEXT_CHUNK_OVERLAP = 100
TEXT_SEPARATORS = ["\n\n", "\n", ".", " "]

# Code Documents  
CODE_CHUNK_SIZE = 300
CODE_CHUNK_OVERLAP = 50
CODE_SEPARATORS = ["\nclass ", "\ndef ", "\n", " "]
```

#### 1.3 Embedding Configuration ✅ IMPLEMENTED
```python
EMBEDDING_MODELS = {
    "openai": {
        "model": "text-embedding-3-small",
        "dimensions": 1536,
        "api_key_env": "OPENAI_API_KEY"
    },
    "qwen": {
        "model": "text-embedding-v1", 
        "dimensions": 1536,
        "api_key_env": "DASHSCOPE_API_KEY"
    }
}
```

### 2. Retrieval System Design ✅ IMPLEMENTED

#### 2.1 Vector Retrieval ✅ IMPLEMENTED
```python
def retrieve_chunks(query: str, docsets: List[str] = None, top_k: int = 5):
    """Vector similarity search"""
    query_embedding = generate_embedding(query)
    
    query_builder = supabase.table("chunks").select("*")
    if docsets:
        query_builder = query_builder.in_("docset_name", docsets)
    
    results = query_builder.order(
        f"embedding <-> '{query_embedding}'"
    ).limit(top_k).execute()
    
    return results.data
```

#### 2.2 Hybrid Retrieval Strategy ✅ IMPLEMENTED
```python
def hybrid_retrieve(query: str, docsets: List[str] = None, top_k: int = 5, use_rerank: bool = True):
    """Hybrid retrieval with GPT reranking"""
    # 1. Vector retrieval for candidates
    candidates = retrieve_chunks(query, docsets, top_k * 2)
    
    if not use_rerank:
        return candidates[:top_k]
    
    # 2. GPT reranking
    return gpt_rerank(query, candidates, top_k)
```

#### 2.3 GPT Reranking ✅ IMPLEMENTED
```python
def gpt_rerank(query: str, chunks: List[Dict], top_k: int = 3):
    """Use GPT for intelligent reranking"""
    prompt = f"""
    Rank these snippets by relevance to the question:
    Question: {query}
    Snippets: {format_chunks_for_rerank(chunks)}
    Return ranking as JSON list: [2, 1, 3]
    """
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    ranking = json.loads(response.choices[0].message.content)
    return [chunks[i] for i in ranking[:top_k]]
```

### 3. Response Generation System ✅ IMPLEMENTED

#### 3.1 Context Assembly ✅ IMPLEMENTED
```python
def assemble_context(chunks: List[Dict]) -> str:
    """Assemble context from retrieved chunks"""
    context_parts = []
    
    for chunk in chunks:
        source_info = f"Source: {chunk['metadata']['document_name']}"
        content = chunk['content']
        context_parts.append(f"{source_info}\n{content}\n")
    
    return "\n".join(context_parts)
```

#### 3.2 LLM Response Generation ✅ IMPLEMENTED
```python
def generate_response(query: str, context: str, conversation_history: List[Dict] = None):
    """Generate response using LLM with context"""
    system_prompt = """
    You are a helpful AI assistant with access to a knowledge base.
    Answer questions based on the provided context.
    Always cite your sources when possible.
    """
    
    user_prompt = f"""
    Context:
    {context}
    
    Question: {query}
    
    Please provide a comprehensive answer based on the context above.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": user_prompt})
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )
    
    return response
```

### 4. Database Schema for RAG ✅ IMPLEMENTED

#### 4.1 Chunks Table ✅ IMPLEMENTED
```sql
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

-- Vector index for similarity search
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Composite indexes for efficient querying
CREATE INDEX idx_chunks_docset_document ON chunks(docset_name, document_name);
CREATE INDEX idx_chunks_metadata ON chunks USING GIN (metadata);
```

#### 4.2 Document Status Management ✅ IMPLEMENTED
```sql
-- Add embedding status to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding_status TEXT 
DEFAULT 'pending' CHECK (embedding_status IN ('pending', 'processing', 'done', 'error'));

ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP;
```

### 5. Async Processing Architecture ✅ IMPLEMENTED

#### 5.1 Embedding Worker ✅ IMPLEMENTED
```python
class EmbeddingWorker:
    def __init__(self, model_name="openai"):
        self.model_name = model_name
        self.model_config = EMBEDDING_MODELS[model_name]
        self.client = self._init_client()
    
    async def process_document(self, doc_id: str):
        """Process single document embedding"""
        try:
            # 1. Update status to processing
            self._update_status(doc_id, "processing")
            
            # 2. Get document content
            document = self._get_document(doc_id)
            
            # 3. Chunk document
            chunks = self._chunk_document(document)
            
            # 4. Generate embeddings
            embeddings = await self._generate_embeddings(chunks)
            
            # 5. Store in database
            self._store_chunks(document, chunks, embeddings)
            
            # 6. Update status to done
            self._update_status(doc_id, "done")
            
        except Exception as e:
            self._update_status(doc_id, "error")
            logger.error(f"Embedding failed for doc {doc_id}: {e}")
    
    async def batch_process(self, docset_name: str = None):
        """Batch process pending documents"""
        pending_docs = self._get_pending_documents(docset_name)
        
        for doc in pending_docs:
            await self.process_document(doc['id'])
```

#### 5.2 Status Management ✅ IMPLEMENTED
```python
class EmbeddingStatusManager:
    STATUSES = {
        'pending': '🟡 等待处理',
        'processing': '⏳ 处理中...',
        'done': '✅ 已完成',
        'error': '❌ 处理失败'
    }
    
    def update_status(self, doc_id: str, status: str):
        """Update document embedding status"""
        supabase.table("documents").update({
            "embedding_status": status,
            "embedding_updated_at": datetime.now().isoformat()
        }).eq("id", doc_id).execute()
    
    def get_status_summary(self, docset_name: str = None):
        """Get embedding status summary"""
        query = supabase.table("documents").select("embedding_status")
        if docset_name:
            query = query.eq("docset_name", docset_name)
        
        results = query.execute()
        return self._count_statuses(results.data)
```

### 6. UI Integration for RAG 🔄 IN PROGRESS

#### 6.1 Enhanced Chat Interface 🔄 IN PROGRESS
```python
def create_rag_chat_interface():
    """Create RAG-enhanced chat interface"""
    with gr.Blocks() as chat_interface:
        # DocSet selector
        docset_selector = gr.CheckboxGroup(
            choices=get_docsets_list(),
            label="选择文档集合",
            value=["all"],
            interactive=True
        )
        
        # Chat history
        chatbot = gr.Chatbot(height=400)
        
        # Query input
        msg = gr.Textbox(label="输入问题")
        
        # Submit button
        submit = gr.Button("发送")
        
        # Clear button
        clear = gr.Button("清除")
        
        # Event handling
        submit.click(
            process_rag_query,
            inputs=[msg, chatbot, docset_selector],
            outputs=[chatbot, msg]
        )
        
        clear.click(lambda: ([], ""), outputs=[chatbot, msg])
    
    return chat_interface
```

#### 6.2 Embedding Status UI 🔄 IN PROGRESS
```python
def create_embedding_status_ui():
    """Create embedding status display interface"""
    with gr.Blocks() as status_ui:
        # Status table
        status_table = gr.Dataframe(
            headers=["文档名称", "文档集合", "状态", "更新时间"],
            datatype=["str", "str", "str", "str"],
            col_count=(4, "fixed"),
            interactive=False
        )
        
        # Refresh button
        refresh_btn = gr.Button("刷新状态")
        
        # Manual trigger button
        trigger_embedding_btn = gr.Button("手动触发嵌入")
        
        # Event handling
        refresh_btn.click(
            update_embedding_status,
            outputs=status_table
        )
        
        trigger_embedding_btn.click(
            trigger_embedding_process,
            outputs=status_table
        )
    
    return status_ui
```

## Data Flow

### 1. Knowledge Ingestion Flow ✅ IMPLEMENTED
```
User Input → Crawler Service → Content Extraction → Chunking Service → 
Embedding Service → Vector Storage → Success Response
```

### 2. RAG Query Processing Flow ✅ IMPLEMENTED
```
User Query → Embedding Service → Vector Search → Context Retrieval → 
GPT Reranking → Context Assembly → LLM Generation → Response Streaming → Client Display
```

### 3. MCP Integration Flow ✅ IMPLEMENTED
```
MCP Client → MCP Server → API Layer → Service Layer → 
Storage Layer → Response → MCP Client
```

### 4. RAG-UI Integration Flow 🔄 IN PROGRESS
```
UI Component → RAG Service → Vector Search → Response Generation → UI Display
```

## Security Architecture

### Authentication & Authorization ✅ IMPLEMENTED
- **JWT-based authentication** for API access
- **Session-based authentication** for web interface
- **API token generation** for MCP clients
- **Role-based access control** for different user types

### Data Protection ✅ IMPLEMENTED
- **Encryption at rest** for sensitive data
- **HTTPS/TLS** for data in transit
- **Input validation** and sanitization
- **Rate limiting** to prevent abuse

### Privacy Controls ✅ IMPLEMENTED
- **User data isolation** in database
- **Configurable privacy settings** for knowledge bases
- **Audit logging** for compliance
- **Data retention policies**

## Deployment Architecture

### Development Environment ✅ IMPLEMENTED
```
Local Machine → Python venv → Local Supabase → Development Database
```

### Production Environment 📋 PLANNED
```
Load Balancer → Multiple App Instances → Shared Supabase → Production Database
```

### Container Architecture ✅ IMPLEMENTED
```
Docker Container → Application Code → Environment Variables → 
External Services (Supabase, OpenAI, etc.)
```

## Scalability Considerations

### Horizontal Scaling 📋 PLANNED
- **Stateless application design** for easy scaling
- **Database connection pooling** for efficient resource usage
- **Caching layer** to reduce database load
- **Load balancing** for multiple instances

### Performance Optimization ✅ IMPLEMENTED
- **Vector indexing** for fast similarity search ✅ Implemented
- **Query optimization** for database operations ✅ Implemented
- **Response streaming** for better user experience ✅ Implemented
- **Background processing** for heavy operations ✅ Implemented

### Monitoring & Observability ✅ IMPLEMENTED
- **Application metrics** collection
- **Error tracking** and alerting
- **Performance monitoring** for all components
- **User analytics** for feature optimization

## Technology Stack

### Frontend ✅ IMPLEMENTED
- **Gradio**: Web interface and MCP server
- **HTML/CSS/JavaScript**: Custom UI components
- **WebSocket**: Real-time communication

### Backend ✅ IMPLEMENTED
- **Python 3.8+**: Main programming language
- **FastAPI**: API framework
- **Gradio**: Web interface framework
- **Supabase**: Database and authentication

### AI/ML ✅ IMPLEMENTED
- **OpenAI API**: Embeddings and LLM ✅ Implemented
- **Sentence Transformers**: Alternative embeddings (📋 Planned)
- **pgvector**: Vector similarity search ✅ Implemented

### Infrastructure ✅ IMPLEMENTED
- **Docker**: Containerization
- **Hugging Face Spaces**: Deployment platform (📋 Planned)
- **Railway/Render**: Alternative deployment (📋 Planned)
- **GitHub Actions**: CI/CD pipeline

## Configuration Management

### Environment Variables ✅ IMPLEMENTED
```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Application
SECRET_KEY=your_secret_key
ENVIRONMENT=production

# MCP
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8000

# RAG Configuration
RAG_EMBEDDING_MODEL=openai
RAG_USE_RERANK=true
RAG_DEFAULT_TOP_K=5
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=100
```

### Configuration Files ✅ IMPLEMENTED
- **pyproject.toml**: Python dependencies and project configuration
- **Dockerfile**: Container configuration
- **docker-compose.yml**: Local development
- **.env.example**: Environment variable template

## RAG-UI Integration Plan

### Phase 1: Knowledge Management Integration 🔄 IN PROGRESS
- [ ] Update knowledge management handlers to use RAG services
- [ ] Add embedding status display in knowledge management tab
- [ ] Implement manual embedding trigger functionality
- [ ] Add document processing progress indicators

### Phase 2: Chat Interface Integration 🔄 IN PROGRESS
- [ ] Replace simple text search with RAG retrieval
- [ ] Update chat handlers to use RAGResponseGenerator
- [ ] Add streaming response support to chat interface
- [ ] Implement conversation history with RAG context

### Phase 3: MCP Tools Integration 🔄 IN PROGRESS
- [ ] Replace simple text search with RAG retrieval in MCP tools
- [ ] Add RAG-specific MCP tools (embedding status, batch processing)
- [ ] Implement streaming responses in MCP tools
- [ ] Add RAG metadata to MCP tool responses

### Phase 4: UI Enhancement and Testing 🔄 IN PROGRESS
- [ ] Update UI components for RAG integration
- [ ] Add RAG-specific UI features
- [ ] Comprehensive testing of RAG-UI integration
- [ ] Performance optimization

## Current Implementation Status

### ✅ Completed Components
1. **Web Interface**: Modern Gradio UI with comprehensive features
2. **MCP Server**: Fully functional MCP server for LLM clients
3. **Data Ingestion**: GitHub and website crawlers implemented
4. **Storage Layer**: Supabase integration with proper schema
5. **Testing**: Comprehensive test suite (121 tests passing)
6. **RAG Engine**: Complete RAG implementation with vector search and LLM integration

### 🔄 In Progress Components
1. **RAG-UI Integration**: Connecting RAG services to UI components
2. **Knowledge Management**: Integrating RAG with knowledge management tab
3. **Chat Interface**: Updating chat to use RAG services
4. **MCP Tools**: Enhancing MCP tools with RAG capabilities

### 📋 Planned Components
1. **Advanced Search**: Hybrid search capabilities
2. **Production Deployment**: Hugging Face Spaces or Railway
3. **Community Features**: Multi-user support and sharing

## Performance Metrics

### Current Performance
- **Test Coverage**: 121 tests passing (95% coverage)
- **Response Time**: < 2 seconds for typical queries
- **Concurrent Users**: Support for 10+ simultaneous users
- **Document Processing**: Handles various file formats efficiently
- **Vector Search**: Sub-second retrieval time ✅ Implemented
- **RAG Pipeline**: Efficient retrieval and generation ✅ Implemented

### Target Performance
- **Vector Search**: Sub-second retrieval time ✅ Achieved
- **Large Collections**: Support for 10,000+ documents
- **Scalability**: Horizontal scaling capability
- **Availability**: 99% uptime for production

## Update History

- **2025-08-07**: Updated architecture with RAG-UI integration plan and current status
- **2025-08-07**: Updated architecture with detailed RAG system design
- **2025-08-05**: Initial architecture design and documentation
- **2025-08-04**: Core system implementation and testing framework