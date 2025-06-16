import os
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from src.core.config import settings

RAW_DATA_DIR = Path("data/raw")
SUPPORTED_EXTENSIONS = {".txt", ".md"}
# CHROMA_PERSIST_DIR = Path("data/vector_store")
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
    """Initialize ChromaDB and return a client."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    print(f"Initializing ChromaDB with persist directory: {CHROMA_PERSIST_DIR}")
    return chromadb.Client(Settings(persist_directory=str(CHROMA_PERSIST_DIR), anonymized_telemetry=False))

def store_chunks_in_chroma(chunks: List[Dict], collection_name: str = "documents"):
    """Store document chunks in ChromaDB as vector embeddings."""
    client = setup_chroma_db()
    print(f"Creating or getting collection: {collection_name}")
    collection = client.get_or_create_collection(collection_name)
    print(f"Collection created: {collection_name}")
    for chunk in chunks:
        print(f"Storing chunk: {chunk['filename']}_{chunk['chunk_id']}")
        collection.add(
            documents=[chunk["content"]],
            metadatas=[{
                "filename": chunk["filename"],
                "filepath": chunk["filepath"],
                "filetype": chunk["filetype"],
                "chunk_id": chunk["chunk_id"],
            }],
            ids=[f"{chunk['filename']}_{chunk['chunk_id']}"],
        )
    print(f"Stored {len(chunks)} chunks in collection: {collection_name}")

def main():
    docs = list_documents()
    print(f"Found {len(docs)} supported documents in {RAW_DATA_DIR}.")
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

if __name__ == "__main__":
    main() 