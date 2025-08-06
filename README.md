# RAGSpace - AI Knowledge Hub

🤖 Build and query your personal knowledge base with AI assistance.

## Features

- **📚 Knowledge Base Management**: Upload files, add websites, and import GitHub repositories
- **💬 AI Chat Interface**: Query your knowledge base with natural language
- **🔗 MCP Integration**: Connect with Cursor, Claude Desktop, and other LLM clients
- **🎨 Modern UI**: Tabbed interface with sidebar layout and responsive design
- **🗄️ Supabase Database**: Persistent storage with PostgreSQL and real-time capabilities
- **🚀 Easy Deployment**: One-click deployment to Render, Railway, or Hugging Face Spaces

## Project Structure

```
fun-withus-ragspace/
├── src/
│   └── ragspace/
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── document.py      # Document model
│       │   └── docset.py        # DocSet model
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── manager.py       # Memory-based DocSetManager
│       │   └── supabase_manager.py  # Supabase-based DocSetManager
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── handlers.py      # UI event handlers
│       │   └── components/      # UI components
│       │       ├── __init__.py
│       │       ├── knowledge_management.py
│       │       ├── chat_interface.py
│       │       └── mcp_tools.py
│       └── mcp/
│           ├── __init__.py
│           └── tools.py         # MCP tool definitions
├── app.py              # Main application entry point
├── dev.py              # Development server with auto-reload
├── pyproject.toml      # Poetry project configuration
├── Makefile            # Simple command aliases
├── Dockerfile         # Docker configuration
├── supabase/          # Supabase CLI configuration
│   ├── config.toml    # Supabase configuration
│   ├── migrations/    # Database migrations
│   ├── seed/          # Seed data
│   └── functions/     # Edge Functions (future)
├── scripts/           # Utility scripts
├── tests/             # Test files
├── env.example        # Environment variables template
└── README.md          # This file
```

## Quick Start

### Prerequisites

1. **Supabase Project**: Create a new project at [supabase.com](https://supabase.com)
2. **Supabase CLI**: Install Supabase CLI for local development
   ```bash
   # macOS
   brew install supabase/tap/supabase
   
   # Windows
   choco install supabase
   
   # Linux
   curl -fsSL https://supabase.com/install.sh | sh
   ```

### Local Development

#### Using Poetry (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ragspace.git
   cd ragspace
   ```

2. **Install Poetry (if not already installed)**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Setup Supabase CLI**
   ```bash
   # Run the setup script
   ./scripts/supabase_setup.sh
   
   # Or manually:
   supabase init
   supabase login
   supabase link --project-ref your-project-ref
   ```

5. **Apply database migrations**
   ```bash
   # Apply migrations to remote database
   supabase db push
   
   # Or apply to local database for testing
   supabase db reset
   ```

6. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase credentials
   ```

7. **Test Supabase integration**
   ```bash
   poetry run python test_supabase_integration.py
   ```

8. **Run the application**
   ```bash
   poetry run python app.py
   # Or activate the environment first:
   poetry shell
   python app.py
   ```

9. **Open in browser**
   Navigate to `http://localhost:8000`

#### Using pip (Alternative)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ragspace.git
   cd ragspace
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:8000`

### Deployment

#### Render (Recommended)

1. **Fork this repository**
2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New Web Service"
   - Connect your GitHub repository
   - Select the repository and branch

3. **Configure the service**
   - **Name**: `ragspace`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

#### Other Platforms

- **Railway**: Use the `railway.json` configuration
- **Hugging Face Spaces**: Use the Spaces configuration
- **Docker**: Use the provided `Dockerfile`

## MCP Integration

RAGSpace includes a built-in MCP (Model Context Protocol) server that allows LLM clients to access your knowledge base.

### Testing MCP Server with mcp-inspector

You can test the MCP server using the official MCP Inspector tool in command-line mode:

1. **Install mcp-remote**
   ```bash
   npm install -g mcp-remote
   ```

2. **Create mcp-inspector configuration**
   Create a file named `mcp_inspector_config.json`:
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

3. **List available tools**
   ```bash
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/list
   ```

4. **Call a tool**
   ```bash
   # List all docsets
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name list_docset --params '{}'
   
   # Ask a question
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name ask --params '{"query": "What is available?", "docset": null}'
   
   # Create a docset
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name create_docset_ui --params '{"name": "gradio mcp", "description": "Gradio MCP integration"}'
   ```

### Available MCP Tools

The following tools are available through the MCP server:

**Core DocSet Tools:**
- `list_docset` - List all docsets
- `ask` - Ask a question (with optional docset parameter)

> **Note**: Only the core DocSet tools are exposed to MCP clients. UI management tools are hidden from MCP to keep the interface clean and focused.

### Testing Steps

1. **Start the Gradio server**
   ```bash
   # Using Poetry
   poetry run python app.py
   
   # Using pip
   source venv/bin/activate
   python app.py
   ```

2. **Verify server is running**
   ```bash
   curl -s http://localhost:8000/ | head -5
   ```

3. **Test MCP connection**
   ```bash
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/list
   ```

4. **Test tool execution**
   ```bash
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name list_docset --params '{}'
   ```

### Connecting with Cursor

1. **Open Cursor**
2. **Go to Settings** → **MCP Servers**
3. **Add new server**:
   ```json
   {
     "name": "RAGSpace",
     "description": "Query your knowledge base",
     "sse_url": "https://your-app.onrender.com/gradio_api/mcp/sse"
   }
   ```

### Connecting with Claude Desktop

1. **Open Claude Desktop**
2. **Go to Settings** → **MCP Servers**
3. **Add the same configuration as above**

## Development Phases

### Phase 1: Foundation ✅
- [x] Basic Gradio interface
- [x] MCP server integration
- [x] Deployment configuration
- [x] File upload interface

### Phase 2: Data Ingestion (Next)
- [ ] GitHub repository crawler
- [ ] Web scraping functionality
- [ ] Document processing pipeline
- [ ] Vector embedding generation

### Phase 3: RAG Implementation
- [ ] Vector database integration
- [ ] Semantic search functionality
- [ ] LLM integration for responses
- [ ] Context retrieval and generation

### Phase 4: Advanced Features
- [ ] Multi-user authentication
- [ ] Knowledge base management
- [ ] Community sharing features
- [ ] Advanced analytics

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `OPENAI_API_KEY` | OpenAI API key | (required for Phase 3) |
| `SUPABASE_URL` | Supabase project URL | (required for Phase 4) |
| `SUPABASE_KEY` | Supabase API key | (required for Phase 4) |

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/your-username/ragspace/issues)
- **Discussions**: [Join the community](https://github.com/your-username/ragspace/discussions)
- **Documentation**: [Full documentation](https://github.com/your-username/ragspace/wiki)

## Roadmap

- [ ] **RAG Pipeline**: Intelligent document processing and retrieval
- [ ] **Vector Search**: Semantic search across your knowledge base
- [ ] **Multi-user Support**: Team collaboration and sharing
- [ ] **Advanced Analytics**: Usage insights and performance metrics
- [ ] **API Marketplace**: Third-party integrations and plugins

---

Built with ❤️ using [Gradio](https://gradio.app) and [MCP](https://modelcontextprotocol.io) 