"""
UI Event Handlers for RAGSpace
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, AsyncGenerator

def get_docset_manager():
    """Get the current docset manager"""
    from ..storage import docset_manager
    return docset_manager

def get_rag_manager():
    """Get the RAG manager"""
    from ..services.rag import RAGManager
    return RAGManager()

def create_docset_ui(name: str, description: str) -> str:
    """Create a new docset - UI handler"""
    docset_manager = get_docset_manager()
    return docset_manager.create_docset(name, description)

def upload_file_to_docset(files, docset_name: str) -> str:
    """Handle file uploads to specific docset - UI handler"""
    if files is None:
        return "No files uploaded"
    
    if not docset_name.strip():
        return "Please specify a docset name"
    
    file_info = []
    for file in files:
        # Extract original filename from the full path
        import os
        if hasattr(file, 'name'):
            # Handle both string and Mock objects
            if isinstance(file.name, str):
                original_filename = os.path.basename(file.name)
            else:
                # For Mock objects, try to get the name from the mock
                original_filename = str(file.name) if hasattr(file.name, '__str__') else "Unknown file"
        else:
            original_filename = "Unknown file"
        
        # For demo purposes, create a simple document from file name
        title = f"Uploaded: {original_filename}"
        
        # Handle different file object types
        try:
            if hasattr(file, 'size'):
                file_size = f"{file.size} bytes"
            elif hasattr(file, 'name'):
                file_size = "Unknown size"
            else:
                file_size = "Unknown size"
            
            if hasattr(file, 'type'):
                file_type = file.type
            else:
                file_type = "Unknown"
            
            content = f"File: {original_filename}\nSize: {file_size}\nType: {file_type}"
        except Exception as e:
            content = f"File: {original_filename}\nError reading file info: {str(e)}"
        
        docset_manager = get_docset_manager()
        result = docset_manager.add_document_to_docset(docset_name, title, content, "file")
        
        # Check if the operation was successful
        if "✅" in result:
            file_info.append(f"✅ Added: {original_filename}")
        else:
            file_info.append(f"❌ Failed: {original_filename} - {result}")
    
    return "\n".join(file_info)

def add_url_to_docset(url: str, docset_name: str, website_type: str = "website") -> str:
    """Handle URL input for web scraping to specific docset - UI handler"""
    if not url.strip():
        return "Please enter a valid URL"
    
    if not docset_name.strip():
        return "Please specify a docset name"
    
    # For demo purposes, create a document from URL
    title = f"Website: {url}"
    content = f"URL: {url}\nType: {website_type}\n\nWeb scraping functionality will be implemented in the next phase."
    metadata = {"url": url, "type": website_type}
    
    # Use "url" as the document type for all website documents
    docset_manager = get_docset_manager()
    return docset_manager.add_document_to_docset(docset_name, title, content, "url", metadata)

def add_github_repo_to_docset(repo_url: str, docset_name: str, branch: str = "main") -> str:
    """Handle GitHub repository input to specific docset - UI handler"""
    if not repo_url.strip():
        return "Please enter a valid GitHub repository URL"
    
    if not docset_name.strip():
        return "Please specify a docset name"
    
    # Use the new GitHub service to fetch repository content
    docset_manager = get_docset_manager()
    return docset_manager.add_github_repo_to_docset(repo_url, docset_name, branch)

# RAG Business Logic Functions
async def process_rag_query(query: str, history, docset_name: str = None) -> tuple:
    """Process user query using RAG and return response - UI handler"""
    if not query.strip():
        return history, ""
    
    try:
        # Get the RAG manager
        rag_manager = get_rag_manager()
        
        # Convert single docset_name to list format for RAG manager
        docsets = [docset_name] if docset_name else None
        
        # Process query with RAG - handle async generator
        response_chunks = []
        async for chunk in rag_manager.query_knowledge_base(query, docsets):
            response_chunks.append(chunk)
        
        # Combine all chunks into a single response
        response = "".join(response_chunks)
        
        # Return the updated history with new messages
        new_history = history + [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ]
        return new_history, ""
        
    except Exception as e:
        error_response = f"❌ Error processing query: {str(e)}"
        new_history = history + [
            {"role": "user", "content": query},
            {"role": "assistant", "content": error_response}
        ]
        return new_history, ""

def process_rag_query_sync(query: str, docset_name: str = None) -> str:
    """Synchronous version of RAG query processing for MCP tools"""
    try:
        # Get the RAG manager
        rag_manager = get_rag_manager()
        
        # Convert single docset_name to list format for RAG manager
        docsets = [docset_name] if docset_name else None
        
        # Process query with RAG synchronously - handle async generator
        response_chunks = []
        async def get_response():
            async for chunk in rag_manager.query_knowledge_base(query, docsets):
                response_chunks.append(chunk)
        
        asyncio.run(get_response())
        response = "".join(response_chunks)
        return response
        
    except Exception as e:
        return f"❌ Error processing query: {str(e)}"

def process_query(query: str, history, docset_name: str = None) -> tuple:
    """Process user query and return response - UI handler (legacy function for compatibility)"""
    if not query.strip():
        return history, ""
    
    # Use the new RAG-based query processing
    return asyncio.run(process_rag_query(query, history, docset_name))

def clear_chat() -> tuple:
    """Clear the chat history - UI handler"""
    return [], ""

async def trigger_embedding_process(docset_name: str = None) -> str:
    """Trigger embedding process for documents - UI handler"""
    try:
        rag_manager = get_rag_manager()
        result = await rag_manager.process_document_embeddings(docset_name)
        
        if result.get("status") == "success":
            return f"✅ Embedding process completed successfully"
        else:
            return f"❌ Embedding process failed: {result.get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error triggering embedding process: {str(e)}"

def trigger_embedding_process_sync(docset_name: str = None) -> str:
    """Synchronous version of embedding trigger for MCP tools"""
    try:
        rag_manager = get_rag_manager()
        result = asyncio.run(rag_manager.process_document_embeddings(docset_name))
        
        if result.get("status") == "success":
            return f"✅ Embedding process completed successfully"
        else:
            return f"❌ Embedding process failed: {result.get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"❌ Error triggering embedding process: {str(e)}"

def get_embedding_status(docset_name: str = None) -> str:
    """Get embedding status for documents - UI handler"""
    try:
        docset_manager = get_docset_manager()
        
        if docset_name:
            documents = docset_manager.list_documents_in_docset(docset_name)
        else:
            # Get all documents from all docsets
            docsets = docset_manager.get_docsets_dict()
            documents = []
            for ds_name in docsets.keys():
                docs = docset_manager.list_documents_in_docset(ds_name)
                documents.extend(docs)
        
        # Format status information
        status_info = []
        status_counts = {"pending": 0, "processing": 0, "done": 0, "error": 0}
        
        for doc in documents:
            if isinstance(doc, dict):
                status = doc.get('embedding_status', 'pending')
                status_counts[status] = status_counts.get(status, 0) + 1
                status_info.append(f"- {doc.get('name', 'Unknown')}: {status}")
        
        result = f"Embedding Status Summary:\n"
        result += f"✅ Done: {status_counts.get('done', 0)}\n"
        result += f"⏳ Processing: {status_counts.get('processing', 0)}\n"
        result += f"🟡 Pending: {status_counts.get('pending', 0)}\n"
        result += f"❌ Error: {status_counts.get('error', 0)}\n\n"
        result += "Detailed Status:\n" + "\n".join(status_info)
        
        return result
        
    except Exception as e:
        return f"Error getting embedding status: {str(e)}"

def list_documents(docset_name: str = None) -> str:
    """List documents in a docset or all documents - UI handler"""
    try:
        docset_manager = get_docset_manager()
        
        if docset_name:
            documents = docset_manager.list_documents_in_docset(docset_name)
            result = f"Documents in '{docset_name}':\n"
        else:
            # Get all documents from all docsets
            docsets = docset_manager.get_docsets_dict()
            documents = []
            for ds_name in docsets.keys():
                docs = docset_manager.list_documents_in_docset(ds_name)
                documents.extend(docs)
            result = "All Documents:\n"
        
        for doc in documents:
            if isinstance(doc, dict):
                name = doc.get('name', 'Unknown')
                doc_type = doc.get('type', 'unknown')
                status = doc.get('embedding_status', 'pending')
                result += f"- {name} ({doc_type}) - {status}\n"
        
        return result
        
    except Exception as e:
        return f"Error listing documents: {str(e)}"

def get_rag_metadata(query: str, docset_name: str = None) -> Dict[str, Any]:
    """Get RAG metadata for a query - UI handler"""
    try:
        rag_manager = get_rag_manager()
        result = asyncio.run(rag_manager.query_with_metadata(query, [docset_name] if docset_name else None))
        return result
    except Exception as e:
        return {
            "status": "error",
            "query": query,
            "error": str(e),
            "response": "",
            "sources": [],
            "metadata": {}
        } 