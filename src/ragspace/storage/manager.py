"""
Mock DocSet Manager for RAGSpace (Testing)
"""

import time
from typing import Dict, Optional, List
from ..models import DocSet, Document
from . import StorageInterface

class MockDocsetManager(StorageInterface):
    """Mock DocSet Manager for testing - implements StorageInterface"""
    
    def __init__(self):
        self.docsets: Dict[str, DocSet] = {}
    
    def create_docset(self, name: str, description: str = "") -> str:
        """Create a new docset"""
        if not name.strip():
            return f"DocSet name cannot be empty."
        
        if name in self.docsets:
            return f"DocSet '{name}' already exists."
        
        self.docsets[name] = DocSet(name, description)
        return f"✅ DocSet '{name}' created successfully."
    
    def get_docset_by_name(self, name: str) -> Optional[Dict]:
        """Get a docset by name - returns dict for compatibility with Supabase"""
        docset = self.docsets.get(name)
        if docset:
            return {
                "id": docset.name,  # Use name as id for mock compatibility
                "name": docset.name,
                "description": docset.description,
                "created_at": docset.metadata.get('created_at', time.time())
            }
        return None
    
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
    

    
    def list_documents_in_docset(self, docset_name: str) -> List[Dict]:
        """List all documents in a specific docset"""
        if docset_name not in self.docsets:
            return []
        
        docset = self.docsets[docset_name]
        if not docset.documents:
            return []
        
        # Convert documents to dict format for UI compatibility
        documents = []
        for doc in docset.documents:
            doc_dict = {
                "id": doc.id,
                "name": doc.title,
                "type": doc.doc_type,
                "content": doc.content,
                "url": doc.metadata.get('url'),
                "added_date": doc.metadata.get('added_date', time.time()),
                "parent_id": doc.metadata.get('parent_id')
            }
            documents.append(doc_dict)
        
        return documents
    
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
    
    def get_docsets_dict(self) -> Dict[str, Dict]:
        """Get all docsets as a dictionary (for UI compatibility)"""
        return {name: self.get_docset_by_name(name) for name in self.docsets.keys()}
    
    def add_document_to_docset(self, docset_name: str, title: str, content: str, 
                              doc_type: str = "file", metadata: Optional[Dict] = None, 
                              parent_id: Optional[str] = None) -> str:
        """Add a document to a specific docset with parent_id support"""
        if not docset_name.strip():
            return f"DocSet name cannot be empty."
        
        if docset_name not in self.docsets:
            return f"DocSet '{docset_name}' not found. Please create it first."
        
        # Add parent_id to metadata if provided
        if metadata is None:
            metadata = {}
        if parent_id:
            metadata['parent_id'] = parent_id
        
        doc = Document(title, content, doc_type, metadata)
        self.docsets[docset_name].add_document(doc)
        
        return f"✅ Document '{title}' added to docset '{docset_name}'."
    
    def add_url_to_docset(self, url: str, docset_name: str, **kwargs) -> str:
        """Mock URL to docset functionality"""
        # For testing, just add a mock document
        mock_content = f"Mock content from URL: {url}"
        mock_metadata = {"url": url, "crawler_options": kwargs}
        
        return self.add_document_to_docset(
            docset_name=docset_name,
            title=f"Mock Document from {url}",
            content=mock_content,
            doc_type="website",
            metadata=mock_metadata
        )
    
    def add_github_repo_to_docset(self, repo_url: str, docset_name: str, branch: str = "main") -> str:
        """Mock GitHub repo to docset functionality"""
        # For testing, just add a mock repository document
        mock_content = f"Mock GitHub repository: {repo_url} (branch: {branch})"
        mock_metadata = {"url": repo_url, "branch": branch, "type": "github"}
        
        return self.add_document_to_docset(
            docset_name=docset_name,
            title=f"Mock GitHub Repo: {repo_url}",
            content=mock_content,
            doc_type="github",
            metadata=mock_metadata
        )
    
    def get_document_with_children(self, docset_name: str, parent_name: str = None) -> Dict:
        """Mock get documents with children functionality"""
        if docset_name not in self.docsets:
            return {"error": f"DocSet '{docset_name}' not found"}
        
        docset = self.docsets[docset_name]
        parents = []
        
        # Find parent documents (those without parent_id)
        for doc in docset.documents:
            if not doc.metadata.get('parent_id'):
                # Find children for this parent
                children = []
                for child_doc in docset.documents:
                    if child_doc.metadata.get('parent_id') == doc.id:
                        children.append({
                            "id": child_doc.id,
                            "name": child_doc.title,
                            "type": child_doc.doc_type,
                            "content": child_doc.content,
                            "url": child_doc.metadata.get('url'),
                            "added_date": child_doc.metadata.get('added_date', time.time())
                        })
                
                parent_with_children = {
                    "id": doc.id,
                    "name": doc.title,
                    "type": doc.doc_type,
                    "content": doc.content,
                    "url": doc.metadata.get('url'),
                    "added_date": doc.metadata.get('added_date', time.time()),
                    "children": children
                }
                parents.append(parent_with_children)
        
        return {"documents": parents}
    
    def get_child_documents(self, parent_id: str) -> List[Dict]:
        """Mock get child documents functionality"""
        children = []
        for docset in self.docsets.values():
            for doc in docset.documents:
                if doc.metadata.get('parent_id') == parent_id:
                    children.append({
                        "id": doc.id,
                        "name": doc.title,
                        "type": doc.doc_type,
                        "content": doc.content,
                        "url": doc.metadata.get('url'),
                        "added_date": doc.metadata.get('added_date', time.time())
                    })
        return children
    
    def get_crawler_rate_limit(self, crawler_name: str = None) -> Dict:
        """Mock crawler rate limit functionality"""
        return {
            "GitHubCrawler": {
                "remaining": 5000,
                "limit": 5000,
                "reset_time": time.time() + 3600
            },
            "WebsiteCrawler": {
                "remaining": 1000,
                "limit": 1000,
                "reset_time": time.time() + 3600
            }
        }

# Global instance for testing
mock_docset_manager = MockDocsetManager() 