# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Commands
- **Start Streamlit UI**: `./scripts/run_app.sh` or `streamlit run src/ui/app.py`
- **Start FastAPI backend**: `./scripts/run_api.sh` or `python -m uvicorn src.app.api:app --host 0.0.0.0 --port 8000 --reload`
- **Run data ingestion**: `./scripts/ingest_data.sh` or `python -m src.ingestion.ingest`
- **Run tests**: `pytest tests/`
- **Run single test**: `pytest tests/test_specific.py`

### Virtual Environment
Always activate the virtual environment before running commands:
```bash
source venv/bin/activate
```

Set PYTHONPATH when running modules directly:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Architecture

### Core Components
- **RAG Engine** (`src/core/rag_engine.py`): Handles document retrieval, prompt formatting, and OpenAI API calls
- **Document Service** (`src/core/document_service.py`): Manages document upload, storage, and metadata
- **Database Manager** (`src/core/database.py`): SQLite database operations for document metadata
- **Configuration** (`src/core/config.py`): Centralized settings using Pydantic with environment variable loading

### Data Flow
1. Documents are placed in `data/raw/` or uploaded via API
2. Ingestion service (`src/ingestion/ingest.py`) processes documents and stores vectors in ChromaDB
3. User queries are processed by RAG engine which retrieves relevant chunks and generates answers
4. FastAPI backend (`src/app/api.py`) provides REST endpoints for chat, document management
5. Streamlit UI (`src/ui/app.py`) provides web interface for end users

### Storage Structure
- **ChromaDB**: Vector database stored in `data/chroma/` (persistent)
- **SQLite**: Document metadata in `data/documents.db`
- **File uploads**: Stored in `data/uploads/`
- **Raw documents**: Initially in `data/raw/`

### API Design
FastAPI backend follows RESTful conventions:
- `/chat` - POST for Q&A queries
- `/documents` - GET/POST/DELETE for document management
- `/collections` - GET for ChromaDB collection info
- All responses use consistent Pydantic models (ChatResponse, DocumentResponse, etc.)

## Environment Configuration

Required environment variables (set in `.env`):
- `OPENAI_API_KEY`: OpenAI API key for embeddings and completions
- `OPENAI_MODEL_NAME`: Model name (default: "gpt-4.1-nano")
- `CHROMA_PERSIST_DIRECTORY`: ChromaDB storage path (default: "./data/chroma")
- `DATABASE_URL`: SQLite database URL (default: "sqlite:///./data/documents.db")

## Key Development Patterns

### Configuration Management
All settings are managed through `src/core/config.py` using Pydantic settings with environment variable loading. Use `get_settings()` to access configuration.

### Error Handling
- RAG engine returns structured responses with status indicators
- FastAPI uses HTTP exceptions with proper status codes
- All operations include try-catch blocks with logging

### Document Processing
- Files are validated for type and size before processing
- ChromaDB collections use "documents" as default collection name
- Metadata includes filename, upload timestamp, and content area

### Testing
Test files are in `tests/` directory. Use `pytest` to run all tests or specify individual test files.