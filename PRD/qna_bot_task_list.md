# QnA Bot Implementation Task List

## Phase 1: Core Document Processing & Basic Q&A
This phase focuses on getting the basic document processing and Q&A functionality working.

### 1.0 Basic Project Setup & Infrastructure
- [x] **1.1 Set up project structure and environment**
  - [x] Create directory structure
  - [x] Set up virtual environment
  - [x] Create requirements.txt with initial dependencies
  - [x] Set up .env for configuration

- [x] **1.2 Implement basic configuration management**
  - [x] Create config.py for environment variables
  - [x] Set up OpenAI API key handling
  - [x] Tests for config management (all passed)

### 2.0 Document Processing Pipeline
- [x] **2.1 Implement basic document loader**
  - [x] Support for .txt and .md files initially
  - [x] Basic file validation

- [x] **2.2 Implement text chunking**
  - [x] Create text splitter with configurable chunk size
  - [x] Add metadata to chunks (source file, position)

- [x] **2.3 Set up vector store**
  - [x] Initialize ChromaDB
  - [x] Implement basic embedding generation
  - [x] Create storage for document chunks

### 3.0 Basic Q&A Engine
- [x] **3.1 Implement core RAG logic**
  - [x] Create basic prompt template
  - [x] Implement context retrieval
  - [x] Set up OpenAI API integration

- [x] **3.2 Implement answer generation**
  - [x] Basic answer formatting
  - [x] Source citation handling

## Phase 2: Basic Web Interface & Document Management
This phase adds a simple web interface and basic document management capabilities.

### 4.0 Basic Web Interface
- [x] **4.1 Set up Streamlit frontend**
  - [x] Create basic chat interface
  - [x] Implement message history display

- [x] **4.2 Implement FastAPI backend**
  - [x] Create /chat endpoint
  - [x] Set up basic error handling

### 5.0 Basic Document Management
- [x] **5.1 Implement document upload**
  - [x] Basic file upload interface
  - [x] File type validation
  - [x] Size limit enforcement

- [x] **5.2 Implement document listing**
  - [x] Show uploaded documents
  - [x] Basic document metadata display
  - [x] Ensure all UI elements function, eg view and delete buttons

- [x] **5.3 Consolidate admin and app UI**
  - [x] Update README.md based on latest implementations

## Phase 3: Enhanced Features & Error Handling
This phase adds more robust features and error handling.

### 6.0 Enhanced Chat
- [ ] **6.1 Allow users to clear and start a new chat**

### 7.0 Enhanced Document Processing
- [ ] **7.1 Support multiple file uploads**
  - [ ] Allow users to upload multiple documents at once

- [ ] **7.2 Add support for additional file types**
  - [ ] PDF, DOCX, XLSX, PPTX, CSV

- [ ] **7.3 Implement document versioning**
  - [ ] Basic version tracking
  - [ ] Version metadata storage

- [ ] **7.4 How to handle document deletion involving active chat**

### 8.0 Enhanced Admin Portal
- [ ] **8.1 Implement API key and model selection**

### 9.0 Error Handling & Validation
- [ ] Check what are the error handling that are missing, come up with task list and implement. Some backlogs
  - [ ] API error handling
  - [ ] File processing errors
  - [ ] Question length limits / chat input field limits
  - [ ] For upload documents, how to handle duplicated filename and document title

### 10.0 Others
- [ ] Change frontend stacks from Streamlit to something else?
