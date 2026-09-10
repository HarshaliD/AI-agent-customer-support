# Errors and Lessons Log

## Phase 1 Lessons & Debugging Record

### 1. Database Connection & Environment Management
- **Issue**: Database connection setup requires MySQL credentials (`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_DATABASE`) from environment variables.
- **Fix**: Used `python-dotenv` with `.env` and `.env.example` templates, ensuring DB credentials are never hardcoded.

### 2. Multi-turn Chat Context Format
- **Issue**: Simply sending raw strings or single messages to the LLM prevents multi-turn memory.
- **Fix**: Convert stored database records into explicit LangChain message classes (`HumanMessage` and `AIMessage`) before passing the history array to `ChatGoogleGenerativeAI`.

### 3. Model Latency & Quota Optimization
- **Issue**: Standard preview/reasoning models (e.g. `gemini-3.6-flash`) can exhibit higher latency (~17-30s per request) and strict free-tier rate limits (20 requests/day).
- **Fix**: Switched model default in `chat_service.py` to `gemini-3.5-flash-lite` (configurable via `GEMINI_MODEL`), reducing response times down to ~2s. Additionally, added context window slicing (`messages[-10:]`) in `chat.py` to keep prompt payload small and fast.

# Phase 2 — Errors and Lessons

## 1. Chroma / HNSW Native Library Issue

### Problem

The existing Python 3.12 Conda environment had native dependency problems while working with Chroma/HNSW.

This caused issues with the HNSW-related native components.

### Lesson

Some Python packages are dependent on compiled/native libraries and may not work correctly in every Python environment.

### Solution

Created a separate standard CPython 3.11 virtual environment:

`.venv311`

Verified:

- Python 3.11.9
- `hnswlib` 0.8.0 imported successfully

This allowed Chroma and HNSW to work correctly.

### General lesson

When a package fails at the native-library level, the problem may be the Python environment or binary compatibility rather than the application code itself.

---

## 2. langchain-text-splitters Dependency

### Problem

`RecursiveCharacterTextSplitter` required the text-splitter package.

### Solution

Installed:

`langchain-text-splitters`

### Lesson

LangChain functionality can be split into separate packages, so imports and dependencies should be checked when adding a new component.

---

## 3. Misunderstanding `chunk_size`

### Initial assumption

A `chunk_size` of 500 meant every chunk would contain exactly 500 characters.

### Correction

`RecursiveCharacterTextSplitter` treats the value as a target/upper size and uses separators while splitting.

### Lesson

Chunk size is not necessarily exact.

---

## 4. Misunderstanding `k` in Similarity Search

### Observation

A return-policy question with `k=2` returned two chunks from essentially the same policy document.

### Initial assumption

`k=2` might mean two different documents.

### Correction

`k=2` means the two nearest chunks.

The same document may provide both chunks.

### Lesson

`k` controls the number of retrieved chunks, not the number of source documents.

---

## 5. Confusing Chroma With the Embedding Model

### Initial confusion

The roles of Chroma and embeddings were unclear.

### Correction

Embedding model:

Text
→ vector

Chroma:

Vector + document content + metadata
→ stores/searches them

### Lesson

The vector database does not create the semantic embedding itself.

---

## 6. Query Is Not Stored During Retrieval

### Misunderstanding

It was initially unclear whether the user's question gets added to Chroma.

### Correction

During retrieval:

User question
→ embedding
→ similarity search against already stored vectors

The query vector is used for searching and is not automatically inserted into the knowledge base.

### Lesson

Indexing and retrieval are separate operations.

---

## 7. `ChatPromptValue` vs Message List

### Problem

While integrating the RAG prompt, the prompt object and the actual message list needed by the model were temporarily confused.

### Correction

`rag_prompt.invoke(...)` returns a `ChatPromptValue`.

The model call uses the messages contained inside it:

`prompt.messages`

### Lesson

A prompt template is used to construct the final message structure. The resulting `ChatPromptValue` contains the actual LangChain messages.

---

## 8. `MessagesPlaceholder` Understanding

### Initial confusion

It was unclear why `{question}` could not simply be used for chat history.

### Correction

`question` is one text value.

`chat_history` is a list of message objects containing different roles.

`MessagesPlaceholder("chat_history")` provides a location where those existing messages can be inserted without converting the whole history into one text block.

### Lesson

Use a placeholder when inserting a list of existing LangChain messages.

---

## 9. Vector Store Should Not Be Rebuilt on Every Chat Request

### Problem

Loading/creating the vector store inside every request would be unnecessary and expensive.

### Solution

Load the persisted Chroma store once during FastAPI startup and keep the Python vector-store object in:

`app.state.vector_store`

### Lesson

Application-level resources that can be reused should be initialized once rather than repeatedly per request.

---

## 10. Gemini Automatic Function Calling Warning

### Observation

During testing, Gemini emitted a warning mentioning automatic function calling (AFC).

### Important point

The RAG generation still completed successfully.

### Lesson

The warning did not indicate that the Phase 2 RAG pipeline had failed.

