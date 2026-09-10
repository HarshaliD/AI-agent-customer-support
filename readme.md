# AI Customer Support Agent

An AI-powered customer support agent built with **FastAPI, LangChain, Google Gemini, ChromaDB, LangGraph, and MySQL**.

---

## 🚀 Overview

This repository is built incrementally following an 8-phase project guide. Currently, **Phase 1 (Basic LLM Chat)**, **Phase 2 (RAG Integration)**, **Phase 3 (Tool Calling)**, and **Phase 4 (Agent Workflows & LangGraph Orchestration)** are fully implemented.

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

### Phase 3 — Tool Calling & Function Execution
- **LangChain Tool Integration**: `@tool` decorated functions exposing name, description, and parameter schemas to Gemini via `bind_tools()`.
- **Centralized Tool Registry**: Controlled list (`AVAILABLE_TOOLS`) in `backend/app/tools/available_tools.py`.
- **Tool Dispatcher & Security Boundary**: Execution dispatcher in `tool_executer.py` validating requests against an allowlist before executing Python code.
- **Customer & Order Capabilities**:
  - `get_order`: Retrieves live order status from MySQL.
  - `get_customer`: Retrieves customer profile details.
  - `cancel_order`: Enforces business rules (cancels only `processing` orders).
  - `create_ticket`: Logs support tickets into MySQL.
  - `request_refund`: Submits pending refund requests.
  - `search_knowledge_base`: Wraps RAG retrieval system as a tool so Gemini dynamically queries company knowledge.
- **Multi-Turn Tool Execution Loop**: Autonomous processing loop handling multi-step tool calls, converting outputs to `ToolMessage` instances, and multi-turn context support.

### Phase 4 — Agent Workflows & LangGraph Orchestration
- **LangGraph Workflow Engine**: Replaced ad-hoc tool loops with a compiled `StateGraph` state machine for explicit request understanding, routing, and node transitions.
- **Structured State Management**: `SupportState` schema tracking `user_message`, `chat_history`, `intent`, `order_id`, `order_result`, `knowledge_result`, and `final_response`.
- **Pydantic Structured Intent Routing**: Replaced substring matching with strict Pydantic `IntentResult` classification (`Literal["ORDER_STATUS", "ORDER_CANCELLATION", "GENERAL_QUERY"]`).
- **Multi-Branch Business Logic & Controlled Errors**:
  - **Order Status Flow**: Retrieves order status and handles nonexistent order cases gracefully via dedicated `order_not_found` node.
  - **Order Cancellation Flow**: Inspects live database status, routes between `cancellation_eligible` and `cancellation_not_eligible` nodes, and executes state mutations safely via `cancel_order`.
  - **General Knowledge RAG Flow**: Routes policy/FAQ questions directly to `search_knowledge_base` retrieval.
- **Multi-Turn Context & Pronoun Resolution**: Integrates persistent MySQL chat history into `SupportState.chat_history` so the workflow resolves follow-up references (e.g. *"Can I cancel it?"*) to earlier order context (`ORD-10245`).

---

## 🏗️ System Architecture

```text
Client
  │
  ▼
FastAPI (POST /chat)
  │
  ├─► Save User Message & Retrieve Conversation History (MySQL)
  │
  ▼
SupportState (user_message + chat_history)
  │
  ▼
LangGraph Workflow Engine (workflow.py)
  │
  ▼
understand_request (Pydantic Intent Classification & Order ID Extraction)
  │
  ├─────────────── Conditional Intent Router ───────────────┐
  │                             │                           │
  ▼                             ▼                           ▼
ORDER_STATUS               ORDER_CANCELLATION         GENERAL_QUERY
  │                             │                           │
order_flow                 cancellation_flow           general_flow
  │                             │                           │
get_order (MySQL)          get_order (MySQL)          search_knowledge_base
  │                             │                     (ChromaDB RAG)
route_order_result         route_cancellation_result       │
  │                             │                           │
  ├──► order_not_found          ├──► order_not_found        │
  │                             ├──► cancellation_not_eligible
  └──► generate_response        └──► cancellation_eligible  │
                                             │               │
                                        cancel_order         │
                                             │               │
                                      cancellation_completed │
  ┌──────────────────────────────────────────┴───────────────┘
  ▼
final_response
  │
  ▼
Save Assistant Response to MySQL & Return Response to Client
```

---

## 📁 Project Structure

```text
AI-Agent-Customer-Support/
├── backend/
│   └── app/
│       ├── agents/
│       │   └── workflow.py      # LangGraph Workflow Engine & Nodes
│       ├── api/
│       │   └── chat.py          # FastAPI Chat Endpoint & Workflow Invocation
│       ├── db/                  # MySQL Database & SQLAlchemy Models
│       ├── models/              # ORM Models (Customer, Order, Ticket, Refund)
│       ├── rag/                 # RAG Module (Loader, Chunker, Embeddings, Chroma)
│       ├── schemas/
│       │   ├── chat.py          # Chat request/response validation schemas
│       │   └── workflow.py      # SupportState & IntentResult schemas
│       ├── services/            # LLM Chat Service
│       ├── tools/               # Tool Definitions & Dispatcher
│       │   ├── available_tools.py # Central registry of approved tools
│       │   ├── tool_executer.py   # Dispatcher and execution allowlist
│       │   ├── order_tools.py     # Order retrieval tool
│       │   ├── customer_tools.py  # Customer lookup tool
│       │   ├── cancellation_tools.py # Order cancellation tool
│       │   ├── ticket_tools.py    # Ticketing tool
│       │   ├── refund_tools.py    # Refund request tool
│       │   └── knowledge_tools.py # RAG knowledge base tool
│       └── main.py              # FastAPI Application Entrypoint
├── frontend/                    # React UI Chat Interface
├── guides/                      # Learning Logs, Errors & Architecture Docs
│   ├── LEARNING_LOG.md
│   ├── ERRORS_AND_LESSONS.md
│   ├── ARCHITECTURE.md
│   └── AI_Customer_Support_Agent_Project_Guide.md
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

Run tests for the tools and RAG modules:
```bash
pytest backend/app/tools/
pytest backend/app/rag/
```

---

## 📌 Project Status

- [x] **Phase 1**: Basic LLM Chat & Session Memory
- [x] **Phase 2**: RAG Integration (ChromaDB + Gemini Embeddings)
- [x] **Phase 3**: Tool Calling & Function Execution
- [x] **Phase 4**: Agentic Orchestration & LangGraph Workflows
- [ ] **Phase 5**: Advanced Guardrails & Text-to-SQL
- [ ] **Phase 6**: Observability & Cost Tracking
- [ ] **Phase 7**: Evaluation Framework
- [ ] **Phase 8**: Deployment & Containerization


