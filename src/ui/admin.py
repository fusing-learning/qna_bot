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
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        area_filter = st.selectbox(
            "Filter by Area",
            ["All", "HR", "Finance", "IT", "Operations", "Sales", "Marketing", "Legal", "Other"]
        )
    
    with col2:
        limit = st.selectbox("Documents per page", [10, 25, 50, 100])
    
    with col3:
        if st.button("Refresh"):
            st.rerun()
    
    # Get documents
    area_param = None if area_filter == "All" else area_filter
    docs_data = get_documents(limit=limit, area=area_param)
    
    if docs_data and docs_data.get("status") == "success":
        documents = docs_data.get("documents", [])
        stats = docs_data.get("stats", {})
        
        # Show stats
        st.info(f"Showing {len(documents)} of {stats.get('total_documents', 0)} documents")
        
        if documents:
            # Create DataFrame for display
            df_data = []
            for doc in documents:
                df_data.append({
                    "ID": doc.get("id"),
                    "Filename": doc.get("original_filename", "Unknown"),
                    "Title": doc.get("title", "N/A"),
                    "Area": doc.get("area", "N/A"),
                    "Size": format_file_size(doc.get("file_size", 0)),
                    "Type": doc.get("file_type", "N/A"),
                    "Uploaded": format_date(doc.get("uploaded_at", "")),
                    "Actions": f"View | Delete"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Document actions
            st.subheader("Document Actions")
            doc_id = st.number_input("Enter Document ID", min_value=1, step=1)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("View Document Details"):
                    if doc_id:
                        doc_data = requests.get(f"{API_BASE_URL}/documents/{doc_id}")
                        if doc_data.status_code == 200:
                            doc_info = doc_data.json()
                            if doc_info.get("status") == "success":
                                st.json(doc_info.get("document", {}))
                            else:
                                st.error("Document not found.")
                        else:
                            st.error("Failed to fetch document details.")
            
            with col2:
                if st.button("Delete Document"):
                    if doc_id:
                        if st.checkbox("I confirm I want to delete this document"):
                            if delete_document(doc_id):
                                st.success("Document deleted successfully!")
                                st.rerun()
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