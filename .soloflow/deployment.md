# RAGSpace Deployment Guide

## Deployment Options

### 1. Hugging Face Spaces (Recommended for Demo)

**Advantages**:
- Free hosting for demos and prototypes
- Easy integration with Gradio applications
- Built-in support for MCP servers
- Automatic HTTPS and domain management
- Community visibility and discoverability

**Limitations**:
- Limited resources for production workloads
- Sleep mode for inactive applications
- No persistent storage (use external services)
- Rate limiting on API calls

**Setup Process**:
1. Create Hugging Face account and Space
2. Configure Space settings for Gradio application
3. Set up environment variables for external services
4. Deploy application and test functionality
5. Configure custom domain (optional)

**Status**: 📋 Planned for Phase 3 deployment

### 2. Railway (Recommended for Production)

**Advantages**:
- Generous free tier with good performance
- Easy deployment from GitHub repository
- Automatic HTTPS and custom domains
- Built-in database and Redis support
- Good monitoring and logging

**Setup Process**:
1. Connect GitHub repository to Railway
2. Configure environment variables
3. Set up Supabase database connection
4. Deploy and configure custom domain
5. Set up monitoring and alerts

**Status**: 📋 Planned for Phase 3 deployment

### 3. Render (Alternative Production Option)

**Advantages**:
- Free tier available for small applications
- Easy deployment and scaling
- Good support for Python applications
- Automatic HTTPS and custom domains
- Built-in monitoring

**Setup Process**:
1. Connect GitHub repository to Render
2. Configure build settings and environment
3. Set up external services (Supabase, OpenAI)
4. Deploy and test functionality
5. Configure custom domain and SSL

**Status**: 📋 Planned for Phase 3 deployment

### 4. Self-Hosted (Advanced Users)

**Advantages**:
- Complete control over infrastructure
- No usage limits or rate limiting
- Custom security configurations
- Full data privacy and control

**Requirements**:
- VPS or cloud server (AWS, DigitalOcean, etc.)
- Docker and Docker Compose
- Domain name and SSL certificate
- Basic server administration skills

**Status**: ✅ Ready for deployment

## Environment Configuration

### Required Environment Variables

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_CHAT_MODEL=gpt-3.5-turbo

# Application Configuration
SECRET_KEY=your_secret_key_for_sessions
ENVIRONMENT=production
DEBUG=false

# MCP Server Configuration
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8000
MCP_SERVER_HOST=0.0.0.0

# Database Configuration
DATABASE_URL=your_database_connection_string
VECTOR_DIMENSION=1536

# Optional: Alternative Embedding Models
HUGGINGFACE_API_KEY=your_huggingface_api_key
SENTENCE_TRANSFORMERS_MODEL=all-MiniLM-L6-v2

# Optional: Monitoring and Analytics
SENTRY_DSN=your_sentry_dsn
ANALYTICS_KEY=your_analytics_key
```

### Environment Setup by Platform

#### Hugging Face Spaces
```yaml
# .github/workflows/deploy.yml
name: Deploy to Hugging Face Spaces
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Spaces
        uses: huggingface/huggingface_hub@v0.1.0
        with:
          token: ${{ secrets.HF_TOKEN }}
          repo: ${{ secrets.HF_REPO }}
```

#### Railway
```json
// railway.json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

#### Render
```yaml
# render.yaml
services:
  - type: web
    name: ragspace
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

## Database Setup

### Supabase Configuration ✅ IMPLEMENTED

1. **Create Supabase Project**:
   - Sign up at <https://supabase.com>
   - Create new project
   - Note down project URL and API keys

2. **Enable pgvector Extension**:
   ```sql
   -- Run in Supabase SQL editor
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Create Database Schema** ✅ IMPLEMENTED:
   ```sql
   -- Users table (extends Supabase auth.users)
   CREATE TABLE public.users (
     id UUID REFERENCES auth.users(id) PRIMARY KEY,
     email TEXT UNIQUE NOT NULL,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Knowledge bases table
   CREATE TABLE public.knowledge_bases (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
     name TEXT NOT NULL,
     description TEXT,
     is_public BOOLEAN DEFAULT false,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Documents table
   CREATE TABLE public.documents (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     knowledge_base_id UUID REFERENCES public.knowledge_bases(id) ON DELETE CASCADE,
     title TEXT NOT NULL,
     content TEXT NOT NULL,
     source_url TEXT,
     file_type TEXT,
     metadata JSONB DEFAULT '{}',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Vector embeddings table
   CREATE TABLE public.embeddings (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
     content_chunk TEXT NOT NULL,
     embedding vector(1536),
     chunk_index INTEGER,
     metadata JSONB DEFAULT '{}',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Conversations table
   CREATE TABLE public.conversations (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
     knowledge_base_id UUID REFERENCES public.knowledge_bases(id),
     title TEXT,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Messages table
   CREATE TABLE public.messages (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     conversation_id UUID REFERENCES public.conversations(id) ON DELETE CASCADE,
     role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
     content TEXT NOT NULL,
     metadata JSONB DEFAULT '{}',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

4. **Set up Row Level Security (RLS)** ✅ IMPLEMENTED:
   ```sql
   -- Enable RLS on all tables
   ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
   ALTER TABLE public.knowledge_bases ENABLE ROW LEVEL SECURITY;
   ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
   ALTER TABLE public.embeddings ENABLE ROW LEVEL SECURITY;
   ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
   ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

   -- Create RLS policies
   -- Users can only access their own data
   CREATE POLICY "Users can view own profile" ON public.users
     FOR SELECT USING (auth.uid() = id);

   -- Knowledge bases: users can access their own or public ones
   CREATE POLICY "Users can manage own knowledge bases" ON public.knowledge_bases
     FOR ALL USING (auth.uid() = user_id OR is_public = true);

   -- Documents: users can access documents in their knowledge bases
   CREATE POLICY "Users can access documents in their knowledge bases" ON public.documents
     FOR ALL USING (
       EXISTS (
         SELECT 1 FROM public.knowledge_bases kb
         WHERE kb.id = knowledge_base_id
         AND (kb.user_id = auth.uid() OR kb.is_public = true)
       )
     );

   -- Embeddings: users can access embeddings for their documents
   CREATE POLICY "Users can access embeddings for their documents" ON public.embeddings
     FOR ALL USING (
       EXISTS (
         SELECT 1 FROM public.documents d
         JOIN public.knowledge_bases kb ON d.knowledge_base_id = kb.id
         WHERE d.id = document_id
         AND (kb.user_id = auth.uid() OR kb.is_public = true)
       )
     );

   -- Conversations: users can access their own conversations
   CREATE POLICY "Users can manage own conversations" ON public.conversations
     FOR ALL USING (auth.uid() = user_id);

   -- Messages: users can access messages in their conversations
   CREATE POLICY "Users can access messages in their conversations" ON public.messages
     FOR ALL USING (
       EXISTS (
         SELECT 1 FROM public.conversations c
         WHERE c.id = conversation_id
         AND c.user_id = auth.uid()
       )
     );
   ```

## Application Deployment

### Docker Configuration ✅ IMPLEMENTED

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "app.py"]
```

