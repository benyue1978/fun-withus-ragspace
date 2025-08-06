"""
DocSet Manager for RAGSpace
"""

import time
from typing import Dict, Optional
from ..models import DocSet, Document

class DocSetManager:
    """Manages DocSets and their operations"""
    
    def __init__(self):
        self.docsets: Dict[str, DocSet] = {}
    
    def create_docset(self, name: str, description: str = "") -> str:
        """Create a new docset"""
        if name in self.docsets:
            return f"DocSet '{name}' already exists."
        
        self.docsets[name] = DocSet(name, description)
        return f"✅ DocSet '{name}' created successfully."
    
    def get_docset(self, name: str) -> Optional[DocSet]:
        """Get a docset by name"""
        return self.docsets.get(name)
    
    def list_docsets(self) -> str:
        """List all docsets"""
        if not self.docsets:
            return "No docsets available."
        
        result = "📚 Available DocSets:\n\n"
        for name, docset in self.docsets.items():
            result += f"📁 {name}\n"
            result += f"   Description: {docset.description}\n"
            result += f"   Documents: {len(docset.documents)}\n"
            result += f"   Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(docset.metadata['created_at']))}\n"
            result += f"   Updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(docset.metadata['updated_at']))}\n\n"
        
        return result
    
    def add_document_to_docset(self, docset_name: str, title: str, content: str, 
                              doc_type: str = "file", metadata: Optional[Dict] = None) -> str:
        """Add a document to a specific docset"""
        if docset_name not in self.docsets:
            return f"DocSet '{docset_name}' not found. Please create it first."
        
        doc = Document(title, content, doc_type, metadata)
        self.docsets[docset_name].add_document(doc)
        
        return f"✅ Document '{title}' added to docset '{docset_name}'. Total documents: {len(self.docsets[docset_name].documents)}"
    
    def list_documents_in_docset(self, docset_name: str) -> str:
        """List all documents in a specific docset"""
        if docset_name not in self.docsets:
            return f"DocSet '{docset_name}' not found."
        
        docset = self.docsets[docset_name]
        if not docset.documents:
            return f"DocSet '{docset_name}' is empty."
        
        result = f"📚 Documents in DocSet '{docset_name}':\n\n"
        for i, doc in enumerate(docset.documents, 1):
            result += f"{i}. {doc.title}\n"
            result += f"   Type: {doc.doc_type}\n"
            if doc.metadata.get('url'):
                result += f"URL: {doc.metadata['url']}\n"
            result += f"   ID: {doc.id}\n\n"
        
        return result
    
    def query_knowledge_base(self, query: str, docset_name: Optional[str] = None) -> str:
        """Query the knowledge base"""
        if not self.docsets:
            return "No docsets available. Please create a docset first."
        
        # If docset_name is specified, search only in that docset
        if docset_name:
            if docset_name not in self.docsets:
                return f"DocSet '{docset_name}' not found."
            search_docsets = {docset_name: self.docsets[docset_name]}
        else:
            # Search in all docsets
            search_docsets = self.docsets
        
        # Search for relevant documents
        results = []
        for docset_name, docset in search_docsets.items():
            for doc in docset.documents:
                if query.lower() in doc.content.lower() or query.lower() in doc.title.lower():
                    results.append((docset_name, doc))
        
        if results:
            response = f"Found {len(results)} relevant documents:\n\n"
            for i, (docset_name, doc) in enumerate(results[:5]):
                response += f"📄 [{docset_name}] {doc.title}\n"
                response += f"Type: {doc.doc_type}\n"
                if doc.metadata.get('url'):
                    response += f"URL: {doc.metadata['url']}\n"
                response += f"{doc.content[:200]}...\n\n"
            return response
        else:
            docset_info = f" in docset '{docset_name}'" if docset_name else ""
            return f"No documents found matching '{query}'{docset_info}. Try adding more documents to the knowledge base."

# Global instance
docset_manager = DocSetManager() 