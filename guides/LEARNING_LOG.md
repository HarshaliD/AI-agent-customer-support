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
