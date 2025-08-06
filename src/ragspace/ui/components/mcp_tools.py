"""
MCP Tools UI Component
"""

import gradio as gr

def get_docset_manager():
    """Get the current docset manager"""
    from src.ragspace.storage import docset_manager
    return docset_manager

from src.ragspace.mcp.tools import list_docset, ask

# Import MCP tools locally to avoid circular imports
def _get_mcp_tools():
    """Get MCP tools without circular import"""
    from src.ragspace.mcp.tools import list_docset, ask
    return list_docset, ask

def create_mcp_tools_tab():
    """Create the MCP tools tab"""
    
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
                    value="• list_docset - List all docsets\n• ask - Query knowledge base",
                    interactive=False,
                    lines=8
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
                    gr.Markdown("### Test list_docset")
                    test_list_docset_button = gr.Button("Test list_docset")
                    test_list_docset_output = gr.Textbox(
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
                    refresh_mcp_docsets_button = gr.Button("🔄 Refresh DocSets", variant="secondary", size="sm")
                    test_ask_button = gr.Button("Test ask")
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
                3. Test ask: `mcp-inspector --config mcp_inspector_config.json --server ragspace --cli --method tools/call --tool-name ask --params '{"query": "test", "docset": null}'`
                """)
        
        # Connect MCP tool testing
        def test_list_docset_tool():
            """Test list_docset MCP tool"""
            try:
                list_docset_func, ask_func = _get_mcp_tools()
                result = list_docset_func()
                return gr.Textbox(value=str(result))
            except Exception as e:
                return gr.Textbox(value=f"Error: {str(e)}")
        
        def test_ask_tool(query, docset):
            """Test ask MCP tool"""
            try:
                list_docset_func, ask_func = _get_mcp_tools()
                result = ask_func(query, docset if docset else None)
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
        
        test_list_docset_button.click(
            test_list_docset_tool,
            outputs=test_list_docset_output,
            api_name=False
        )
        
        test_ask_button.click(
            test_ask_tool,
            [test_ask_query, test_ask_docset],
            test_ask_output,
            api_name=False
        )
    
    return tab 