# Learning Log

## Phase 1 — Basic LLM Chat & Frontend Integration

### Milestone Status: Completed

### Implementation Summary
In Phase 1, we built the core backend foundation and a clean React frontend interface for the AI Customer Support Agent.

Key components created/updated:
- **`frontend/src/App.jsx`**: Clean React customer support chat UI managing state for input messages, conversation history, `conversation_id` tracking across requests, loading states, and error handling.
- **`frontend/src/App.css`**: Styling for user/assistant message bubbles, session tags, input controls, loading state indicators, and responsive layouts.
- **`backend/app/main.py`**: FastAPI entrypoint with CORS middleware enabled for `http://localhost:5173`.
- **`backend/app/api/chat.py`**: API endpoint `POST /chat` handling conversation lifecycle, message logging, and multi-turn prompt construction.
- **`backend/app/services/chat_service.py`**: LLM interaction layer isolating LangChain `ChatGoogleGenerativeAI` model invocations.
- **`backend/app/schemas/chat.py`**: Pydantic model (`ChatRequest`) for strict request body validation.
- **`backend/app/database/database.py` & `init_db.py`**: Database connection setup using SQLAlchemy engine, session maker, and table creation script.
- **`backend/app/models/conversation.py` & `message.py`**: SQLAlchemy ORM models defining the relational database schema (`conversations` and `messages` tables).

---

### Technical Concepts Learned & Applied
1. **Frontend-Backend Contract**: Frontend communicates via `POST /chat` passing `{ message: string, conversation_id: number | null }` and updating `conversation_id` state from the response payload (`{ conversation_id: number, response: string }`).
2. **Session Persistence**: Initial request sends `conversation_id: null` to generate a new session. Subsequent requests supply the assigned `conversation_id` so the backend retrieves the exact MySQL history and maintains multi-turn context.
3. **UX & Input State Control**: Input fields and submission buttons are disabled while awaiting API responses (`loading: true`), preventing duplicate submissions and race conditions.

# Phase 2 — RAG Integration

## Goal

Enable the customer support AI to answer questions using NovaMart's knowledge base through Retrieval-Augmented Generation (RAG), while preserving Phase 1 conversation memory.

## Knowledge Base

Created a fictional NovaMart knowledge base for the project.

Files:

- `knowledge_base/return_policy.txt`
- `knowledge_base/refund_policy.txt`
- `knowledge_base/shipping_policy.txt`
- `knowledge_base/warranty_policy.txt`
- `knowledge_base/product_faq.txt`

## 1. Document Loading

Created:

`backend/app/rag/document_loader.py`

Used LangChain `TextLoader` to load `.txt` files as LangChain `Document` objects.

Flow:

Knowledge files
→ `TextLoader`
→ LangChain Documents

Result:

5 files → 5 Documents

## 2. Document Chunking

Created:

`backend/app/rag/chunker.py`

Used:

`RecursiveCharacterTextSplitter`

Configuration:

- `chunk_size = 500`
- `chunk_overlap = 100`

Important:

- `chunk_size` is a target/upper sizing value, not a guarantee that every chunk is exactly 500 characters.
- `chunk_overlap` allows neighboring chunks to share content.
- RecursiveCharacterTextSplitter uses a hierarchy of separators to split documents.
- Chunking is not semantic clustering.

Result:

5 Documents → 9 chunks

## 3. Embeddings

Created:

`backend/app/rag/embeddings.py`

Used Gemini embedding model:

`gemini-embedding-001`

Concept:

Text → numerical vector

The tested query embedding returned a vector containing 3072 numbers.

Important:

The embedding model creates vectors. The vector store stores/searches those vectors.

## 4. Vector Store

Created:

`backend/app/rag/vector_store.py`

Used:

Chroma

Chroma stores:

- embeddings/vectors
- original document content
- metadata

Important:

Chroma is the vector store, not the embedding model.

## 5. Chroma.from_documents()

Learned that `Chroma.from_documents()` is a convenient ingestion operation.

Conceptually:

Documents
→ embedding model
→ vectors
→ Chroma

It creates embeddings for the supplied documents and stores them in the vector store.

## 6. HNSW

Encountered HNSW while working with Chroma.

Important:

HNSW is a vector similarity indexing/search technique.

It is not:

- a chunking method
- an embedding model

Mental model:

Chunking → breaks documents into pieces

Embedding → converts text into vectors

