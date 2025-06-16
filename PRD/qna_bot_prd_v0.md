## 1. Introduction

This document outlines the requirements for a new Question & Answering (Q&A) chatbot. The primary goal of this project is to provide users with a reliable and accurate way to get answers to their questions based **exclusively** on a pre-defined set of internal documents. The chatbot will feature a simple web interface, maintain conversational context for follow-up questions, and provide sources for its answers to ensure transparency and trust.

## 2. Problem Statement & Goals

**Problem:** Users (e.g. employees) currently struggle to find accurate information quickly within our internal wiki, which includes extensive and varied collection of documents. Manually searching through them is time-consuming and inefficient.

**Goals:**
- **User Goal:** To receive quick, accurate, and citable answers to questions about our internal knowledge base.
- **Business Goal:** To reduce the time spent by users searching for information and decrease the number of repetitive questions sent to support teams.
- **Technical Goal:** To build a scalable and maintainable AI system that can ingest various document types and provide answers strictly grounded in the provided context, without hallucination.

## 3. User Personas
- **End-User (e.g. employee):** Needs to ask specific questions related to internal policies. Values speed, accuracy, and knowing the source of the information. Is not technically savvy.
- **Administrator:** Responsible for curating and updating the knowledge base documents that the chatbot uses. Needs a straightforward process to add, update, or remove documents.

## 4. Functional Requirements
### 4.1. Web-based Chat Interface
A clean, minimalist web interface for user interaction.
- **FR-1.1:** A main chat window to display the ongoing conversation and history.
- **FR-1.2:** A text input field for the user to type and submit their questions.    
- **FR-1.3:** The chatbot's response must be displayed clearly, formatted in a user-friendly way, eg with bold / italic if applicable, or bullet points instead of jumbled texts.
- **FR-1.4:** Each answer must be accompanied by the relevant source documents that were used to generate the answer. The source should be clearly identifiable (e.g., document name and link to open the document, page number if applicable). The source should be clearly separated from the answer, eg using footnote.

### 4.2. Core Q&A Engine
The engine that generates answers based on user queries and the knowledge base.
- **FR-2.1:** The chatbot's responses must be **strictly grounded** in the information available in the ingested document set. The model should not use any external knowledge or make up information (hallucinate).
- **FR-2.2:** The system must identify the most relevant chunks of text from the source documents to formulate an answer.
- **FR-2.3:** If a user's question cannot be answered from the provided documents, the chatbot must respond with a polite and clear message stating that it does not have the information. This message should also provide a clear call-to-action, such as "I cannot find an answer to that in my knowledge base. For further assistance, please contact the [Relevant Team Name] at [email@company.com]." The call-to-action can be maintained in one of the datasets.
- **FR-2.4 (Conversational Context):** The chatbot must maintain the context of the current conversation. Users should be able to ask follow-up questions that refer to the previous turns in the same session (e.g., "Can you elaborate on the second point?").

### 4.3. Data Ingestion & Processing
A backend pipeline to load, parse, and prepare documents for the Q&A engine.
- **FR-3.1:** The system must be able to load and parse documents from a specified directory.
- **FR-3.2:** The ingestion pipeline must support the following common document formats:
    - Plain Text (.txt)
    - Markdown (.md)        
    - PDF (.pdf)   
    - Microsoft Word (.docx)
    - Microsoft PowerPoint (.pptx)
    - Microsoft Excel (.xlsx)
    - Comma-Separated Values (.csv)
- **FR-3.3:** During ingestion, documents must be processed into smaller, searchable text chunks (e.g., by paragraph or a fixed token size).    
- **FR-3.4:** These text chunks must be converted into vector embeddings and stored in a vector database for efficient semantic search. Metadata (e.g., source document name, page number) must be stored alongside each chunk.

