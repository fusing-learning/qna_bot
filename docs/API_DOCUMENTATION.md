# QnA Bot API Documentation

## Overview
The QnA Bot API provides a RESTful interface for document-based question answering. It uses a RAG (Retrieval-Augmented Generation) system to answer questions based on ingested documents.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
**GET** `/health`

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "message": "QnA Bot API is running"
}
```

### 2. Root Endpoint
**GET** `/`

Same as health check endpoint.

### 3. Chat Endpoint
**POST** `/chat`

Process a question and return an answer based on the document knowledge base.

**Request Body:**
```json
{
  "question": "What is the annual leave policy?",
  "collection_name": "documents"  // Optional, defaults to "documents"
}
```

**Response:**
```json
{
  "answer": "Employees are entitled to 18 days of annual leave per calendar year...",
  "status": "success",
  "sources": ["HR_Policy.md"],
  "error_message": null
}
```

**Error Response:**
```json
{
  "answer": "",
  "status": "error",
  "sources": [],
  "error_message": "Error description"
}
```

### 4. Collections Endpoint
**GET** `/collections`

List available ChromaDB collections.

**Response:**
```json
{
  "collections": ["documents"],
  "count": 1
}
```

## Error Handling

### Validation Errors
- **400 Bad Request**: Invalid input data
- **422 Unprocessable Entity**: Validation errors (e.g., empty question, question too long)

### Server Errors
- **500 Internal Server Error**: Unexpected server errors

## Request/Response Models

### ChatRequest
- `question` (string, required): The question to ask (1-1000 characters)
- `collection_name` (string, optional): ChromaDB collection name (defaults to "documents")

### ChatResponse
- `answer` (string): The generated answer
- `status` (string): "success" or "error"
- `sources` (array): List of source documents used
- `error_message` (string, optional): Error description if status is "error"

### HealthResponse
- `status` (string): "healthy"
- `message` (string): Status message

## Usage Examples

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the working hours?"}'

# List collections
curl http://localhost:8000/collections
```

### Using Python requests
```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/chat",
    json={"question": "What is the annual leave policy?"}
)
result = response.json()
print(result["answer"])
```

## Running the API

1. Start the API server:
   ```bash
   ./scripts/run_api.sh
   ```

2. The API will be available at `http://localhost:8000`

3. Interactive API documentation is available at `http://localhost:8000/docs`

## Notes

- The API requires documents to be ingested before it can answer questions
- Questions are limited to 1000 characters
- The API uses OpenAI's GPT model for answer generation
- Source citations are automatically included in responses 