HNSW → helps search vectors efficiently

## 7. Chroma Persistence

Created persistent storage:

`chroma_db/`

Added:

`load_vector_store()`

This allows the application to open the previously persisted vector store rather than rebuilding the embeddings every time.

Important distinction:

`chroma_db/`
= persistent data on disk

`vector_store`
= Python object used by the application

## 8. FastAPI Lifespan Integration

Updated `backend/app/main.py` to load the vector store when the FastAPI application starts.

Used:

`app.state.vector_store`

Concept:

FastAPI starts
→ load vector store once
→ store it in `app.state`
→ reuse it across requests

The deeper details of `async`, `yield`, and `asynccontextmanager` were intentionally parked for later learning.

## 9. Retrieval

Created:

`backend/app/rag/retrieval.py`

Used:

`vector_store.similarity_search(question, k=2)`

Retrieval flow:

User question
→ question is embedded
→ compare with stored vectors
→ retrieve nearest chunks

Important:

The question is not added to Chroma during retrieval.

`k=2` means return the 2 nearest chunks. It does not mean 2 different documents.

A query may therefore retrieve multiple chunks from the same document.

## 10. Context Building

Retrieved chunks were combined into a text context before sending them to Gemini.

Flow:

Retrieved chunks
→ combine `page_content`
→ RAG context

## 11. RAG Prompt

Created:

`backend/app/rag/prompt.py`

Used:

`ChatPromptTemplate`

The prompt contains:

- system instructions
- retrieved knowledge/context
- conversation history
- current user question

## 12. MessagesPlaceholder

Added:

`MessagesPlaceholder("chat_history")`

Purpose:

Provide a slot for a list of LangChain message objects.

Example:

- `HumanMessage`
- `AIMessage`
- `HumanMessage`
- `AIMessage`

Important distinction:

`{question}`
= one text value

`MessagesPlaceholder("chat_history")`
= list of message objects

This allows conversation history to preserve message roles.

## 13. Generation

Created:

`backend/app/rag/generation.py`

The generation stage sends the RAG prompt to Gemini and extracts the generated response.

Flow:

Retrieved context
+
conversation history
+
current question
→ Gemini
→ answer

## 14. RAG + Phase 1 Memory Integration

Integrated RAG into:

`POST /chat`

Final Phase 2 flow:

User question
→ FastAPI
→ save user message to MySQL
→ retrieve conversation history
→ convert history to `HumanMessage` / `AIMessage`
→ embed question
→ Chroma similarity search
→ retrieve relevant chunks
→ build RAG context
→ combine context + chat history + current question
→ Gemini
→ save assistant response to MySQL
→ return response to frontend

## 15. Testing

Successfully tested:

### Return policy

Question about return period returned the policy value:

30 calendar days.

### Shipping

Question about shipping returned information from the shipping policy.

### Warranty

Question about warranty returned information based on the warranty knowledge document.

### Multi-turn + RAG

Confirmed that conversation memory and RAG can work together.

## Key Phase 2 Mental Model

RAG = company knowledge

MySQL = conversation memory

Gemini = response generation

Chroma = vector storage and similarity search

Embedding model = converts text into vectors

## Phase 2 Status

COMPLETE

---

# PHASE 3 — TOOL CALLING

## Goal

Teach the LLM to use controlled application tools to retrieve data and perform supported actions.

The main idea learned:

> LLM decides what capability it needs → application validates and executes the tool → result is returned to the LLM → LLM continues or gives the final response.

---

## 1. What is a Tool?

A tool is an application capability that is exposed to the LLM.

A normal Python function does not automatically become an LLM tool.

Using LangChain's `@tool` decorator exposes a function with:

- Tool name
- Description
- Input schema
- Arguments and their expected types

Example:

```python
@tool
def get_order(order_id: str):
    ...
```

The LLM can see that the tool exists and understands that it expects an `order_id` string.

The LLM does not execute the Python function itself.

## 2. Tools Implemented

The following tools were implemented:

- `get_order`
- `get_customer`
- `cancel_order`
- `create_ticket`
- `request_refund`
- `search_knowledge_base`

### `get_order`

Retrieves order information from MySQL using the order ID.

### `get_customer`

Retrieves customer information from MySQL using the customer ID.

### `cancel_order`

Cancels an order only when its status is processing.

### `create_ticket`

Creates a support ticket in the database.

