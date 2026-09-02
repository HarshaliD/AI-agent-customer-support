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

