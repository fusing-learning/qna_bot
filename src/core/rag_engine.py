import chromadb
from chromadb.config import Settings
from typing import List, Dict
import os
from pathlib import Path
from openai import OpenAI
from src.core.config import settings

CHROMA_PERSIST_DIR = Path(settings.CHROMA_PERSIST_DIRECTORY)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def setup_chroma_db():
    """Initialize ChromaDB and return a client."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    print(f"Initializing ChromaDB with persist directory: {CHROMA_PERSIST_DIR}")
    return chromadb.Client(Settings(persist_directory=str(CHROMA_PERSIST_DIR), anonymized_telemetry=False))

def list_collections():
    """List all collections in ChromaDB."""
    db = setup_chroma_db()
    collections = db.list_collections()
    print("Available collections:", collections)

def retrieve_relevant_chunks(query: str, collection_name: str = "documents", n_results: int = 3) -> List[Dict]:
    """Retrieve relevant document chunks from ChromaDB based on the query."""
    db = setup_chroma_db()
    collection = db.get_collection(collection_name)
    results = collection.query(query_texts=[query], n_results=n_results)
    return [
        {
            "content": doc,
            "metadata": meta,
        }
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]

def format_prompt(chunks: List[Dict], query: str) -> str:
    """Format the retrieved chunks and query into a prompt for the OpenAI API."""
    context = "\n\n".join([chunk["content"] for chunk in chunks])
    return f"""Context:
{context}

Question: {query}

Answer:"""

def generate_answer(prompt: str) -> str:
    """Call the OpenAI API to generate an answer based on the prompt."""
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def main(query: str) -> str:
    """Main function to retrieve chunks, format the prompt, and generate an answer."""
    chunks = retrieve_relevant_chunks(query)
    prompt = format_prompt(chunks, query)
    answer = generate_answer(prompt)
    return answer

if __name__ == "__main__":
    list_collections()  # List available collections
    query = "What is the annual leave policy?"
    answer = main(query)
    print(f"Query: {query}")
    print(f"Answer: {answer}") 