### `request_refund`

Creates a pending refund request.

This does not directly move money.

### `search_knowledge_base`

Wraps the Phase 2 RAG retrieval system as a tool so Gemini can decide when it needs company knowledge.

## 3. RAG Became a Tool

In Phase 2, RAG was automatically used by the chat endpoint.

In Phase 3, the existing RAG system was wrapped inside:

`search_knowledge_base(query)`

This means Gemini can decide when knowledge retrieval is necessary.

The conceptual distinction is:

- RAG = Knowledge
- Tools = Actions / live data
- Agent = Decision and orchestration

## 4. `bind_tools()`

`bind_tools()` makes the approved tools available to Gemini.

Example:

```python
model_with_tools = model.bind_tools(AVAILABLE_TOOLS)
```

This tells Gemini:

These are the tools you are allowed to request, and these are their schemas.

`bind_tools()` does not execute any tool.

It also does not force Gemini to use a tool.

## 5. Central Tool Registry

A centralized tool list was created in:

`backend/app/tools/available_tools.py`

It contains:

```python
AVAILABLE_TOOLS = [
    get_order,
    get_customer,
    cancel_order,
    create_ticket,
    request_refund,
    search_knowledge_base,
]
```

This provides one controlled list of tools available to the agent.

## 6. Tool Dispatcher

The dispatcher is located in:

`backend/app/tools/tool_executer.py`

It creates a mapping:

```python
tools = {tool.name: tool for tool in AVAILABLE_TOOLS}
```

and uses the requested tool name to find the corresponding Python tool.

The dispatcher also acts as an allowlist.

Unknown tool names are rejected instead of being executed.

Example:

```
Gemini requests:
delete_customer

        ↓

execute_tool()

        ↓

Unknown tool

        ↓

Rejected
```

This is an important application-side security boundary.

The LLM is not trusted to define or execute arbitrary application capabilities.

## 7. Tool Execution Flow

The complete Phase 3 tool-calling flow is:

```
User
 ↓
Gemini
 ↓
Gemini requests a tool
 ↓
Application receives tool call
 ↓
execute_tool()
 ↓
Approved Python tool executes
 ↓
Tool result
 ↓
ToolMessage
 ↓
Gemini receives result
 ↓
Gemini decides whether another tool is needed
 ↓
Final response
```

## 8. Tool Calling Loop

The agent uses a while loop because a request may require multiple tool-call rounds.

Simplified flow:

```python
while True:
    response = model_with_tools.invoke(messages)

    if not response.tool_calls:
        break

    messages.append(response)

    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(
            ToolMessage(...)
        )
```

The loop stops when Gemini returns a response with no tool calls.

The for loop handles multiple tool calls returned in the same model response.

## 9. Multiple Tool Calls

A single user request can require several tools.

Example:

```
User:
Check order ORD-10245 and create a ticket
for customer CUS-001.

        ↓

Gemini
        ↓
get_order()
        ↓
tool result
        ↓
Gemini
        ↓
create_ticket()
        ↓
tool result
        ↓
Gemini
        ↓
final response
```

This demonstrated that the system can perform multi-step tool interactions.

## 10. Multi-turn Tool Calling

The Phase 3 `/chat` endpoint uses the existing conversation history stored in MySQL.

The current user message is saved first and then included when conversation history is retrieved.

This allows Gemini to understand references from previous turns.

Example:

```
User:
Can I cancel ORD-10247?

Gemini:
The order is eligible for cancellation.
Would you like me to cancel it?

User:
Yes, cancel it.
```

Gemini can understand that it refers to `ORD-10247` because the conversation history is provided.

## 11. Application Business Rules

The LLM is not responsible for enforcing business rules.

For example, `cancel_order()` checks the actual database state:

```python
if order.status != "processing":
    return {
        "success": False,
        "error": ...
    }
```

Therefore:

```
Gemini suggests cancellation
        ↓
cancel_order()
        ↓
Database checked
        ↓
processing → allowed
shipped → rejected
```

This demonstrates an important principle:

The LLM can suggest an action, but the application enforces whether that action is allowed.

## 12. Tool Validation / Failure Cases Tested

### Nonexistent order

Tested:

`ORD-99999`

The system correctly reported that the order was not found and did not invent an order status.

### Nonexistent customer

Tested:

`CUS-999`

The system correctly reported that the customer was not found and did not invent an email address.

