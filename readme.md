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

## 📚 Detailed Phase-by-Phase Implementation (Phases 1 — 8)

The project follows an 8-phase architectural progression, transitioning from a basic stateless chat endpoint to a deterministic, observable, and fully evaluated agentic system.

---

### Phase 1 — Basic LLM Chat & Session Memory
* **Objective**: Build the foundational backend and conversational persistence layer.
* **Architecture**:
  ```text
  Client / React UI → FastAPI POST /chat → MySQL (Load History) → LangChain → Google Gemini → MySQL (Persist Message) → Response
  ```
* **Key Components**:
  - `backend/app/main.py`: FastAPI server with asynchronous request handling and CORS middleware.
  - `backend/app/api/chat.py`: REST endpoint managing conversation lifecycle and database sessions.
  - `backend/app/database/database.py` & `models/`: SQLAlchemy ORM mapping `conversations` (1-to-many) to `messages`.
  - `backend/app/services/chat_service.py`: LLM connector utilizing `langchain-google-genai`.
* **Key Capabilities**:
  - Multi-turn context preservation across sessions using unique `conversation_id` identifiers.
  - Conversational history formatted dynamically into LangChain `HumanMessage` and `AIMessage` objects.

---

### Phase 2 — RAG (Retrieval-Augmented Generation) & Distance Calibration
* **Objective**: Ground the model in company policy documentation to prevent hallucinations when answering customer questions.
* **Architecture**:
  ```text
  Text Documents (.txt) → RecursiveCharacterTextSplitter → Google Embeddings (text-embedding-004) → ChromaDB Vector Store → Similarity Search with Distance Threshold (≤ 0.70) → Context Augmentation → Gemini Answer
  ```
* **Key Components**:
  - `knowledge_base/`: Fictional NovaMart policies covering return, refund, shipping, warranty, and product FAQs.
  - `backend/app/rag/document_loader.py` & `chunker.py`: Text ingestion and recursive chunking (`chunk_size=500`, `chunk_overlap=100`).
  - `backend/app/rag/embeddings.py` & `vector_store.py`: Vector embeddings and persistent ChromaDB index.
  - `backend/app/rag/retrieval.py`: Similarity search pipeline with distance scoring.
* **Distance Calibration**:
  - Calibrated with `evaluation/rag_calibration.py` to establish a strict distance cutoff (`RAG_DISTANCE_THRESHOLD = 0.70`).
  - Queries with similarity distance exceeding 0.70 are tagged as out-of-domain, ensuring the agent does not attempt to answer unrelated queries using company policy excerpts.

---

### Phase 3 — Controlled Tool Calling & Function Execution
* **Objective**: Empower the LLM to access live customer and order data and perform business mutations safely.
* **Architecture**:
  ```text
  LLM Tool Call Proposal → Tool Dispatcher (Allowlist Check) → Application-Level Validation → Tool Execution → MySQL / ChromaDB → ToolMessage Result → LLM Synthesis
  ```
* **Key Components**:
  - `backend/app/tools/available_tools.py`: Central registry of validated `@tool` functions.
  - `backend/app/tools/tool_executer.py`: Security boundary ensuring Gemini only executes approved functions.
  - `order_tools.py`, `customer_tools.py`, `cancellation_tools.py`, `refund_tools.py`, `ticket_tools.py`, `knowledge_tools.py`.
* **Security & Business Rules**:
  - Strict parameter validation to prevent prompt injection and unauthorized mutations.
  - Orders can only be cancelled if their status is `processing`; shipped or delivered orders reject cancellation attempts.

---

### Phase 4 — Agentic Orchestration & LangGraph Workflows
* **Objective**: Replace unbounded LLM tool loops with an explicit, predictable state machine controlling business logic transitions.
* **Architecture**:
  ```text
  User Message + History → understand_request (Pydantic Intent Classifier)
      ├── ORDER_STATUS ─────► order_flow ──► get_order ──► route_order_result ──► generate_response
      ├── ORDER_CANCELLATION ► cancellation_flow ──► get_order ──► check_eligibility ──► confirmation
      ├── ORDER_REFUND ──────► refund_flow ──► validate_order ──► check_amount ──► execute_refund
      ├── COMPLAINT ────────► complaint_flow ──► log_ticket ──► generate_response
      ├── HUMAN_ESCALATION ─► escalation_flow ──► create_priority_ticket ──► generate_response
      └── GENERAL_QUERY ────► general_flow ──► search_knowledge_base ──► generate_response
  ```
