"""
Knowledge Management UI Component
"""

import gradio as gr
import time
from src.ragspace.storage.supabase_manager import supabase_docset_manager
from src.ragspace.ui.handlers import (
    create_docset_ui,
    upload_file_to_docset,
    add_url_to_docset,
    add_github_repo_to_docset
)

def create_knowledge_management_tab():
    """Create the Knowledge Management tab with improved layout"""
    
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
                    docset_list = gr.Dropdown(
                        choices=[],
                        type="value",
                        allow_custom_value=False,
                        filterable=True,
                        label="Select DocSet",
                        interactive=True
                    )
                    list_docsets_output = gr.Textbox(
                        type="text",
                        lines=8,
                        label="DocSets Info",
                        interactive=False
                    )
            
            # Right main content - Documents and Add content
            with gr.Column(scale=3, elem_classes=["main-content"]):
                gr.Markdown("## 📄 Documents")
                
                # Selected DocSet info
                selected_docset_info = gr.Textbox(
                    type="text",
                    lines=3,
                    label="Selected DocSet Info",
                    interactive=False
                )
                
                # Documents list
                documents_list = gr.Dataframe(
                    value={"headers": ["Document Name", "Type", "URL", "Added Date"], "data": []},
                    headers=["Document Name", "Type", "URL", "Added Date"],
                    row_count=(1, "dynamic"),
                    col_count=(4, "fixed"),
                    datatype=["str", "str", "str", "str"],
                    type="pandas",
                    label="Documents in Selected DocSet",
                    interactive=False
                )
                
                # Action buttons
                with gr.Row():
                    refresh_docs_button = gr.Button("🔄 Refresh Documents", variant="secondary", size="lg")
                    export_docset_button = gr.Button("📤 Export DocSet", variant="secondary", size="lg")
                
                # Add content section
                gr.Markdown("## 📥 Add Content")
                
                with gr.Tabs():
                    # File upload tab
                    with gr.Tab("📄 Upload Files"):
                        upload_docset_name = gr.Dropdown(
                            choices=[],
                            type="value",
                            allow_custom_value=False,
                            filterable=True,
                            label="Target DocSet"
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
                        url_docset_name = gr.Dropdown(
                            choices=[],
                            type="value",
                            allow_custom_value=False,
                            filterable=True,
                            label="Target DocSet"
                        )
                        url_input = gr.Textbox(
                            type="text",
                            lines=1,
                            placeholder="https://example.com/docs",
                            label="Website URL"
                        )
                        website_type = gr.Dropdown(
                            choices=[["docs", "docs"], ["github", "github"], ["website", "website"]],
                            value="docs",
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
                        github_docset_name = gr.Dropdown(
                            choices=[],
                            type="value",
                            allow_custom_value=False,
                            filterable=True,
                            label="Target DocSet"
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
                
                # Search section
                gr.Markdown("### 🔍 Search in DocSet")
                search_input = gr.Textbox(
                    type="text",
                    lines=1,
                    placeholder="Search within the selected docset...",
                    label="Search Documents",
                    scale=3
                )
                search_button = gr.Button("Search", variant="secondary", size="lg", scale=1)
                search_results = gr.Textbox(
                    type="text",
                    lines=5,
                    label="Search Results",
                    interactive=False
                )
        
        # Connect sidebar interactions
        def update_docset_lists():
            """Update both DocSet dropdowns with current list"""
            docsets = supabase_docset_manager.get_docsets_dict()
            choices = list(docsets.keys()) if docsets else []
            return gr.Dropdown(choices=choices), gr.Dropdown(choices=choices), gr.Dropdown(choices=choices), gr.Dropdown(choices=choices)
        
        def update_documents(docset_name):
            """Update documents list when DocSet is selected"""
            if not docset_name:
                return gr.Dataframe(value=[]), gr.Textbox(value="")
            
            try:
                # Get documents from Supabase
                docset = supabase_docset_manager.get_docset_by_name(docset_name)
                if not docset:
                    return gr.Dataframe(value=[]), gr.Textbox(value=f"DocSet '{docset_name}' not found")
                
                # Get documents for this docset
                result = supabase_docset_manager.supabase.table("documents").select("*").eq("docset_id", docset["id"]).order("added_date", desc=True).execute()
                
                docset_info = f"DocSet: {docset_name}\nDocuments: {len(result.data)}"
                
                # Convert documents to dataframe format
                doc_rows = []
                for doc in result.data:
                    doc_rows.append([
                        doc['name'],
                        doc['type'],
                        doc.get('url', 'N/A'),
                        doc['added_date']
                    ])
                
                return gr.Dataframe(value=doc_rows), gr.Textbox(value=docset_info)
            except Exception as e:
                return gr.Dataframe(value=[]), gr.Textbox(value=f"Error: {str(e)}")
        
        # Connect events
        create_docset_button.click(
            create_docset_ui, 
            [docset_name_input, docset_desc_input], 
            create_docset_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            upload_docset_name, url_docset_name, github_docset_name, docset_list
        ], api_name=False)
        
        list_docsets_button.click(
            lambda: supabase_docset_manager.list_docsets(), 
            outputs=list_docsets_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            upload_docset_name, url_docset_name, github_docset_name, docset_list
        ], api_name=False)
        
        docset_list.change(
            update_documents,
            docset_list,
            [documents_list, selected_docset_info],
            api_name=False
        )
        
        # File upload
        file_input.upload(
            upload_file_to_docset, 
            [file_input, upload_docset_name], 
            file_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            upload_docset_name, url_docset_name, github_docset_name, docset_list
        ], api_name=False)
        
        # URL upload
        url_button.click(
            add_url_to_docset, 
            [url_input, url_docset_name, website_type], 
            url_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            upload_docset_name, url_docset_name, github_docset_name, docset_list
        ], api_name=False)
        
        # GitHub upload
        github_button.click(
            add_github_repo_to_docset, 
            [github_input, github_docset_name], 
            github_output,
            api_name=False
        ).then(update_docset_lists, outputs=[
            upload_docset_name, url_docset_name, github_docset_name, docset_list
        ], api_name=False)
        
        # Refresh documents
        refresh_docs_button.click(
            update_documents,
            docset_list,
            [documents_list, selected_docset_info],
            api_name=False
        ) 