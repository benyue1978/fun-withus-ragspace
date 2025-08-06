-- Seed data for RAGSpace
-- This file will be executed after migrations

-- Insert sample docsets
INSERT INTO docsets (name, description) VALUES 
  ('gradio mcp', 'Gradio MCP integration documentation'),
  ('python examples', 'Python code examples and tutorials'),
  ('ai knowledge base', 'AI and machine learning resources')
ON CONFLICT (name) DO NOTHING;

-- Get the docset IDs for sample documents
DO $$
DECLARE
  gradio_docset_id uuid;
  python_docset_id uuid;
  ai_docset_id uuid;
BEGIN
  SELECT id INTO gradio_docset_id FROM docsets WHERE name = 'gradio mcp';
  SELECT id INTO python_docset_id FROM docsets WHERE name = 'python examples';
  SELECT id INTO ai_docset_id FROM docsets WHERE name = 'ai knowledge base';
  
  -- Insert sample documents for gradio mcp
  INSERT INTO documents (docset_id, name, type, content) VALUES 
    (gradio_docset_id, 'Gradio MCP Server', 'file', 'Gradio provides MCP server functionality through the gradio[mcp] package. This allows you to expose Python functions as MCP tools that can be used by LLM clients like Cursor and Claude Desktop.'),
    (gradio_docset_id, 'MCP Protocol', 'url', 'Model Context Protocol enables LLM clients to interact with external tools. It provides a standardized way for AI models to access external data sources and perform actions.'),
    (gradio_docset_id, 'Gradio Interface', 'file', 'Gradio is a Python library for creating web interfaces for machine learning models. It provides a simple way to create UIs with just a few lines of Python code.')
  ON CONFLICT DO NOTHING;
  
  -- Insert sample documents for python examples
  INSERT INTO documents (docset_id, name, type, content) VALUES 
    (python_docset_id, 'Python Basics', 'file', 'Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.'),
    (python_docset_id, 'Data Structures', 'file', 'Python provides several built-in data structures including lists, tuples, dictionaries, and sets. Each has specific use cases and performance characteristics.'),
    (python_docset_id, 'Async Programming', 'file', 'Python supports asynchronous programming with async/await syntax. This is useful for I/O-bound operations and concurrent programming.')
  ON CONFLICT DO NOTHING;
  
  -- Insert sample documents for ai knowledge base
  INSERT INTO documents (docset_id, name, type, content) VALUES 
    (ai_docset_id, 'Machine Learning Basics', 'file', 'Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.'),
    (ai_docset_id, 'Neural Networks', 'file', 'Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information.'),
    (ai_docset_id, 'Natural Language Processing', 'file', 'NLP is a field of AI that focuses on the interaction between computers and human language. It includes tasks like text classification, translation, and generation.')
  ON CONFLICT DO NOTHING;
END $$; 