# AI Customer Support Agent

An enterprise-ready, AI-powered customer support agent built with **FastAPI, LangChain, Google Gemini, ChromaDB, LangGraph, MySQL, and React (Vite)**.

---

## 🚀 Overview

This system provides automated, multi-turn customer support combining:
- **Retrieval-Augmented Generation (RAG)** grounded in company policies to answer customer inquiries without hallucinations.
- **Dynamic Tool Execution & Database Integration** to securely perform live lookups and state mutations (order status, order cancellation, refunds, customer profiles, ticketing).
- **LangGraph State Machine Orchestration** providing deterministic workflow routing, multi-turn human-in-the-loop confirmations, refund approval guardrails, and customer escalation.
- **Enterprise Observability & Action Logging** recording every tool call, latency, and status in MySQL, with optional LangSmith tracing.
- **Automated Evaluation Framework** benchmarking intent classification, tool accuracy, behavior, and latency across 50 curated real-world scenarios.
- **Modern React Chat UI** for an interactive, responsive customer support experience.

---

## ✨ Features Implemented

### Phase 1 — Basic LLM Chat & Session Memory
- **FastAPI Backend**: Asynchronous REST API serving high-performance chat endpoints with CORS support.
- **Google Gemini Integration**: Connected via `langchain-google-genai`.
- **Request Validation**: Strict Pydantic models for incoming chat payloads.
- **MySQL Persistence**: SQLAlchemy models managing persistent `conversations` and `messages`.
- **Multi-Turn Conversation Memory**: Historical conversation context retrieved from MySQL and formatted into LangChain message structures across multi-turn sessions.

### Phase 2 — RAG (Retrieval-Augmented Generation) & Threshold Calibration
- **Knowledge Base Storage**: Policy and FAQ documents stored under `knowledge_base/` (`product_faq.txt`, `refund_policy.txt`, `return_policy.txt`, `shipping_policy.txt`, `warranty_policy.txt`).
- **Document Loading & Chunking**: Recursive text splitting (`RecursiveCharacterTextSplitter`) with customizable chunk size (`500`) and overlap (`100`).
- **Vector Embeddings**: Google Generative AI embeddings (`models/text-embedding-004` / `gemini-embedding-001`).
- **ChromaDB Storage**: Persistent vector storage for indexing document chunks and running similarity searches with distance scoring.
- **Distance Threshold Calibration**: Relevancy score filtering (`RAG_DISTANCE_THRESHOLD = 0.70`) calibrated via `evaluation/rag_calibration.py` to prevent answering out-of-domain questions with irrelevant context.
- **Auto-Initialization**: Automatic knowledge base loading and vector store setup on application startup.

### Phase 3 — Tool Calling & Function Execution
- **LangChain Tool Integration**: `@tool` decorated functions exposing schemas and parameters to Gemini.
- **Centralized Tool Registry**: Controlled list (`AVAILABLE_TOOLS`) in `backend/app/tools/available_tools.py`.
- **Tool Dispatcher & Security Boundary**: Execution dispatcher in `tool_executer.py` validating requests against an allowlist before executing code.
- **Customer & Order Capabilities**:
  - `get_order`: Retrieves live order status, shipping carrier, and tracking numbers from MySQL.
  - `get_customer`: Retrieves customer profile details.
  - `cancel_order`: Enforces business rules (cancels only `processing` orders).
  - `create_ticket`: Logs support tickets into MySQL.
  - `request_refund`: Submits pending refund requests with reason and amount.
  - `search_knowledge_base`: Wraps RAG retrieval system as a tool for dynamic knowledge querying.

### Phase 4 — Agent Workflows & LangGraph Orchestration
- **LangGraph State Machine Engine**: Compiled `StateGraph` state machine for explicit request understanding, routing, and node transitions.
- **Structured State Management**: `SupportState` schema tracking `user_message`, `chat_history`, `intent`, `order_id`, `order_result`, `knowledge_result`, `refund_amount`, `approval_required`, `approval_status`, `pending_action`, `pending_order_id`, `user_confirmation`, and `final_response`.
- **11-Class Pydantic Intent Routing**: Strict structured intent classification via `IntentResult`:
  - `ORDER_STATUS`, `ORDER_CANCELLATION`, `ORDER_REFUND`, `RETURN`, `PAYMENT`, `ACCOUNT`, `PRODUCT_INFORMATION`, `COMPLAINT`, `TECHNICAL_SUPPORT`, `HUMAN_ESCALATION`, `GENERAL_QUERY`.
