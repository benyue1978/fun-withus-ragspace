"""
MCP Tools Component - Improved Architecture
Using component-based architecture with better separation of concerns
"""

import gradio as gr
from typing import List, Dict, Any, Optional
from .base_component import BaseComponent, ComponentState


class MCPToolsComponent(BaseComponent):
    """MCP Tools Component with improved architecture"""
    
    def __init__(self):
        super().__init__("mcp_tools")
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
            # Left sidebar - MCP info
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                self._create_sidebar_section(initial_data)
            
            # Right main content - Tool testing
            with gr.Column(scale=3, elem_classes=["main-content"]):
                self._create_tool_testing_section(initial_data)
    
    def _get_initial_data(self) -> Dict[str, Any]:
        """Get initial data - separated for better testing"""
        try:
            docsets = self.docset_manager.get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            
            return {
                "choices": choices
            }
        except Exception as e:
            print(f"Error getting initial data: {e}")
            return {"choices": []}
    
    def _create_sidebar_section(self, initial_data: Dict[str, Any]):
        """Create sidebar section"""
        gr.Markdown("## 🔧 MCP Server", elem_classes=["markdown-enhanced"])
        
        with gr.Group(elem_classes=["card"]):
            gr.Markdown("### 📊 Server Status")
            
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
        
        # Register components
        self.add_component("mcp_status", mcp_status)
        self.add_component("mcp_tools_list", mcp_tools_list)
        self.add_component("mcp_config_info", mcp_config_info)
    
    def _create_tool_testing_section(self, initial_data: Dict[str, Any]):
        """Create tool testing section"""
        gr.Markdown("## 🧪 MCP Tool Testing", elem_classes=["markdown-enhanced"])
        
        # Test list_docsets
        with gr.Group(elem_classes=["card"]):
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
        
        # Test ask
        with gr.Group(elem_classes=["card"]):
            gr.Markdown("### Test ask")
            
            test_ask_query = gr.Textbox(
                label="Query",
                placeholder="What documents do I have?",
                scale=2
            )
            
            # Get initial docset list for MCP testing
            test_ask_docset = gr.Dropdown(
                label="DocSet (optional)",
                choices=initial_data["choices"],
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
        
        # Register components
        self.add_component("test_list_docsets_button", test_list_docsets_button)
        self.add_component("test_list_docsets_output", test_list_docsets_output)
        self.add_component("test_ask_query", test_ask_query)
        self.add_component("test_ask_docset", test_ask_docset)
        self.add_component("refresh_mcp_docsets_button", refresh_mcp_docsets_button)
        self.add_component("test_ask_button", test_ask_button)
        self.add_component("test_ask_output", test_ask_output)
        self.add_component("mcp_inspector_instructions", mcp_inspector_instructions)
    
    def setup_events(self):
        """Setup event handlers - clean separation of event binding"""
        # Get components
        test_list_button = self.get_component("test_list_docsets_button")
        test_list_output = self.get_component("test_list_docsets_output")
        test_ask_button = self.get_component("test_ask_button")
        test_ask_query = self.get_component("test_ask_query")
        test_ask_docset = self.get_component("test_ask_docset")
        test_ask_output = self.get_component("test_ask_output")
        refresh_button = self.get_component("refresh_mcp_docsets_button")
        
        # Setup event handlers
        self._setup_test_events(test_list_button, test_list_output, test_ask_button, test_ask_query, test_ask_docset, test_ask_output)
        self._setup_refresh_events(refresh_button, test_ask_docset)
    
    def _setup_test_events(self, test_list_button, test_list_output, test_ask_button, test_ask_query, test_ask_docset, test_ask_output):
        """Setup test related events"""
        from src.ragspace.ui.handlers import test_list_docsets_tool, test_ask_tool
        
        # Test list_docsets
        test_list_button.click(
            test_list_docsets_tool,
            outputs=test_list_output,
            api_name=False
        )
        
        # Test ask
        test_ask_button.click(
            test_ask_tool,
            [test_ask_query, test_ask_docset],
            test_ask_output,
            api_name=False
        )
    
    def _setup_refresh_events(self, refresh_button, docset_dropdown):
        """Setup refresh related events"""
        from src.ragspace.ui.handlers import update_mcp_docset_list
        
        refresh_button.click(
            update_mcp_docset_list,
            outputs=[docset_dropdown],
            api_name=False
        )


def create_mcp_tools_tab():
    """Create the MCP tools tab using the improved component"""
    component = MCPToolsComponent()
    component.create_ui()
    component.setup_events() 