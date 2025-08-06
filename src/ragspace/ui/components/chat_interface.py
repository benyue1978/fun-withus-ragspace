"""
Chat Interface Tab Component
"""

import gradio as gr
from src.ragspace.storage.manager import docset_manager
from src.ragspace.ui.handlers import process_query, clear_chat

def create_chat_interface_tab():
    """Create the chat interface tab"""
    
    with gr.Tab("💬 Chat with Knowledge Base", id=1) as tab:
        with gr.Row():
            # Chat sidebar
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                gr.Markdown("## 💬 Chat Settings")
                
                # DocSet selection for chat
                chat_docset_dropdown = gr.Dropdown(
                    label="🔍 Search in Specific DocSet",
                    choices=[],
                    interactive=True,
                    info="Leave empty to search all docsets"
                )
                
                # Chat history management
                with gr.Group():
                    gr.Markdown("### 📝 Chat History")
                    clear_chat_button = gr.Button("🗑️ Clear Chat")
                    export_chat_button = gr.Button("📤 Export Chat")
                
                # Chat statistics
                with gr.Group():
                    gr.Markdown("### 📊 Statistics")
                    chat_stats = gr.Textbox(
                        label="Session Stats",
                        value="Messages: 0\nQueries: 0\nDocSets Used: 0",
                        interactive=False
                    )
            
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
                
                # Quick actions
                with gr.Row():
                    quick_actions = gr.Dropdown(
                        choices=[
                            "What documents do I have?",
                            "Summarize my knowledge base",
                            "Find similar documents",
                            "What are the main topics?",
                            "Show me the latest additions"
                        ],
                        label="Quick Actions",
                        value=None
                    )
                    quick_action_button = gr.Button("Use Action", variant="secondary")
                
                # Response details
                with gr.Accordion("🔍 Response Details", open=False):
                    response_source = gr.Textbox(
                        label="Sources Used",
                        interactive=False,
                        lines=3
                    )
                    response_confidence = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=0.8,
                        label="Confidence Score",
                        interactive=False
                    )
        
        # Connect chat interactions
        def update_chat_docset_list():
            """Update chat DocSet dropdown"""
            docsets = docset_manager.docsets
            choices = list(docsets.keys()) if docsets else []
            return gr.Dropdown(choices=choices)
        
        def process_chat_query(message, chat_history, docset_name):
            """Process chat query with optional docset filtering"""
            return process_query(message, chat_history, docset_name)
        
        # Connect events
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