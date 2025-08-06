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
    """Create the knowledge management tab"""
    
    # Get initial docsets
    initial_docsets = get_docset_manager().get_docsets_dict()
    initial_choices = list(initial_docsets.keys()) if initial_docsets else []
    initial_selected = initial_choices[0] if initial_choices else None
    
    def get_docset_data(docset_name):
        """Get docset and documents data"""
        try:
            docset_manager = get_docset_manager()
            docset = docset_manager.get_docset_by_name(docset_name)
            documents = docset_manager.list_documents_in_docset(docset_name) if docset_name else []
            return docset, documents, None
        except Exception as e:
            return None, [], str(e)
    
    def convert_documents_to_dataframe(documents):
        """Convert documents to dataframe format"""
        doc_rows = []
        for doc in documents:
            # Ensure doc is a dictionary
            if not isinstance(doc, dict):
                print(f"Warning: Skipping non-dict document: {type(doc)}")
                continue
                
            doc_rows.append([
                doc.get('name', 'Unknown'),
                doc.get('type', 'unknown'),
                doc.get('url', 'N/A'),
                doc.get('added_date', 'Unknown')
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
                
                # DocSet management section
                with gr.Group():
                    gr.Markdown("### 📚 DocSet Management")
                    
                    # Create new DocSet
                    with gr.Row():
                        docset_name_input = gr.Textbox(
                            label="📝 DocSet Name",
                            placeholder="Enter docset name...",
                            elem_classes=["input-modern"]
                        )
                        docset_desc_input = gr.Textbox(
                            label="📄 Description",
                            placeholder="Enter description...",
                            elem_classes=["input-modern"]
                        )
                    
                    with gr.Row():
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
                # Get initial docset list
                initial_docsets = get_docset_manager().get_docsets_dict()
                initial_choices = list(initial_docsets.keys()) if initial_docsets else []
                
                docset_list = gr.Dropdown(
                    choices=initial_choices,
                    label="📚 Available DocSets",
                    interactive=True,
                    elem_classes=["input-modern"]
                )
                

                
                # DocSet actions
                with gr.Group():
                    refresh_docs_button = gr.Button(
                        "🔄 Refresh Documents", 
                        variant="secondary", 
                        size="lg",
                        elem_classes=["button-secondary"]
                    )
            
            # Right main content - Documents and Add content
            with gr.Column(scale=3, elem_classes=["main-content"]):
                gr.Markdown("## 📄 Documents", elem_classes=["markdown-enhanced"])
                
                # Selected DocSet info with modern card
                with gr.Group(elem_classes=["card"]):
                    gr.Markdown("### 📊 DocSet Overview")
                    selected_docset_info = gr.Textbox(
                        type="text",
                        lines=3,
                        label="📋 Selected DocSet Info",
                        interactive=False,
                        elem_classes=["input-modern"]
                    )
                
                # Documents list with modern styling
                with gr.Group(elem_classes=["card"]):
                    gr.Markdown("### 📚 Documents List")
                    documents_list = gr.Dataframe(
                        headers=["📄 Document Name", "📁 Type", "🔗 URL", "📅 Added Date"],
                        row_count=(1, "dynamic"),
                        col_count=(4, "fixed"),
                        datatype=["str", "str", "str", "str"],
                        type="pandas",
                        label="📋 Documents in Selected DocSet",
                        interactive=False
                    )
                
                # Add content section - now collapsible
                with gr.Accordion("📥 Add Content", open=False):
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
                                placeholder="owner/repository or https://github.com/owner/repo",
                                label="GitHub Repository"
                            )
                            github_branch = gr.Textbox(
                                type="text",
                                lines=1,
                                value="main",
                                label="Branch (optional)",
                                info="Leave as 'main' for most repositories"
                            )
                            github_button = gr.Button("Add Repository", variant="secondary", size="lg")
                            github_output = gr.Textbox(
                                type="text",
                                lines=3,
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
                return gr.Dataframe(value=[])
            if not docset:
                return gr.Dataframe(value=[])
            
            # Ensure documents is a list
            if not isinstance(documents, list):
                return gr.Dataframe(value=[])
            
            doc_rows = convert_documents_to_dataframe(documents)
            
            return gr.Dataframe(value=doc_rows)
        
        def update_docset_info(docset_name):
            """Update DocSets Info when a docset is selected"""
            print(f"🔍 update_docset_info called with: {docset_name}")
            
            if not docset_name:
                print("  → No docset name provided")
                return gr.Textbox(value="Select a DocSet to view details")
            
            docset, documents, error = get_docset_data(docset_name)
            print(f"  → Got docset: {docset is not None}, documents: {len(documents) if isinstance(documents, list) else 'not list'}, error: {error}")
            
            if error:
                print(f"  → Error: {error}")
                return gr.Textbox(value=f"Error loading docset info: {error}")
            if not docset:
                print(f"  → Docset not found: {docset_name}")
                return gr.Textbox(value=f"DocSet '{docset_name}' not found")
            
            # Ensure documents is a list
            if not isinstance(documents, list):
                print(f"  → Documents is not a list: {type(documents)}")
                return gr.Textbox(value="Error: Invalid document data format")
            
            info_text = create_docset_info_text(docset, documents, docset_name)
            print(f"  → Generated info text: {len(info_text)} characters")
            return gr.Textbox(value=info_text)
        
        def update_target_docsets(docset_name):
            """Update Target DocSet textboxes when a docset is selected"""
            if not docset_name:
                return gr.Textbox(value="Select a DocSet from the sidebar"), gr.Textbox(value="Select a DocSet from the sidebar"), gr.Textbox(value="Select a DocSet from the sidebar")
            return gr.Textbox(value=docset_name), gr.Textbox(value=docset_name), gr.Textbox(value=docset_name)
        
        # Connect events
        # Auto-load docsets on page load by triggering the create button (which will update the list)
        create_docset_button.click(
            create_docset_ui, 
            [docset_name_input, docset_desc_input], 
            create_docset_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            docset_list
        ], api_name=False)
        
        # Separate event bindings for better debugging
        docset_list.change(
            update_documents,
            docset_list,
            documents_list,
            api_name=False
        )
        
        docset_list.change(
            update_docset_info,
            docset_list,
            selected_docset_info,
            api_name=False
        )
        
        docset_list.change(
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
            [github_input, github_docset_name, github_branch], 
            github_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            docset_list
        ], api_name=False)
        
        # Refresh documents
        refresh_docs_button.click(
            update_documents,
            docset_list,
            documents_list,
            api_name=False
        ) 