"""
MCP Tools for RAGSpace
"""

from src.ragspace.storage.manager import docset_manager
import gradio as gr

def list_docset():
    """List all docsets"""
    try:
        # Get the raw docsets dictionary
        docsets = docset_manager.docsets
        if not docsets:
            return "No docsets found."
        
        result = "Available DocSets:\n"
        for name, docset in docsets.items():
            result += f"- {name}"
            if docset.description:
                result += f": {docset.description}"
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error listing docsets: {str(e)}"

def ask(query: str, docset: str = None):
    """Query the knowledge base"""
    try:
        if not query.strip():
            return "Please provide a query."
        
        # For now, return a simple response
        # In the future, this will integrate with RAG pipeline
        response = f"Query: {query}"
        if docset:
            response += f"\nDocSet: {docset}"
        
        response += "\n\nThis is a placeholder response. RAG functionality will be implemented soon."
        return response
    except Exception as e:
        return f"Error processing query: {str(e)}" 
    
def expose_mcp_tools():
    """Expose MCP tools"""
    hidden_btn_list_docset = gr.Button("hidden", render=False)
    hidden_btn_list_docset.click(
        fn=list_docset,
        inputs=[],
        outputs=[],
        api_name="list_docset"
    )
    hidden_btn_ask = gr.Button("hidden", render=False)
    hidden_btn_ask.click(
        fn=ask,
        inputs=[],
        outputs=[],
        api_name="ask"
    )
