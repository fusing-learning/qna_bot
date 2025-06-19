import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from src.core.config import settings
import logging
import asyncio

# Set up logging
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path(settings.UPLOAD_DIRECTORY)
UPLOAD_DATA_DIR = Path(settings.UPLOAD_DIRECTORY)
SUPPORTED_EXTENSIONS = {".txt", ".md"}  # Basic support for now
CHROMA_PERSIST_DIR = Path(settings.CHROMA_PERSIST_DIRECTORY)

def list_documents(directory: Path = RAW_DATA_DIR) -> List[Path]:
    """List all supported documents in the directory."""
    return [f for f in directory.iterdir() if f.suffix in SUPPORTED_EXTENSIONS and f.is_file()]

def load_document(file_path: Path) -> Dict:
    """Load a document and return its content and metadata."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {
        "filename": file_path.name,
        "filepath": str(file_path),
        "filetype": file_path.suffix,
        "content": content,
    }

def chunk_document(doc: Dict, chunk_size: int = 1000) -> List[Dict]:
    """Split document content into chunks of specified size and add metadata."""
    content = doc["content"]
    chunks = []
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i + chunk_size]
        chunks.append({
            "filename": doc["filename"],
            "filepath": doc["filepath"],
            "filetype": doc["filetype"],
            "chunk_id": i // chunk_size,
            "content": chunk,
        })
    return chunks

def setup_chroma_db():
    """Initialize ChromaDB and return a persistent client."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    print(f"Initializing ChromaDB with persist directory: {CHROMA_PERSIST_DIR}")
    # Use PersistentClient instead of Client with Settings
    return chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))

def store_chunks_in_chroma(chunks: List[Dict], collection_name: str = "documents"):
    """Store document chunks in ChromaDB as vector embeddings."""
    client = setup_chroma_db()
    print(f"Creating or getting collection: {collection_name}")
    collection = client.get_or_create_collection(collection_name)
    print(f"Collection created: {collection_name}")
    
    # Process chunks in batches to avoid potential issues
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        documents = [chunk["content"] for chunk in batch]
        metadatas = [{
            "filename": chunk["filename"],
            "filepath": chunk["filepath"],
            "filetype": chunk["filetype"],
            "chunk_id": chunk["chunk_id"],
            "original_filename": chunk.get("original_filename", chunk["filename"]),
        } for chunk in batch]
        ids = [f"{chunk['filename']}_{chunk['chunk_id']}" for chunk in batch]
        
        print(f"Storing batch {i//batch_size + 1}: {len(batch)} chunks")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
    
    print(f"Stored {len(chunks)} chunks in collection: {collection_name}")
    
    # Verify the data was stored
    count = collection.count()
    print(f"Collection now contains {count} total documents")

def process_single_document(file_path: str, document_id: Optional[int] = None) -> Dict[str, str]:
    """Process a single document file and add it to the vector store."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "status": "error",
                "message": f"File not found: {file_path}"
            }
        
        if path.suffix not in SUPPORTED_EXTENSIONS:
            return {
                "status": "error", 
                "message": f"Unsupported file type: {path.suffix}. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
            }
        
        logger.info(f"Processing document: {file_path}")
        doc = load_document(path)
        
        # Get original filename if document_id is provided
        original_filename = None
        if document_id:
            from src.core.database import db_manager
            document_record = db_manager.get_document(document_id)
            if document_record:
                original_filename = document_record.get("original_filename")
        
        if not doc["content"].strip():
            return {
                "status": "error",
                "message": f"Empty file: {path.name}"
            }
        
        chunks = chunk_document(doc)
        
        # Add document_id and original_filename to chunks if provided
        if document_id:
            for chunk in chunks:
                chunk["document_id"] = document_id
                if original_filename:
                    chunk["original_filename"] = original_filename
        
        store_chunks_in_chroma(chunks)
        
        logger.info(f"Successfully processed document: {path.name} ({len(chunks)} chunks)")
        return {
            "status": "success",
            "message": f"Successfully processed {path.name}",
            "chunks_created": len(chunks)
        }
        
    except Exception as e:
        error_msg = f"Error processing {file_path}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

def process_documents(file_paths: List[str]) -> Dict[str, str]:
    """Process a list of document files and add them to the vector store."""
    try:
        processed_count = 0
        errors = []
        
        for file_path in file_paths:
            result = process_single_document(file_path)
            if result["status"] == "success":
                processed_count += 1
            else:
                errors.append(result["message"])
        
        if processed_count > 0:
            return {
                "status": "success",
                "message": f"Processed {processed_count} documents successfully",
                "processed_count": processed_count,
                "errors": errors
            }
        else:
            return {
                "status": "error",
                "message": "No documents were processed successfully",
                "errors": errors
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in process_documents: {str(e)}"
        }

def main():
    docs = list_documents()
    print(f"Found {len(docs)} supported documents in {RAW_DATA_DIR}.")
    
    if not docs:
        print("No documents found. Make sure you have .txt or .md files in the data/raw directory.")
        return
    
    for doc_path in docs:
        doc = load_document(doc_path)
        if not doc["content"].strip():
            print(f"[WARNING] {doc['filename']} is empty. Skipping.")
            continue
        print(f"Loaded: {doc['filename']} ({doc['filetype']}) - {len(doc['content'])} chars")
        chunks = chunk_document(doc)
        print(f"Chunked into {len(chunks)} chunks.")
        store_chunks_in_chroma(chunks)
        print(f"Stored chunks in ChromaDB.")
    
    print(f"\nIngestion complete! Check the directory: {CHROMA_PERSIST_DIR}")
    print("You should see database files like 'chroma.sqlite3' in that directory.")

if __name__ == "__main__":
    main()