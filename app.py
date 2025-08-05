import os
import gradio as gr
from dotenv import load_dotenv
import logging
import json
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for demo purposes
knowledge_base = []
conversations = []

def query_knowledge_base(query: str) -> str:
    """Query the knowledge base"""
    if not knowledge_base:
        return "Knowledge base is empty. Please add some documents first. (Auto-reload test!)"
    
    # Simple search for demo purposes
    results = []
    for doc in knowledge_base:
        if query.lower() in doc.get('content', '').lower():
            results.append(doc)
    
    if results:
        return f"Found {len(results)} relevant documents:\n\n" + "\n\n".join([
            f"📄 {doc.get('title', 'Untitled')}\n{doc.get('content', '')[:200]}..."
            for doc in results[:3]
        ])
    else:
        return f"No documents found matching '{query}'. Try adding more documents to the knowledge base."

def add_document(title: str, content: str) -> str:
    """Add a document to the knowledge base"""
    doc = {
        'title': title,
        'content': content,
        'id': len(knowledge_base) + 1
    }
    knowledge_base.append(doc)
    return f"✅ Document '{title}' added to knowledge base. Total documents: {len(knowledge_base)}"

def list_documents() -> str:
    """List all documents in the knowledge base"""
    if not knowledge_base:
        return "Knowledge base is empty. (Auto-reload test 3!)"
    
    return "📚 Documents in knowledge base:\n\n" + "\n".join([
        f"{i+1}. {doc.get('title', 'Untitled')} (ID: {doc.get('id')})"
        for i, doc in enumerate(knowledge_base)
    ])

def create_gradio_interface():
    """Create the main Gradio interface"""
    
    def process_query(query, history):
        """Process user query and return response"""
        if not query.strip():
            return history, ""
        
        # Use the knowledge base query function
        response = query_knowledge_base(query)
        
        # Return the updated history with new messages
        # For messages format, we need to append new messages to the history
        new_history = history + [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ]
        return new_history, ""
    
    def upload_file(files):
        """Handle file uploads"""
        if files is None:
            return "No files uploaded"
        
        file_info = []
        for file in files:
            # For demo purposes, create a simple document from file name
            title = f"Uploaded: {file.name}"
            content = f"File: {file.name}\nSize: {file.size} bytes\nType: {file.type if hasattr(file, 'type') else 'Unknown'}"
            
            add_document(title, content)
            file_info.append(f"✅ Added: {file.name}")
        
        return "\n".join(file_info)
    
    def add_url(url):
        """Handle URL input for web scraping"""
        if not url.strip():
            return "Please enter a valid URL"
        
        # For demo purposes, create a document from URL
        title = f"Website: {url}"
        content = f"URL: {url}\n\nWeb scraping functionality will be implemented in the next phase."
        
        add_document(title, content)
        return f"✅ Added website: {url}"
    
    def add_github_repo(repo_url):
        """Handle GitHub repository input"""
        if not repo_url.strip():
            return "Please enter a valid GitHub repository URL"
        
        # For demo purposes, create a document from repo URL
        title = f"GitHub Repository: {repo_url}"
        content = f"Repository: {repo_url}\n\nRepository crawling functionality will be implemented in the next phase."
        
        add_document(title, content)
        return f"✅ Added repository: {repo_url}"
    
    def clear_chat():
        """Clear the chat history"""
        return [], ""
    
    # Create the interface
    with gr.Blocks(title="RAGSpace - AI Knowledge Hub", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🤖 RAGSpace - AI Knowledge Hub")
        gr.Markdown("Build and query your personal knowledge base with AI assistance.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 📚 Knowledge Base")
                
                # File upload section
                gr.Markdown("### Upload Files")
                file_output = gr.Textbox(label="Upload Status", interactive=False)
                file_input = gr.File(
                    label="Upload Documents",
                    file_types=[".txt", ".md", ".pdf", ".docx"],
                    file_count="multiple"
                )
                file_input.upload(upload_file, file_input, file_output)
                               
                # GitHub repository section
                gr.Markdown("### Add GitHub Repository")
                github_output = gr.Textbox(label="Repository Status", interactive=False)
                github_input = gr.Textbox(label="GitHub Repository", placeholder="owner/repository")
                github_button = gr.Button("Add Repository")
                github_button.click(add_github_repo, github_input, github_output)
                
                # URL input section
                gr.Markdown("### Add Website")
                url_output = gr.Textbox(label="URL Status", interactive=False)
                url_input = gr.Textbox(label="Website URL", placeholder="https://example.com/docs")
                url_button = gr.Button("Add Website")
                url_button.click(add_url, url_input, url_output)
 
                # Knowledge base status
                gr.Markdown("### Knowledge Base Status")
                status_text = gr.Textbox(
                    value="No documents added yet. Upload files or add URLs to get started.",
                    label="Status",
                    interactive=False
                )
                
                # List documents button
                list_button = gr.Button("List Documents")
                list_output = gr.Textbox(label="Documents", interactive=False)
                list_button.click(list_documents, outputs=list_output)
            
            with gr.Column(scale=2):
                gr.Markdown("## 💬 Chat with Your Knowledge Base")
                
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=400,
                    show_label=True,
                    type="messages"  # Use messages format to avoid deprecation warning
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Ask a question about your knowledge base",
                        placeholder="How do I implement authentication?",
                        scale=4
                    )
                    send = gr.Button("Send", scale=1)
                
                # Clear chat button
                clear = gr.Button("Clear Chat")
                
                # Connect chat components
                send.click(process_query, [msg, chatbot], [chatbot, msg])
                msg.submit(process_query, [msg, chatbot], [chatbot, msg])
                clear.click(clear_chat, outputs=[chatbot, msg])
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("""
        ### 🚀 Features Coming Soon
        - **RAG Pipeline**: Intelligent document processing and retrieval
        - **Vector Search**: Semantic search across your knowledge base
        - **MCP Integration**: Connect with Cursor, Claude Desktop, and other LLM clients
        - **Multi-user Support**: Team collaboration and sharing
        - **Advanced Analytics**: Usage insights and performance metrics
        """)
    
    return demo

def main():
    """Main application entry point"""
    try:
        # Check if we're in development mode
        is_dev = os.getenv("DEV_MODE", "false").lower() == "true"
        
        if is_dev:
            print("🚀 Starting in development mode with auto-reload...")
            print("📝 Any changes to .py files will automatically restart the server")
            print("🌐 Server will be available at: http://localhost:8000")
            print("🔧 MCP Server will be available at: http://localhost:8000/gradio_api/mcp/")
            print("⏹️  Press Ctrl+C to stop the server")
            print("-" * 60)
        
        # Create Gradio interface
        demo = create_gradio_interface()
        
        # Launch with MCP server enabled
        demo.launch(
            server_name="0.0.0.0",
            server_port=int(os.getenv("PORT", 8000)),
            mcp_server=True,  # Enable MCP server
            share=False,  # Disable public sharing for production
            debug=is_dev  # Enable debug mode for development
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == "__main__":
    main() 