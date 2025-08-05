# RAGSpace - AI Knowledge Hub

## Project Overview

RAGSpace is a modular RAG (Retrieval-Augmented Generation) system that enables users to build personalized knowledge bases and share community knowledge through MCP (Model Context Protocol). The project aims to bridge the gap between individual knowledge management and community-driven AI knowledge sharing.

## Core Vision

### Dual Positioning Strategy

1. **Community Knowledge Hub** (Context7 Alternative)
   - Target: Open source users, framework maintainers, developers working with niche technologies
   - Use case: Upload documentation, notes, GitHub issues, blogs for rare libraries (e.g., pymavlink, lcov, tiny-dnn)
   - Value: Enable LLMs to provide meaningful answers for long-tail technology stack questions

2. **Personal RAG Deployment** (Self-Hosted Knowledge Base)
   - Target: Independent developers, researchers, small teams
   - Use case: Build private knowledge bases for research papers, development projects, or personal documentation
   - Value: Self-hosted RAG service with privacy control and sustainable evolution

## Key Features

### Modular Architecture
- **Gradio Web Interface**: User-friendly interface for knowledge management
- **MCP Server Integration**: Seamless integration with Cursor, Claude Desktop, and other LLM clients
- **Multi-source Data Ingestion**: Support for GitHub repositories, documentation websites, PDFs, and text files
- **Vector Database Storage**: Persistent storage with Supabase + pgvector
- **Multi-user Support**: User authentication and data isolation
- **Community Sharing**: Public knowledge sets for community contribution

### Technical Stack
- **Frontend**: Gradio for web interface
- **Backend**: Python with FastAPI/Gradio
- **Database**: Supabase with pgvector for vector storage
- **Embedding**: OpenAI text-embedding-ada-002 or Sentence Transformers
- **LLM Integration**: OpenAI GPT models or local alternatives
- **Deployment**: Hugging Face Spaces, Railway, or self-hosted

## Development Phases

### Phase 1: Core Foundation
- [ ] Basic Gradio web interface
- [ ] API endpoint exposure
- [ ] Deployable web application
- [ ] MCP server integration

### Phase 2: Data Ingestion
- [ ] GitHub repository crawler
- [ ] Documentation website crawler
- [ ] File upload and processing
- [ ] Text chunking and embedding

### Phase 3: RAG Implementation
- [ ] Vector database integration
- [ ] Semantic search functionality
- [ ] Context retrieval and generation
- [ ] Response streaming

### Phase 4: Advanced Features
- [ ] Multi-user authentication
- [ ] Knowledge base management
- [ ] Community sharing features
- [ ] Advanced search and filtering

## Project Goals

1. **Accessibility**: Easy deployment and setup for individual developers
2. **Scalability**: Support for both personal and community use cases
3. **Privacy**: Self-hosted option for sensitive data
4. **Integration**: Seamless MCP integration with existing developer tools
5. **Community**: Open source with community contribution support

## Target Users

- **Individual Developers**: Building personal knowledge bases for their projects
- **Open Source Maintainers**: Creating documentation hubs for their projects
- **Research Teams**: Managing research papers and technical documentation
- **Small Teams**: Collaborative knowledge management with privacy control

## Success Metrics

- Number of deployed instances
- Community knowledge sets created
- MCP client integrations
- User engagement and retention
- Open source community contribution