### 4.4 Web-based Admin Panel
A clean web interface for the admin to manage the documents for the Q&A engine and API setting.
- FR-4.1: A main window to display all the documents that the Q&A engine is currently using.
- FR-4.2: An upload button for admin to upload new documents into the repository for the Q&A engine to refer to. When clicking on the button, an interface should appear for the admin to choose a file to upload or drag & drop a file to upload the file. There should also be Title, Description, and Areas fields for admin to indicate what the document's title, to describe in more details what it includes, and which area does the document concern (eg HR, Finance etc)
- FR-4.3: A delete button next to each listed document to delete the document. There should be a user confirmation box prompted to confirm that user's action as the deletion would be non-reversible.
- FR-4.4: A checkbox next to each listed document so that user could perform bulk actions on the documents if needed.
- FR-4.5: A secure API key field for admin to input the API key. This field should be treated like a password field with the relevant security feature.
- FR-4.6: A free-text field for admin to input the OpenAI API model. (Note: As this is a demo to start with, we would use only OpenAI API)

### 4.5 Document Management Specifications
- FR-5.1: Maximum file size limits:
  - Individual file size: 10MB per file
  - Total upload size: 100MB per batch
- FR-5.2: Document versioning system:
  - Keep the last 3 versions of each document
  - Store version metadata (timestamp, who updated it)
  - Archive old versions but keep them accessible for reference
- FR-5.3: Document deletion handling:
  - Mark documents as "deleted" in the database but maintain in vector store for 24-48 hours
  - Show warning message for active sessions referencing deleted documents
  - Remove from vector store after grace period

### 4.6 Security & Access Control
- FR-6.1: Rate limiting:
  - 60 requests per minute per IP address
  - 1000 requests per hour per IP address
- FR-6.2: Admin authentication system (to be implemented in future versions)

### 4.7 Error Handling & Edge Cases
- FR-7.1: OpenAI API error handling:
  - Implement 3-retry mechanism with exponential backoff
  - Show user-friendly error messages
  - Log errors for admin review
- FR-7.2: Document upload error handling:
  - Validate file types and sizes before processing
  - Show clear error messages for invalid files
  - Provide upload summary (successful/failed)
- FR-7.3: Input limitations:
  - Maximum question length: 500 characters
  - Maximum chat input field length: 1000 characters

### 4.8 Performance Specifications
- FR-8.1: Request timeout: 30 seconds for the entire request
- FR-8.2: Analytics tracking (to be implemented in future versions):
  - Track most common questions
  - Monitor system performance
  - User feedback collection

### 4.9 User Experience Features
- FR-9.1: User feedback mechanism (to be implemented in future versions):
  - Allow users to rate answer helpfulness
  - Collect feedback on answer quality
- FR-9.2: Chat history export (to be implemented in future versions)

## 5. Non-Functional Requirements
- **NFR-1 (Performance):** The P95 (95th percentile) latency for a response should be under 8 seconds from the moment the user submits a question.    
- **NFR-2 (Scalability):** The system should be designed to handle at least 100 concurrent users. The data ingestion pipeline should be able to process a knowledge base of at least 1,000 documents / 1 GB of text data.
- **NFR-3 (Maintainability):** The process of updating the knowledge base (re-indexing documents) should be automated via a script. The core components (API, LLM, Vector DB) should be modular to allow for future upgrades.

## 6. Acceptance Criteria

|            |                                                                                                                   |                                                                       |                                                                                                                                                                                                                 |
| ---------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Feature ID | Given (Precondition)                                                                                              | When (Action)                                                         | Then (Expected Outcome)                                                                                                                                                                                         |
| **AC-1.1** | The user opens the chatbot's web page.                                                                            | The user views the interface.                                         | The page displays a chat history window, a text input box, and a "Send" button.                                                                                                                                 |
| **AC-1.2** | The knowledge base contains a document policy.pdf that states "Annual leave is 25 days."                          | The user asks, "How many days of annual leave do I get?"              | The chatbot responds with an answer like "You are entitled to 25 days of annual leave." and lists policy.pdf as the source.                                                                                     |
| **AC-1.3** | The chatbot has provided an answer with sources.                                                                  | The user inspects the response.                                       | The answer text is clearly distinct from the source list. The source list contains clickable or easily identifiable document names (e.g., "Source: policy.pdf, page 3").                                        |
| **AC-2.1** | The knowledge base contains no information about the moon's distance from Earth.                                  | The user asks, "How far is the moon from the Earth?"                  | The chatbot responds with a pre-defined message like "I cannot find an answer to that in my knowledge base. For further assistance, please contact the [Relevant Team]." and does not provide a factual answer. |
| **AC-2.2** | The user has asked, "What are our main products?" and the chatbot has answered "We sell Product A and Product B." | The user asks the follow-up question, "Tell me more about Product A." | The chatbot provides details specifically about Product A, using the context from the first question to understand the pronoun "it" or the specific noun.                                                       |
| **AC-3.1** | A directory contains files: guide.docx, data.xlsx, spec.pdf, notes.txt, project.md, slides.pptx, users.csv.       | The administrator runs the ingestion script on that directory.        | The script completes without errors. The vector database contains text chunks and metadata from all seven documents. The system is ready to answer questions about their content.                               |
| **AC-3.2** | An Excel file data.xlsx has a table with a row "Q4 Revenue" and a value "$500,000".                               | The user asks, "What was the revenue for Q4?"                         | The chatbot correctly extracts and provides the answer "$500,000" and cites data.xlsx as the source.                                                                                                            |
## 7. Proposed Tech Stack

