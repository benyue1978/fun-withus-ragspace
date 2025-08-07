"""
Storage interface for RAGSpace
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List

class StorageInterface(ABC):
    """Abstract storage interface for RAGSpace"""
    
    @abstractmethod
    def create_docset(self, name: str, description: str = "") -> str:
        """Create a new docset"""
        pass
    
    @abstractmethod
    def get_docset_by_name(self, name: str) -> Optional[Dict]:
        """Get a docset by name"""
        pass
    
    @abstractmethod
    def list_docsets(self) -> str:
        """List all docsets"""
        pass
    
    @abstractmethod
    def add_document_to_docset(self, docset_name: str, title: str, content: str, 
                              doc_type: str = "file", metadata: Optional[Dict] = None) -> str:
        """Add a document to a specific docset"""
        pass
    
    @abstractmethod
    def list_documents_in_docset(self, docset_name: str) -> str:
        """List all documents in a specific docset"""
        pass
    
    @abstractmethod
    def query_knowledge_base(self, query: str, docset_name: Optional[str] = None) -> str:
        """Query the knowledge base"""
        pass
    
    @abstractmethod
    def get_docsets_dict(self) -> Dict[str, Dict]:
        """Get all docsets as a dictionary (for UI compatibility)"""
        pass

# Import implementations
from .manager import MockDocsetManager
from .supabase_manager import SupabaseDocsetManager

# Default to Mock for now, will be switched to Supabase when needed
docset_manager: StorageInterface = MockDocsetManager()

def use_supabase():
    """Switch to Supabase storage (for production)"""
    global docset_manager
    docset_manager = SupabaseDocsetManager()

def use_mock():
    """Switch to Mock storage (for testing)"""
    global docset_manager
    docset_manager = MockDocsetManager()

__all__ = [
    "StorageInterface",
    "MockDocsetManager", 
    "SupabaseDocsetManager",
    "docset_manager",
    "use_supabase",
    "use_mock"
] 