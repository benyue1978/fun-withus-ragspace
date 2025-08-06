"""
Supabase DocSet Manager for RAGSpace
"""

import os
import time
from typing import Dict, Optional, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseDocsetManager:
    """Manages DocSets and their operations using Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
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
                              doc_type: str = "file", metadata: Optional[Dict] = None) -> str:
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
                "url": metadata.get("url") if metadata else None
            }
            
            # Insert document
            result = self.supabase.table("documents").insert(doc_data).execute()
            
            print(f"✅ Added document '{title}' to docset '{docset_name}'")
            return f"✅ Document '{title}' added to docset '{docset_name}'."
            
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return f"❌ Error adding document to '{docset_name}': {str(e)}"
    
    def list_documents_in_docset(self, docset_name: str) -> str:
        """List all documents in a specific docset"""
        try:
            # Get docset by name
            docset = self.get_docset_by_name(docset_name)
            if not docset:
                return f"DocSet '{docset_name}' not found."
            
            # Get documents for this docset
            result = self.supabase.table("documents").select("*").eq("docset_id", docset["id"]).order("added_date", desc=True).execute()
            
            if not result.data:
                return f"DocSet '{docset_name}' is empty."
            
            response = f"📚 Documents in DocSet '{docset_name}':\n\n"
            for i, doc in enumerate(result.data, 1):
                response += f"{i}. {doc['name']}\n"
                response += f"   Type: {doc['type']}\n"
                if doc.get('url'):
                    response += f"   URL: {doc['url']}\n"
                response += f"   ID: {doc['id']}\n"
                response += f"   Added: {doc['added_date']}\n\n"
            
            print(f"✅ Listed {len(result.data)} documents in docset '{docset_name}'")
            return response
            
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            return f"❌ Error listing documents in '{docset_name}': {str(e)}"
    
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

# Global instance
supabase_docset_manager = SupabaseDocsetManager() 