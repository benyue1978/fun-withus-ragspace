"""
UI Event Handlers for RAGSpace
"""

import asyncio
import logging
import gradio as gr
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
        
        # Return the updated history with new messages in dictionary format for Gradio Chatbot
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

def process_rag_query_sync(query: str, docset_name: str = None) -> List[Dict[str, str]]:
    """Synchronous version of RAG query processing for MCP tools"""
    try:
        rag_manager = get_rag_manager()
        # Convert single docset_name to list format for RAG manager
        docsets = [docset_name] if docset_name else None
        response_chunks = []
        
        async def get_response():
            async for chunk in rag_manager.query_knowledge_base(query, docsets):
                response_chunks.append(chunk)
        
        asyncio.run(get_response())
        response = "".join(response_chunks)
        
        return [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ]
    except Exception as e:
        return [
            {"role": "user", "content": query},
            {"role": "assistant", "content": f"❌ Error processing query: {str(e)}"}
        ]

def process_query(query: str, history, docset_name: str = None) -> tuple:
    """Process user query - UI handler"""
    if not query.strip():
        return history, ""
    
    try:
        # Use the synchronous version for UI
        new_messages = process_rag_query_sync(query, docset_name)
        # Convert to dictionary format for Gradio Chatbot with type="messages"
        if isinstance(new_messages, list) and len(new_messages) >= 2:
            new_history = history + new_messages
        else:
            new_history = history + [
                {"role": "user", "content": query},
                {"role": "assistant", "content": str(new_messages)}
            ]
        return new_history, ""
    except Exception as e:
        error_response = f"❌ Error processing query: {str(e)}"
        new_history = history + [
            {"role": "user", "content": query},
            {"role": "assistant", "content": error_response}
        ]
        return new_history, ""

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

def create_docset(name: str) -> tuple:
    """Create a new docset - UI handler"""
    if not name.strip():
        return "❌ Please enter a docset name", None
    
    try:
        docset_manager = get_docset_manager()
        result = docset_manager.create_docset(name, f"DocSet: {name}")
        
        if "✅" in result:
            # Update docset list
            docsets = docset_manager.get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            return result, gr.Dropdown(choices=choices, value=name)
        else:
            return result, None
    except Exception as e:
        return f"❌ Error creating docset: {str(e)}", None

def update_documents(docset_name: str) -> gr.Dataframe:
    """Update documents list when DocSet is selected"""
    if not docset_name:
        return gr.Dataframe(value=[])
    
    try:
        docset_manager = get_docset_manager()
        documents = docset_manager.list_documents_in_docset(docset_name)
        
        if not isinstance(documents, list):
            return gr.Dataframe(value=[])
        
        doc_rows = convert_documents_to_dataframe(documents)
        return gr.Dataframe(value=doc_rows)
    except Exception as e:
        print(f"Error updating documents: {e}")
        return gr.Dataframe(value=[])

def update_docset_info(docset_name: str) -> str:
    """Update DocSet info when a docset is selected"""
    if not docset_name:
        return "Select a DocSet to view details"
    
    try:
        docset, documents, error = get_docset_data(docset_name)
        
        if error:
            return f"Error loading docset info: {error}"
        
        if not docset:
            return f"DocSet '{docset_name}' not found"
        
        if not isinstance(documents, list):
            return "Error: Invalid document data format"
        
        info_text = create_docset_info_text(docset, documents, docset_name)
        return info_text
    except Exception as e:
        return f"Error updating docset info: {str(e)}"

def trigger_embedding_for_docset(docset_name: str) -> str:
    """Trigger embedding process for the selected docset"""
    if not docset_name:
        return "❌ Please select a DocSet first"
    
    try:
        rag_manager = get_rag_manager()
        
        async def trigger_embedding():
            return await rag_manager.trigger_embedding_for_docset(docset_name)
        
        result = asyncio.run(trigger_embedding())
        
        if result.get("status") == "success":
            return "🧠 Trigger Embedding"
        else:
            return f"❌ Failed to trigger embedding: {result.get('message', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error triggering embedding: {str(e)}"

