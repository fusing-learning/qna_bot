# QnA Bot

A question-answering chatbot that provides answers based on internal documents.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

4. Run tests:
   ```bash
   pytest tests/
   ```

5. To start the servers:
   ```bash
   bash scripts/run_api.sh # To activate the API
   bash scripts/run_app.sh # To activate the unified web interface (chat + admin)
   ```

## Project Structure

```
qna_bot/
├── data/
│   ├── raw/              # Place source documents here
│   └── vector_store/     # Vector database storage
├── scripts/
│   └── ingest_data.sh    # Data ingestion script
├── src/
│   ├── app/             # FastAPI application
│   ├── core/            # Core functionality
│   ├── ingestion/       # Document processing
│   └── ui/              # Streamlit interface (unified chat & admin)
└── tests/               # Test files
```

## Usage

- The unified Streamlit web interface provides both the chat (Q&A) and document management (admin) features.
- Use the sidebar navigation to switch between Chat, Dashboard, Upload Documents, Document List, and Settings.
- All document upload, listing, and management features are now accessible from the same interface as the chat.

## Development

- The project uses FastAPI for the backend API
- Streamlit for the web interface
- LangChain for RAG implementation
- ChromaDB for vector storage

## Testing

Run the test suite:
```bash
pytest tests/
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL_NAME`: Model to use (gpt-4.1-mini or gpt-4.1-nano)
- `APP_ENV`: Environment (development, testing, production)
- `DEBUG`: Debug mode (True/False)
- `CHROMA_PERSIST_DIRECTORY`: Vector store directory
- `API_HOST`: API host address
- `API_PORT`: API port number 