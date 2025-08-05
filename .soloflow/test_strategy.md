# RAGSpace Testing Strategy

## Testing Overview

### Testing Philosophy
- **Modular Testing**: Test each component independently
- **Integration Testing**: Verify component interactions
- **End-to-End Testing**: Validate complete user workflows
- **Performance Testing**: Ensure system scalability
- **Security Testing**: Validate authentication and data protection

### Testing Pyramid
```
    E2E Tests (Few, Critical Paths)
         ▲
    Integration Tests (Medium)
         ▲
    Unit Tests (Many, Fast)
```

## Unit Testing

### Core Components to Test

#### 1. Data Processing Modules
```python
# test_data_processing.py
import pytest
from ragspace.processors.text_processor import TextProcessor
from ragspace.processors.github_processor import GitHubProcessor
from ragspace.processors.web_processor import WebProcessor

class TestTextProcessor:
    def test_text_chunking(self):
        processor = TextProcessor()
        text = "This is a long text that needs to be chunked into smaller pieces."
        chunks = processor.chunk_text(text, chunk_size=20)
        assert len(chunks) > 1
        assert all(len(chunk) <= 20 for chunk in chunks)

    def test_code_chunking(self):
        processor = TextProcessor()
        code = """
        def hello_world():
            print("Hello, World!")
        
        def another_function():
            return "test"
        """
        chunks = processor.chunk_code(code)
        assert len(chunks) > 0
        # Verify code chunks maintain function boundaries

class TestGitHubProcessor:
    def test_repository_validation(self):
        processor = GitHubProcessor()
        valid_repo = "owner/repo"
        invalid_repo = "invalid-repo-format"
        
        assert processor.validate_repository(valid_repo) == True
        assert processor.validate_repository(invalid_repo) == False

    def test_content_extraction(self):
        processor = GitHubProcessor()
        # Mock GitHub API response
        mock_content = {
            "type": "file",
            "content": "print('Hello World')",
            "encoding": "base64"
        }
        extracted = processor.extract_content(mock_content)
        assert "print('Hello World')" in extracted

class TestWebProcessor:
    def test_url_validation(self):
        processor = WebProcessor()
        valid_url = "https://example.com"
        invalid_url = "not-a-url"
        
        assert processor.validate_url(valid_url) == True
        assert processor.validate_url(invalid_url) == False

    def test_content_extraction(self):
        processor = WebProcessor()
        mock_html = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        extracted = processor.extract_content(mock_html)
        assert "Title" in extracted
        assert "Content" in extracted
```

#### 2. Embedding and Vector Operations
```python
# test_embeddings.py
import pytest
import numpy as np
from ragspace.embeddings.embedding_service import EmbeddingService
from ragspace.vector.vector_store import VectorStore

class TestEmbeddingService:
    def test_text_embedding(self):
        service = EmbeddingService()
        text = "This is a test sentence."
        embedding = service.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == 1536  # OpenAI ada-002 dimension

    def test_batch_embedding(self):
        service = EmbeddingService()
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = service.embed_batch(texts)
        
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)

class TestVectorStore:
    def test_vector_storage(self):
        store = VectorStore()
        vectors = [np.random.rand(1536) for _ in range(5)]
        metadata = [{"text": f"chunk_{i}"} for i in range(5)]
        
        ids = store.store_vectors(vectors, metadata)
        assert len(ids) == 5

    def test_similarity_search(self):
        store = VectorStore()
        # Store test vectors
        query_vector = np.random.rand(1536)
        results = store.similarity_search(query_vector, k=3)
        
        assert len(results) <= 3
        assert all('score' in result for result in results)
```

#### 3. RAG Pipeline Components
```python
# test_rag_pipeline.py
import pytest
from ragspace.rag.retriever import Retriever
from ragspace.rag.generator import Generator
from ragspace.rag.pipeline import RAGPipeline

class TestRetriever:
    def test_context_retrieval(self):
        retriever = Retriever()
        query = "How to use the API?"
        
        # Mock vector store with test data
        context = retriever.retrieve_context(query, k=3)
        
        assert len(context) <= 3
        assert all('content' in item for item in context)

class TestGenerator:
    def test_response_generation(self):
        generator = Generator()
        query = "What is the main function?"
        context = ["The main function is the entry point."]
        
        response = generator.generate_response(query, context)
        
        assert isinstance(response, str)
        assert len(response) > 0

class TestRAGPipeline:
    def test_end_to_end_pipeline(self):
        pipeline = RAGPipeline()
        query = "How to install the package?"
        
        response = pipeline.process_query(query)
        
        assert isinstance(response, dict)
        assert 'answer' in response
        assert 'sources' in response
```

