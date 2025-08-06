"""
UI Event Handlers for RAGSpace
"""

def get_docset_manager():
    """Get the current docset manager"""
    from ..storage import docset_manager
    return docset_manager

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

def add_github_repo_to_docset(repo_url: str, docset_name: str) -> str:
    """Handle GitHub repository input to specific docset - UI handler"""
    if not repo_url.strip():
        return "Please enter a valid GitHub repository URL"
    
    if not docset_name.strip():
        return "Please specify a docset name"
    
    # For demo purposes, create a document from repo URL
    title = f"GitHub Repository: {repo_url}"
    content = f"Repository: {repo_url}\n\nRepository crawling functionality will be implemented in the next phase."
    metadata = {"url": repo_url, "type": "github"}
    
    docset_manager = get_docset_manager()
    return docset_manager.add_document_to_docset(docset_name, title, content, "github", metadata)

def process_query(query: str, history, docset_name: str = None) -> tuple:
    """Process user query and return response - UI handler"""
    if not query.strip():
        return history, ""
    
    # Get the current docset manager
    docset_manager = get_docset_manager()
    # Use the knowledge base query function
    response = docset_manager.query_knowledge_base(query, docset_name)
    
    # Return the updated history with new messages
    new_history = history + [
        {"role": "user", "content": query},
        {"role": "assistant", "content": response}
    ]
    return new_history, ""

def clear_chat() -> tuple:
    """Clear the chat history - UI handler"""
    return [], "" 