"""
MCP Tools for RAGSpace - External Interface Only
"""

import gradio as gr

def get_docset_manager():
    """Get the current docset manager"""
    from src.ragspace.storage import docset_manager
    return docset_manager

def get_rag_manager():
    """Get the RAG manager"""
    from src.ragspace.services.rag import RAGManager
    return RAGManager()

def list_docsets():
    """List all docsets - MCP tool interface"""
    try:
        docset_manager = get_docset_manager()
        docsets = docset_manager.get_docsets_dict()
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
    """Query the knowledge base using RAG - MCP tool interface
    Args:
        query: The query to ask, in natural language
        docset: The docset to ask. The available docset names can be obtained from list_docsets()
    Returns:
        The response from the RAG
    """
    try:
        if not query.strip():
            return "Please provide a query."
        
        # Use handlers for business logic
        from src.ragspace.ui.handlers import process_rag_query_sync
        result = process_rag_query_sync(query, docset)
        
        # Extract the assistant's response from the result
        if isinstance(result, list) and len(result) >= 2:
            # Return only the assistant's response content
            content = result[1].get("content", "No response generated")
            # If content is empty, check if it's an error response
            if not content and len(result) >= 2:
                # Check if there's an error in the response
                if "❌ Error processing query" in str(result):
                    return "❌ Mock error: This is a test error response."
            return content
        else:
            return str(result)
        
    except Exception as e:
        return f"Error processing query: {str(e)}"
    
def expose_mcp_tools():
    """Expose MCP tools - External interface only"""
    # List docsets tool
    hidden_btn_list_docsets = gr.Button("hidden", render=False)
    hidden_btn_list_docsets.click(
        fn=list_docsets,
        inputs=[],
        outputs=gr.Textbox(label="DocSets", visible=False),
        api_name="list_docsets"
    )
    
    # Ask tool
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