### Invalid cancellation

Attempted cancellation of a shipped order.

The tool rejected the action because only processing orders can be cancelled.

### Real cancellation

Created/tested:

`ORD-10247`

The order was initially:

`processing`

The user first asked:

> Can I cancel order ORD-10247?

The system checked the order and explained that cancellation was possible without immediately performing the action.

The user then explicitly confirmed:

> Yes, cancel it.

The cancellation tool executed and changed the database status to:

`cancelled`

This demonstrated that the tools perform real application actions rather than simulated responses.

## 13. Important Phase 3 Lesson

The system is already capable of performing real actions.

This means:

LLM + tools

is powerful, but also introduces risk.

The LLM can:

- choose the wrong tool
- produce incorrect arguments
- misunderstand a request
- attempt an inappropriate action

Therefore, tool execution cannot rely entirely on the LLM's judgment.

This leads directly into later concepts such as:

- Guardrails
- Application validation
- Human-in-the-loop approval
- Escalation

These are intentionally not implemented as part of Phase 3.

---

# Phase 4 — Agent Workflow

## Goal

Build a structured agent workflow using LangGraph so customer requests can be understood, routed through appropriate workflows, connected to tools/RAG, and completed through explicit state transitions.

---

## 1. Why Agent Workflows?

Phase 3 introduced tool calling.

Phase 3 flow:

User
→ Gemini
→ Tool Call
→ Application executes tool
→ Tool Result
→ Gemini
→ Final Response

Phase 4 introduces explicit workflow orchestration.

The workflow provides structure around:

- request understanding
- state
- routing
- conditional decisions
- tool execution
- final response generation

Conceptual flow:

User
→ FastAPI
→ LangGraph Workflow
→ Nodes / Routing
→ Tools or RAG
→ Final Response

---

## 2. Workflow

A workflow is a structured sequence of steps that can contain:

- nodes
- edges
- conditional branches
- tool calls
- final responses

Example cancellation workflow:

User wants cancellation
→ Understand request
→ Extract order ID
→ Get order
→ Check order status
→ Route based on status
→ Cancel if eligible
→ Return response

---

## 3. State

State contains the information currently available to the workflow.

Created:

`backend/app/schemas/workflow.py`

Our `SupportState` contains:

- `user_message`
- `chat_history`
- `intent`
- `order_id`
- `order_result`
- `knowledge_result`
- `final_response`

State allows information produced by one node to be used by later nodes.

Example:

`understand_request`

extracts:

`order_id = ORD-10245`

That value is stored in state and later used by the order/cancellation workflow.

---

## 4. Nodes

A LangGraph node is an ordinary Python function registered with the graph.

Example:

```python
graph.add_node("order_flow", order_flow)
```

The string is the LangGraph node name.

The Python function performs the actual work.

Nodes implemented include:

- `understand_request`
- `order_flow`
- `cancellation_flow`
- `general_flow`
- `generate_response`
- `order_not_found`
- `cancellation_eligible`
- `cancellation_completed`
- `cancellation_not_eligible`

---

## 5. Edges

Edges connect nodes and determine workflow movement.

Example:

```python
graph.add_edge(
    "general_flow",
    "generate_response"
)
```

This creates a fixed transition from `general_flow` to `generate_response`.

---

## 6. Conditional Edges

Conditional edges allow the workflow to branch based on the current state.

Example:

```python
graph.add_conditional_edges(
    "understand_request",
    route_by_intent
)
```

The routing function examines the state and returns the next node.

Intent routing:

ORDER_STATUS
    ↓
order_flow

ORDER_CANCELLATION
    ↓
cancellation_flow

GENERAL_QUERY
    ↓
general_flow

---

## 7. Routing vs Node

Important distinction:

Routing answers:

"WHERE should the workflow go?"

A node answers:

"WHAT work should be performed?"

For example:

`route_cancellation_result()`

decides whether the workflow should go to:

- `order_not_found`
- `cancellation_eligible`
- `cancellation_not_eligible`

It does not perform the cancellation itself.

---

## 8. Structured Output for Intent Classification

Initially, intent routing used substring matching.

Example:

```python
if "ORDER" in state["intent"].upper():
```

This was unreliable because Gemini could return natural-language text containing the word "order" instead of a clean intent.

We changed the workflow to use Pydantic structured output.

