"""
RAGSpace - AI Knowledge Hub
Main application entry point
"""

import os
import gradio as gr
from dotenv import load_dotenv
import logging

# Import UI components
from src.ragspace.ui.components import (
    create_knowledge_management_tab,
    create_chat_interface_tab,
    create_mcp_tools_tab
)

# Import MCP tools
from src.ragspace.mcp.tools import expose_mcp_tools

# Import storage management
from src.ragspace.storage import use_supabase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_gradio_interface():
    """Create the main Gradio interface with modern layout"""
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
    }
    .sidebar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        color: white;
    }
    .main-content {
        background: #2d3748;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        color: #e2e8f0;
    }
    .main-content .markdown {
        color: #e2e8f0;
    }
    .main-content .textbox {
        background: #4a5568;
        color: #e2e8f0;
    }
    .main-content .dropdown {
        background: #4a5568;
        color: #e2e8f0;
    }
    .main-content .button {
        background: #667eea;
        color: white;
    }
    .main-content .dataframe {
        background: #4a5568;
        color: #e2e8f0;
    }
    .docset-item {
        background: white;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .docset-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .document-item {
        background: #f1f3f4;
        border-radius: 6px;
        padding: 8px;
        margin: 3px 0;
        font-size: 0.9em;
    }
    """
    
    # Create the interface
    with gr.Blocks(title="RAGSpace - AI Knowledge Hub", theme=gr.themes.Soft(), css=custom_css) as demo:
        gr.Markdown("# 🤖 RAGSpace - AI Knowledge Hub")
        gr.Markdown("Build and query your personal knowledge base with AI assistance.")
        
        with gr.Tabs() as tabs:
            # Create UI components
            create_knowledge_management_tab()
            create_chat_interface_tab()
            create_mcp_tools_tab()
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("""
        ### 🚀 Current Features
        - **Knowledge Management**: Create and manage document collections
        - **File Upload**: Upload documents to your knowledge base
        - **URL Integration**: Add websites and GitHub repositories
        - **AI Chat**: Query your knowledge base with natural language
        - **MCP Integration**: Model Context Protocol support for external tools
        """)

        # MCP Tools - Define functions with api_name to control exposure
        expose_mcp_tools()

    return demo

def main():
    """Main application entry point"""
    try:
        # Switch to Supabase storage for production
        use_supabase()
        
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