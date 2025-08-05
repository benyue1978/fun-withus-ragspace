# RAGSpace - AI Knowledge Hub

🤖 Build and query your personal knowledge base with AI assistance.

## Features

- **📚 Knowledge Base Management**: Upload files, add websites, and import GitHub repositories
- **💬 AI Chat Interface**: Query your knowledge base with natural language
- **🔗 MCP Integration**: Connect with Cursor, Claude Desktop, and other LLM clients
- **🚀 Easy Deployment**: One-click deployment to Render, Railway, or Hugging Face Spaces

## Quick Start

### Local Development

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
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name list_documents --params '{}'
   ```

### Available MCP Tools

The following tools are available through the MCP server:

- `upload_file` - Handle file uploads
- `add_url` - Handle URL input for web scraping
- `add_github_repo` - Handle GitHub repository input
- `list_documents` - List all documents in the knowledge base
- `process_query` - Process user query and return response
- `process_query_1` - Alternative process query tool
- `clear_chat` - Clear the chat history

### Testing Steps

1. **Start the Gradio server**
   ```bash
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
   mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name list_documents --params '{}'
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

## Project Structure

```
ragspace/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── render.yaml        # Render deployment config
├── Dockerfile         # Docker configuration
├── README.md          # This file
└── .soloflow/         # Project documentation
    ├── overview.md
    ├── requirements.md
    ├── system_architecture.md
    ├── tasks.md
    ├── test_strategy.md
    ├── ui_design.md
    ├── deployment.md
    └── notes.md
```

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