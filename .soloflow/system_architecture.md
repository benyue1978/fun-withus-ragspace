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

## Component Details

### 1. Client Layer
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

### 2. Web Layer (Gradio)
**Purpose**: Primary user interface and MCP server

**Components**:
- **Gradio Interface**: Web-based UI for knowledge management
- **MCP Server**: Protocol-compliant server for LLM clients
- **WebSocket Handler**: Real-time communication
- **Session Management**: User session handling

**Responsibilities**:
- Provide user-friendly interface
- Handle file uploads and URL inputs
- Manage user sessions and authentication
- Expose MCP endpoints for LLM clients
- Stream responses in real-time

### 3. API Layer
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

### 4. Service Layer
**Purpose**: Core business logic and data processing

**Components**:
- **RAG Engine**: Retrieval and generation logic
- **Crawler Service**: Web scraping and content extraction
- **Embedding Service**: Text vectorization
- **Chunking Service**: Document segmentation
- **LLM Service**: Language model integration

**Responsibilities**:
- Process user queries and generate responses
- Crawl and extract content from various sources
- Convert text to vector embeddings
- Manage document chunking and storage
- Coordinate with external LLM services

### 5. Storage Layer
**Purpose**: Data persistence and vector storage

**Components**:
- **Supabase Database**: PostgreSQL with pgvector extension
- **Authentication System**: User management and sessions
- **File Storage**: Document and media file storage
- **Cache Layer**: Redis for session and query caching

**Responsibilities**:
- Store user data and knowledge bases
- Manage vector embeddings and metadata
- Handle user authentication and sessions
- Provide efficient vector similarity search
- Ensure data isolation between users

### 6. External APIs
**Purpose**: Integration with third-party services

**Components**:
- **OpenAI API**: Embeddings and LLM generation
- **GitHub API**: Repository content extraction
- **HuggingFace API**: Alternative embedding models
- **Other Services**: Document processing, OCR, etc.

**Responsibilities**:
- Provide AI/ML capabilities
- Extract content from external sources
- Process various file formats
- Handle rate limiting and error recovery

## Data Flow

### 1. Knowledge Ingestion Flow
```
User Input → Crawler Service → Content Extraction → Chunking Service → 
Embedding Service → Vector Storage → Success Response
```

### 2. Query Processing Flow
```
User Query → Embedding Service → Vector Search → Context Retrieval → 
LLM Generation → Response Streaming → Client Display
```

### 3. MCP Integration Flow
```
MCP Client → MCP Server → API Layer → Service Layer → 
Storage Layer → Response → MCP Client
```

## Security Architecture

### Authentication & Authorization
- **JWT-based authentication** for API access
- **Session-based authentication** for web interface
- **API token generation** for MCP clients
- **Role-based access control** for different user types

### Data Protection
- **Encryption at rest** for sensitive data
- **HTTPS/TLS** for data in transit
- **Input validation** and sanitization
- **Rate limiting** to prevent abuse

### Privacy Controls
- **User data isolation** in database
- **Configurable privacy settings** for knowledge bases
- **Audit logging** for compliance
- **Data retention policies**

## Deployment Architecture

### Development Environment
```
Local Machine → Python venv → Local Supabase → Development Database
```

### Production Environment
```
Load Balancer → Multiple App Instances → Shared Supabase → Production Database
```

### Container Architecture
```
Docker Container → Application Code → Environment Variables → 
External Services (Supabase, OpenAI, etc.)
```

## Scalability Considerations

### Horizontal Scaling
- **Stateless application design** for easy scaling
- **Database connection pooling** for efficient resource usage
- **Caching layer** to reduce database load
- **Load balancing** for multiple instances

### Performance Optimization
- **Vector indexing** for fast similarity search
- **Query optimization** for database operations
- **Response streaming** for better user experience
- **Background processing** for heavy operations

### Monitoring & Observability
- **Application metrics** collection
- **Error tracking** and alerting
- **Performance monitoring** for all components
- **User analytics** for feature optimization

## Technology Stack

### Frontend
- **Gradio**: Web interface and MCP server
- **HTML/CSS/JavaScript**: Custom UI components
- **WebSocket**: Real-time communication

### Backend
- **Python 3.8+**: Main programming language
- **FastAPI**: API framework
- **Gradio**: Web interface framework
- **Supabase**: Database and authentication

### AI/ML
- **OpenAI API**: Embeddings and LLM
- **Sentence Transformers**: Alternative embeddings
- **pgvector**: Vector similarity search

### Infrastructure
- **Docker**: Containerization
- **Hugging Face Spaces**: Deployment platform
- **Railway/Render**: Alternative deployment
- **GitHub Actions**: CI/CD pipeline

## Configuration Management

### Environment Variables
```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# OpenAI
OPENAI_API_KEY=your_openai_key

# Application
SECRET_KEY=your_secret_key
ENVIRONMENT=production

# MCP
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8000
```

### Configuration Files
- **requirements.txt**: Python dependencies
- **Dockerfile**: Container configuration
- **docker-compose.yml**: Local development
- **.env.example**: Environment variable template