- **Multi-Branch Business Logic & Controlled Errors**:
  - **Order Status Flow**: Retrieves order status and handles nonexistent order cases gracefully via dedicated `order_not_found` node.
  - **Order Cancellation with Multi-Turn Confirmation**: Checks order eligibility and explicitly asks the user for confirmation before executing state mutations.
  - **Refund Approval Guardrails**: Validates refund eligibility, evaluates refund amount thresholds, routes to human manager approval when limits are exceeded, and handles approved/pending/rejected states.
  - **Complaint & Human Escalation Flows**: Routes frustrated customers or explicit escalation requests to specialized flows (`complaint_flow`, `escalation_flow`).
  - **General Knowledge RAG Flow**: Routes policy/FAQ questions directly to calibrated `search_knowledge_base` retrieval.
- **Context-Aware Pronoun Resolution**: Integrates persistent MySQL chat history into `SupportState.chat_history` so the workflow resolves follow-up references (e.g. *"Can I cancel it?"*) to earlier order context (`ORD-10245`).

### Observability & Logging
- **Database Action Logging**: Every tool execution is recorded in the `agent_actions` MySQL table via `action_logger.py`, tracking `conversation_id`, `tool_name`, `arguments`, `result`, `status` (`success` / `error`), and `latency`.
- **LangSmith Tracing Support**: Optional LangChain tracing integration for deep inspection of agent graph execution steps and LLM tokens.

### Modern Frontend Chat Interface
- **React + Vite Application**: Fast, responsive chat UI in `frontend/`.
- **Session Lifecycle Management**: Automatically manages session creation and preserves `conversation_id` across turns.
- **Real-Time Indicators**: Dynamic online status badges, loading states, and error handling.

---

## 🏗️ System Architecture

### 1. Request-Response & Database Architecture
![AI Agent Customer Support - System Architecture](./architecture_diagram.png)

### 2. LangGraph Agent Workflow
![AI Agent Customer Support - Workflow Diagram](./workflow_diagram.png)

---

## 📁 Project Structure

```text
AI-Agent-Customer-Support/
├── backend/
│   └── app/
│       ├── agents/
│       │   └── workflow.py         # LangGraph StateGraph engine, nodes & routers
│       ├── api/
│       │   └── chat.py             # FastAPI chat endpoint & workflow invocation
│       ├── database/
│       │   ├── database.py         # SQLAlchemy engine & session maker
│       │   └── init_db.py          # Database table creation script
│       ├── models/                 # SQLAlchemy ORM models
│       │   ├── agent_action.py     # Tool execution observability logs
│       │   ├── conversation.py     # Conversation session table
│       │   ├── customer.py         # Customer account profile table
│       │   ├── message.py          # Message history table
│       │   ├── order.py            # Order management table
│       │   ├── refund.py           # Refund request table
│       │   └── ticket.py           # Customer support ticket table
│       ├── rag/                    # RAG Knowledge Pipeline
│       │   ├── chunker.py          # RecursiveCharacterTextSplitter
│       │   ├── document_loader.py  # Knowledge base file loaders
│       │   ├── embeddings.py       # Google Gemini embedding model
│       │   ├── retrieval.py        # Vector search & distance threshold filtering
│       │   └── vector_store.py     # ChromaDB persistence & indexing
│       ├── schemas/
│       │   ├── chat.py             # ChatRequest & ChatResponse schemas
│       │   └── workflow.py         # SupportState & IntentResult schemas
│       ├── services/
│       │   ├── action_logger.py    # Tool execution & latency logger
│       │   └── chat_service.py     # Gemini model initialization
│       ├── tools/                  # Tool definitions & registry
│       │   ├── available_tools.py  # Central registry of approved tools
│       │   ├── cancellation_tools.py # Order cancellation tool
│       │   ├── customer_tools.py   # Customer lookup tool
│       │   ├── knowledge_tools.py  # RAG search tool
│       │   ├── order_tools.py      # Order retrieval tool
│       │   ├── refund_tools.py     # Refund submission tool
│       │   ├── ticket_tools.py     # Support ticketing tool
│       │   └── tool_executer.py    # Allowlist validation & execution dispatcher
│       └── main.py                 # FastAPI application entrypoint & CORS config
├── chroma_db/                      # Persistent ChromaDB vector database
├── evaluation/                     # Automated evaluation & calibration suite
│   ├── evaluator.py                # 50-test-case benchmark runner
│   ├── rag_calibration.py         # Distance threshold calibration script
│   ├── results.json                # Latest evaluation benchmark report
│   └── test_cases.json             # Curated benchmark scenarios
├── frontend/                       # React + Vite customer chat interface
│   ├── src/
│   │   ├── App.jsx                 # Chat UI component & API interaction
│   │   ├── App.css                 # Interface styling & animations
│   │   └── main.jsx                # React DOM entrypoint
│   ├── package.json                # Frontend dependencies
│   └── vite.config.js              # Vite configuration
├── guides/                         # Technical documentation & project logs
│   ├── AI_Customer_Support_Agent_Project_Guide.md # Master project blueprint
│   ├── ARCHITECTURE.md             # Architecture breakdown
│   ├── ERRORS_AND_LESSONS.md       # Debugging log & architectural lessons
│   └── LEARNING_LOG.md             # Detailed milestone progression log
├── knowledge_base/                 # NovaMart support policies & FAQs
│   ├── product_faq.txt
│   ├── refund_policy.txt
│   ├── return_policy.txt
│   ├── shipping_policy.txt
│   └── warranty_policy.txt
├── requirements.txt                # Python dependencies
└── README.md
```

