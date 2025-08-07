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

### Phase 1: Core Foundation ✅ COMPLETED
- [x] Basic Gradio web interface
- [x] API endpoint exposure
- [x] Deployable web application
- [x] MCP server integration
- [x] Basic streaming responses
- [x] Supabase integration
- [x] Comprehensive test suite (121 tests passing)

### Phase 2: Data Ingestion 🔄 IN PROGRESS
- [x] GitHub repository crawler (implemented)
- [x] Documentation website crawler (implemented)
- [x] File upload and processing (implemented)
- [ ] Text chunking and embedding (pending)
- [ ] Vector database integration (pending)
- [ ] Content preprocessing pipeline (pending)

### Phase 3: RAG Implementation 📋 PLANNED
- [ ] Vector database integration
- [ ] Semantic search functionality
- [ ] Context retrieval and generation
- [ ] Response streaming
- [ ] OpenAI LLM integration

### Phase 4: Advanced Features 📋 PLANNED
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

## Current Status

### ✅ Completed Features
- **Core Application**: Fully functional Gradio interface with modern UI
- **MCP Server**: Integrated MCP server for LLM client integration
- **Data Ingestion**: GitHub and website crawlers implemented
- **Storage**: Supabase integration with proper database schema
- **Testing**: Comprehensive test suite with 121 passing tests
- **Documentation**: Complete project documentation structure

### 🔄 In Progress
- **Vector Database**: Setting up pgvector integration
- **Embedding Pipeline**: Implementing OpenAI embedding integration
- **RAG Pipeline**: Developing retrieval and generation logic

### 📋 Next Steps
- **Phase 2 Completion**: Finish vector database and embedding integration
- **Phase 3 Implementation**: Implement full RAG pipeline
- **Production Deployment**: Deploy to Hugging Face Spaces or Railway
- **Community Features**: Add multi-user support and sharing capabilities

## Technical Achievements

### Code Quality
- **Test Coverage**: 121 comprehensive tests covering all major components
- **Code Structure**: Well-organized modular architecture
- **Documentation**: Complete API and system documentation
- **Error Handling**: Robust error handling and logging

### Infrastructure
- **Database**: Supabase integration with proper schema
- **Authentication**: Basic authentication system in place
- **Deployment**: Docker and environment configuration ready
- **Monitoring**: Health checks and logging implemented

## Update History

- **2025-08-07**: Project status updated - Phase 1 completed, Phase 2 in progress
- **2025-08-05**: Initial project setup and documentation structure
- **2025-08-04**: Core application development and testing framework