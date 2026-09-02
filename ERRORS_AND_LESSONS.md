# Errors and Lessons Log

## Phase 1 Lessons & Debugging Record

### 1. Database Connection & Environment Management
- **Issue**: Database connection setup requires MySQL credentials (`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_DATABASE`) from environment variables.
- **Fix**: Used `python-dotenv` with `.env` and `.env.example` templates, ensuring DB credentials are never hardcoded.

### 2. Multi-turn Chat Context Format
- **Issue**: Simply sending raw strings or single messages to the LLM prevents multi-turn memory.
- **Fix**: Convert stored database records into explicit LangChain message classes (`HumanMessage` and `AIMessage`) before passing the history array to `ChatGoogleGenerativeAI`.

### 3. Model Compatibility & Automatic Function Calling Warnings
- **Lesson**: When utilizing modern Gemini models with `langchain-google-genai`, ensure API keys and model parameters align with supported endpoints (`gemini-3.6-flash`).
