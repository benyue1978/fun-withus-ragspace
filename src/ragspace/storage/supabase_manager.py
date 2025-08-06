"""
Supabase DocSet Manager for RAGSpace (Production)
"""

import os
import time
from typing import Dict, Optional, List
from supabase import create_client, Client
from dotenv import load_dotenv
from . import StorageInterface
from ..services import crawler_registry, register_default_crawlers

# Load environment variables
load_dotenv()

class SupabaseDocsetManager(StorageInterface):
    """Manages DocSets and their operations using Supabase - implements StorageInterface"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Register default crawlers with proper environment loading
        register_default_crawlers()
        
        print(f"✅ Supabase client initialized with URL: {supabase_url}")
    
    def create_docset(self, name: str, description: str = "") -> str:
        """Create a new docset"""
        try:
            # Check if docset already exists
            existing = self.supabase.table("docsets").select("id").eq("name", name).execute()
            if existing.data:
                return f"DocSet '{name}' already exists."
            
            # Create new docset
            result = self.supabase.table("docsets").insert({
                "name": name,
                "description": description
            }).execute()
            
            print(f"✅ Created docset: {name}")
            return f"✅ DocSet '{name}' created successfully."
            
        except Exception as e:
            print(f"❌ Error creating docset: {e}")
            return f"❌ Error creating DocSet '{name}': {str(e)}"
    
    def list_docsets(self) -> str:
        """List all docsets"""
        try:
            result = self.supabase.table("docsets").select("*").order("created_at", desc=True).execute()
            
            if not result.data:
                return "No docsets available."
            
            response = "📚 Available DocSets:\n\n"
            for docset in result.data:
                # Get document count for each docset
                doc_count = self.supabase.table("documents").select("id", count="exact").eq("docset_id", docset["id"]).execute()
                count = doc_count.count if doc_count.count is not None else 0
                
                response += f"📁 {docset['name']}\n"
                response += f"   Description: {docset['description'] or 'No description'}\n"
                response += f"   Documents: {count}\n"
                response += f"   Created: {docset['created_at']}\n\n"
            
            print(f"✅ Listed {len(result.data)} docsets")
            return response
            
        except Exception as e:
            print(f"❌ Error listing docsets: {e}")
            return f"❌ Error listing docsets: {str(e)}"
    
    def get_docset_by_name(self, name: str) -> Optional[Dict]:
        """Get a docset by name"""
        try:
            result = self.supabase.table("docsets").select("*").eq("name", name).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error getting docset '{name}': {e}")
            return None
    
    def add_document_to_docset(self, docset_name: str, title: str, content: str, 
                              doc_type: str = "file", metadata: Optional[Dict] = None, 
                              parent_id: Optional[str] = None) -> str:
        """Add a document to a specific docset"""
        try:
            # Get docset by name
            docset = self.get_docset_by_name(docset_name)
            if not docset:
                return f"DocSet '{docset_name}' not found. Please create it first."
            
            # Prepare document data
            doc_data = {
                "docset_id": docset["id"],
                "name": title,
                "type": doc_type,
                "content": content,
                "url": metadata.get("url") if metadata else None,
                "metadata": metadata or {},
                "parent_id": parent_id
            }
            
            # Insert document
            result = self.supabase.table("documents").insert(doc_data).execute()
            
            print(f"✅ Added document '{title}' to docset '{docset_name}'")
            return f"✅ Document '{title}' added to docset '{docset_name}'."
            
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return f"❌ Error adding document to '{docset_name}': {str(e)}"
    
    def list_documents_in_docset(self, docset_name: str) -> List[Dict]:
        """List all documents in a specific docset"""
        try:
            # Get docset by name
            docset = self.get_docset_by_name(docset_name)
            if not docset:
                return []
            
            # Get documents for this docset
            result = self.supabase.table("documents").select("*").eq("docset_id", docset["id"]).order("added_date", desc=True).execute()
            
            if not result.data:
                return []
            
            print(f"✅ Listed {len(result.data)} documents in docset '{docset_name}'")
            return result.data
            
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            return []
    
    def query_knowledge_base(self, query: str, docset_name: Optional[str] = None) -> str:
        """Query the knowledge base"""
        try:
            # Build query
            query_builder = self.supabase.table("documents").select("*, docsets(name)")
            
            if docset_name:
                # Get docset by name
                docset = self.get_docset_by_name(docset_name)
                if not docset:
                    return f"DocSet '{docset_name}' not found."
                query_builder = query_builder.eq("docset_id", docset["id"])
            
            result = query_builder.execute()
            
            if not result.data:
                docset_info = f" in docset '{docset_name}'" if docset_name else ""
                return f"No documents found{docset_info}. Try adding more documents to the knowledge base."
            
            # Search for relevant documents
            results = []
            query_lower = query.lower()
            for doc in result.data:
                if (query_lower in doc['content'].lower() or 
                    query_lower in doc['name'].lower()):
                    results.append(doc)
            
            if results:
                response = f"Found {len(results)} relevant documents:\n\n"
                for i, doc in enumerate(results[:5]):
                    docset_name = doc.get('docsets', {}).get('name', 'Unknown')
                    response += f"📄 [{docset_name}] {doc['name']}\n"
                    response += f"Type: {doc['type']}\n"
                    if doc.get('url'):
                        response += f"URL: {doc['url']}\n"
                    response += f"{doc['content'][:200]}...\n\n"
                return response
            else:
                docset_info = f" in docset '{docset_name}'" if docset_name else ""
                return f"No documents found matching '{query}'{docset_info}. Try adding more documents to the knowledge base."
                
        except Exception as e:
            print(f"❌ Error querying knowledge base: {e}")
            return f"❌ Error querying knowledge base: {str(e)}"
    
    def get_docsets_dict(self) -> Dict[str, Dict]:
        """Get all docsets as a dictionary (for UI compatibility)"""
        try:
            result = self.supabase.table("docsets").select("*").execute()
            return {docset["name"]: docset for docset in result.data}
        except Exception as e:
            print(f"❌ Error getting docsets dict: {e}")
            return {}
    
    def add_url_to_docset(self, url: str, docset_name: str, **kwargs) -> str:
        """Add content from URL to a specific docset using appropriate crawler"""
        try:
            # Get docset by name
            docset = self.get_docset_by_name(docset_name)
            if not docset:
                return f"DocSet '{docset_name}' not found. Please create it first."
            
            # Get appropriate crawler for URL
            crawler = crawler_registry.get_crawler_for_url(url)
            if not crawler:
                supported_patterns = [c.get_supported_url_patterns() for c in crawler_registry.get_all_crawlers()]
                return f"❌ No crawler available for URL: {url}\nSupported patterns: {supported_patterns}"
            
            # Crawl the URL
            crawl_result = crawler.crawl(url, **kwargs)
            
            if not crawl_result.success:
                return f"❌ Failed to crawl URL: {crawl_result.message}"
            
            # Convert crawled item to document format
            root_item = crawl_result.root_item
            if not root_item:
                return "❌ No content found from URL"
            
            # Check if parent document already exists
            existing_parent = self.supabase.table("documents").select("id").eq("name", root_item.name).eq("docset_id", docset["id"]).execute()
            
            if existing_parent.data:
                print(f"⚠️ Parent document '{root_item.name}' already exists in docset '{docset_name}'")
                parent_id = existing_parent.data[0]["id"]
            else:
                # Add the main document (parent)
                parent_result = self.add_document_to_docset(
                    docset_name=docset_name,
                    title=root_item.name,
                    content=root_item.content,
                    doc_type=root_item.type.value,
                    metadata=root_item.metadata
                )
                
                if "❌" in parent_result:
                    return parent_result
                
                # Get the parent document ID for child documents
                parent_doc = self.supabase.table("documents").select("id").eq("name", root_item.name).eq("docset_id", docset["id"]).order("added_date", desc=True).limit(1).execute()
                
                if not parent_doc.data:
                    return f"❌ Failed to get parent document ID"
                
                parent_id = parent_doc.data[0]["id"]
            
            # Get the parent document ID for child documents
            parent_doc = self.supabase.table("documents").select("id").eq("name", root_item.name).eq("docset_id", docset["id"]).order("added_date", desc=True).limit(1).execute()
            
            if not parent_doc.data:
                return f"❌ Failed to get parent document ID"
            
            parent_id = parent_doc.data[0]["id"]
            child_count = 0
            
            # Add child documents
            for child in (root_item.children or []):
                try:
                    # Check if child document already exists
                    existing_child = self.supabase.table("documents").select("id").eq("name", child.name).eq("parent_id", parent_id).execute()
                    
                    if existing_child.data:
                        print(f"⚠️ Child document '{child.name}' already exists")
                        continue
                    
                    child_result = self.add_document_to_docset(
                        docset_name=docset_name,
                        title=child.name,
                        content=child.content,
                        doc_type=child.type.value,
                        metadata=child.metadata,
                        parent_id=parent_id
                    )
                    if "✅" in child_result:
                        child_count += 1
                except Exception as e:
                    print(f"❌ Error adding child document {child.name}: {e}")
                    continue
            
            return f"✅ {root_item.type.value.title()} '{root_item.name}' added to docset '{docset_name}' with {child_count} child documents."
                
        except Exception as e:
            print(f"❌ Error adding URL content: {e}")
            return f"❌ Error adding URL content to '{docset_name}': {str(e)}"
    
    def add_github_repo_to_docset(self, repo_url: str, docset_name: str, branch: str = "main") -> str:
        """Add a GitHub repository to a specific docset (backward compatibility)"""
        return self.add_url_to_docset(repo_url, docset_name, branch=branch)
    
    def get_crawler_rate_limit(self, crawler_name: str = None) -> Dict:
        """Get rate limit information for crawlers"""
        if crawler_name:
            crawler = next((c for c in crawler_registry.get_all_crawlers() 
                          if c.__class__.__name__.lower() == crawler_name.lower()), None)
            if crawler:
                return crawler.get_rate_limit_info()
            return {"error": f"Crawler '{crawler_name}' not found"}
        
        # Return rate limit info for all crawlers
        return {
            crawler.__class__.__name__: crawler.get_rate_limit_info()
            for crawler in crawler_registry.get_all_crawlers()
        }
    
    def get_document_with_children(self, docset_name: str, parent_name: str = None) -> Dict:
        """Get documents with their children (for GitHub repositories)"""
        try:
            docset = self.get_docset_by_name(docset_name)
            if not docset:
                return {"error": f"DocSet '{docset_name}' not found"}
            
            # Get parent documents (repositories)
            parent_query = self.supabase.table("documents").select("*").eq("docset_id", docset["id"]).is_("parent_id", "null")
            
            if parent_name:
                parent_query = parent_query.eq("name", parent_name)
            
            parent_docs = parent_query.execute()
            
            result = []
            for parent in parent_docs.data:
                # Get children for this parent
                children = self.supabase.table("documents").select("*").eq("parent_id", parent["id"]).execute()
                
                parent_with_children = {
                    **parent,
                    "children": children.data
                }
                result.append(parent_with_children)
            
            return {"documents": result}
            
        except Exception as e:
            print(f"❌ Error getting documents with children: {e}")
            return {"error": str(e)}
    
    def get_child_documents(self, parent_id: str) -> List[Dict]:
        """Get all child documents for a given parent"""
        try:
            result = self.supabase.table("documents").select("*").eq("parent_id", parent_id).execute()
            return result.data
        except Exception as e:
            print(f"❌ Error getting child documents: {e}")
            return []

# Global instance - removed to avoid initialization on import
# supabase_docset_manager = SupabaseDocsetManager() 