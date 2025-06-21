import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def format_date(date_str: str) -> str:
    """Format date string for display."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

def upload_document(file, title: str, description: str, area: str) -> Dict[str, Any]:
    """Upload a document to the API."""
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
    """Get documents from the API."""
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
    """Delete a document from the API."""
    try:
        response = requests.delete(f"{API_BASE_URL}/documents/{document_id}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting document: {str(e)}")
        return False

def get_document_stats() -> Dict[str, Any]:
    """Get document statistics from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/stats")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching stats: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="QnA Bot - Document Management",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 QnA Bot - Document Management")
    st.markdown("---")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["📊 Dashboard", "📤 Upload Documents", "📋 Document List", "⚙️ Settings"]
    )
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📤 Upload Documents":
        show_upload_page()
    elif page == "📋 Document List":
        show_document_list()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    """Show the dashboard with statistics."""
    st.header("📊 Dashboard")
    
    # Get document statistics
    stats_data = get_document_stats()
    
    if stats_data and stats_data.get("status") == "success":
        stats = stats_data.get("stats", {})
        
        # Create metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Documents",
                value=stats.get("total_documents", 0)
            )
        
        with col2:
            st.metric(
                label="Total Size",
                value=format_file_size(stats.get("total_size_bytes", 0))
            )
        
        with col3:
            # Get documents by type
            docs_by_type = stats.get("documents_by_type", {})
            if docs_by_type:
                most_common_type = max(docs_by_type.items(), key=lambda x: x[1])
                st.metric(
                    label="Most Common Type",
                    value=f"{most_common_type[0]} ({most_common_type[1]})"
                )
            else:
                st.metric(label="Most Common Type", value="N/A")
        
        with col4:
            # API health check
            try:
                response = requests.get(f"{API_BASE_URL}/health")
                if response.status_code == 200:
                    st.metric(label="API Status", value="🟢 Healthy")
                else:
                    st.metric(label="API Status", value="🔴 Error")
            except:
                st.metric(label="API Status", value="🔴 Offline")
        
        # Documents by type chart
        st.subheader("Documents by Type")
        if docs_by_type:
            df = pd.DataFrame(list(docs_by_type.items()), columns=["File Type", "Count"])
            st.bar_chart(df.set_index("File Type"))
        else:
            st.info("No documents uploaded yet.")
        
        # Recent activity
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
    """Show the document upload page."""
    st.header("📤 Upload Documents")
    
    with st.form("upload_form"):
        st.subheader("Upload New Document")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'md', 'pdf', 'docx', 'pptx', 'xlsx', 'csv'],
            help="Supported formats: TXT, MD, PDF, DOCX, PPTX, XLSX, CSV"
        )
        
        # Metadata fields
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title (optional)", placeholder="Enter document title")
            area = st.selectbox(
                "Area/Category (optional)",
                ["", "HR", "Finance", "IT", "Operations", "Sales", "Marketing", "Legal", "Other"]
            )
        
        with col2:
            description = st.text_area(
                "Description (optional)", 
                placeholder="Enter document description",
                height=100
            )
        
        # Upload button
        submit_button = st.form_submit_button("Upload Document")
        
        if submit_button and uploaded_file is not None:
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
    """Show the document list page."""
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
        # Initialize pagination in session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        
        # Get current page from session state
        current_page = st.session_state.current_page
        offset = current_page * limit
        
        st.write(f"Page: {current_page + 1}")
    
    with col4:
        if st.button("Refresh"):
            st.rerun()
    
    # Get documents
    area_param = None if area_filter == "All" else area_filter
    docs_data = get_documents(limit=limit, offset=offset, area=area_param)
    
    if docs_data and docs_data.get("status") == "success":
        documents = docs_data.get("documents", [])
        stats = docs_data.get("stats", {})
        
        # Show stats and pagination info
        total_docs = stats.get('total_documents', 0)
        total_pages = (total_docs + limit - 1) // limit if total_docs > 0 else 1
        
        st.info(f"Showing {len(documents)} of {total_docs} documents (Page {current_page + 1} of {total_pages})")
        
        # Pagination controls
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
            # Bulk actions
            st.subheader("Bulk Actions")
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                select_all = st.checkbox("Select All")
            
            with col2:
                if st.button("Delete Selected", type="secondary"):
                    selected_docs = [doc_id for doc_id in st.session_state.get('selected_docs', []) if st.session_state.get(f'select_{doc_id}', False)]
                    if selected_docs:
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
            
            # Initialize selected_docs if not exists
            if 'selected_docs' not in st.session_state:
                st.session_state['selected_docs'] = []
            
            # Create DataFrame for display with checkboxes
            st.subheader("Documents")
            for doc in documents:
                col1, col2, col3, col4, col5 = st.columns([0.5, 2, 1, 1, 1])
                
                with col1:
                    # Handle select all
                    if select_all:
                        st.session_state[f'select_{doc["id"]}'] = True
                    
                    selected = st.checkbox("", key=f'select_{doc["id"]}', value=st.session_state.get(f'select_{doc["id"]}', False))
                    if selected and doc["id"] not in st.session_state['selected_docs']:
                        st.session_state['selected_docs'].append(doc["id"])
                    elif not selected and doc["id"] in st.session_state['selected_docs']:
                        st.session_state['selected_docs'].remove(doc["id"])
                
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
                
                # Show confirmation dialog
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
                
                # Show document details if requested
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
    """Show the settings page."""
    st.header("⚙️ Settings")
    
    st.subheader("API Configuration")
    st.code(f"API Base URL: {API_BASE_URL}")
    
    # Test API connection
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

if __name__ == "__main__":
    main() 