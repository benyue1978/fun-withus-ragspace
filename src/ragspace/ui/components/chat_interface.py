"""
Chat Interface UI Component
"""

import gradio as gr
import asyncio

def get_docset_manager():
    """Get the current docset manager"""
    from src.ragspace.storage import docset_manager
    return docset_manager

from src.ragspace.ui.handlers import (
    process_query, 
    clear_chat, 
    trigger_embedding_process,
    get_embedding_status,
    get_rag_metadata
)

def create_chat_interface_tab():
    """Create the chat interface tab"""
    with gr.Tab("💬 Chat with Knowledge Base", id="chat_tab") as tab:
        with gr.Row():
            # Left sidebar - Chat settings
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                gr.Markdown("## 💬 Chat Settings", elem_classes=["markdown-enhanced"])
                
                # DocSet selection for targeted queries
                initial_choices = []
                try:
                    docsets = get_docset_manager().get_docsets_dict()
                    initial_choices = list(docsets.keys()) if docsets else []
                except Exception as e:
                    print(f"Error loading docsets: {e}")
                
                chat_docset_dropdown = gr.Dropdown(
                    label="🔍 Search in Specific DocSet",
                    choices=initial_choices,
                    interactive=True
                )
                
                # Refresh docset list button
                refresh_chat_docsets_button = gr.Button(
                    "🔄 Refresh DocSets", 
                    variant="primary", 
                    size="lg",
                    elem_classes=["button-primary"]
                )
                
                clear_chat_button = gr.Button(
                    "🗑️ Clear Chat",
                    variant="primary",
                    size="lg",
                    elem_classes=["button-primary"]
                )
            
            # Main chat area
            with gr.Column(scale=3, elem_classes=["main-content"]):
                gr.Markdown("## 🤖 AI Assistant")
                
                # Chat history with modern styling
                chat_history = gr.Chatbot(
                    value=[],
                    height=400,
                    label="💬 Chat History",
                    elem_classes=["chat-modern"],
                    type="messages"
                )
                
                # Query input with modern styling
                query_input = gr.Textbox(
                    type="text",
                    lines=2,
                    placeholder="Ask a question about your documents...",
                    label="💬 Your Question",
                    elem_classes=["input-modern"]
                )
                
                # Query button with modern styling
                query_button = gr.Button(
                    "Ask Question",
                    variant="primary",
                    size="lg",
                    elem_classes=["button-primary"]
                )
        
        # Connect chat interactions
        # Auto-update docset dropdown on page load
        def load_chat_docsets():
            """Load docsets into chat dropdown"""
            docsets = get_docset_manager().get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            return gr.Dropdown(choices=choices)
        
        def process_chat_query(message, chat_history, docset_name):
            """Process chat query"""
            if not message.strip():
                return chat_history, ""
            
            try:
                # Process the query
                new_history, _ = process_query(message, chat_history, docset_name)
                return new_history, ""
                
            except Exception as e:
                error_response = f"❌ Error processing query: {str(e)}"
                new_history = chat_history + [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": error_response}
                ]
                return new_history, ""
        
        # Refresh docset list button
        refresh_chat_docsets_button.click(
            load_chat_docsets,
            outputs=[chat_docset_dropdown],
            api_name=False
        )
        
        # Query button
        query_button.click(
            process_chat_query, 
            [query_input, chat_history, chat_docset_dropdown], 
            [chat_history, query_input],
            api_name=False
        )
        
        # Enter key submission
        query_input.submit(
            process_chat_query, 
            [query_input, chat_history, chat_docset_dropdown], 
            [chat_history, query_input],
            api_name=False
        )
        
        # Clear chat button
        clear_chat_button.click(
            clear_chat, 
            outputs=[chat_history, query_input],
            api_name=False
        )
    
    return tab 