# AI Customer Support Agent — Architecture

## Current Phase

**Phase 1 — Basic LLM Chat**

## 1. High-Level Architecture

```text
Client / Frontend
       |
       | POST /chat
       ↓
FastAPI Backend
       |
       ↓
Chat API
       |
       ├──────────────→ MySQL
       |                 |
       |                 ├── conversations
       |                 └── messages
       |
       ↓
Chat Service
       |
       ↓
LangChain
       |
       ↓
Google Gemini
       |
       ↓
Assistant Response
       |
       ↓
Save response to MySQL
       |
       ↓
FastAPI Response
```

## 2. Request Flow

### New Conversation

```text
Client → POST /chat
       → conversation_id = None
       → Create Conversation
       → MySQL generates conversation ID
       → Save user message
       → Retrieve conversation history
       → Convert history to LangChain messages
       → Send messages to Gemini
       → Receive assistant response
       → Save assistant response
       → Return response + conversation_id
```

### Existing Conversation

```text
Client → POST /chat
       → conversation_id = existing ID
       → Save new user message
       → Retrieve messages belonging to conversation
       → Convert database messages to LangChain messages
       → Send conversation history to Gemini
       → Receive assistant response
       → Save assistant response
       → Return response
```

## 3. Backend Components

### FastAPI

Handles HTTP requests and API routing.

Main application:

`backend/app/main.py`

Chat endpoint:

`POST /chat`

### Chat API

File:

`backend/app/api/chat.py`

Responsibilities:

- Receive chat requests
- Create or continue conversations
- Save user messages
- Retrieve conversation history
- Convert database messages into LangChain messages
- Save assistant responses
- Return the response

### Chat Service

File:

`backend/app/services/chat_service.py`

Responsibilities:

- Initialize the Gemini model
- Invoke Gemini through LangChain
- Return the assistant's text response

### Pydantic Schema

File:

`backend/app/schemas/chat.py`

```python
class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None
```

`conversation_id` is optional because the first message does not belong to an existing conversation.

## 4. Database Architecture

MySQL provides persistent conversation storage.

Database:

`ai_customer_support`

SQLAlchemy is used as the ORM.

Database configuration:

`backend/app/database/database.py`

Database initialization:

`backend/app/database/init_db.py`

## 5. Database Tables

### conversations

Stores one record for each conversation.

```text
id
created_at
updated_at
```

### messages

Stores individual messages belonging to conversations.

```text
id
conversation_id
role
content
created_at
```

Relationship:

```text
Conversation
     |
     | 1
     |
     | many
     ↓
 Messages
```

The same conversation ID is used for multiple messages.

## 6. Conversation Memory

The application does not depend on Gemini remembering previous API calls.

```text
MySQL
  ↓
Stored conversation history
  ↓
Application retrieves messages
  ↓
Convert to LangChain messages
  ↓
HumanMessage / AIMessage
  ↓
Gemini
```

Therefore:

- **MySQL** provides persistent storage.
- **FastAPI/application logic** manages conversation retrieval.
- **LangChain** represents messages and handles model invocation.
- **Gemini** generates the response.

## 7. Database Session vs Conversation

### Database Session

```python
db = SessionLocal()
```

Provides a temporary way for the current request to interact with MySQL.

It is closed after the request:

```python
db.close()
```

### Conversation

A persistent record in the `conversations` table identified by `conversation_id`.

## 8. Phase 1 Scope

Implemented:

- FastAPI
- Pydantic
- Gemini
- LangChain
- MySQL
- SQLAlchemy
- Conversation storage
- Message storage
- Conversation ID handling
- Conversation history retrieval
- LangChain message conversion
- Basic multi-turn conversation

Not implemented yet:

- RAG
- Vector database
- Pinecone
- Knowledge retrieval
- Tool calling
- Agents
- Multi-agent architecture
- Human-in-the-loop
- Text-to-SQL
- Advanced guardrails
- Evaluation framework
- Observability
- Docker
- AWS deployment

These belong to later phases.
