"""
Knowledge Management Component - Improved Architecture
Using component-based architecture with better separation of concerns
"""

import gradio as gr
from typing import List, Dict, Any, Optional
from .base_component import BaseComponent, ComponentState


class KnowledgeManagementComponent(BaseComponent):
    """Knowledge Management Component with improved architecture"""
    
    def __init__(self):
        super().__init__("knowledge_management")
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
            # Left sidebar - DocSet management
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                self._create_docset_management_section(initial_data)
            
            # Right main content - Documents and Add content
            with gr.Column(scale=3, elem_classes=["main-content"]):
                self._create_documents_section(initial_data)
                self._create_add_content_section(initial_data)
    
    def _get_initial_data(self) -> Dict[str, Any]:
        """Get initial data - separated for better testing"""
        try:
            docsets = self.docset_manager.get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            selected = choices[0] if choices else None
            
            return {
                "choices": choices,
                "selected": selected,
                "initial_info": self._get_docset_info(selected) if selected else "",
                "initial_documents": self._get_documents_data(selected) if selected else []
            }
        except Exception as e:
            print(f"Error getting initial data: {e}")
            return {"choices": [], "selected": None, "initial_info": "", "initial_documents": []}
    
    def _create_docset_management_section(self, initial_data: Dict[str, Any]):
        """Create DocSet management section"""
        gr.Markdown("## 📚 DocSet Management", elem_classes=["markdown-enhanced"])
        
        with gr.Group(elem_classes=["card"]):
            gr.Markdown("### ✨ Create New DocSet")
            
            create_docset_name = gr.Textbox(
                type="text",
                lines=1,
                placeholder="Enter DocSet name...",
                label="📝 DocSet Name",
                elem_classes=["input-modern"]
            )
            
            create_docset_button = gr.Button(
                "✨ Create DocSet", 
                variant="primary", 
                size="lg",
                elem_classes=["button-primary"]
            )
            
            create_docset_output = gr.Textbox(
                type="text",
                lines=2,
                label="📤 Status",
                interactive=False
            )
        
        # DocSet selection
        gr.Markdown("### 🎯 Select DocSet")
        
        docset_list = gr.Dropdown(
            choices=initial_data["choices"],
            value=initial_data["selected"],
            label="📚 Available DocSets",
            interactive=True,
            elem_classes=["input-modern"]
        )
        
        # Register components
        self.add_component("create_docset_name", create_docset_name)
        self.add_component("create_docset_button", create_docset_button)
        self.add_component("create_docset_output", create_docset_output)
        self.add_component("docset_list", docset_list)
    
    def _create_documents_section(self, initial_data: Dict[str, Any]):
        """Create documents section"""
        gr.Markdown("## 📄 Documents", elem_classes=["markdown-enhanced"])
        
        # Selected DocSet info
        with gr.Group(elem_classes=["card"]):
            gr.Markdown("### 📋 DocSet Overview")
            
            selected_docset_info = gr.Textbox(
                type="text",
                lines=5,
                label="📋 Selected DocSet Info",
                value=initial_data["initial_info"],
                interactive=False,
                elem_classes=["input-modern"]
            )
        
        # Documents list
        with gr.Group(elem_classes=["card"]):
            gr.Markdown("### 📚 Documents List")
            
            with gr.Row():
                refresh_docs_button = gr.Button(
                    "🔄 Refresh Documents",
                    variant="primary",
                    size="lg",
                    elem_classes=["button-primary"]
                )
                trigger_embedding_button = gr.Button(
                    "🧠 Trigger Embedding",
                    variant="primary",
                    size="lg",
                    elem_classes=["button-primary"]
                )
            
            documents_list = gr.Dataframe(
                headers=["📄 Document Name", "📁 Type", "🔗 URL", "📅 Added Date", "🧠 Embedding Status"],
                value=initial_data["initial_documents"],
                row_count=(1, "dynamic"),
                col_count=(5, "fixed"),
                datatype=["str", "str", "str", "str", "str"],
                type="pandas",
                label="📋 Documents in Selected DocSet",
                interactive=False
            )
        
        # Register components
        self.add_component("selected_docset_info", selected_docset_info)
        self.add_component("refresh_docs_button", refresh_docs_button)
        self.add_component("trigger_embedding_button", trigger_embedding_button)
        self.add_component("documents_list", documents_list)
    
    def _create_add_content_section(self, initial_data: Dict[str, Any]):
        """Create add content section"""
        with gr.Accordion("📥 Add Content", open=False):
            with gr.Tabs():
                self._create_file_upload_tab(initial_data)
                self._create_url_upload_tab(initial_data)
                self._create_github_upload_tab(initial_data)
    
    def _create_file_upload_tab(self, initial_data: Dict[str, Any]):
        """Create file upload tab"""
        with gr.Tab("📄 Upload Files"):
            upload_docset_name = gr.Textbox(
                value=initial_data["selected"] if initial_data["selected"] else "Select a DocSet from the sidebar",
                label="Target DocSet",
                interactive=False,
                visible=False
            )
            
            file_input = gr.File(
                file_count="multiple",
                file_types=[".txt", ".md", ".pdf", ".docx"],
                type="filepath",
                label="Upload Documents"
            )
            
            file_output = gr.Textbox(
                type="text",
                lines=1,
                label="Upload Status",
                interactive=False
            )
            
            # Register components
            self.add_component("upload_docset_name", upload_docset_name)
            self.add_component("file_input", file_input)
            self.add_component("file_output", file_output)
    
    def _create_url_upload_tab(self, initial_data: Dict[str, Any]):
        """Create URL upload tab"""
        with gr.Tab("🌐 Add Website"):
            url_docset_name = gr.Textbox(
                value=initial_data["selected"] if initial_data["selected"] else "Select a DocSet from the sidebar",
                label="Target DocSet",
                interactive=False,
                visible=False
            )
            
            url_input = gr.Textbox(
                type="text",
                lines=1,
                placeholder="https://example.com/docs",
                label="Website URL"
            )
            
            website_type = gr.Dropdown(
                choices=[["website", "website"], ["github", "github"]],
                value="website",
                type="value",
                allow_custom_value=False,
                filterable=True,
                label="Website Type"
            )
            
            url_button = gr.Button(
                "Add Website", 
                variant="primary", 
                size="lg",
                elem_classes=["button-primary"]
            )
            
            url_output = gr.Textbox(
                type="text",
                lines=1,
                label="URL Status",
                interactive=False
            )
            
            # Register components
            self.add_component("url_docset_name", url_docset_name)
            self.add_component("url_input", url_input)
            self.add_component("website_type", website_type)
            self.add_component("url_button", url_button)
            self.add_component("url_output", url_output)
    
    def _create_github_upload_tab(self, initial_data: Dict[str, Any]):
        """Create GitHub upload tab"""
        with gr.Tab("🐙 Add GitHub Repo"):
            github_docset_name = gr.Textbox(
                value=initial_data["selected"] if initial_data["selected"] else "Select a DocSet from the sidebar",
                label="Target DocSet",
                interactive=False,
                visible=False
            )
            
            github_input = gr.Textbox(
                type="text",
                lines=1,
                placeholder="owner/repository or https://github.com/owner/repo",
                label="GitHub Repository"
            )
            
            branch_input = gr.Textbox(
                type="text",
                lines=1,
                placeholder="main",
                label="Branch (optional)"
            )
            
            github_button = gr.Button(
                "Add Repository", 
                variant="primary", 
                size="lg",
                elem_classes=["button-primary"]
            )
            
            github_output = gr.Textbox(
                type="text",
                lines=3,
                label="Repository Status",
                interactive=False
            )
            
            # Register components
            self.add_component("github_docset_name", github_docset_name)
            self.add_component("github_input", github_input)
            self.add_component("branch_input", branch_input)
            self.add_component("github_button", github_button)
            self.add_component("github_output", github_output)
    
    def setup_events(self):
        """Setup event handlers - clean separation of event binding"""
        # Get components
        create_docset_button = self.get_component("create_docset_button")
        create_docset_name = self.get_component("create_docset_name")
        create_docset_output = self.get_component("create_docset_output")
        docset_list = self.get_component("docset_list")
        refresh_docs_button = self.get_component("refresh_docs_button")
        trigger_embedding_button = self.get_component("trigger_embedding_button")
        documents_list = self.get_component("documents_list")
        selected_docset_info = self.get_component("selected_docset_info")
        
        # File upload components
        file_input = self.get_component("file_input")
        file_output = self.get_component("file_output")
        upload_docset_name = self.get_component("upload_docset_name")
        
        # URL upload components
        url_button = self.get_component("url_button")
        url_input = self.get_component("url_input")
        website_type = self.get_component("website_type")
        url_output = self.get_component("url_output")
        url_docset_name = self.get_component("url_docset_name")
        
        # GitHub upload components
        github_button = self.get_component("github_button")
        github_input = self.get_component("github_input")
        branch_input = self.get_component("branch_input")
        github_output = self.get_component("github_output")
        github_docset_name = self.get_component("github_docset_name")
        
        # Setup event handlers
        self._setup_docset_events(create_docset_button, create_docset_name, create_docset_output, docset_list)
        self._setup_document_events(docset_list, refresh_docs_button, trigger_embedding_button, documents_list, selected_docset_info)
        self._setup_upload_events(file_input, file_output, upload_docset_name, url_button, url_input, website_type, url_output, url_docset_name, github_button, github_input, branch_input, github_output, github_docset_name)
    
    def _setup_docset_events(self, create_button, name_input, output, docset_list):
        """Setup DocSet related events"""
        from src.ragspace.ui.handlers import create_docset
        
        create_button.click(
            create_docset,
            [name_input],
            [output, docset_list],
            api_name=False
        )
    
    def _setup_document_events(self, docset_list, refresh_button, trigger_button, documents_list, docset_info):
        """Setup document related events"""
        from src.ragspace.ui.handlers import update_documents, update_docset_info, trigger_embedding_for_docset
        
        # DocSet selection events
        docset_list.change(
            update_documents,
            docset_list,
            documents_list,
            api_name=False
        ).then(
            update_docset_info,
            docset_list,
            docset_info,
            api_name=False
        )
        
        # Refresh and trigger events
        refresh_button.click(
            update_documents,
            docset_list,
            documents_list,
            api_name=False
        )
        
        trigger_button.click(
            lambda: "⏳ Processing...",
            outputs=trigger_button,
            api_name=False
        ).then(
            trigger_embedding_for_docset,
            docset_list,
            trigger_button,
            api_name=False
        ).then(
            update_documents,
            docset_list,
            documents_list,
            api_name=False
        ).then(
            update_docset_info,
            docset_list,
            docset_info,
            api_name=False
        )
    
    def _setup_upload_events(self, file_input, file_output, file_docset, url_button, url_input, website_type, url_output, url_docset, github_button, github_input, branch_input, github_output, github_docset):
        """Setup upload related events"""
        from src.ragspace.ui.handlers import upload_files, add_url_to_docset, add_github_repo_to_docset, update_target_docsets, update_documents, update_docset_info
        
        # Get the main docset dropdown from the sidebar
        docset_list = self.get_component("docset_list")
        documents_list = self.get_component("documents_list")
        docset_info = self.get_component("docset_info")
        
        # File upload events - use the selected docset from sidebar
        file_input.upload(
            upload_files,
            [file_input, docset_list],
            [file_output, file_docset],
            api_name=False
        ).then(
            update_documents,
            docset_list,
            documents_list,
            api_name=False
        ).then(
            update_docset_info,
            docset_list,
            docset_info,
            api_name=False
        )
        
        # URL upload events - use the selected docset from sidebar
        url_button.click(
            add_url_to_docset,
            [url_input, docset_list, website_type],
            url_output,
            api_name=False
        ).then(
            update_documents,
            docset_list,
            documents_list,
            api_name=False
        ).then(
            update_docset_info,
            docset_list,
            docset_info,
            api_name=False
        )
        
        # GitHub upload events - use the selected docset from sidebar
        github_button.click(
            add_github_repo_to_docset,
            [github_input, docset_list, branch_input],
            github_output,
            api_name=False
        ).then(
            update_documents,
            docset_list,
            documents_list,
            api_name=False
        ).then(
            update_docset_info,
            docset_list,
            docset_info,
            api_name=False
        )
    
    def _get_docset_info(self, docset_name: Optional[str]) -> str:
        """Get DocSet info - separated for better testing"""
        if not docset_name:
            return ""
        
        try:
            from src.ragspace.ui.handlers import get_docset_data, create_docset_info_text
            docset, documents, error = get_docset_data(docset_name)
            if not error and docset:
                return create_docset_info_text(docset, documents, docset_name)
        except Exception as e:
            print(f"Error getting docset info: {e}")
        
        return ""
    
    def _get_documents_data(self, docset_name: Optional[str]) -> List[List[str]]:
        """Get documents data - separated for better testing"""
        if not docset_name:
            return []
        
        try:
            from src.ragspace.ui.handlers import get_docset_data, convert_documents_to_dataframe
            docset, documents, error = get_docset_data(docset_name)
            if not error and isinstance(documents, list):
                return convert_documents_to_dataframe(documents)
        except Exception as e:
            print(f"Error getting documents data: {e}")
        
        return []


def create_knowledge_management_tab():
    """Create the knowledge management tab using the improved component"""
    component = KnowledgeManagementComponent()
    component.create_ui()
    component.setup_events() 