This stack is chosen to be Python-centric, leveraging the rich ecosystem of AI/ML libraries while ensuring a scalable and modern architecture.

|   |   |   |
|---|---|---|
|Component|Primary Recommendation|Alternatives|
|**Backend API Framework**|**FastAPI**|Flask|
|**AI/RAG Orchestration**|**LangChain**|LlamaIndex|
|**LLM (Generation)**|**OpenAI gpt-4o or gpt-3.5-turbo**|Anthropic Claude 3, Open-source (Mixtral)|
|**Embedding Model**|**OpenAI text-embedding-3-small**|Open-source (e.g., BAAI/bge-base-en-v1.5)|
|**Vector Store**|**ChromaDB**|FAISS, Pinecone, Weaviate|
|**Frontend UI (Initial)**|**Streamlit**|Gradio|
|**Environment Mgmt**|**Poetry** or **venv** with requirements.txt|Conda|

---

### **Rationale for Tech Stack Choices:**

- **FastAPI (Backend):** It's an asynchronous, high-performance Python framework perfect for building APIs that serve ML models. Its native async support is critical for handling concurrent users (NFR-2) and I/O-bound operations like calling an LLM API. Automatic data validation with Pydantic and API documentation (Swagger UI) significantly speeds up development.
    
- **LangChain (AI Orchestration):** This is the industry-standard framework for building LLM applications. It directly addresses key functional requirements:
    
    - **FR-3.2 (Document Loaders):** LangChain has a comprehensive suite of loaders for all specified document types (PDF, DOCX, XLSX, PPTX, etc.), saving significant development time.
        
    - **FR-3.3 (Text Splitting):** It provides robust text splitters (e.g., RecursiveCharacterTextSplitter) to chunk documents effectively.
        
    - **FR-2.4 (Conversational Context):** It has built-in memory modules (ConversationBufferMemory) to manage chat history seamlessly.
        
- **OpenAI Models (LLM & Embeddings):** Using OpenAI's APIs is the fastest way to achieve a high-quality, reliable result.
    
    - gpt-4.1 is exceptionally good at following the strict instructions required for a grounded response (FR-2.1), such as "Only use the provided context to answer the question." Can use gpt-4.1-nano or gpt-4.1-mini as a start for cost-saving purpose.
        
    - text-embedding-3-small provides a great balance of high performance and low cost for creating vector embeddings (FR-3.4).
        
- **ChromaDB (Vector Store):** It's a powerful, open-source vector database that is extremely easy to set up for local development and can be run in a client/server mode for production. It integrates seamlessly with LangChain and can persist the database to disk, making it ideal for a project starting from scratch.
    
- **Streamlit (Frontend):** For V1, Streamlit is the perfect choice. It allows an AI engineer to build a functional, interactive chat interface (FR-1.1, FR-1.2) in pure Python with minimal effort. This accelerates the feedback loop and allows for focus on the core AI engine. A more complex frontend (e.g., React) can be built later if needed.
    

## 8. Proposed Project Structure

This structure separates concerns (ingestion, application logic, UI) and promotes maintainability (NFR-3).

