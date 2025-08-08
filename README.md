# RAGSpace - AI Knowledge Hub

[English](README.md) | [中文](README_zh.md)

🤖 Build and query your personal knowledge base with AI assistance.

## 🚀 Quick Start

### Prerequisites

1. **Supabase Project**: Create a new project at [supabase.com](https://supabase.com)
2. **Environment Setup**: Copy and configure environment variables

### Local Setup

1. **Clone and install**
   ```bash
   git clone https://github.com/your-username/ragspace.git
   cd ragspace
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in browser**
   Navigate to `http://localhost:8000`

## ✨ Features

- **📚 Knowledge Base Management**: Upload files, add websites, and import GitHub repositories
- **🕷️ Web Crawling System**: Automatic content extraction from URLs and GitHub repositories
- **💬 AI Chat Interface**: Query your knowledge base with natural language
- **🔗 MCP Integration**: Connect with Cursor, Claude Desktop, and other LLM clients
- **🎨 Modern UI**: Tabbed interface with sidebar layout and responsive design
- **🗄️ Supabase Database**: Persistent storage with PostgreSQL and real-time capabilities
- **⚙️ Configurable Crawlers**: Environment-based configuration for all crawlers
- **🚀 Easy Deployment**: One-click deployment to Render, Railway, or Hugging Face Spaces
- **🔍 Document Source Attribution**: Clickable source links that take you directly to the original documents

## 🎯 Use Cases

### Personal Knowledge Management
- **Research Papers**: Upload and query academic papers
- **Project Documentation**: Build knowledge bases for your projects
- **Learning Notes**: Organize study materials and notes
- **Technical Documentation**: Store and search technical guides

### Team Collaboration
- **Shared Knowledge Base**: Create team documentation hubs
- **Code Documentation**: Import GitHub repositories for code search
- **Process Documentation**: Store and query team procedures
- **Meeting Notes**: Organize and search meeting records

### Community Knowledge Sharing
- **Open Source Projects**: Create documentation hubs for your projects
- **Technical Communities**: Share knowledge with the community
- **Educational Content**: Build learning resource collections
- **Niche Technology**: Document rare or specialized technologies

## 🔍 Document Source Attribution

RAGSpace includes advanced document source attribution that provides clickable links back to the original sources:

### GitHub Source Attribution
- **Line Number Links**: Direct links to specific lines in GitHub files (e.g., `#L15-L25`)
- **Repository Information**: Preserves repo, branch, and file path information
- **Commit Tracking**: Maintains commit SHA for version control
- **Code Snippets**: Precise line number tracking for code documentation

### Website Source Attribution
- **URL Preservation**: Maintains original website URLs
- **Page Titles**: Preserves document titles and metadata
- **Content Structure**: Tracks content depth and organization

### File Upload Attribution
- **Document Names**: Preserves original file names
- **Upload Metadata**: Tracks file type, size, and upload date
- **Content Organization**: Maintains document structure

### Example Source Attribution
When you ask a question, RAGSpace provides responses with clickable source links:

```
Question: "How do I implement authentication?"

Response: "To implement authentication, you need to use JWT tokens..."

Sources:
1. [README.md](https://github.com/user/repo/blob/main/README.md#L45-L52)
2. [auth.js](https://github.com/user/repo/blob/main/src/auth.js#L1-L20)
3. [API Documentation](https://docs.example.com/api/authentication)
```

## 📖 How to Use

### 1. Create a DocSet
1. Go to the "📚 Knowledge Management" tab
2. Enter a name and description for your knowledge base
3. Click "Create DocSet"

### 2. Add Content
You can add content in three ways:

#### File Upload
1. Select your DocSet from the sidebar
2. Go to "📁 Add Files" tab
3. Upload PDF, TXT, MD, or other text files
4. Files will be automatically processed and embedded

#### Website Content
1. Select your DocSet from the sidebar
2. Go to "🌐 Add URL" tab
3. Enter a website URL
4. Choose content type (website, documentation, etc.)
5. Click "Add URL"

#### GitHub Repository
1. Select your DocSet from the sidebar
2. Go to "🐙 Add GitHub Repo" tab
3. Enter repository URL (e.g., `owner/repo` or `https://github.com/owner/repo`)
4. Optionally specify a branch
5. Click "Add Repository"

### 3. Query Your Knowledge Base
1. Go to the "💬 Chat Interface" tab
2. Select your DocSet from the dropdown
3. Ask questions in natural language
4. Get AI-powered responses with source citations

### 4. Use with MCP Clients
Connect with Cursor, Claude Desktop, or other LLM clients:

#### Cursor Integration
1. Open Cursor Settings → MCP Servers
2. Add server configuration:
   ```json
   {
     "name": "RAGSpace",
     "description": "Query your knowledge base",
     "sse_url": "https://your-app.onrender.com/gradio_api/mcp"
   }
   ```

#### Claude Desktop Integration
1. Open Claude Desktop Settings → MCP Servers
2. Add the same configuration as above

## 🔧 MCP Integration

RAGSpace includes a built-in MCP (Model Context Protocol) server that allows LLM clients to access your knowledge base.

### Available MCP Tools

**Core Tools:**
- `list_docset` - List all document collections
- `ask` - Query your knowledge base with natural language

### Testing MCP Server

1. **Install mcp-remote**
   ```bash
   npm install -g mcp-remote
   ```

2. **Create configuration file** `mcp_inspector_config.json`:
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

3. **Test the connection**
   ```bash
   # List available tools
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/list
   
   # Ask a question
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name ask --params '{"query": "What is available?", "docset": null}'
   ```

## 🚀 Deployment

### Render (Recommended)

1. **Fork this repository**
2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New Web Service"
   - Connect your GitHub repository

3. **Configure the service**
   - **Name**: `ragspace`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

4. **Set environment variables**
   - Add all required environment variables from `env.example`

5. **Deploy**
   - Click "Create Web Service"

### Other Platforms

- **Railway**: Use the `railway.json` configuration
- **Hugging Face Spaces**: Use the Spaces configuration
- **Docker**: Use the provided `Dockerfile`

## ⚙️ Configuration

### Environment Variables

#### Required Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | (required) |
| `SUPABASE_KEY` | Supabase API key | (required) |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |

#### GitHub Crawler Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub API token | (optional) |
| `GITHUB_FILE_TYPES` | Supported file types | `.md,.py,.js,.ts,.txt,.rst,.adoc,.json,.yaml,.yml` |
| `GITHUB_MAX_FILE_SIZE` | Maximum file size (bytes) | `50000` |
| `GITHUB_MAX_DEPTH` | Maximum directory depth | `10` |

#### Website Crawler Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `WEBSITE_MAX_DEPTH` | Maximum crawl depth | `3` |
| `WEBSITE_MAX_PAGES` | Maximum pages to crawl | `10` |
| `WEBSITE_TIMEOUT` | Request timeout (seconds) | `10` |

## 🏗️ Development

### Project Structure

```
fun-withus-ragspace/
├── src/
│   └── ragspace/
│       ├── config/                    # Configuration management
│       ├── models/                    # Data models
│       ├── services/                  # Crawler services
│       ├── storage/                   # Database management
│       ├── ui/                        # UI components
│       └── mcp/                       # MCP server
├── app.py              # Main application entry point
├── tests/              # Test files
└── supabase/           # Database migrations
```

### Development Setup

#### Using Poetry (Recommended)

1. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Setup Supabase CLI**
   ```bash
   ./scripts/supabase_setup.sh
   ```

4. **Apply database migrations**
   ```bash
   supabase db push
   ```

5. **Run the application**
   ```bash
   poetry run python app.py
   ```

#### Using pip

1. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_crawler_system.py
pytest tests/test_ui_integration.py
```

## 📊 Data Structure

### Database Schema

#### DocSets Table
```sql
CREATE TABLE docsets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  description text,
  created_at timestamp DEFAULT now()
);
```

#### Documents Table
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

### Crawler System

The system includes a flexible crawler architecture:

#### Available Crawlers
- **GitHubCrawler**: Fetches repository contents and individual files
- **WebsiteCrawler**: Extracts content from general websites
- **MockCrawler**: Provides test data for development

#### Crawler Interface
```python
class CrawlerInterface:
    def crawl(self, url: str, **kwargs) -> CrawlResult
    def can_handle(self, url: str) -> bool
    def get_supported_url_patterns(self) -> List[str]
    def get_rate_limit_info(self) -> Dict[str, Any]
