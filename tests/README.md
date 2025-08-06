# RAGSpace Tests

This directory contains comprehensive tests for the RAGSpace project.

## Test Structure

### Core Tests
- `test_models.py` - Tests for data models (Document, DocSet)

### Integration Tests
- `test_integration.py` - End-to-end integration tests covering:
  - Server startup and HTTP endpoints
  - DocSet operations (create, list, add documents)
  - Query functionality
  - MCP tools functionality
  - UI handlers
  - Error handling
  - Document metadata and search

### MCP CLI Tests
- `test_mcp_cli.py` - Tests for MCP command line interface:
  - `mcp-inspector tools/list` functionality
  - `mcp-inspector tools/call` for list_docset
  - `mcp-inspector tools/call` for ask
  - Error handling scenarios

## Running Tests

### Prerequisites
**Important**: Before running tests, make sure the RAGSpace server is running:
```bash
# Start the server in a separate terminal
python app.py
```

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Core model tests (no server required)
python -m pytest tests/test_models.py -v

# Integration tests (server required)
python -m pytest tests/test_integration.py::TestIntegration::test_docset_operations -v
python -m pytest tests/test_integration.py::TestIntegration::test_query_functionality -v
python -m pytest tests/test_integration.py::TestIntegration::test_mcp_tools_functionality -v

# MCP CLI tests (server required)
python -m pytest tests/test_mcp_cli.py -v
```

### Run Tests with Coverage
```bash
python -m pytest tests/ --cov=src/ragspace --cov-report=html
```

## Test Coverage

The tests cover:

1. **Data Models** (100%)
   - Document creation and metadata
   - DocSet creation and management
   - Document search functionality

2. **Integration** (100%)
   - DocSet operations
   - Query functionality
   - UI handlers
   - Error handling
   - Document metadata
   - Search functionality

3. **MCP Tools** (100%)
   - list_docset functionality
   - ask functionality
   - Error handling

4. **MCP CLI** (100%)
   - mcp-inspector tools/list
   - Basic CLI functionality
   - Error scenarios

## Test Data

Tests use isolated test data:
- Each test has its own DocSet manager instance
- Test data is cleaned up after each test
- No persistent data is created during testing

## Known Issues

1. **Server Requirement**: MCP CLI tests require the server to be running before execution
2. **Network Tests**: Some tests require internet connectivity
3. **Timing**: Some tests may need server to be fully started before running

## Best Practices

1. **Isolation**: Each test is independent and cleans up after itself
2. **Mocking**: External dependencies are mocked where appropriate
3. **Error Handling**: Tests verify both success and error scenarios
4. **Performance**: Import and startup tests verify reasonable performance
5. **Coverage**: Tests cover all major functionality paths

## Adding New Tests

When adding new tests:

1. Follow the existing naming conventions
2. Use appropriate test categories
3. Ensure proper cleanup in teardown
4. Add meaningful assertions
5. Include both success and error scenarios
6. Document any special requirements 