import streamlit as st
import sys
from pathlib import Path
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.core.rag_engine import main as rag_main
from src.core.config import settings

# Configuration for admin API
API_BASE_URL = "http://localhost:8000"

# Set page config (only call once)
st.set_page_config(
    page_title="QnA Bot",
    page_icon="🤖",
    layout="wide"
)

# --- Admin utility functions (from admin.py) ---
def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def format_date(date_str: str) -> str:
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

def upload_document(file, title: str, description: str, area: str) -> Dict[str, Any]:
    try:
        files = {"file": file}
        data = {
            "title": title if title else None,
            "description": description if description else None,
            "area": area if area else None
        }
        response = requests.post(f"{API_BASE_URL}/documents/upload", files=files, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading document: {str(e)}")
        return None

def get_documents(limit: int = 100, offset: int = 0, area: str = None) -> Dict[str, Any]:
    try:
        params = {"limit": limit, "offset": offset}
        if area:
            params["area"] = area
        response = requests.get(f"{API_BASE_URL}/documents", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching documents: {str(e)}")
        return None

def delete_document(document_id: int) -> bool:
    try:
        response = requests.delete(f"{API_BASE_URL}/documents/{document_id}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting document: {str(e)}")
        return False

def get_document_stats() -> Dict[str, Any]:
    try:
        response = requests.get(f"{API_BASE_URL}/documents/stats")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching stats: {str(e)}")
        return None

# --- Chat UI logic (from app.py) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def display_chat_message(role: str, content: str):
    with st.chat_message(role):
        st.markdown(content)

# --- Admin UI sections (from admin.py) ---
def show_dashboard():
    st.header("📊 Dashboard")
    stats_data = get_document_stats()
    if stats_data and stats_data.get("status") == "success":
        stats = stats_data.get("stats", {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Documents", value=stats.get("total_documents", 0))
        with col2:
            st.metric(label="Total Size", value=format_file_size(stats.get("total_size_bytes", 0)))
        with col3:
            docs_by_type = stats.get("documents_by_type", {})
            if docs_by_type:
                most_common_type = max(docs_by_type.items(), key=lambda x: x[1])
                st.metric(label="Most Common Type", value=f"{most_common_type[0]} ({most_common_type[1]})")
            else:
                st.metric(label="Most Common Type", value="N/A")
        with col4:
            try:
                response = requests.get(f"{API_BASE_URL}/health")
                if response.status_code == 200:
                    st.metric(label="API Status", value="🟢 Healthy")
                else:
                    st.metric(label="API Status", value="🔴 Error")
            except:
                st.metric(label="API Status", value="🔴 Offline")
        st.subheader("Documents by Type")
        if docs_by_type:
            df = pd.DataFrame(list(docs_by_type.items()), columns=["File Type", "Count"])
            st.bar_chart(df.set_index("File Type"))
        else:
            st.info("No documents uploaded yet.")
        st.subheader("Recent Documents")
        recent_docs = get_documents(limit=5)
        if recent_docs and recent_docs.get("status") == "success":
            documents = recent_docs.get("documents", [])
            if documents:
                for doc in documents:
                    with st.expander(f"📄 {doc.get('original_filename', 'Unknown')}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**Title:** {doc.get('title', 'N/A')}")
                            st.write(f"**Area:** {doc.get('area', 'N/A')}")
                            st.write(f"**Size:** {format_file_size(doc.get('file_size', 0))}")
                        with col2:
                            st.write(f"**Uploaded:** {format_date(doc.get('uploaded_at', ''))}")
                            if st.button(f"Delete", key=f"delete_{doc['id']}"):
                                if delete_document(doc['id']):
                                    st.success("Document deleted successfully!")
                                    st.rerun()
            else:
                st.info("No documents found.")
    else:
        st.error("Failed to load dashboard data.")

def show_upload_page():
    st.header("📤 Upload Documents")
    with st.form("upload_form"):
        st.subheader("Upload New Document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'md', 'pdf', 'docx', 'pptx', 'xlsx', 'csv'],
            help="Supported formats: TXT, MD, PDF, DOCX, PPTX, XLSX, CSV"
        )
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title (required)", placeholder="Enter document title")
            area = st.selectbox(
                "Area/Category (required)",
                ["", "HR", "Finance", "IT", "Operations", "Sales", "Marketing", "Legal", "Other"]
            )
        with col2:
            description = st.text_area(
                "Description (optional)", 
                placeholder="Enter document description",
                height=100
            )
        submit_button = st.form_submit_button("Upload Document")
        if submit_button and uploaded_file is not None:
            if not title or title.strip() == "":
                st.error("Please enter a Title for the document.")
            elif not area or area.strip() == "":
                st.error("Please select an Area/Category.")
            else:
                with st.spinner("Uploading document..."):
                    result = upload_document(uploaded_file, title, description, area)
                    if result and result.get("status") == "success":
                        st.success("Document uploaded successfully!")
                        st.json(result.get("document", {}))
                    else:
                        st.error("Failed to upload document.")
        elif submit_button and uploaded_file is None:
            st.error("Please select a file to upload.")

def show_document_list():
    st.header("📋 Document List")
    # Filters and Pagination
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        area_filter = st.selectbox(
            "Filter by Area",
            ["All", "HR", "Finance", "IT", "Operations", "Sales", "Marketing", "Legal", "Other"]
        )
    with col2:
        limit = st.selectbox("Documents per page", [10, 25, 50, 100])
    with col3:
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        current_page = st.session_state.current_page
        offset = current_page * limit
        st.write(f"Page: {current_page + 1}")
    with col4:
        if st.button("Refresh"):
            st.rerun()
    area_param = None if area_filter == "All" else area_filter
    docs_data = get_documents(limit=limit, offset=offset, area=area_param)
    if docs_data and docs_data.get("status") == "success":
        documents = docs_data.get("documents", [])
        stats = docs_data.get("stats", {})
        total_docs = stats.get('total_documents', 0)
        total_pages = (total_docs + limit - 1) // limit if total_docs > 0 else 1
        st.info(f"Showing {len(documents)} of {total_docs} documents (Page {current_page + 1} of {total_pages})")
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
            with col1:
                if st.button("⏮️ First", disabled=current_page == 0):
                    st.session_state.current_page = 0
                    st.rerun()
            with col2:
                if st.button("⏪ Previous", disabled=current_page == 0):
                    st.session_state.current_page = max(0, current_page - 1)
                    st.rerun()
            with col3:
                st.write(f"Page {current_page + 1} of {total_pages}")
            with col4:
                if st.button("Next ⏩", disabled=current_page >= total_pages - 1):
                    st.session_state.current_page = min(total_pages - 1, current_page + 1)
                    st.rerun()
            with col5:
                if st.button("Last ⏭️", disabled=current_page >= total_pages - 1):
                    st.session_state.current_page = total_pages - 1
                    st.rerun()
        if documents:
            st.subheader("Bulk Actions")
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                select_all = st.checkbox("Select All", key="select_all")
                if select_all:
                    for doc in documents:
                        if doc["id"] not in st.session_state.get('selected_docs', []):
                            st.session_state.setdefault('selected_docs', []).append(doc["id"])
                else:
                    st.session_state['selected_docs'] = []
            with col2:
                if st.button("Delete Selected", type="secondary"):
                    selected_docs = [doc_id for doc_id in st.session_state.get('selected_docs', []) if st.session_state.get(f'select_{doc_id}', False)]
                    if not selected_docs:
                        st.error("Please select at least one document to delete.")
                    else:
                        st.session_state['confirm_bulk_delete'] = selected_docs
            with col3:
                if st.session_state.get('confirm_bulk_delete'):
                    st.warning(f"Delete {len(st.session_state['confirm_bulk_delete'])} documents?")
                    col3a, col3b = st.columns(2)
                    with col3a:
                        if st.button("Confirm Bulk Delete", type="primary"):
                            deleted_count = 0
                            for doc_id in st.session_state['confirm_bulk_delete']:
                                if delete_document(doc_id):
                                    deleted_count += 1
                            st.success(f"Deleted {deleted_count} documents!")
                            st.session_state['confirm_bulk_delete'] = None
                            st.session_state['selected_docs'] = []
                            st.rerun()
                    with col3b:
                        if st.button("Cancel Bulk Delete"):
                            st.session_state['confirm_bulk_delete'] = None
                            st.rerun()
            if 'selected_docs' not in st.session_state:
                st.session_state['selected_docs'] = []
            st.subheader("Documents")
            for doc in documents:
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 1, 1, 1, 1])
                with col1:
                    # Use a simple callback-based approach
                    def on_checkbox_change():
                        doc_id = doc["id"]
                        checkbox_key = f'select_{doc_id}'
                        if st.session_state.get(checkbox_key, False):
                            if doc_id not in st.session_state.get('selected_docs', []):
                                st.session_state.setdefault('selected_docs', []).append(doc_id)
                        else:
                            if doc_id in st.session_state.get('selected_docs', []):
                                st.session_state['selected_docs'].remove(doc_id)
                    
                    selected = st.checkbox("Select", 
                                         key=f'select_{doc["id"]}', 
                                         value=doc["id"] in st.session_state.get('selected_docs', []),
                                         label_visibility="hidden",
                                         on_change=on_checkbox_change)
                with col2:
                    st.write(f"**{doc.get('original_filename', 'Unknown')}**")
                    st.write(f"_{doc.get('title', 'No title')}_ | {doc.get('area', 'No area')} | {format_file_size(doc.get('file_size', 0))}")
                with col3:
                    st.write(f"**ID:** {doc.get('id')}")
                    st.write(f"**Type:** {doc.get('file_type', 'N/A')}")
                with col4:
                    st.write(f"**Uploaded:**")
                    st.write(f"{format_date(doc.get('uploaded_at', ''))}")
                with col5:
                    if st.button("View", key=f"view_{doc['id']}"):
                        st.session_state[f"show_details_{doc['id']}"] = not st.session_state.get(f"show_details_{doc['id']}", False)
                    if st.button("Delete", key=f"delete_btn_{doc['id']}", type="secondary"):
                        st.session_state[f"confirm_delete_{doc['id']}"] = True
                with col6:
                    if st.button("Edit", key=f"edit_btn_{doc['id']}"):
                        st.session_state[f"edit_doc_{doc['id']}"] = True
                if st.session_state.get(f"edit_doc_{doc['id']}", False):
                    with st.form(f"edit_form_{doc['id']}", clear_on_submit=False):
                        new_title = st.text_input("Edit Title", value=doc.get('title') or "", key=f"edit_title_{doc['id']}")
                        new_description = st.text_area("Edit Description", value=doc.get('description') or "", key=f"edit_desc_{doc['id']}")
                        new_area = st.selectbox("Edit Area/Category (required)", ["HR", "Finance", "IT", "Operations", "Sales", "Marketing", "Legal", "Other"], index=max(0, ["HR", "Finance", "IT", "Operations", "Sales", "Marketing", "Legal", "Other"].index(doc.get('area')) if doc.get('area') in ["HR", "Finance", "IT", "Operations", "Sales", "Marketing", "Legal", "Other"] else 0), key=f"edit_area_{doc['id']}")
                        edit_submit = st.form_submit_button("Save Changes")
                        edit_cancel = st.form_submit_button("Cancel")
                        if edit_submit:
                            if not new_area or new_area.strip() == "":
                                st.error("Area/Category is required.")
                            else:
                                try:
                                    resp = requests.put(f"{API_BASE_URL}/documents/{doc['id']}", json={
                                        "title": new_title,
                                        "description": new_description,
                                        "area": new_area
                                    })
                                    if resp.status_code == 200 and resp.json().get("status") == "success":
                                        st.success("Document updated successfully.")
                                        st.session_state[f"edit_doc_{doc['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to update document: {resp.json().get('message', resp.text)}")
                                except Exception as e:
                                    st.error(f"Error updating document: {str(e)}")
                        if edit_cancel:
                            st.session_state[f"edit_doc_{doc['id']}"] = False
                            st.rerun()
                if st.session_state.get(f"confirm_delete_{doc['id']}", False):
                    st.warning(f"Delete {doc.get('original_filename')}?")
                    col5a, col5b = st.columns(2)
                    with col5a:
                        if st.button("Confirm", key=f"confirm_{doc['id']}", type="primary"):
                            if delete_document(doc['id']):
                                st.success(f"Document deleted!")
                                st.session_state[f"confirm_delete_{doc['id']}"] = False
                                st.rerun()
                    with col5b:
                        if st.button("Cancel", key=f"cancel_{doc['id']}"):
                            st.session_state[f"confirm_delete_{doc['id']}"] = False
                            st.rerun()
                if st.session_state.get(f"show_details_{doc['id']}", False):
                    with st.expander(f"Details for {doc.get('original_filename')}", expanded=True):
                        doc_data = requests.get(f"{API_BASE_URL}/documents/{doc['id']}")
                        if doc_data.status_code == 200:
                            doc_info = doc_data.json()
                            if doc_info.get("status") == "success":
                                doc_details = doc_info.get("document", {})
                                detail_col1, detail_col2 = st.columns(2)
                                with detail_col1:
                                    st.write(f"**Original Filename:** {doc_details.get('original_filename')}")
                                    st.write(f"**Title:** {doc_details.get('title', 'N/A')}")
                                    st.write(f"**Description:** {doc_details.get('description', 'N/A')}")
                                    st.write(f"**Area:** {doc_details.get('area', 'N/A')}")
                                with detail_col2:
                                    st.write(f"**File Size:** {format_file_size(doc_details.get('file_size', 0))}")
                                    st.write(f"**File Type:** {doc_details.get('file_type', 'N/A')}")
                                    st.write(f"**Uploaded:** {format_date(doc_details.get('uploaded_at', ''))}")
                                    st.write(f"**Version:** {doc_details.get('version', 1)}")
                                st.write(f"**File Path:** `{doc_details.get('file_path', 'N/A')}`")
                            else:
                                st.error("Failed to load document details.")
                        else:
                            st.error("Failed to fetch document details.")
                st.divider()
        else:
            st.info("No documents found.")
    else:
        st.error("Failed to load documents.")

def show_settings():
    st.header("⚙️ Settings")
    st.subheader("API Configuration")
    st.code(f"API Base URL: {API_BASE_URL}")
    if st.button("Test API Connection"):
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                st.success("✅ API connection successful!")
                st.json(response.json())
            else:
                st.error("❌ API connection failed!")
        except Exception as e:
            st.error(f"❌ API connection failed: {str(e)}")
    st.subheader("System Information")
    st.info("""
    **Supported File Types:** TXT, MD, PDF, DOCX, PPTX, XLSX, CSV
    
    **File Size Limits:**
    - Individual file: 10MB
    - Batch upload: 100MB
    
    **Storage:** Local file system with SQLite metadata database
    """)

# --- Main unified UI ---
def main():
    st.sidebar.title("QnA Bot Navigation")
    page = st.sidebar.selectbox(
        "Go to...",
        ["Chat", "Dashboard", "Upload Documents", "Document List", "Settings"]
    )
    if page == "Chat":
        st.title("🤖 QnA Bot")
        
        # New Chat button in the sidebar
        if st.sidebar.button("🔄 New Chat", type="primary"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("""
        Welcome to the QnA Bot! Ask questions about your documents, and I'll help you find the answers.
        
        The bot uses advanced AI to:
        - Search through your documents
        - Find relevant information
        - Provide clear, well-cited answers
        """)
        for message in st.session_state.messages:
            display_chat_message(message["role"], message["content"])
        if prompt := st.chat_input("Ask a question about your documents"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            display_chat_message("user", prompt)
            with st.spinner("Thinking..."):
                response = rag_main(prompt)
                if response["status"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"]
                    })
                    display_chat_message("assistant", response["answer"])
                else:
                    error_message = f"Error: {response['answer']}"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })
                    display_chat_message("assistant", error_message)
    elif page == "Dashboard":
        show_dashboard()
    elif page == "Upload Documents":
        show_upload_page()
    elif page == "Document List":
        show_document_list()
    elif page == "Settings":
        show_settings()

if __name__ == "__main__":
    main() 