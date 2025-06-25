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

# Define relevance threshold
RELEVANCE_THRESHOLD = 0.3  # Adjust based on your needs

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

def retrieve_relevant_chunks(query: str, collection_name: str = "documents", n_results: int = 5) -> List[Dict]:
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
        
        # Retrieve more results initially to filter by relevance
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, count),  # Don't request more than available
            include=["documents", "metadatas", "distances"]
        )
        print(f"Retrieved {len(results['documents'][0])} chunks")
        
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            relevance_score = 1 - dist  # Convert distance to relevance score
            
            # Only include chunks above relevance threshold
            if relevance_score >= RELEVANCE_THRESHOLD:
                chunks.append({
                    "content": doc,
                    "metadata": meta,
                    "relevance_score": relevance_score
                })
        
        print(f"Filtered to {len(chunks)} relevant chunks (threshold: {RELEVANCE_THRESHOLD})")
        
        # Print relevant chunks for debugging
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"Source: {chunk['metadata'].get('original_filename', chunk['metadata'].get('filename', 'Unknown'))}")
            print(f"Relevance: {chunk['relevance_score']:.2f}")
            print(f"Content: {chunk['content'][:200]}...")
        
        return chunks
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return []

def format_prompt(chunks: List[Dict], query: str) -> str:
    """Format the retrieved chunks and query into a prompt for the OpenAI API."""
    print("\nFormatting prompt...")
    
    # Sort chunks by relevance score
    chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Format context with source information
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("original_filename", chunk["metadata"].get("filename", "Unknown source"))
        context_parts.append(f"[Source {i}: {source}]\n{chunk['content']}")
    
    context = "\n\n".join(context_parts)
    
    return f"""You are a helpful AI assistant. Answer the following question based on the provided context. Follow these guidelines:

1. If the context doesn't contain enough information to answer the question, say so clearly WITHOUT mentioning sources or source numbers.
2. Do NOT include any source references, citations, or mentions of documents in your answer.
3. Do NOT add "Summary of sources used" or any source-related text.
4. Provide ONLY a clear, direct answer based on the available information.
5. Format your answer in a clear, structured way with bullet points when appropriate.

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
                    3. Professional and informative
                    4. Based only on the provided context"""
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
        # Step 1: Retrieve chunks with relevance filtering
        chunks = retrieve_relevant_chunks(query)
        
        # Step 2: Check if we have any relevant chunks
        if not chunks:
            print("No relevant chunks found. Skipping API call to save costs.")
            return {
                "answer": "I don't have any relevant information to answer this question. Please try rephrasing your question or ask about a different topic.",
                "status": "success",
                "sources": []
            }
        
        # Step 3: Only call API if we have relevant chunks
        prompt = format_prompt(chunks, query)
        result = generate_answer(prompt)
        
        if result["status"] == "success":
            answer = result["answer"].strip()
            
            # Clean up any AI-generated source references
            import re
            answer = re.sub(r'Summary of sources used:.*?\n\n', '', answer, flags=re.DOTALL)
            answer = re.sub(r'Sources:.*?\n\n', '', answer, flags=re.DOTALL)
            answer = re.sub(r'\[Source \d+[^\]]*\]', '', answer)
            answer = answer.strip()
            
            # Check if the answer indicates no relevant information was found
            answer_lower = answer.lower()
            no_info_patterns = [
                r'does not.*(?:contain|include|provide|have).*(?:information|definition|explanation)',
                r'do not.*(?:contain|include|provide|have).*(?:information|definition|explanation)', 
                r'(?:no|not enough|insufficient).*information',
                r'cannot.*(?:answer|provide|find)',
                r'unable to.*(?:answer|provide|find)',
                r'not.*(?:available|provided|found).*(?:in|within).*(?:context|document)',
                r'context.*does not.*(?:contain|include|provide)',
                r'provided.*context.*does not'
            ]
            
            has_no_info = any(re.search(pattern, answer_lower) for pattern in no_info_patterns)
            has_relevant_info = not has_no_info
            
            # Only add sources if we have relevant information
            if has_relevant_info:
                # Get unique sources from chunks (already filtered by relevance)
                sources = []
                seen_sources = set()
                for chunk in chunks:
                    # Prefer title, fallback to filename
                    title = chunk["metadata"].get("title")
                    if title and title.strip():
                        source_name = title
                    else:
                        source_name = chunk["metadata"].get("original_filename", 
                                                          chunk["metadata"].get("filename", "Unknown"))
                    
                    if source_name not in seen_sources:
                        sources.append(source_name)
                        seen_sources.add(source_name)
                
                if sources:
                    formatted_answer = f"{answer}\n\nSources: {', '.join(sources)}"
                    return {
                        "answer": formatted_answer,
                        "status": "success",
                        "sources": sources
                    }
            
            # Return answer without sources
            return {
                "answer": answer,
                "status": "success",
                "sources": []
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
            "Who is the Head of Operations?",
            "What is the meaning of quantum physics?"  # Likely not in HR docs
        ]
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Testing query: {query}")
            result = main(query)
            print("\n=== Final Result ===")
            print(f"Query: {query}")
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result.get('sources', [])}")
            print(f"{'='*50}\n")
    else:
        print("No collections found. Run ingest.py first to create the vector database.")