* **Key Components**:
  - `backend/app/agents/workflow.py`: Compiled `StateGraph` state machine with nodes, conditional edges, and error routers.
  - `backend/app/schemas/workflow.py`: Centralized `SupportState` and structured `IntentResult`.
* **Capabilities**:
  - 11-intent classification covering orders, returns, payments, accounts, complaints, escalations, and general FAQs.
  - Context-aware pronoun resolution: accurately extracts order IDs across turns (e.g., resolving "Can I cancel it?" to `ORD-10245`).

---

### Phase 5 — Guardrails & Human-in-the-Loop (HITL) Approval
* **Objective**: Guard against risky business actions and enforce operational boundaries.
* **Key Guardrails**:
  - **Multi-Turn Cancellation Confirmation**: The agent halts execution and asks the user for explicit confirmation before mutating database records.
  - **Refund Amount Threshold Checks**:
    - Low-value refunds (within policy limits) proceed automatically.
    - High-value refunds or requests exceeding limits trigger `refund_requires_approval` and require manager sign-off.
  - **Complaint & Escalation Handling**: Dedicated flows that acknowledge frustration, open high-priority tickets, and escalate to human supervisors when requested.

---

### Phase 6 — Enterprise Observability & Action Logging
* **Objective**: Provide comprehensive auditability, debugging traces, and performance telemetry for every agent decision.
* **Key Components**:
  - `backend/app/services/action_logger.py`: Intercepts every tool invocation and writes an audit record into the `agent_actions` database table.
  - `backend/app/models/agent_action.py`: Tracks `conversation_id`, `tool_name`, `arguments`, `result`, `status` (`success` / `error`), and `latency` (in seconds).
  - **LangSmith Tracing**: Integrated LangChain callbacks providing node-by-node graph execution traces and token usage metrics.

---

### Phase 7 — Automated Evaluation & Calibration Framework
* **Objective**: Establish empirical, reproducible benchmarks measuring agent intent accuracy, tool selection, execution reliability, and response latency.
* **Key Components**:
  - `evaluation/evaluator.py`: Automated test runner executing end-to-end conversation flows against live database sessions.
  - `evaluation/test_cases.json`: Curated dataset of 50 multi-turn test scenarios covering all intents and edge cases.
  - `evaluation/rag_calibration.py`: Distance threshold validation suite.
  - `evaluation/results.json`: Output benchmark reports with granular failure traces and latency stats.

---

### Phase 8 — Containerization & Deployment (Upcoming Roadmap)
* **Objective**: Package the application for reproducible production deployment.
* **Planned Scope**:
  - Multi-stage Dockerfiles for backend (Python 3.11) and frontend (Node/Nginx).
  - Docker Compose service definition linking FastAPI, React, MySQL 8.0, and ChromaDB.
  - Production environment configuration and optional AWS cloud deployment (ECS / EC2 / RDS).

---

## 🏗️ System Architecture

### 1. Request-Response & Database Architecture
![AI Agent Customer Support - System Architecture](./architecture_diagram.png)

### 2. LangGraph High-Level Workflow
![AI Agent Customer Support - Workflow Diagram](./workflow_diagram.png)

### 3. Detailed LangGraph Nodewise Execution Flow
![LangGraph Nodewise Execution Flow](./langraph_nodes_diagram.png)

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

## 📌 Project Roadmap

- [x] **Phase 1**: Basic LLM Chat, Session Management & MySQL Persistence
- [x] **Phase 2**: RAG Integration (ChromaDB + Gemini Embeddings + Distance Calibration)
- [x] **Phase 3**: Tool Calling & Centralized Function Execution Registry
- [x] **Phase 4**: Agentic Orchestration & LangGraph Workflows
- [x] **Phase 5**: Guardrails & Human-in-the-Loop Approval (Cancellation confirmation, refund thresholds)
- [x] **Phase 6**: Observability & Action Logging (MySQL `agent_actions` + LangSmith)
- [x] **Phase 7**: Automated Evaluation Suite (50 benchmark test cases + RAG calibration)
- [ ] **Phase 8**: Containerization (Docker) & Cloud Deployment