Tool calling belongs to Phase 3, so this was treated as a warning encountered during the environment/model integration rather than as a Phase 2 blocker.

---

# Phase 2 Overall Lessons

1. RAG has separate stages:
   loading → chunking → embedding → indexing → retrieval → context → generation

2. Conversation memory and RAG solve different problems.

3. Vector stores store/search embeddings; they do not replace the embedding model.

4. Retrieval returns chunks, not necessarily whole documents.

5. Prompt construction and conversation history are separate concerns.

6. Persistent vector storage avoids rebuilding the index every time the application starts or receives a request.

7. Environment and native dependency compatibility can affect vector database libraries.

## Phase 2 Status

COMPLETE

---

# PHASE 3 — ERRORS & LESSONS

## 1. Gemini Generated an Invalid Customer ID

### What happened

During a refund-related test, Gemini generated/used an incorrect customer ID instead of a valid customer ID from the database.

It attempted to call:

```text
get_customer("ORD-10245")
```

even though `ORD-10245` is an order ID, not a customer ID.

### What I learned

LLMs can generate incorrect tool arguments even when the tool schema is correct.

The application cannot blindly trust LLM-generated arguments.

---

## 2. Gemini Did Not Choose the Expected Refund Tool

### What happened

During a refund request, Gemini did not call:

`request_refund()`

as expected.

Instead, it attempted other tool calls and eventually created a support ticket.

### What I learned

Providing the LLM with the correct tools does not guarantee that it will always choose the correct tool or workflow.

This is one reason we will need a more structured agent workflow later.

---

## 3. Unknown Tool Was Rejected

### What happened

I tested the dispatcher with an invalid tool:

`delete_customer`

The dispatcher rejected it with:

`Unknown tool: delete_customer`

### What I learned

The application maintains an allowlist of approved tools.

The LLM cannot be allowed to execute arbitrary application functions.

---

## 4. Real Database Mutation During Cancellation Test

### What happened

When I confirmed:

> Yes, cancel it.

for `ORD-10247`, the cancellation tool actually changed the database:

`processing` → `cancelled`

### What I learned

Tools can perform real side effects, not just return information.

This is important because actions that modify data will eventually need stronger validation, guardrails, and potentially human approval.

---

## 5. No Dedicated Unexpected Tool-Failure Handling Yet

### What happened

We did not encounter an actual database/tool crash during testing.

However, we identified that if a tool raises an unexpected exception, the current `execute_tool()` implementation does not yet provide a dedicated recovery mechanism.

### What I learned

There is a difference between:

- A tool successfully returning a business error
- A tool unexpectedly crashing

For example:

- Order not found → expected tool result
- Database connection failure → unexpected tool failure

---

# PHASE 4 — ERRORS & LESSONS

## 1. Initial Intent Routing Using Substring Matching Was Unreliable

### Error

The initial routing logic checked whether the returned intent contained the word `"ORDER"`.

Example:

```python
if "ORDER" in state["intent"].upper():
```

Gemini returned a natural-language response containing the word "order", which could incorrectly route the request to the order workflow.

### Cause

The LLM response was not constrained to a fixed structured intent.

### Fix

Introduced Pydantic structured output with `Literal`:

```python
class IntentResult(BaseModel):
    intent: Literal[
        "ORDER_STATUS",
        "ORDER_CANCELLATION",
        "GENERAL_QUERY"
    ]
```

The router now checks the exact intent value.

### Lesson

Do not use loose substring matching for important workflow routing.

Use structured output when the application expects a fixed set of values.

---

## 2. SupportState Was Accidentally Undefined

### Error

After modifying `workflow.py`, Uvicorn failed to start with:

```text
NameError: name 'SupportState' is not defined
```

The error occurred at:

```python
def understand_request(state: SupportState):
```

### Cause

The required imports at the top of `workflow.py` were accidentally removed while modifying the file.

### Fix

Restored:

```python
from backend.app.schemas.workflow import SupportState, IntentResult
```

along with the other required imports.

### Lesson

When replacing individual functions in a Python module, preserve the module-level imports used by the rest of the file.

---

## 3. Multi-Turn Reference Initially Failed

### Error

This conversation initially failed:

> User: Where is my order ORD-10245?
> User: Can I cancel it?

The second message resulted in:

> *"I'm sorry, but I couldn't find that order."*

### Cause

The conversation history was being stored in MySQL and retrieved by the API, but it was not being passed into the LangGraph workflow.

Therefore, the second workflow execution did not know which order "it" referred to.

### Fix

Added `chat_history` to `SupportState`.

The API now passes the retrieved conversation history into the workflow.

`understand_request` uses the previous conversation together with the current user message.

### Result

The same conversation then worked:

> User: Where is my order ORD-10245?
> Assistant: Your order ORD-10245 has been shipped.
> User: Can I cancel it?
> Assistant: Order ORD-10245 cannot be cancelled because its current status is 'shipped'.

### Lesson

Storing conversation history is not enough.

The active workflow must receive the relevant conversation context.


