from fastapi import FastAPI
from backend.app.api.chat import router as chat_router

app = FastAPI()

app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "AI Customer Support Agent is running"}

#uvicorn backend.app.main:app --reload