def upload_files(files, docset_name: str) -> tuple:
    """Handle file uploads to specific docset - UI handler"""
    if files is None:
        return "No files uploaded", None
    
    if not docset_name.strip():
        return "Please specify a docset name", None
    
    file_info = []
    for file in files:
        # Extract original filename from the full path
        import os
        if hasattr(file, 'name'):
            if isinstance(file.name, str):
                original_filename = os.path.basename(file.name)
            else:
                original_filename = str(file.name) if hasattr(file.name, '__str__') else "Unknown file"
        else:
            original_filename = "Unknown file"
        
        title = f"Uploaded: {original_filename}"
        
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
        
        if "✅" in result:
            file_info.append(f"✅ Added: {original_filename}")
        else:
            file_info.append(f"❌ Failed: {original_filename} - {result}")
    
    return "\n".join(file_info), gr.Textbox(value=docset_name)

def update_target_docsets(docset_name: str) -> gr.Textbox:
    """Update target docset dropdowns"""
    if not docset_name:
        return gr.Textbox(value="")
    return gr.Textbox(value=docset_name)



def clear_chat_history() -> gr.Chatbot:
    """Clear chat history"""
    return gr.Chatbot(value=[])

def update_docset_lists() -> gr.Dropdown:
    """Update DocSet dropdown with current list"""
    docset_manager = get_docset_manager()
    docsets = docset_manager.get_docsets_dict()
    choices = list(docsets.keys()) if docsets else []
    return gr.Dropdown(choices=choices)

def test_list_docsets_tool() -> str:
    """Test list_docsets MCP tool"""
    try:
        result = list_documents()
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def test_ask_tool(query: str, docset: str) -> str:
    """Test ask MCP tool"""
    try:
        result = process_rag_query_sync(query, docset if docset else None)
        # Extract the assistant's response from the result
        if isinstance(result, list) and len(result) >= 2:
            # Return only the assistant's response content
            return result[1].get("content", "No response generated")
        else:
            return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def update_mcp_docset_list() -> gr.Dropdown:
    """Update MCP test DocSet dropdown"""
    docset_manager = get_docset_manager()
    docsets = docset_manager.get_docsets_dict()
    choices = list(docsets.keys()) if docsets else []
    return gr.Dropdown(choices=choices)

def get_docset_data(docset_name: str) -> tuple:
    """Get docset and documents data"""
    try:
        docset_manager = get_docset_manager()
        docset = docset_manager.get_docset_by_name(docset_name)
        documents = docset_manager.list_documents_in_docset(docset_name) if docset_name else []
        return docset, documents, None
    except Exception as e:
        return None, [], str(e)

def convert_documents_to_dataframe(documents: List[Dict]) -> List[List[str]]:
    """Convert documents to dataframe format"""
    doc_rows = []
    for doc in documents:
        if not isinstance(doc, dict):
            print(f"Warning: Skipping non-dict document: {type(doc)}")
            continue
            
        doc_rows.append([
            doc.get('name', 'Unknown'),
            doc.get('type', 'unknown'),
            doc.get('url', 'N/A'),
            doc.get('added_date', 'Unknown'),
            doc.get('embedding_status', 'pending')
        ])
    return doc_rows

def create_docset_info_text(docset: Dict, documents: List[Dict], docset_name: str) -> str:
    """Create detailed docset info text with RAG status"""
    info_lines = [
        f"📁 DocSet: {docset_name}",
        f"📝 Description: {docset.get('description', 'No description')}",
        f"📅 Created: {docset.get('created_at', 'Unknown')}",
        f"📄 Documents: {len(documents)}",
        "",
        "📋 Document Types:"
    ]
    
    # Count document types
    type_counts = {}
    embedding_status_counts = {"pending": 0, "processing": 0, "done": 0, "error": 0}
    
    for doc in documents:
        doc_type = doc.get('type', 'unknown')
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        # Count embedding status
        embedding_status = doc.get('embedding_status', 'pending')
        embedding_status_counts[embedding_status] = embedding_status_counts.get(embedding_status, 0) + 1
    
    for doc_type, count in type_counts.items():
        info_lines.append(f"  • {doc_type}: {count}")
    
    if not documents:
        info_lines.append("  • No documents yet")
    
    # Add RAG status information
    info_lines.extend([
        "",
        "🧠 RAG Status:",
        f"  • ✅ Embedded: {embedding_status_counts.get('done', 0)}",
        f"  • ⏳ Processing: {embedding_status_counts.get('processing', 0)}",
        f"  • 🟡 Pending: {embedding_status_counts.get('pending', 0)}",
        f"  • ❌ Error: {embedding_status_counts.get('error', 0)}"
    ])
    
    return "\n".join(info_lines) 