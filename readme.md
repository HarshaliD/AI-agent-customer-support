# AI Customer Support Agent

An AI-powered customer support agent built with **FastAPI, LangChain, Google Gemini, ChromaDB, and MySQL**.

---

## 🚀 Overview

This repository is built incrementally following an 8-phase project guide. Currently, **Phase 1 (Basic LLM Chat)** and **Phase 2 (RAG Integration)** are fully implemented.

---

## ✨ Features Implemented

### Phase 1 — Basic LLM Chat
- **FastAPI Backend**: Asynchronous REST API serving chat endpoints.
- **Google Gemini Integration**: Connected via `langchain-google-genai`.
- **Request Validation**: Pydantic models for incoming chat requests.
- **MySQL Persistence**: SQLAlchemy models managing `conversations` and `messages`.
- **Multi-Turn Conversation Memory**: Historical conversation context retrieved from MySQL and included in LLM calls.

### Phase 2 — RAG (Retrieval-Augmented Generation) Integration
- **Knowledge Base Storage**: Policy and FAQ documents stored under `knowledge_base/` (`product_faq.txt`, `refund_policy.txt`, `return_policy.txt`, `shipping_policy.txt`, `warranty_policy.txt`).
- **Document Loading & Chunking**: Recursive text splitting (`RecursiveCharacterTextSplitter`) with customizable chunk size and overlap.
- **Vector Embeddings**: Google Generative AI embeddings (`models/text-embedding-004`).
- **Vector Database**: Persistent **ChromaDB** storage for indexing document chunks and running similarity search.
- **Contextual Prompting**: Grounding LLM responses strictly in retrieved knowledge base context to prevent hallucinations.
- **Auto-Initialization**: Automatic knowledge base loading and vector store setup on application startup.

---

## 🏗️ System Architecture

```text
Client
  │
  ▼
FastAPI (POST /api/chat)
  │
  ├─► Conversation Memory (MySQL: conversations & messages)
  │
  └─► RAG Pipeline
        │
        ├─► Similarity Search (Chroma Vector DB)
        │     ▲
        │     └── Knowledge Base Docs (knowledge_base/*.txt)
        │
        ├─► Relevant Context + Chat History
        │
        └─► LangChain Prompt Template
              │
              ▼
        Google Gemini LLM
              │
              ▼
        Generated Answer (Grounded in context)
              │
              ▼
        Saved to MySQL & Returned to Client
```

---

## 📁 Project Structure

```text
AI-Agent-Customer-Support/
├── backend/
│   └── app/
│       ├── api/
│       │   └── chat.py          # FastAPI Chat Endpoints
│       ├── db/                  # MySQL Database & SQLAlchemy Models
│       ├── rag/                 # RAG Module
│       │   ├── document_loader.py # Loads knowledge base documents
│       │   ├── chunker.py         # Document text splitter
│       │   ├── embeddings.py      # Gemini text embeddings setup
│       │   ├── vector_store.py    # ChromaDB initialization & operations
│       │   ├── retrieval.py       # Knowledge retrieval logic
│       │   ├── prompt.py          # Grounded prompt templates
│       │   ├── generation.py      # LLM answer generation
│       │   └── rag_service.py     # End-to-end RAG orchestrator
│       └── main.py              # FastAPI Application Entrypoint
├── guides/                      # Project Guides & Documentation
├── knowledge_base/              # Support Policies & FAQ Documents
├── requirements.txt             # Python Dependencies
└── README.md
```

---

## 🛠️ Setup & Running

### Prerequisites
- Python 3.11+
- MySQL Instance
- Google Gemini API Key (`GEMINI_API_KEY`)

### Environment Setup
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/db_name
```

### Installation
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the API
```bash
uvicorn backend.app.main:app --reload
```

---

## 🧪 Testing

Run tests for the RAG modules:
```bash
pytest backend/app/rag/
```

---

## 📌 Project Status

- [x] **Phase 1**: Basic LLM Chat & Session Memory
- [x] **Phase 2**: RAG Integration (ChromaDB + Gemini Embeddings)
- [ ] **Phase 3**: Customer Tools & Order Management
- [ ] **Phase 4**: Agentic Orchestration
- [ ] **Phase 5**: Advanced Guardrails & Text-to-SQL
- [ ] **Phase 6**: Observability & Cost Tracking
- [ ] **Phase 7**: Evaluation Framework
- [ ] **Phase 8**: Deployment & Containerization
