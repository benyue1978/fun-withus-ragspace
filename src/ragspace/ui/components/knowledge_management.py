"""
Knowledge Management UI Component
"""

import gradio as gr
import time

def get_docset_manager():
    """Get the current docset manager"""
    from src.ragspace.storage import docset_manager
    return docset_manager

from src.ragspace.ui.handlers import (
    create_docset_ui,
    upload_file_to_docset,
    add_url_to_docset,
    add_github_repo_to_docset
)

def create_knowledge_management_tab():
    """Create the Knowledge Management tab with improved layout"""
    
    # Define helper functions first
    def get_docset_data(docset_name):
        """Get docset and its documents data"""
        if not docset_name:
            return None, None, None
        
        try:
            docset_manager = get_docset_manager()
            docset = docset_manager.get_docset_by_name(docset_name)
            if not docset:
                return None, None, None
            
            # For mock manager, we need to get documents differently
            # Since mock doesn't have direct database access, we'll use the list_documents_in_docset method
            documents_text = docset_manager.list_documents_in_docset(docset_name)
            # Parse the text to extract document information
            documents = []
            lines = documents_text.split('\n')
            for line in lines:
                if line.strip().startswith('1.') or line.strip().startswith('2.') or line.strip().startswith('3.'):
                    # Extract document info from the text format
                    parts = line.strip().split(' ')
                    if len(parts) >= 2:
                        doc_name = ' '.join(parts[1:])
                        documents.append({
                            'name': doc_name,
                            'type': 'file',  # Default for mock
                            'url': None,
                            'added_date': 'Unknown'
                        })
            
            return docset, documents, None
        except Exception as e:
            return None, None, str(e)
    
    def convert_documents_to_dataframe(documents):
        """Convert documents to dataframe format"""
        doc_rows = []
        for doc in documents:
            doc_rows.append([
                doc['name'],
                doc['type'],
                doc.get('url', 'N/A'),
                doc['added_date']
            ])
        return doc_rows
    
    def create_docset_info_text(docset, documents, docset_name):
        """Create detailed docset info text"""
        info_lines = [
            f"📁 DocSet: {docset_name}",
            f"📝 Description: {docset.get('description', 'No description')}",
            f"📅 Created: {docset.get('created_at', 'Unknown')}",
            f"📄 Documents: {len(documents)}",
            "",
            "📋 Document Types:"
        ]
        
        # Count document types
        type_counts = {}
        for doc in documents:
            doc_type = doc.get('type', 'unknown')
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        for doc_type, count in type_counts.items():
            info_lines.append(f"  • {doc_type}: {count}")
        
        if not documents:
            info_lines.append("  • No documents yet")
        
        return "\n".join(info_lines)
    
    with gr.Tab("📚 Knowledge Management", id=0):
        with gr.Row():
            # Left sidebar - DocSet management only
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                gr.Markdown("## 📁 DocSets")
                
                with gr.Group():
                    gr.Markdown("### ➕ Create New DocSet")
                    
                    docset_name_input = gr.Textbox(
                        type="text",
                        lines=1,
                        placeholder="e.g., gradio mcp",
                        label="DocSet Name"
                    )
                    docset_desc_input = gr.Textbox(
                        type="text",
                        lines=1,
                        placeholder="Optional description",
                        label="Description"
                    )
                    create_docset_button = gr.Button("Create DocSet", variant="primary", size="lg")
                    create_docset_output = gr.Textbox(
                        type="text",
                        lines=1,
                        label="Status",
                        interactive=False
                    )
                
                with gr.Group():
                    gr.Markdown("### 📋 All DocSets")
                    list_docsets_button = gr.Button("🔄 Refresh DocSets", variant="secondary", size="lg")
                    # Get initial docsets
                    initial_docsets = get_docset_manager().get_docsets_dict()
                    initial_choices = list(initial_docsets.keys()) if initial_docsets else []
                    initial_selected = initial_choices[0] if initial_choices else None
                    
                    docset_list = gr.Dropdown(
                        choices=initial_choices,
                        value=initial_selected,
                        type="value",
                        allow_custom_value=False,
                        filterable=True,
                        label="Select DocSet",
                        interactive=True
                    )
                    # Get initial docset info
                    if initial_selected:
                        docset, documents, error = get_docset_data(initial_selected)
                        if error:
                            initial_docset_info = f"Error loading docset info: {error}"
                        elif docset:
                            initial_docset_info = create_docset_info_text(docset, documents, initial_selected)
                        else:
                            initial_docset_info = "Select a DocSet to view details"
                    else:
                        initial_docset_info = "No docsets available."
                    
                    list_docsets_output = gr.Textbox(
                        type="text",
                        lines=8,
                        label="DocSets Info",
                        interactive=False,
                        value=initial_docset_info
                    )
            
            # Right main content - Documents and Add content
            with gr.Column(scale=3, elem_classes=["main-content"]):
                gr.Markdown("## 📄 Documents")
                
                # Get initial documents and info for selected docset
                initial_documents = []
                initial_selected_info = ""
                if initial_selected:
                    docset, documents, error = get_docset_data(initial_selected)
                    if error:
                        initial_selected_info = f"Error loading documents: {error}"
                    elif docset:
                        initial_selected_info = f"DocSet: {initial_selected}\nDocuments: {len(documents)}"
                        initial_documents = convert_documents_to_dataframe(documents)
                
                # Selected DocSet info
                selected_docset_info = gr.Textbox(
                    type="text",
                    lines=3,
                    label="Selected DocSet Info",
                    interactive=False,
                    value=initial_selected_info
                )
                
                # Documents list
                documents_list = gr.Dataframe(
                    value=initial_documents,
                    headers=["Document Name", "Type", "URL", "Added Date"],
                    row_count=(1, "dynamic"),
                    col_count=(4, "fixed"),
                    datatype=["str", "str", "str", "str"],
                    type="pandas",
                    label="Documents in Selected DocSet",
                    interactive=False
                )
                
                # DocSet actions
                with gr.Group():
                    refresh_docs_button = gr.Button("🔄 Refresh Documents", variant="secondary", size="lg")
                
                # Add content section
                gr.Markdown("## 📥 Add Content")
                
                with gr.Tabs():
                    # File upload tab
                    with gr.Tab("📄 Upload Files"):
                        upload_docset_name = gr.Textbox(
                            value=initial_selected if initial_selected else "Select a DocSet from the sidebar",
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
                    
                    # URL upload tab
                    with gr.Tab("🌐 Add Website"):
                        url_docset_name = gr.Textbox(
                            value=initial_selected if initial_selected else "Select a DocSet from the sidebar",
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
                        url_button = gr.Button("Add Website", variant="secondary", size="lg")
                        url_output = gr.Textbox(
                            type="text",
                            lines=1,
                            label="URL Status",
                            interactive=False
                        )
                    
                    # GitHub upload tab
                    with gr.Tab("🐙 Add GitHub Repo"):
                        github_docset_name = gr.Textbox(
                            value=initial_selected if initial_selected else "Select a DocSet from the sidebar",
                            label="Target DocSet",
                            interactive=False,
                            visible=False
                        )
                        github_input = gr.Textbox(
                            type="text",
                            lines=1,
                            placeholder="owner/repository",
                            label="GitHub Repository"
                        )
                        github_button = gr.Button("Add Repository", variant="secondary", size="lg")
                        github_output = gr.Textbox(
                            type="text",
                            lines=1,
                            label="Repository Status",
                            interactive=False
                        )
        
        # Connect sidebar interactions
        def update_docset_lists():
            """Update DocSet dropdown with current list"""
            docsets = get_docset_manager().get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            return gr.Dropdown(choices=choices)
        
        def update_documents(docset_name):
            """Update documents list when DocSet is selected"""
            docset, documents, error = get_docset_data(docset_name)
            
            if error:
                return gr.Dataframe(value=[]), gr.Textbox(value=f"Error: {error}")
            if not docset:
                return gr.Dataframe(value=[]), gr.Textbox(value=f"DocSet '{docset_name}' not found" if docset_name else "")
            
            doc_rows = convert_documents_to_dataframe(documents)
            docset_info = f"DocSet: {docset_name}\nDocuments: {len(documents)}"
            
            return gr.Dataframe(value=doc_rows), gr.Textbox(value=docset_info)
        
        def update_docset_info(docset_name):
            """Update DocSets Info when a docset is selected"""
            if not docset_name:
                return gr.Textbox(value="Select a DocSet to view details")
            
            docset, documents, error = get_docset_data(docset_name)
            
            if error:
                return gr.Textbox(value=f"Error loading docset info: {error}")
            if not docset:
                return gr.Textbox(value=f"DocSet '{docset_name}' not found")
            
            info_text = create_docset_info_text(docset, documents, docset_name)
            return gr.Textbox(value=info_text)
        
        def update_target_docsets(docset_name):
            """Update Target DocSet textboxes when a docset is selected"""
            if not docset_name:
                return gr.Textbox(value="Select a DocSet from the sidebar"), gr.Textbox(value="Select a DocSet from the sidebar"), gr.Textbox(value="Select a DocSet from the sidebar")
            return gr.Textbox(value=docset_name), gr.Textbox(value=docset_name), gr.Textbox(value=docset_name)
        
        # Connect events
        # Auto-load docsets on page load by triggering the refresh button
        list_docsets_button.click(
            lambda: get_docset_manager().list_docsets(), 
            outputs=list_docsets_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            docset_list
        ], api_name=False)
        
        create_docset_button.click(
            create_docset_ui, 
            [docset_name_input, docset_desc_input], 
            create_docset_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            docset_list
        ], api_name=False)
        
        docset_list.change(
            update_documents,
            docset_list,
            [documents_list, selected_docset_info],
            api_name=False
        ).then(
            update_docset_info,
            docset_list,
            list_docsets_output,
            api_name=False
        ).then(
            update_target_docsets,
            docset_list,
            [upload_docset_name, url_docset_name, github_docset_name],
            api_name=False
        )
        
        # File upload
        file_input.upload(
            upload_file_to_docset, 
            [file_input, upload_docset_name], 
            file_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            docset_list
        ], api_name=False)
        
        # URL upload
        url_button.click(
            add_url_to_docset, 
            [url_input, url_docset_name, website_type], 
            url_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            docset_list
        ], api_name=False)
        
        # GitHub upload
        github_button.click(
            add_github_repo_to_docset, 
            [github_input, github_docset_name], 
            github_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            docset_list
        ], api_name=False)
        
        # Refresh documents
        refresh_docs_button.click(
            update_documents,
            docset_list,
            [documents_list, selected_docset_info],
            api_name=False
        ) 