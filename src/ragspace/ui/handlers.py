"""
UI Event Handlers for RAGSpace
"""

from ..storage.supabase_manager import supabase_docset_manager

def create_docset_ui(name: str, description: str) -> str:
    """Create a new docset - UI handler"""
    return supabase_docset_manager.create_docset(name, description)

def upload_file_to_docset(files, docset_name: str) -> str:
    """Handle file uploads to specific docset - UI handler"""
    if files is None:
        return "No files uploaded"
    
    if not docset_name.strip():
        return "Please specify a docset name"
    
    file_info = []
    for file in files:
        # For demo purposes, create a simple document from file name
        title = f"Uploaded: {file.name}"
        content = f"File: {file.name}\nSize: {file.size} bytes\nType: {file.type if hasattr(file, 'type') else 'Unknown'}"
        
        result = supabase_docset_manager.add_document_to_docset(docset_name, title, content, "file")
        file_info.append(f"✅ Added: {file.name}")
    
    return "\n".join(file_info)

def add_url_to_docset(url: str, docset_name: str, website_type: str = "docs") -> str:
    """Handle URL input for web scraping to specific docset - UI handler"""
    if not url.strip():
        return "Please enter a valid URL"
    
    if not docset_name.strip():
        return "Please specify a docset name"
    
    # For demo purposes, create a document from URL
    title = f"Website: {url}"
    content = f"URL: {url}\nType: {website_type}\n\nWeb scraping functionality will be implemented in the next phase."
    metadata = {"url": url, "type": website_type}
    
    return supabase_docset_manager.add_document_to_docset(docset_name, title, content, "website", metadata)

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
    
    return supabase_docset_manager.add_document_to_docset(docset_name, title, content, "github", metadata)

def process_query(query: str, history, docset_name: str = None) -> tuple:
    """Process user query and return response - UI handler"""
    if not query.strip():
        return history, ""
    
    # Use the knowledge base query function
    response = supabase_docset_manager.query_knowledge_base(query, docset_name)
    
    # Return the updated history with new messages
    new_history = history + [
        {"role": "user", "content": query},
        {"role": "assistant", "content": response}
    ]
    return new_history, ""

def clear_chat() -> tuple:
    """Clear the chat history - UI handler"""
    return [], "" 