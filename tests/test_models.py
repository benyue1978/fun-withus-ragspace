"""
Tests for RAGSpace models
"""

import pytest
from src.ragspace.models import Document, DocSet

class TestDocument:
    def test_document_creation(self):
        """Test Document creation"""
        doc = Document("Test Document", "Test content", "file")
        assert doc.title == "Test Document"
        assert doc.content == "Test content"
        assert doc.doc_type == "file"
        assert doc.id is None
    
    def test_document_with_metadata(self):
        """Test Document creation with metadata"""
        metadata = {"url": "https://example.com", "type": "website"}
        doc = Document("Test Document", "Test content", "website", metadata)
        assert doc.metadata["url"] == "https://example.com"
        assert doc.metadata["type"] == "website"

class TestDocSet:
    def test_docset_creation(self):
        """Test DocSet creation"""
        docset = DocSet("Test DocSet", "Test description")
        assert docset.name == "Test DocSet"
        assert docset.description == "Test description"
        assert len(docset.documents) == 0
    
    def test_add_document(self):
        """Test adding document to DocSet"""
        docset = DocSet("Test DocSet")
        doc = Document("Test Document", "Test content")
        
        docset.add_document(doc)
        assert len(docset.documents) == 1
        assert doc.id == 1
        assert docset.documents[0] == doc
    
    def test_search_documents(self):
        """Test document search"""
        docset = DocSet("Test DocSet")
        doc1 = Document("Python Guide", "Python programming guide")
        doc2 = Document("JavaScript Guide", "JavaScript programming guide")
        
        docset.add_document(doc1)
        docset.add_document(doc2)
        
        results = docset.search_documents("Python")
        assert len(results) == 1
        assert results[0].title == "Python Guide" 