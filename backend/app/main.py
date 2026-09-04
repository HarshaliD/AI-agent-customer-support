from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.chat import router as chat_router
from backend.app.rag.vector_store import load_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading vector store...")

    app.state.vector_store = load_vector_store()

    print("Vector store loaded!")

    yield

    print("Application shutting down...")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "AI Customer Support Agent is running"}