---

## 🛠️ Setup & Running

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- MySQL Server (v8.0+)
- Google Gemini API Key (`GEMINI_API_KEY`)

### 1. Environment Setup
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/ai_customer_support

# Optional: LangSmith Observability Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=ai-customer-support-agent
```

### 2. Backend Installation & Database Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize MySQL tables and populate test records
python -m backend.app.database.init_db
```

### 3. Start Backend API
```bash
uvicorn backend.app.main:app --reload --port 8000
```
The FastAPI backend will start at `http://localhost:8000`. You can inspect the interactive OpenAPI documentation at `http://localhost:8000/docs`.

### 4. Start Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
The frontend will start at `http://localhost:5173`.

---

## 🧪 Testing & Evaluation

### Run Unit Tests
```bash
pytest backend/app/tools/
pytest backend/app/rag/
```

### Run RAG Distance Threshold Calibration
Calibrate similarity search distance thresholds across in-domain and out-of-domain queries:
```bash
python evaluation/rag_calibration.py
```

### Run Benchmark Evaluation Suite
Run the 50-test-case automated evaluation suite benchmarking intent classification, tool selection, execution reliability, and response latency:
```bash
python evaluation/evaluator.py
```

---

## 📊 Evaluation Results

The agent was evaluated against **50 curated real-world scenarios** covering order tracking, cancellations, refunds, multi-turn follow-ups, policy queries, complaints, and escalations:

| Metric | Result |
|---|---:|
| **Intent Classification Accuracy** | **100.0%** |
| **Tool Selection Accuracy** | **100.0%** |
| **Execution Success Rate** | **100.0%** |
| **Average Response Latency** | **5.33 sec** |
| **Evaluated Test Scenarios** | **50** |

> **Evaluation Notes:**  
> - **100% Intent & Tool Accuracy**: The Pydantic structured output model correctly categorized all 11 intents and invoked the appropriate database/knowledge tools.
> - **Zero Execution Failures**: The agent workflow completed 50/50 test scenarios without unhandled exceptions or state corruptions.

---

## 📌 Project Roadmap

- [x] **Phase 1**: Basic LLM Chat, Session Management & MySQL Persistence
- [x] **Phase 2**: RAG Integration (ChromaDB + Gemini Embeddings + Distance Calibration)
- [x] **Phase 3**: Tool Calling & Centralized Function Execution Registry
- [x] **Phase 4**: Agentic Orchestration & LangGraph Workflows
- [x] **Phase 5**: Guardrails & Human-in-the-Loop Approval (Cancellation confirmation, refund thresholds)
- [x] **Phase 6**: Observability & Action Logging (MySQL `agent_actions` + LangSmith)
- [x] **Phase 7**: Automated Evaluation Suite (50 benchmark test cases + RAG calibration)
- [ ] **Phase 8**: Containerization (Docker) & Cloud Deployment
