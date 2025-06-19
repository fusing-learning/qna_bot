import os
import shutil
import uuid
import logging
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from src.core.config import settings
from src.core.database import db_manager

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for managing document uploads and processing."""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIRECTORY)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Document service initialized with upload directory: {self.upload_dir}")
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate uploaded file."""
        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            return False, f"File size {file.size} exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        
        # Check file type
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            return False, f"File type {file_extension} is not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        
        # Check if filename is provided
        if not file.filename:
            return False, "Filename is required"
        
        return True, "File is valid"
    
    def save_uploaded_file(self, file: UploadFile) -> str:
        """Save uploaded file to disk."""
        # Generate unique filename to avoid conflicts
        original_filename = file.filename
        file_extension = Path(original_filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create file path
        file_path = self.upload_dir / unique_filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"Saved uploaded file: {original_filename} -> {file_path}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"Error saving file {original_filename}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
    
    async def upload_document(self, 
                            file: UploadFile,
                            title: str = None,
                            description: str = None,
                            area: str = None):
        """Upload and process a document."""
        try:
            # Validate file
            is_valid, error_message = self.validate_file(file)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
            
            # Save file
            file_path = self.save_uploaded_file(file)
            file_size = os.path.getsize(file_path)
            file_extension = Path(file.filename).suffix.lower()
            
            # Add to database
            document_id = db_manager.add_document(
                filename=Path(file_path).name,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_extension,
                title=title,
                description=description,
                area=area
            )
            
            # Get the created document
            document = db_manager.get_document(document_id)
            
            return {
                "status": "success",
                "document": document,
                "message": "Document uploaded successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in upload_document: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    
    def list_documents(self, limit: int = 100, offset: int = 0, area: str = None):
        """List documents with optional filtering."""
        try:
            documents = db_manager.list_documents(limit=limit, offset=offset, area=area)
            stats = db_manager.get_document_stats()
            
            return {
                "status": "success",
                "documents": documents,
                "stats": stats,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": stats["total_documents"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error listing documents: {str(e)}"
            )
    
    def get_document(self, document_id: int):
        """Get a specific document."""
        try:
            document = db_manager.get_document(document_id)
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document with ID {document_id} not found"
                )
            
            # Get document versions
            versions = db_manager.get_document_versions(document_id)
            
            return {
                "status": "success",
                "document": document,
                "versions": versions
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting document: {str(e)}"
            )
    
    def delete_document(self, document_id: int):
        """Delete a document (soft delete)."""
        try:
            # Check if document exists
            document = db_manager.get_document(document_id)
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document with ID {document_id} not found"
                )
            
            # Soft delete document
            success = db_manager.delete_document(document_id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to delete document"
                )
            
            return {
                "status": "success",
                "message": f"Document {document_id} deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting document: {str(e)}"
            )
    
    def get_document_stats(self):
        """Get document statistics."""
        try:
            stats = db_manager.get_document_stats()
            return {
                "status": "success",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting document stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting document stats: {str(e)}"
            )

# Global document service instance
document_service = DocumentService() 