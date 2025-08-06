"""
DocSet model for RAGSpace
"""

import time
from typing import List, Optional
from .document import Document

class DocSet:
    """Represents a collection of documents"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.documents: List[Document] = []
        self.metadata = {
            "created_at": time.time(),
            "updated_at": time.time()
        }
    
    def add_document(self, doc: Document) -> None:
        """Add a document to this docset"""
        doc.id = len(self.documents) + 1
        self.documents.append(doc)
        self.metadata["updated_at"] = time.time()
    
    def get_document_by_id(self, doc_id: int) -> Optional[Document]:
        """Get a document by its ID"""
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None
    
    def search_documents(self, query: str) -> List[Document]:
        """Search documents in this docset"""
        results = []
        query_lower = query.lower()
        for doc in self.documents:
            if (query_lower in doc.content.lower() or 
                query_lower in doc.title.lower()):
                results.append(doc)
        return results
    
    def __str__(self) -> str:
        return f"DocSet(name='{self.name}', documents={len(self.documents)})"
    
    def __repr__(self) -> str:
        return self.__str__() 