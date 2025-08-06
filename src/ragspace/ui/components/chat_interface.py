"""
Chat Interface UI Component
"""

import gradio as gr

def get_docset_manager():
    """Get the current docset manager"""
    from src.ragspace.storage import docset_manager
    return docset_manager

from src.ragspace.ui.handlers import process_query, clear_chat

def create_chat_interface_tab():
    """Create the chat interface tab"""
    
    with gr.Tab("💬 Chat with Knowledge Base", id=1) as tab:
        with gr.Row():
            # Chat sidebar
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                gr.Markdown("## 💬 Chat Settings")
                
                # DocSet selection for chat
                # Get initial docset list
                initial_docsets = get_docset_manager().get_docsets_dict()
                initial_choices = list(initial_docsets.keys()) if initial_docsets else []
                
                chat_docset_dropdown = gr.Dropdown(
                    label="🔍 Search in Specific DocSet",
                    choices=initial_choices,
                    interactive=True,
                    info="Leave empty to search all docsets"
                )
                
                # Refresh docset list button
                refresh_chat_docsets_button = gr.Button("🔄 Refresh DocSets", variant="secondary", size="sm")
                
                # Chat history management
                with gr.Group():
                    gr.Markdown("### 📝 Chat History")
                    clear_chat_button = gr.Button("🗑️ Clear Chat")
            
            # Main chat area
            with gr.Column(scale=3, elem_classes=["main-content"]):
                gr.Markdown("## 🤖 AI Assistant")
                
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=500,
                    show_label=True,
                    type="messages"
                )
                
                # Input area
                with gr.Row():
                    msg = gr.Textbox(
                        label="Ask a question about your knowledge base",
                        placeholder="How do I implement authentication? What are the best practices for MCP integration?",
                        scale=4,
                        lines=2
                    )
                    send = gr.Button("Send", variant="primary", scale=1)
        
        # Connect chat interactions
        # Auto-update docset dropdown on page load
        def load_chat_docsets():
            """Load docsets into chat dropdown"""
            docsets = get_docset_manager().get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            return gr.Dropdown(choices=choices)
        
        def process_chat_query(message, chat_history, docset_name):
            """Process chat query with optional docset filtering"""
            return process_query(message, chat_history, docset_name)
        
        # Refresh docset list button
        refresh_chat_docsets_button.click(
            load_chat_docsets,
            outputs=[chat_docset_dropdown],
            api_name=False
        )
        
        send.click(
            process_chat_query, 
            [msg, chatbot, chat_docset_dropdown], 
            [chatbot, msg],
            api_name=False
        )
        
        msg.submit(
            process_chat_query, 
            [msg, chatbot, chat_docset_dropdown], 
            [chatbot, msg],
            api_name=False
        )
        
        clear_chat_button.click(
            clear_chat, 
            outputs=[chatbot, msg],
            api_name=False
        )
    
    return tab 