import chromadb
from typing import List, Dict, Optional
import os
from pathlib import Path
from openai import OpenAI
from src.core.config import settings

# Set environment variable to handle tokenizer warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

CHROMA_PERSIST_DIR = Path(settings.CHROMA_PERSIST_DIRECTORY)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def setup_chroma_db():
    """Initialize ChromaDB and return a persistent client."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    print(f"Initializing ChromaDB with persist directory: {CHROMA_PERSIST_DIR}")
    return chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))

def list_collections():
    """List all collections in ChromaDB."""
    db = setup_chroma_db()
    collections = db.list_collections()
    print("Available collections:", [col.name for col in collections])
    return collections

def retrieve_relevant_chunks(query: str, collection_name: str = "documents", n_results: int = 3) -> List[Dict]:
    """Retrieve relevant document chunks from ChromaDB based on the query."""
    print(f"\nRetrieving chunks for query: {query}")
    db = setup_chroma_db()
    
    try:
        collection = db.get_collection(collection_name)
        count = collection.count()
        print(f"Collection '{collection_name}' contains {count} documents")
        
        if count == 0:
            print(f"Warning: Collection '{collection_name}' is empty!")
            return []
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        print(f"Retrieved {len(results['documents'][0])} relevant chunks")
        
        chunks = [
            {
                "content": doc,
                "metadata": meta,
                "relevance_score": 1 - dist  # Convert distance to relevance score
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
        
        # Print retrieved chunks for debugging
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"Source: {chunk['metadata'].get('original_filename', chunk['metadata'].get('filename', 'Unknown'))}")
            print(f"Relevance: {chunk['relevance_score']:.2f}")
            print(f"Content: {chunk['content'][:200]}...")  # Print first 200 chars
        
        return chunks
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return []

def format_prompt(chunks: List[Dict], query: str) -> str:
    """Format the retrieved chunks and query into a prompt for the OpenAI API."""
    print("\nFormatting prompt...")
    if not chunks:
        return f"""You are a helpful AI assistant. Answer the following question based on the available information.

Question: {query}

Answer: I don't have any relevant information to answer this question. Please try rephrasing your question or ask about a different topic."""
    
    # Sort chunks by relevance score
    chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Format context with source information
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("original_filename", chunk["metadata"].get("filename", "Unknown source"))
        context_parts.append(f"[Source {i}: {source}]\n{chunk['content']}")
    
    context = "\n\n".join(context_parts)
    
    return f"""You are a helpful AI assistant. Answer the following question based on the provided context. Follow these guidelines:

1. If the context doesn't contain enough information to answer the question, say so clearly.
2. Always cite your sources using the format [Source X].
3. If information comes from multiple sources, cite each source separately.
4. Format your answer in a clear, structured way:
   - Start with a direct answer
   - Add relevant details in bullet points if needed
   - End with a summary of sources used

Context:
{context}

Question: {query}

Answer:"""

def generate_answer(prompt: str) -> Dict[str, str]:
    """Call the OpenAI API to generate an answer based on the prompt."""
    print("\nGenerating answer...")
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful AI assistant that provides accurate and concise answers based on the given context.
                    Your answers should be:
                    1. Clear and direct
                    2. Well-structured with bullet points when appropriate
                    3. Properly cited with source references
                    4. Professional and informative"""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return {
            "answer": response.choices[0].message.content,
            "status": "success"
        }
    except Exception as e:
        print(f"Error in generate_answer: {str(e)}")
        return {
            "answer": f"Error generating answer: {str(e)}",
            "status": "error"
        }

def main(query: str) -> Dict[str, str]:
    """Main function to retrieve chunks, format the prompt, and generate an answer."""
    print("\n=== Processing Query ===")
    try:
        chunks = retrieve_relevant_chunks(query)
        prompt = format_prompt(chunks, query)
        result = generate_answer(prompt)
        
        if result["status"] == "success":
            # Extract source numbers from the answer
            import re
            source_numbers = set()
            for match in re.finditer(r'\[Source (\d+)\]', result["answer"]):
                source_numbers.add(int(match.group(1)))
            
            # Only include sources that were actually cited
            cited_sources = []
            for i, chunk in enumerate(chunks, 1):
                if i in source_numbers:
                    cited_sources.append(chunk["metadata"].get("original_filename", chunk["metadata"].get("filename", "Unknown")))
            
            # Format the final output
            formatted_answer = result["answer"].strip()
            if cited_sources:
                formatted_answer += f"\n\nSources: {', '.join(cited_sources)}"
            
            return {
                "answer": formatted_answer,
                "status": "success",
                "sources": cited_sources
            }
        else:
            return result
            
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return {
            "answer": f"Error processing query: {str(e)}",
            "status": "error",
            "sources": []
        }

if __name__ == "__main__":
    print("\n=== ChromaDB Status ===")
    collections = list_collections()
    
    if collections:
        # Test with multiple queries
        test_queries = [
            "What is the annual leave policy?",
            "What are the working hours?",
            "Who is the Head of Operations?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Testing query: {query}")
            result = main(query)
            print("\n=== Final Result ===")
            print(f"Query: {query}")
            print(f"Answer: {result['answer']}")
            print(f"{'='*50}\n")
    else:
        print("No collections found. Run ingest.py first to create the vector database.")