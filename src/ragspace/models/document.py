"""
Document model for RAGSpace
"""

from typing import Dict, Any, Optional

class Document:
    """Represents a document in a DocSet"""
    
    def __init__(self, title: str, content: str, doc_type: str = "file", metadata: Optional[Dict[str, Any]] = None):
        self.title = title
        self.content = content
        self.doc_type = doc_type  # "file", "website", "github"
        self.metadata = metadata or {}
        self.id = None  # Will be set when added to docset
    
    def __str__(self) -> str:
        return f"Document(title='{self.title}', type='{self.doc_type}', id={self.id})"
    
    def __repr__(self) -> str:
        return self.__str__() 