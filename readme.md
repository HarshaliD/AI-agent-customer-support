# AI Customer Support Agent

## Phase 1 — Basic LLM Chat

Phase 1 establishes the foundation for an AI-powered customer support system with **FastAPI, LangChain, Google Gemini, and MySQL**.

## What is Implemented

- FastAPI backend with a `POST /chat` endpoint
- Google Gemini integration through LangChain
- Pydantic request validation
- MySQL database with SQLAlchemy
- Conversation and message persistence
- Conversation ID–based chat sessions
- Basic multi-turn conversation memory

## Architecture

```text
Client
  ↓
FastAPI
  ↓
Chat Service
  ↓
LangChain
  ↓
Google Gemini
  ↓
Response
  ↓
MySQL
```

For multi-turn conversations, previous messages are retrieved from MySQL, converted into LangChain messages, and sent to Gemini as conversation context.

## Database

Current tables:

- `conversations`
- `messages`

## Phase 1 Status

**Completed**

## Next Phase

**Phase 2 — RAG Integration**

The project will be expanded incrementally with knowledge retrieval and additional AI agent capabilities in later phases.
