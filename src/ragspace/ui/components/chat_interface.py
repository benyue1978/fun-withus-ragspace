"""
Chat Interface Component - Improved Architecture
Using component-based architecture with better separation of concerns
"""

import gradio as gr
from typing import List, Dict, Any, Optional
from .base_component import BaseComponent, ComponentState


class ChatInterfaceComponent(BaseComponent):
    """Chat Interface Component with improved architecture"""
    
    def __init__(self):
        super().__init__("chat_interface")
        self.docset_manager = self._get_docset_manager()
    
    def _get_docset_manager(self):
        """Get docset manager - separated for better testing"""
        from src.ragspace.storage import docset_manager
        return docset_manager
    
    def create_ui(self):
        """Create the UI - clean separation of UI creation"""
        # Initialize data
        initial_data = self._get_initial_data()
        
        # Create layout
        with gr.Row():
            # Left sidebar - DocSet selection
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                self._create_sidebar_section(initial_data)
            
            # Right main content - Chat area
            with gr.Column(scale=3, elem_classes=["main-content"]):
                self._create_chat_section(initial_data)
    
    def _get_initial_data(self) -> Dict[str, Any]:
        """Get initial data - separated for better testing"""
        try:
            docsets = self.docset_manager.get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            selected = choices[0] if choices else None
            
            return {
                "choices": choices,
                "selected": selected
            }
        except Exception as e:
            print(f"Error getting initial data: {e}")
            return {"choices": [], "selected": None}
    
    def _create_sidebar_section(self, initial_data: Dict[str, Any]):
        """Create sidebar section"""
        gr.Markdown("## 🎯 Chat Settings", elem_classes=["markdown-enhanced"])
        
        with gr.Group(elem_classes=["card"]):
            gr.Markdown("### 📚 DocSet Selection")
            
            # Refresh docset list button
            refresh_chat_docsets_button = gr.Button(
                "🔄 Refresh DocSets", 
                variant="primary", 
                size="lg",
                elem_classes=["button-primary"]
            )
            
            # DocSet dropdown
            chat_docset_dropdown = gr.Dropdown(
                choices=initial_data["choices"],
                value=initial_data["selected"],
                label="📚 Select DocSet for Chat",
                interactive=True,
                elem_classes=["input-modern"]
            )
            
            # Clear chat button
            clear_chat_button = gr.Button(
                "🗑️ Clear Chat",
                variant="primary",
                size="lg",
                elem_classes=["button-primary"]
            )
        
        # Register components
        self.add_component("refresh_chat_docsets_button", refresh_chat_docsets_button)
        self.add_component("chat_docset_dropdown", chat_docset_dropdown)
        self.add_component("clear_chat_button", clear_chat_button)
    
    def _create_chat_section(self, initial_data: Dict[str, Any]):
        """Create chat section"""
        gr.Markdown("## 💬 Chat with RAG", elem_classes=["markdown-enhanced"])
        
        with gr.Group(elem_classes=["card"]):
            gr.Markdown("### 🤖 AI Assistant")
            
            # Chat history
            chat_history = gr.Chatbot(
                label="💬 Chat History",
                height=400,
                elem_classes=["chat-modern"],
                type="messages"
            )
            
            # Query input
            query_input = gr.Textbox(
                type="text",
                lines=2,
                placeholder="Ask a question about your documents...",
                label="📝 Your Question",
                elem_classes=["input-modern"]
            )
            
            # Query button
            query_button = gr.Button(
                "Ask Question",
                variant="primary",
                size="lg",
                elem_classes=["button-primary"]
            )
        
        # Register components
        self.add_component("chat_history", chat_history)
        self.add_component("query_input", query_input)
        self.add_component("query_button", query_button)
    
    def setup_events(self):
        """Setup event handlers - clean separation of event binding"""
        # Get components
        refresh_button = self.get_component("refresh_chat_docsets_button")
        docset_dropdown = self.get_component("chat_docset_dropdown")
        clear_button = self.get_component("clear_chat_button")
        chat_history = self.get_component("chat_history")
        query_input = self.get_component("query_input")
        query_button = self.get_component("query_button")
        
        # Setup event handlers
        self._setup_refresh_events(refresh_button, docset_dropdown)
        self._setup_chat_events(clear_button, chat_history, query_input, query_button, docset_dropdown)
    
    def _setup_refresh_events(self, refresh_button, docset_dropdown):
        """Setup refresh related events"""
        from src.ragspace.ui.handlers import update_docset_lists
        
        refresh_button.click(
            update_docset_lists,
            outputs=[docset_dropdown],
            api_name=False
        )
    
    def _setup_chat_events(self, clear_button, chat_history, query_input, query_button, docset_dropdown):
        """Setup chat related events"""
        from src.ragspace.ui.handlers import process_rag_query, clear_chat_history
        
        # Clear chat
        clear_button.click(
            clear_chat_history,
            outputs=[chat_history],
            api_name=False
        )
        
        # Process query
        query_button.click(
            process_rag_query,
            [query_input, chat_history, docset_dropdown],
            [chat_history, query_input],
            api_name=False
        )
        
        # Enter key support
        query_input.submit(
            process_rag_query,
            [query_input, chat_history, docset_dropdown],
            [chat_history, query_input],
            api_name=False
        )


def create_chat_interface_tab():
    """Create the chat interface tab using the improved component"""
    component = ChatInterfaceComponent()
    component.create_ui()
    component.setup_events() 