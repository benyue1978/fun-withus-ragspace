"""
MCP Tools UI Component - UI Display Only
"""

import gradio as gr

def get_docset_manager():
    """Get the current docset manager"""
    from src.ragspace.storage import docset_manager
    return docset_manager

def create_mcp_tools_tab():
    """Create the MCP tools tab - UI display only"""
    
    with gr.Tab("🔧 MCP Tools", id=2) as tab:
        with gr.Row():
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                gr.Markdown("## 🔧 MCP Server")
                
                # MCP Server status
                mcp_status = gr.Textbox(
                    label="Server Status",
                    value="✅ MCP Server Running\nURL: http://localhost:8000/gradio_api/mcp/",
                    interactive=False
                )
                
                # MCP Tools list
                gr.Markdown("### 🛠️ Available Tools")
                mcp_tools_list = gr.Textbox(
                    label="MCP Tools",
                    value="• list_docsets - List all docsets\n• ask - Query knowledge base using RAG",
                    interactive=False,
                    lines=6
                )
                
                # MCP Configuration
                gr.Markdown("### ⚙️ Configuration")
                mcp_config_info = gr.Textbox(
                    label="MCP Config",
                    value="Server: ragspace\nTransport: HTTP/SSE\nPort: 8000",
                    interactive=False
                )
            
            with gr.Column(scale=3, elem_classes=["main-content"]):
                gr.Markdown("## 🧪 MCP Tool Testing")
                
                # Test MCP tools
                with gr.Group():
                    gr.Markdown("### Test list_docsets")
                    test_list_docsets_button = gr.Button(
                        "Test list_docsets",
                        variant="primary",
                        size="lg",
                        elem_classes=["button-primary"]
                    )
                    test_list_docsets_output = gr.Textbox(
                        label="Result",
                        interactive=False,
                        lines=5
                    )
                
                with gr.Group():
                    gr.Markdown("### Test ask")
                    test_ask_query = gr.Textbox(
                        label="Query",
                        placeholder="What documents do I have?",
                        scale=2
                    )
                    # Get initial docset list for MCP testing
                    initial_mcp_docsets = get_docset_manager().get_docsets_dict()
                    initial_mcp_choices = list(initial_mcp_docsets.keys()) if initial_mcp_docsets else []
                    
                    test_ask_docset = gr.Dropdown(
                        label="DocSet (optional)",
                        choices=initial_mcp_choices,
                        interactive=True,
                        scale=1
                    )
                    
                    # Refresh button for MCP docset list
                    refresh_mcp_docsets_button = gr.Button(
                        "🔄 Refresh DocSets", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["button-primary"]
                    )
                    
                    test_ask_button = gr.Button(
                        "Test ask",
                        variant="primary",
                        size="lg",
                        elem_classes=["button-primary"]
                    )
                    test_ask_output = gr.Textbox(
                        label="Result",
                        interactive=False,
                        lines=8
                    )
                
                # MCP Inspector instructions
                gr.Markdown("### 📋 MCP Inspector Usage")
                mcp_inspector_instructions = gr.Markdown("""
                **To test with mcp-inspector CLI:**
                
                1. Start the server: `make dev`
                2. In another terminal: `mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/list`
                3. Test list_docsets: `mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name list_docsets --params '{}'`
                4. Test ask: `mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name ask --params '{"query": "test", "docset": null}'`
                """)
        
        # Connect MCP tool testing - Use handlers for business logic
        def test_list_docsets_tool():
            """Test list_docsets MCP tool"""
            try:
                from src.ragspace.ui.handlers import list_documents
                result = list_documents()
                return gr.Textbox(value=str(result))
            except Exception as e:
                return gr.Textbox(value=f"Error: {str(e)}")
        
        def test_ask_tool(query, docset):
            """Test ask MCP tool"""
            try:
                from src.ragspace.ui.handlers import process_rag_query_sync
                result = process_rag_query_sync(query, docset if docset else None)
                return gr.Textbox(value=str(result))
            except Exception as e:
                return gr.Textbox(value=f"Error: {str(e)}")
        
        def update_mcp_docset_list():
            """Update MCP test DocSet dropdown"""
            docsets = get_docset_manager().get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            return gr.Dropdown(choices=choices)
        
        # Refresh MCP docset list button
        refresh_mcp_docsets_button.click(
            update_mcp_docset_list,
            outputs=[test_ask_docset],
            api_name=False
        )
        
        test_list_docsets_button.click(
            test_list_docsets_tool,
            outputs=test_list_docsets_output,
            api_name=False
        )
        
        test_ask_button.click(
            test_ask_tool,
            [test_ask_query, test_ask_docset],
            test_ask_output,
            api_name=False
        )
    
    return tab 