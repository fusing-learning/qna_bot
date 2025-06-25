from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from src.core.rag_engine import main as rag_main
from src.core.document_service import document_service
from src.core.database import db_manager
from src.ingestion.ingest import process_single_document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QnA Bot API",
    description="API for document-based question answering",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    collection_name: Optional[str] = Field(default="documents", description="ChromaDB collection name")

class ChatResponse(BaseModel):
    answer: str
    status: str
    sources: List[str] = []
    error_message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

class DocumentResponse(BaseModel):
    status: str
    document: Optional[dict] = None
    documents: Optional[List[dict]] = None
    stats: Optional[dict] = None
    message: Optional[str] = None

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    area: Optional[str] = None

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="QnA Bot API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="QnA Bot API is running"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a question and return an answer based on the document knowledge base.
    
    Args:
        request: ChatRequest containing the question and optional collection name
        
    Returns:
        ChatResponse with the answer, status, and sources
    """
    try:
        logger.info(f"Processing chat request: {request.question[:100]}...")
        
        # Validate input
        if not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        # Process the question using the RAG engine
        result = rag_main(request.question)
        
        logger.info(f"RAG processing completed with status: {result['status']}")
        
        if result["status"] == "success":
            return ChatResponse(
                answer=result["answer"],
                status="success",
                sources=result.get("sources", [])
            )
        else:
            # RAG engine returned an error
            return ChatResponse(
                answer="",
                status="error",
                sources=[],
                error_message=result["answer"]
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/collections")
async def list_collections():
    """
    List available ChromaDB collections.
    
    Returns:
        List of collection names
    """
    try:
        from src.core.rag_engine import list_collections
        collections = list_collections()
        return {
            "collections": [col.name for col in collections],
            "count": len(collections)
        }
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing collections: {str(e)}"
        )

# Document Management Endpoints
@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    area: Optional[str] = Form(None)
):
    """
    Upload a document to the knowledge base.
    
    Args:
        file: The document file to upload
        title: Optional title for the document
        description: Optional description of the document
        area: Optional area/category for the document
        
    Returns:
        DocumentResponse with upload status and document info
    """
    try:
        # Change: Make Title a required field for document upload (Test 3b)
        if not title or title.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required for document upload."
            )
        logger.info(f"Processing document upload: {file.filename}")
        result = await document_service.upload_document(
            file=file,
            title=title,
            description=description,
            area=area
        )
        return DocumentResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/documents", response_model=DocumentResponse)
async def list_documents(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    area: Optional[str] = Query(None)
):
    """
    List documents in the knowledge base.
    
    Args:
        limit: Maximum number of documents to return
        offset: Number of documents to skip
        area: Optional filter by area/category
        
    Returns:
        DocumentResponse with list of documents and stats
    """
    try:
        result = document_service.list_documents(
            limit=limit,
            offset=offset,
            area=area
        )
        
        return DocumentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in list_documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/documents/stats", response_model=DocumentResponse)
async def get_document_stats():
    """
    Get document statistics.
    
    Returns:
        DocumentResponse with document statistics
    """
    try:
        result = document_service.get_document_stats()
        return DocumentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_document_stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int):
    """
    Get a specific document by ID.
    
    Args:
        document_id: The ID of the document to retrieve
        
    Returns:
        DocumentResponse with document details
    """
    try:
        result = document_service.get_document(document_id)
        return DocumentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.delete("/documents/{document_id}", response_model=DocumentResponse)
async def delete_document(document_id: int):
    """
    Delete a document (soft delete).
    
    Args:
        document_id: The ID of the document to delete
        
    Returns:
        DocumentResponse with deletion status
    """
    try:
        result = document_service.delete_document(document_id)
        return DocumentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/documents/{document_id}/process", response_model=DocumentResponse)
async def process_document(document_id: int):
    """
    Process a document for vector store indexing.
    
    Args:
        document_id: The ID of the document to process
        
    Returns:
        DocumentResponse with processing status
    """
    try:
        # Get document details
        document = db_manager.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Process document for vector store
        processing_result = process_single_document(document["file_path"], document_id)
        
        return DocumentResponse(
            status=processing_result["status"],
            message=processing_result["message"],
            document=document
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    update: DocumentUpdateRequest = Body(...)
):
    """
    Update document metadata (title, description, area).
    """
    try:
        result = document_service.update_document(
            document_id=document_id,
            title=update.title,
            description=update.description,
            area=update.area
        )
        return DocumentResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return {
        "status": "error",
        "error_code": exc.status_code,
        "error_message": exc.detail
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}")
    return {
        "status": "error",
        "error_code": 500,
        "error_message": "Internal server error"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 