```

## 🔄 Development Phases

### Phase 1: Foundation ✅
- [x] Basic Gradio interface
- [x] MCP server integration
- [x] Deployment configuration
- [x] File upload interface

### Phase 2: Data Ingestion ✅
- [x] GitHub repository crawler
- [x] Web scraping functionality
- [x] Document processing pipeline
- [x] Configuration management system

### Phase 3: RAG Implementation ✅
- [x] Vector database integration
- [x] Semantic search functionality
- [x] LLM integration for responses
- [x] Context retrieval and generation

### Phase 4: RAG-UI Integration ✅
- [x] Knowledge management integration with RAG
- [x] Chat interface enhancement with RAG
- [x] MCP tools integration with RAG
- [x] UI feedback and status management

### Phase 5: Advanced Features 📋
- [ ] Multi-user authentication
- [ ] Knowledge base management
- [ ] Community sharing features
- [ ] Advanced analytics

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/benyue1978/fun-withus-ragspace/issues)
- **Discussions**: [Join the community](https://github.com/benyue1978/fun-withus-ragspace/discussions)
- **Documentation**: [Full documentation](https://github.com/benyue1978/fun-withus-ragspace/wiki)

## 🗺️ Roadmap

- [ ] **Multi-user Support**: Team collaboration and sharing
- [ ] **Advanced Analytics**: Usage insights and performance metrics
- [ ] **API Marketplace**: Third-party integrations and plugins
- [ ] **Mobile Support**: Mobile-optimized interface
- [ ] **Advanced Search**: Multi-modal search capabilities

---

Built with ❤️ using [Gradio](https://gradio.app) and [MCP](https://modelcontextprotocol.io) 