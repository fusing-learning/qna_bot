#!/usr/bin/env python3
"""
Test script to verify document upload and RAG integration.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.document_service import document_service
from src.core.rag_engine import main as rag_main
from src.core.config import settings
from src.core.database import db_manager
from fastapi import UploadFile
from io import BytesIO

def create_test_document():
    """Create a unique test document for upload that won't conflict with existing data."""
    content = """# QnA Bot Testing Guide

This is a TEST DOCUMENT for verifying the QnA bot upload integration.

## Test Information
- Document Type: Integration Test
- Created: For testing upload-to-RAG pipeline
- Purpose: Verify automatic document processing

## Test Scenarios
The QnA bot should be able to answer questions about this test document.

### Scenario 1: Basic Information
This test document contains information about QnA bot testing procedures.

### Scenario 2: Technical Details
The integration test verifies that uploaded documents are automatically processed into the vector store.

### Scenario 3: Search Functionality
Users should be able to search for information in this test document after upload.

## Test Completion
If you can see this content in search results, the integration is working correctly.
"""
    
    # Create a temporary file-like object
    file_content = BytesIO(content.encode('utf-8'))
    file_content.seek(0)
    
    # Create UploadFile object
    upload_file = UploadFile(
        filename="test_integration_document.md",
        file=file_content,
        size=len(content.encode('utf-8'))
    )
    
    return upload_file

async def test_upload_and_query():
    """Test the complete upload -> process -> query pipeline."""
    print("=== Testing Document Upload and RAG Integration ===\n")
    
    try:
        # 1. Create test document
        print("1. Creating unique test document...")
        test_file = create_test_document()
        
        # 2. Upload document
        print("2. Uploading document...")
        upload_result = await document_service.upload_document(
            file=test_file,
            title="QnA Bot Integration Test Document",
            description="A test document for verifying upload-to-RAG integration",
            area="Testing"
        )
        
        print(f"Upload result: {upload_result['message']}")
        if upload_result.get('vector_processing'):
            print(f"Vector processing: {upload_result['vector_processing']['message']}")
        
        # 3. Test RAG query
        print("\n3. Testing RAG query...")
        query = "What is the purpose of the test document?"
        
        rag_result = rag_main(query)
        
        print(f"Query: {query}")
        print(f"Answer: {rag_result['answer']}")
        print(f"Status: {rag_result['status']}")
        if rag_result.get('sources'):
            print(f"Sources: {rag_result['sources']}")
        
        # 4. Test another query
        print("\n4. Testing another query...")
        query2 = "What does the integration test verify?"
        
        rag_result2 = rag_main(query2)
        
        print(f"Query: {query2}")
        print(f"Answer: {rag_result2['answer']}")
        print(f"Status: {rag_result2['status']}")
        if rag_result2.get('sources'):
            print(f"Sources: {rag_result2['sources']}")
        
        # 5. Summary
        print("\n=== Test Summary ===")
        upload_success = upload_result['status'] == 'success'
        processing_success = upload_result.get('vector_processing', {}).get('status') == 'success'
        query_success = rag_result['status'] == 'success' and 'test' in rag_result['answer'].lower()
        query2_success = rag_result2['status'] == 'success' and 'integration' in rag_result2['answer'].lower()
        
        print(f"Document Upload: {'✓' if upload_success else '✗'}")
        print(f"Vector Processing: {'✓' if processing_success else '✗'}")
        print(f"RAG Query 1 (finds test content): {'✓' if query_success else '✗'}")
        print(f"RAG Query 2 (finds integration content): {'✓' if query2_success else '✗'}")
        
        if all([upload_success, processing_success, query_success, query2_success]):
            print("\n🎉 ALL TESTS PASSED! Upload-to-RAG integration is working!")
            return True
        else:
            print("\n❌ Some tests failed. Check the results above.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    
    # Ensure required directories exist
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
    
    # Run the test
    result = asyncio.run(test_upload_and_query())
    sys.exit(0 if result else 1)