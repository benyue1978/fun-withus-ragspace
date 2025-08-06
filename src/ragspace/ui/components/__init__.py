"""
UI Components for RAGSpace
"""

from .knowledge_management import create_knowledge_management_tab
from .chat_interface import create_chat_interface_tab
from .mcp_tools import create_mcp_tools_tab

__all__ = [
    "create_knowledge_management_tab",
    "create_chat_interface_tab", 
    "create_mcp_tools_tab"
] 