#### 4. API Endpoints
```python
# test_api.py
import pytest
from fastapi.testclient import TestClient
from ragspace.api.main import app

client = TestClient(app)

class TestAPIEndpoints:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_knowledge_base_creation(self):
        data = {
            "name": "Test Knowledge Base",
            "description": "A test knowledge base"
        }
        response = client.post("/api/knowledge-bases", json=data)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_document_upload(self):
        # Test file upload
        files = {"file": ("test.txt", b"Test content", "text/plain")}
        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200

    def test_query_processing(self):
        data = {"query": "What is the main topic?"}
        response = client.post("/api/query", json=data)
        assert response.status_code == 200
        assert "answer" in response.json()
```

## Integration Testing

### Database Integration Tests
```python
# test_database_integration.py
import pytest
from ragspace.database.connection import get_database
from ragspace.models.knowledge_base import KnowledgeBase

class TestDatabaseIntegration:
    @pytest.fixture
    def db_session(self):
        # Setup test database session
        session = get_database()
        yield session
        # Cleanup after test

    def test_knowledge_base_crud(self, db_session):
        # Create
        kb = KnowledgeBase(name="Test KB", description="Test")
        db_session.add(kb)
        db_session.commit()
        
        # Read
        retrieved = db_session.query(KnowledgeBase).filter_by(name="Test KB").first()
        assert retrieved is not None
        assert retrieved.name == "Test KB"
        
        # Update
        retrieved.description = "Updated description"
        db_session.commit()
        
        # Delete
        db_session.delete(retrieved)
        db_session.commit()
        
        # Verify deletion
        assert db_session.query(KnowledgeBase).filter_by(name="Test KB").first() is None
```

### External API Integration Tests
```python
# test_external_apis.py
import pytest
from unittest.mock import patch
from ragspace.services.openai_service import OpenAIService
from ragspace.services.github_service import GitHubService

class TestOpenAIIntegration:
    @patch('openai.Embedding.create')
    def test_embedding_api_call(self, mock_embedding):
        mock_embedding.return_value = {
            'data': [{'embedding': [0.1] * 1536}]
        }
        
        service = OpenAIService()
        embedding = service.embed_text("Test text")
        
        assert len(embedding) == 1536
        mock_embedding.assert_called_once()

    @patch('openai.ChatCompletion.create')
    def test_chat_completion_api_call(self, mock_chat):
        mock_chat.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        
        service = OpenAIService()
        response = service.generate_response("Test query", ["Test context"])
        
        assert response == "Test response"
        mock_chat.assert_called_once()

class TestGitHubIntegration:
    @patch('requests.get')
    def test_repository_content_fetch(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "README.md", "type": "file"}
        ]
        
        service = GitHubService()
        content = service.fetch_repository_content("owner/repo")
        
        assert len(content) > 0
        mock_get.assert_called()
```

## End-to-End Testing

