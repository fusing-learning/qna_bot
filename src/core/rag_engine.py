import chromadb
from typing import List, Dict
import os
from pathlib import Path
from openai import OpenAI
from src.core.config import settings

CHROMA_PERSIST_DIR = Path(settings.CHROMA_PERSIST_DIRECTORY)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def setup_chroma_db():
    """Initialize ChromaDB and return a persistent client."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    print(f"Initializing ChromaDB with persist directory: {CHROMA_PERSIST_DIR}")
    # Use PersistentClient instead of Client with Settings
    return chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))

def list_collections():
    """List all collections in ChromaDB."""
    db = setup_chroma_db()
    collections = db.list_collections()
    print("Available collections:", [col.name for col in collections])
    return collections

def retrieve_relevant_chunks(query: str, collection_name: str = "documents", n_results: int = 3) -> List[Dict]:
    """Retrieve relevant document chunks from ChromaDB based on the query."""
    db = setup_chroma_db()
    
    try:
        collection = db.get_collection(collection_name)
        count = collection.count()
        print(f"Collection '{collection_name}' contains {count} documents")
        
        if count == 0:
            print(f"Warning: Collection '{collection_name}' is empty!")
            return []
        
        results = collection.query(query_texts=[query], n_results=n_results)
        print(f"Retrieved {len(results['documents'][0])} relevant chunks")
        
        return [
            {
                "content": doc,
                "metadata": meta,
            }
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return []

def format_prompt(chunks: List[Dict], query: str) -> str:
    """Format the retrieved chunks and query into a prompt for the OpenAI API."""
    if not chunks:
        return f"Question: {query}\n\nAnswer: I don't have any relevant information to answer this question."
    
    context = "\n\n".join([chunk["content"] for chunk in chunks])
    return f"""Context:
{context}

Question: {query}

Answer:"""

def generate_answer(prompt: str) -> str:
    """Call the OpenAI API to generate an answer based on the prompt."""
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL_NAME,  # Use the model from settings
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {e}"

def main(query: str) -> str:
    """Main function to retrieve chunks, format the prompt, and generate an answer."""
    chunks = retrieve_relevant_chunks(query)
    prompt = format_prompt(chunks, query)
    answer = generate_answer(prompt)
    return answer

if __name__ == "__main__":
    print("=== ChromaDB Status ===")
    collections = list_collections()  # List available collections
    
    if collections:
        query = "What is the annual leave policy?"
        answer = main(query)
        print(f"\nQuery: {query}")
        print(f"Answer: {answer}")
    else:
        print("No collections found. Run ingest.py first to create the vector database.")