```
qna-chatbot/
├── .env                  # Store API keys and configurations (DO NOT COMMIT)
├── .env.example          # Example environment file
├── .gitignore            # Standard git ignore file
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
│
├── data/
│   ├── raw/              # Place all source documents here (pdf, docx, etc.)
│   └── vector_store/     # Persisted ChromaDB vector database will be stored here
│
├── scripts/
│   └── ingest_data.sh    # A simple shell script to run the ingestion process
│
└── src/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py       # FastAPI application entrypoint (API endpoints)
    │   ├── schemas.py    # Pydantic models for API request/response validation
    │   └── api.py        # API router logic
    │
    ├── core/
    │   ├── __init__.py
    │   ├── config.py     # Loads configuration from environment variables
    │   ├── rag_engine.py # The core RAG logic (retrieve, prompt, generate)
    │   └── prompts.py    # Central location for all prompt templates
    │
    ├── ingestion/
    │   ├── __init__.py
    │   └── ingest.py     # Main script for loading, splitting, and embedding documents
    │
    └── ui/
        ├── __init__.py
        └── chat_ui.py    # The Streamlit application code
```

### **Component Breakdown:**

- **data/raw/**: The AI Engineer should place the test dataset you provided here. The ingestion script will read from this directory.
    
- **data/vector_store/**: The ingest.py script will create and save the ChromaDB database here. This separation prevents re-processing documents every time the app starts.
    
- **src/ingestion/ingest.py**: This script will be the heart of the offline pipeline. It will:
    
    1. Load documents from data/raw/ using LangChain's loaders.
        
    2. Split them into chunks.
        
    3. Create embeddings using the chosen model.
        
    4. Store them in the ChromaDB vector store in data/vector_store/.
        
    5. This script should be run once, or whenever the source documents are updated (fulfills NFR-3).
        
- **src/core/rag_engine.py**: This is the most critical module. It will contain a class or functions that:
    
    1. Load the existing vector store from disk.
        
    2. Accept a user query and chat history.
        
    3. Perform a similarity search to retrieve relevant document chunks.
        
    4. Use a prompt template from prompts.py to format the context and question.
        
    5. Call the LLM to generate a grounded answer.
        
    6. Extract the answer and the source documents (including metadata like filename and page number).
        
- **src/core/prompts.py**: A key file for ensuring groundedness (FR-2.1). It will contain templates like:
    
    ```
    SYSTEM_PROMPT = """
    You are an expert Q&A assistant. Your goal is to provide accurate and concise answers based exclusively on the provided context.
    
    GUIDELINES:
    1.  Do not use any external knowledge. If the context does not contain the answer, you MUST say that you do not have enough information.
    2.  Cite the source document for every piece of information you use. The sources are available in the context.
    3.  Format your answer in a clear, user-friendly way using Markdown (e.g., bullet points, bolding).
    
    CONTEXT:
    ---
    {context}
    ---
    
    CHAT HISTORY:
    {chat_history}
    
    QUESTION:
    {question}
    
    ANSWER:
    """
    ```
    
    
- **src/app/main.py**: This sets up the FastAPI server and defines the /chat endpoint, which will take a user's question, call the rag_engine, and return the response in a JSON format.
    
- **src/ui/chat_ui.py**: The Streamlit app. It will have a simple UI to capture user input, make a POST request to the FastAPI backend, and display the conversation history, the chatbot's answer, and the clickable sources (FR-1.4).
    

## 9. High-Level Implementation Plan

1. **Setup**: Create the project structure, set up the virtual environment, and install dependencies from requirements.txt. Add OpenAI API key to .env.
    
2. **Build Ingestion Pipeline**: Implement src/ingestion/ingest.py. Test it with the provided sample dataset to ensure all document types are parsed correctly and the vector store is created.
    
3. **Develop Core RAG Engine**: Build the rag_engine.py. Test this module in isolation by feeding it a question and verifying that it retrieves relevant chunks and cites sources correctly.
    
4. **Create Backend API**: Wire up the RAG engine in the FastAPI app (src/app/). Test the /chat endpoint using a tool like Postman or curl.
    
5. **Build Frontend UI**: Develop the chat_ui.py with Streamlit. Connect it to the FastAPI backend.
    
6. **Test against Acceptance Criteria**: Systematically go through each AC in the PRD, using the sample dataset to validate that the full system behaves as expected. Pay special attention to out-of-scope questions (AC-2.1) and conversational context (AC-2.2).