```python
class IntentResult(BaseModel):
    intent: Literal[
        "ORDER_STATUS",
        "ORDER_CANCELLATION",
        "GENERAL_QUERY"
    ]
    order_id: str
```

This provides a predictable structure for the workflow.

Pydantic defines the expected structure and allowed values.

Gemini performs the semantic classification.

The router uses the structured intent to select the workflow branch.

---

## 9. Order ID Extraction

The workflow also extracts an order ID from the customer message.

Example:

> Can I cancel my order ORD-10245?

Structured result:

- `intent = ORDER_CANCELLATION`
- `order_id = ORD-10245`

If the current message does not contain an order ID, the workflow can use conversation history to determine whether the customer is referring to an order from an earlier message.

---

## 10. MySQL Conversation Memory → Workflow State

Phase 1 and Phase 2 already stored conversation history in MySQL.

Phase 4 connected that persistent memory to the workflow.

Flow:

MySQL
 ↓
Retrieve recent messages
 ↓
Convert to LangChain messages
 ↓
chat_history
 ↓
SupportState
 ↓
understand_request

Important distinction:

MySQL stores persistent conversation memory.

SupportState contains the active information available during the current workflow execution.

---

## 11. Multi-Turn Context

The workflow initially failed to understand:

> Where is my order ORD-10245?
> Can I cancel it?

The second message resulted in an order-not-found response.

Cause:

The conversation was stored in MySQL, but the workflow was not receiving the previous conversation history.

Therefore the second workflow execution had no order ID.

We added `chat_history` to `SupportState` and provided previous conversation messages to `understand_request`.

After the change:

User:
Where is my order ORD-10245?

Assistant:
Your order ORD-10245 has been shipped.

User:
Can I cancel it?

Assistant:
Order ORD-10245 cannot be cancelled because its current status is 'shipped'.

This confirmed that the workflow could use previous conversation context to resolve the reference "it".

---

## 12. Order Status Workflow

The order-status workflow is:

START
 ↓
understand_request
 ↓
ORDER_STATUS
 ↓
order_flow
 ↓
get_order
 ↓
route_order_result

Branches:

Order not found
 ↓
order_not_found
 ↓
END

or:

Order found
 ↓
generate_response
 ↓
END

---

## 13. Cancellation Workflow

The cancellation workflow is:

START
 ↓
understand_request
 ↓
ORDER_CANCELLATION
 ↓
cancellation_flow
 ↓
get_order
 ↓
route_cancellation_result

Branches:

Order not found
 ↓
order_not_found
 ↓
END

Processing
 ↓
cancellation_eligible
 ↓
cancel_order
 ↓
cancellation_completed
 ↓
END

Other status
 ↓
cancellation_not_eligible
 ↓
END

The `cancel_order` tool performs the actual database mutation.

Guardrails and human approval are intentionally not implemented yet because they belong to Phase 5.

---

## 14. RAG Inside the Workflow

The existing Phase 2 RAG system was reused as a workflow capability.

For a general knowledge question:

User
 ↓
understand_request
 ↓
GENERAL_QUERY
 ↓
general_flow
 ↓
search_knowledge_base
 ↓
generate_response
 ↓
END

This allows the workflow to decide which path should use the knowledge base.

---

## 15. FastAPI Integration

The Phase 3 Gemini tool loop was removed from the `/chat` endpoint.

Previously:

`/chat`
 ↓
Gemini + while tool loop
 ↓
`execute_tool()`
 ↓
Final response

Phase 4:

`/chat`
 ↓
Create/retrieve conversation
 ↓
Save user message
 ↓
Retrieve conversation history
 ↓
Create `SupportState`
 ↓
`workflow.invoke()`
 ↓
Extract `final_response`
 ↓
Save assistant response
 ↓
Return response

The API remains responsible for conversation persistence.

LangGraph is responsible for workflow orchestration.

---

## 16. Phase 4 Testing

Successfully tested:

- General RAG questions
- Return policy
- Shipping policy
- Existing order lookup
- Nonexistent order lookup
- Cancellation of shipped orders
- Structured intent classification
- Order ID extraction
- Cancellation workflow
- Multi-turn conversation context
- FastAPI → LangGraph integration

### Existing order

Test:

> Where is my order ORD-10245?

Result:

The system correctly identified the order as shipped and returned tracking number TRK123.

### Nonexistent order

Test:

> Where is my order ORD-99999?

Result:

The system correctly reported that the order was not found and did not invent an order status.

### Cancellation of shipped order

Test:

> Can I cancel order ORD-10245?

Result:

The system checked the actual database status and rejected cancellation because the order was shipped.

### Cancellation of processing order

Test:

> Can I cancel my order ORD-6FC673CE? (status = processing)

Result:

The workflow extracted `ORD-6FC673CE`, checked database status, routed to `cancellation_eligible`, executed `cancel_order`, updated status to `cancelled`, and routed to `cancellation_completed` with the confirmation response:
> Your order ORD-6FC673CE has been cancelled successfully.

### Multi-turn

Test:

> Where is my order ORD-10245?
> Can I cancel it?

Result:

The second request correctly resolved "it" to `ORD-10245` using `chat_history`, checked the order, and rejected cancellation because the order was shipped.

---

## 17. Phase 3 vs Phase 4 Detailed Comparison

The fundamental shift between Phase 3 and Phase 4 is:
- **Phase 3 tested tool capability**: Can the LLM select and call our tools?
- **Phase 4 tested workflow orchestration**: Can the application control a reliable multi-step support process around those tools?

### 🧪 Test Comparison Matrix

| Test Scenario | Phase 3 (Tool Calling) | Phase 4 (Workflow Orchestration) |
|---|---|---|
| **Return policy** | Gemini called `search_knowledge_base` tool directly | `understand_request` → `GENERAL_QUERY` intent → `general_flow` knowledge search → response generation |
| **Order status** | Gemini called `get_order` tool directly | `understand_request` → `ORDER_STATUS` intent → `order_flow` → `get_order` → `route_order_result` → response |
| **Non-existent order** | Tool returned error message to Gemini | `get_order` returns `None` → `route_order_result` routes to dedicated `order_not_found` node → controlled response |
| **Cancellation (Shipped)** | Gemini could attempt `cancel_order`, tool rejected it | `understand_request` → `ORDER_CANCELLATION` → `get_order` → inspect status (`shipped`) → `cancellation_not_eligible` node |
| **Cancellation (Processing)** | Tool successfully cancelled order when called | `understand_request` → `cancellation_flow` → `get_order` → `processing` → `cancellation_eligible` → `cancel_order` → `cancellation_completed` |
| **Multiple operations** | Gemini called `get_order`, `get_customer`, `create_ticket` sequentially in tool loop | The workflow Graph explicitly controls execution flow and state transitions |
| **Invalid Customer ID** | Gemini hallucinated customer ID `ORD-10245` in tool argument | Highlights need for explicit workflow routing & application validation (Phase 5 guardrails) |
| **Multi-turn Context** | Tool loop executed, but history integration into tool state was basic | Conversation history explicitly populated into `SupportState.chat_history` before workflow invocation |
| **"Can I cancel it?"** | Depended entirely on LLM prompt window | Passed explicitly: `chat_history` → Gemini resolves reference "it" to `ORD-10245` → structured routing to `cancellation_flow` |

---

## 18. Phase 3 vs Phase 4 Architecture & mental model

### Phase 3 Architecture: What tool should I use?
```text
User
 ↓
Gemini
 ↓
Tool selection
 ↓
Tool execution
 ↓
Tool result
 ↓
Gemini
 ↓
Final Response
```
*Goal: Give the LLM capabilities.*

### Phase 4 Architecture: What step should happen next?
```text
User
 ↓
FastAPI
 ↓
MySQL (Retrieve history)
 ↓
SupportState (user_message + chat_history)
 ↓
understand_request (Pydantic Intent Classification)
 ↓
LangGraph Router (Conditional Edges)
 ├── ORDER_STATUS ─────► order_flow ──► get_order ──► route_order_result ──► generate_response
 ├── ORDER_CANCELLATION ► cancellation_flow ──► get_order ──► eligibility check ──► cancel_order
 └── GENERAL_QUERY ────► general_flow ──► search_knowledge_base ──► generate_response
 ↓
Final Response Saved & Returned
```
*Goal: Application controls the workflow process around those capabilities.*

---

## 📓 Notebook Key Takeaways

- **Phase 3 = Tool capability**: Gemini decides which tool to request.
- **Phase 4 = Workflow orchestration**: The workflow decides what step should happen next after each result.
- **Phase 3 question**: *"What tool should I use?"*
- **Phase 4 question**: *"What step should happen next?"*