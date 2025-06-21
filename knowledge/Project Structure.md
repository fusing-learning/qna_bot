# **QnA Bot: Project Structure & Onboarding Guide**

Welcome to the team\! This document provides a high-level overview of the QnA Bot's architecture and codebase. Its goal is to help you understand how the different parts of the project fit together.

## **1\. High-Level Architecture**

The application is composed of three main components that work together:

1. **FastAPI Backend (/src/app)**: An API that serves as the main entry point for user interactions. It handles HTTP requests for asking questions and managing documents.  
2. **Core Logic (/src/core)**: The "brain" of the application. This is where the core business logic, including the RAG (Retrieval-Augmented Generation) engine, database interactions, and document processing services, resides.  
3. **Streamlit UI (/src/ui)**: The web-based user interfaces. There are two simple interfaces: one for the main Q\&A chat and another for administrators to manage the knowledge base.

## **2\. Directory and File Breakdown**

Here is a guide to the key directories and files and what they are for.

### **Root Directory (/)**

* requirements.txt: Lists all the Python packages needed to run the project.  
* README.md: The main project documentation with setup and usage instructions.

### **/src \- The Source Code**

This is the main container for all the Python source code.

#### **/src/app \- The API Layer**

*This is where the application handles incoming web requests.*

* api.py: Defines all the API endpoints using the **FastAPI** framework. If you need to add or change how the outside world communicates with the bot (e.g., asking a question, uploading a file), you'll do it here.

#### **/src/core \- The Core Engine**

*This is the heart of the application, containing all the main business logic.*

* config.py: Centralized configuration management. It loads settings like API keys and database paths from environment variables, so we don't hardcode them.  
* rag\_engine.py: The core RAG (Retrieval-Augmented Generation) engine. This file contains the logic for taking a user's question, finding relevant documents from the vector database, and generating an answer using the LLM. **This is the key file for AI Engineers.**  
* database.py: Manages the metadata database (SQLite). It stores information *about* the documents, such as filename, version, and upload date. It does **not** store the document content itself.  
* document\_service.py: Handles the business logic for managing documents (uploading, validating, deleting). It coordinates between the API, the metadata database, and the vector store.

#### **/src/ingestion \- Data Processing**

*This folder contains scripts for processing and loading data into our knowledge base.*

* ingest.py: A script responsible for taking source documents (like .txt or .md files), splitting them into chunks, creating vector embeddings, and storing them in the **ChromaDB** vector store.

#### **/src/ui \- User Interface**

*This is where the web pages that users interact with are defined.*

* app.py: A **Streamlit** application that provides the main chat interface for users to ask questions.  
* admin.py: A separate **Streamlit** application that provides an admin panel for uploading new documents and viewing existing ones.

### **Other Important Directories**

* /data: Contains the persistent data for the application.  
  * /uploads: Raw files uploaded by users are stored here.  
  * /chroma: The ChromaDB vector store.  
  * /db: The SQLite metadata database file.  
* /docs: Project documentation, including the API specification.  
* /scripts: Helper shell scripts to easily run different parts of the application (e.g., run\_api.sh, run\_app.sh).  
* /tests: Contains all automated tests to ensure the code is working correctly.

## **3\. How to Contribute**

* **AI / Backend Developers**: Your work will primarily be in /src/core (improving the RAG engine, database logic) and /src/app (exposing new features via the API). To add a new feature, you would typically start by modifying the document\_service.py or rag\_engine.py and then creating an endpoint for it in api.py.  
* **Frontend Developers / UI/UX**: Your focus will be on the files in /src/ui. You can improve the user experience of the chat and admin pages here.  
* **Product Managers**: The most relevant files for you are PRD/qna\_bot\_prd\_v0.md (the Product Requirements Document), PRD/qna\_bot\_task\_list.md (the task list), and this document. They provide a complete overview of the "what" and "why" of the project.