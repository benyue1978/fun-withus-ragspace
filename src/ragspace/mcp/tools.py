"""
MCP Tools for RAGSpace
"""

from src.ragspace.storage.supabase_manager import supabase_docset_manager
import gradio as gr

def list_docset():
    """List all docsets"""
    try:
        # Get the raw docsets dictionary
        docsets = supabase_docset_manager.get_docsets_dict()
        if not docsets:
            return "No docsets found."
        
        result = "Available DocSets:\n"
        for name, docset in docsets.items():
            result += f"- {name}"
            if docset.get('description'):
                result += f": {docset['description']}"
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error listing docsets: {str(e)}"

def ask(query: str, docset: str = None):
    """Query the knowledge base"""
    try:
        if not query.strip():
            return "Please provide a query."
        
        # Use the Supabase manager to query the knowledge base
        response = supabase_docset_manager.query_knowledge_base(query, docset)
        return response
    except Exception as e:
        return f"Error processing query: {str(e)}" 
    
def expose_mcp_tools():
    """Expose MCP tools"""
    hidden_btn_list_docset = gr.Button("hidden", render=False)
    hidden_btn_list_docset.click(
        fn=list_docset,
        inputs=[],
        outputs=gr.Textbox(label="DocSets", visible=False),
        api_name="list_docset"
    )
    hidden_btn_ask = gr.Button("hidden", render=False)
    hidden_btn_ask.click(
        fn=ask,
        inputs=[
            gr.Textbox(label="Query", visible=False),
            gr.Textbox(label="DocSet (optional)", visible=False)
        ],
        outputs=gr.Textbox(label="Answer", visible=False),
        api_name="ask"
    )