### User Workflow Tests
```python
# test_user_workflows.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserWorkflows:
    @pytest.fixture
    def driver(self):
        driver = webdriver.Chrome()
        yield driver
        driver.quit()

    def test_knowledge_base_creation_workflow(self, driver):
        # Navigate to application
        driver.get("http://localhost:8000")
        
        # Login (if required)
        # Fill in login form...
        
        # Create knowledge base
        create_kb_button = driver.find_element(By.ID, "create-kb")
        create_kb_button.click()
        
        # Fill knowledge base form
        name_input = driver.find_element(By.ID, "kb-name")
        name_input.send_keys("Test Knowledge Base")
        
        desc_input = driver.find_element(By.ID, "kb-description")
        desc_input.send_keys("A test knowledge base")
        
        # Submit form
        submit_button = driver.find_element(By.ID, "submit-kb")
        submit_button.click()
        
        # Verify knowledge base was created
        wait = WebDriverWait(driver, 10)
        success_message = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "Knowledge base created successfully" in success_message.text

    def test_document_upload_workflow(self, driver):
        # Navigate to knowledge base
        driver.get("http://localhost:8000/kb/1")
        
        # Upload file
        file_input = driver.find_element(By.ID, "file-upload")
        file_input.send_keys("/path/to/test/file.txt")
        
        # Submit upload
        upload_button = driver.find_element(By.ID, "upload-submit")
        upload_button.click()
        
        # Verify upload success
        wait = WebDriverWait(driver, 10)
        upload_success = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-success"))
        )
        assert "File uploaded successfully" in upload_success.text

    def test_query_workflow(self, driver):
        # Navigate to chat interface
        driver.get("http://localhost:8000/chat")
        
        # Enter query
        query_input = driver.find_element(By.ID, "query-input")
        query_input.send_keys("What is the main topic?")
        
        # Submit query
        submit_button = driver.find_element(By.ID, "submit-query")
        submit_button.click()
        
        # Wait for response
        wait = WebDriverWait(driver, 30)
        response = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "response"))
        )
        
        # Verify response
        assert len(response.text) > 0
```

### MCP Integration Tests
```python
# test_mcp_integration.py
import pytest
import asyncio
from ragspace.mcp.server import MCPServer
from ragspace.mcp.client import MCPClient

class TestMCPIntegration:
    @pytest.fixture
    def mcp_server(self):
        server = MCPServer()
        return server

    @pytest.fixture
    def mcp_client(self):
        client = MCPClient()
        return client

    def test_mcp_server_startup(self, mcp_server):
        # Test server starts correctly
        assert mcp_server.is_running() == False
        mcp_server.start()
        assert mcp_server.is_running() == True
        mcp_server.stop()

    def test_mcp_tool_discovery(self, mcp_server, mcp_client):
        mcp_server.start()
        
        # Connect client to server
        mcp_client.connect("localhost", 8000)
        
        # Discover available tools
        tools = mcp_client.list_tools()
        
        # Verify expected tools are available
        tool_names = [tool["name"] for tool in tools]
        assert "query_knowledge_base" in tool_names
        assert "add_document" in tool_names
        
        mcp_server.stop()

    def test_mcp_tool_execution(self, mcp_server, mcp_client):
        mcp_server.start()
        mcp_client.connect("localhost", 8000)
        
        # Execute a tool
        result = mcp_client.call_tool("query_knowledge_base", {
            "query": "What is the main topic?",
            "knowledge_base_id": "test-kb-id"
        })
        
        # Verify result structure
        assert "answer" in result
        assert "sources" in result
        
        mcp_server.stop()
```

## Performance Testing

### Load Testing
```python
# test_performance.py
import pytest
import time
import concurrent.futures
from ragspace.api.main import app
from fastapi.testclient import TestClient

class TestPerformance:
    def test_concurrent_queries(self):
        client = TestClient(app)
        
        def make_query(query_id):
            response = client.post("/api/query", json={
                "query": f"Test query {query_id}",
                "knowledge_base_id": "test-kb"
            })
            return response.status_code == 200
        
        # Test concurrent queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_query, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # Verify all queries succeeded
        assert all(results)

    def test_response_time(self):
        client = TestClient(app)
        
        start_time = time.time()
        response = client.post("/api/query", json={
            "query": "Test query",
            "knowledge_base_id": "test-kb"
        })
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Verify response time is within acceptable limits
        assert response_time < 5.0  # 5 seconds max
        assert response.status_code == 200

    def test_vector_search_performance(self):
        from ragspace.vector.vector_store import VectorStore
        
        store = VectorStore()
        
        # Generate test vectors
        test_vectors = [np.random.rand(1536) for _ in range(1000)]
        test_metadata = [{"text": f"chunk_{i}"} for i in range(1000)]
        
        # Store vectors
        start_time = time.time()
        store.store_vectors(test_vectors, test_metadata)
        store_time = time.time() - start_time
        
        # Test search performance
        query_vector = np.random.rand(1536)
        start_time = time.time()
        results = store.similarity_search(query_vector, k=10)
        search_time = time.time() - start_time
        
        # Verify performance metrics
        assert store_time < 10.0  # 10 seconds max for storing 1000 vectors
        assert search_time < 1.0   # 1 second max for search
        assert len(results) == 10
```

