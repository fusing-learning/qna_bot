import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from src.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for document metadata."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_URL.replace("sqlite:///", "")
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    area TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    version INTEGER DEFAULT 1,
                    UNIQUE(filename, version)
                )
            """)
            
            # Create document versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    version INTEGER,
                    file_path TEXT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def add_document(self, 
                    filename: str,
                    original_filename: str,
                    file_path: str,
                    file_size: int,
                    file_type: str,
                    title: Optional[str] = None,
                    description: Optional[str] = None,
                    area: Optional[str] = None) -> int:
        """Add a new document to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO documents 
                (filename, original_filename, file_path, file_size, file_type, title, description, area)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (filename, original_filename, file_path, file_size, file_type, title, description, area))
            
            document_id = cursor.lastrowid
            
            # Add to versions table
            cursor.execute("""
                INSERT INTO document_versions (document_id, version, file_path)
                VALUES (?, ?, ?)
            """, (document_id, 1, file_path))
            
            conn.commit()
            logger.info(f"Added document: {filename} with ID: {document_id}")
            return document_id
    
    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, original_filename, file_path, file_size, file_type,
                       title, description, area, uploaded_at, is_deleted, version
                FROM documents 
                WHERE id = ? AND is_deleted = FALSE
            """, (document_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'filename': row[1],
                    'original_filename': row[2],
                    'file_path': row[3],
                    'file_size': row[4],
                    'file_type': row[5],
                    'title': row[6],
                    'description': row[7],
                    'area': row[8],
                    'uploaded_at': row[9],
                    'is_deleted': bool(row[10]),
                    'version': row[11]
                }
            return None
    
    def list_documents(self, 
                      limit: int = 100, 
                      offset: int = 0,
                      area: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all documents with optional filtering."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT id, filename, original_filename, file_path, file_size, file_type,
                       title, description, area, uploaded_at, is_deleted, version
                FROM documents 
                WHERE is_deleted = FALSE
            """
            params = []
            
            if area:
                query += " AND area = ?"
                params.append(area)
            
            query += " ORDER BY uploaded_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'filename': row[1],
                'original_filename': row[2],
                'file_path': row[3],
                'file_size': row[4],
                'file_type': row[5],
                'title': row[6],
                'description': row[7],
                'area': row[8],
                'uploaded_at': row[9],
                'is_deleted': bool(row[10]),
                'version': row[11]
            } for row in rows]
    
    def update_document(self, 
                       document_id: int,
                       title: Optional[str] = None,
                       description: Optional[str] = None,
                       area: Optional[str] = None) -> bool:
        """Update document metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if area is not None:
                updates.append("area = ?")
                params.append(area)
            
            if not updates:
                return False
            
            query = f"UPDATE documents SET {', '.join(updates)} WHERE id = ?"
            params.append(document_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
    
    def delete_document(self, document_id: int) -> bool:
        """Soft delete a document (mark as deleted)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE documents SET is_deleted = TRUE WHERE id = ?
            """, (document_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def get_document_versions(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all versions of a document."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, document_id, version, file_path, uploaded_at
                FROM document_versions 
                WHERE document_id = ?
                ORDER BY version DESC
            """, (document_id,))
            
            rows = cursor.fetchall()
            return [{
                'id': row[0],
                'document_id': row[1],
                'version': row[2],
                'file_path': row[3],
                'uploaded_at': row[4]
            } for row in rows]
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get document statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total documents
            cursor.execute("SELECT COUNT(*) FROM documents WHERE is_deleted = FALSE")
            total_documents = cursor.fetchone()[0]
            
            # Documents by type
            cursor.execute("""
                SELECT file_type, COUNT(*) 
                FROM documents 
                WHERE is_deleted = FALSE 
                GROUP BY file_type
            """)
            documents_by_type = dict(cursor.fetchall())
            
            # Total file size
            cursor.execute("""
                SELECT SUM(file_size) 
                FROM documents 
                WHERE is_deleted = FALSE
            """)
            total_size = cursor.fetchone()[0] or 0
            
            return {
                'total_documents': total_documents,
                'documents_by_type': documents_by_type,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }

# Global database manager instance
db_manager = DatabaseManager() 