### Docker Compose for Local Development ✅ IMPLEMENTED

```yaml
# docker-compose.yml
version: '3.8'

services:
  ragspace:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## Monitoring and Maintenance

### Health Checks ✅ IMPLEMENTED

```python
# health_check.py
import requests
import time
import sys

def check_health():
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Application is healthy")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    if not check_health():
        sys.exit(1)
```

### Logging Configuration ✅ IMPLEMENTED

```python
# logging_config.py
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Create logger
    logger = logging.getLogger('ragspace')
    logger.setLevel(logging.INFO)

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        'ragspace.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

### Backup and Recovery ✅ IMPLEMENTED

```python
# backup.py
import os
import json
import datetime
from supabase import create_client

def backup_database():
    """Backup database to JSON file"""
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    )
    
    # Backup knowledge bases
    knowledge_bases = supabase.table('knowledge_bases').select('*').execute()
    
    # Backup documents
    documents = supabase.table('documents').select('*').execute()
    
    # Create backup file
    backup_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'knowledge_bases': knowledge_bases.data,
        'documents': documents.data
    }
    
    backup_filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(backup_filename, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"Backup created: {backup_filename}")
    return backup_filename
```

## Security Considerations

### SSL/TLS Configuration ✅ IMPLEMENTED
- Always use HTTPS in production
- Configure SSL certificates (Let's Encrypt for free certificates)
- Set up HSTS headers
- Use secure cookies and sessions

### API Security ✅ IMPLEMENTED
- Implement rate limiting
- Add request validation
- Use API keys for external access
- Monitor for suspicious activity

### Data Protection ✅ IMPLEMENTED
- Encrypt sensitive data at rest
- Use secure database connections
- Implement data retention policies
- Regular security audits

## Cost Optimization

### Free Tier Usage
- Hugging Face Spaces: Free for demos
- Railway: $5/month after free tier
- Render: Free tier available
- Supabase: Free tier with 500MB database
- OpenAI: Pay-per-use, relatively inexpensive

### Cost Monitoring
```python
# cost_monitor.py
import os
import requests
from datetime import datetime

def monitor_openai_usage():
    """Monitor OpenAI API usage and costs"""
    # This would require OpenAI usage API access
    # Implementation depends on OpenAI's usage tracking
    pass

def estimate_monthly_costs():
    """Estimate monthly costs based on usage patterns"""
    # Calculate estimated costs based on:
    # - Number of embeddings generated
    # - Number of LLM API calls
    # - Database storage usage
    # - Bandwidth usage
    pass
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Check Supabase URL and API keys
   - Verify network connectivity
   - Check database schema and permissions

2. **OpenAI API Issues**:
   - Verify API key is valid
   - Check rate limits and quotas
   - Monitor API usage and costs

3. **MCP Server Issues**:
   - Verify MCP server is enabled
   - Check port configuration
   - Test with MCP client tools

4. **Deployment Issues**:
   - Check environment variables
   - Verify build process
   - Monitor application logs

### Debug Mode ✅ IMPLEMENTED

```python
# Enable debug mode for troubleshooting
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
    # Enable detailed error messages
    # Add additional debugging endpoints
```

## Current Deployment Status

### ✅ Completed
- **Local Development**: Docker and docker-compose setup
- **Database**: Supabase integration with proper schema
- **Environment**: Configuration and variable management
- **Monitoring**: Health checks and logging
- **Security**: Authentication and data protection

### 🔄 In Progress
- **Production Deployment**: Setting up deployment platforms
- **Vector Database**: pgvector integration
- **Performance Optimization**: Query optimization and caching

### 📋 Planned
- **Hugging Face Spaces**: Demo deployment
- **Railway/Render**: Production deployment
- **CI/CD Pipeline**: Automated deployment
- **Monitoring**: Advanced monitoring and alerting

## Update History

- **2025-08-07**: Updated deployment status - Local development complete, production deployment in progress
- **2025-08-05**: Initial deployment configuration and documentation
- **2025-08-04**: Docker setup and environment configuration