## Security Testing

### Authentication Tests
```python
# test_security.py
import pytest
from ragspace.auth.authentication import AuthenticationService
from ragspace.auth.authorization import AuthorizationService

class TestAuthentication:
    def test_user_registration(self):
        auth_service = AuthenticationService()
        
        # Test valid registration
        user = auth_service.register_user("test@example.com", "password123")
        assert user is not None
        assert user.email == "test@example.com"
        
        # Test duplicate registration
        with pytest.raises(ValueError):
            auth_service.register_user("test@example.com", "password123")

    def test_user_login(self):
        auth_service = AuthenticationService()
        
        # Register user
        auth_service.register_user("test@example.com", "password123")
        
        # Test valid login
        token = auth_service.login("test@example.com", "password123")
        assert token is not None
        
        # Test invalid login
        with pytest.raises(ValueError):
            auth_service.login("test@example.com", "wrongpassword")

class TestAuthorization:
    def test_resource_access_control(self):
        auth_service = AuthorizationService()
        
        # Test user can access their own resources
        user_id = "user123"
        resource_owner = "user123"
        assert auth_service.can_access_resource(user_id, resource_owner) == True
        
        # Test user cannot access other user's resources
        other_owner = "user456"
        assert auth_service.can_access_resource(user_id, other_owner) == False

    def test_api_token_validation(self):
        auth_service = AuthenticationService()
        
        # Generate API token
        user_id = "user123"
        token = auth_service.generate_api_token(user_id)
        
        # Validate token
        validated_user = auth_service.validate_api_token(token)
        assert validated_user == user_id
        
        # Test invalid token
        with pytest.raises(ValueError):
            auth_service.validate_api_token("invalid-token")
```

## Test Configuration

### pytest Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
```

### Test Environment Setup
```python
# conftest.py
import pytest
import os
import tempfile
from ragspace.database.connection import get_test_database

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    db_url = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
    db = get_test_database(db_url)
    yield db
    # Cleanup test database

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API calls"""
    with patch('openai.Embedding.create') as mock_embedding, \
         patch('openai.ChatCompletion.create') as mock_chat:
        mock_embedding.return_value = {
            'data': [{'embedding': [0.1] * 1536}]
        }
        mock_chat.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        yield mock_embedding, mock_chat
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=ragspace --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    
    - name: Run security tests
      run: |
        pytest tests/security/ -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## Test Data Management

### Test Data Fixtures
```python
# tests/fixtures/test_data.py
import pytest
import json

@pytest.fixture
def sample_documents():
    return [
        {
            "title": "Introduction to Python",
            "content": "Python is a programming language...",
            "source": "https://example.com/python-intro"
        },
        {
            "title": "Machine Learning Basics",
            "content": "Machine learning is a subset of AI...",
            "source": "https://example.com/ml-basics"
        }
    ]

@pytest.fixture
def sample_queries():
    return [
        "What is Python?",
        "How does machine learning work?",
        "What are the benefits of AI?"
    ]

@pytest.fixture
def sample_knowledge_base():
    return {
        "name": "Test Knowledge Base",
        "description": "A test knowledge base for testing",
        "is_public": False
    }
```

## Monitoring Test Results

### Test Metrics
- **Test Coverage**: Aim for >80% code coverage
- **Test Execution Time**: Unit tests <1s, integration tests <30s
- **Test Reliability**: <1% flaky tests
- **Test Maintenance**: Regular review and update of tests

### Test Reporting
```python
# test_reporting.py
import pytest
import json
from datetime import datetime

class TestReporter:
    def __init__(self):
        self.results = []
    
    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            self.results.append({
                'name': report.nodeid,
                'outcome': report.outcome,
                'duration': report.duration,
                'timestamp': datetime.now().isoformat()
            })
    
    def generate_report(self):
        return {
            'summary': {
                'total': len(self.results),
                'passed': len([r for r in self.results if r['outcome'] == 'passed']),
                'failed': len([r for r in self.results if r['outcome'] == 'failed']),
                'skipped': len([r for r in self.results if r['outcome'] == 'skipped'])
            },
            'results': self.results
        }
```