from langchain_chroma import Chroma
from backend.app.rag.embeddings import embeddings


VECTOR_STORE_PATH = "chroma_db"


def create_vector_store(chunks):
    print("1. Entered create_vector_store()")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH,
    )

    print("2. Chroma.from_documents() finished")

    return vector_store


def load_vector_store():
    vector_store = Chroma(
        persist_directory=VECTOR_STORE_PATH,
        embedding_function=embeddings,
    )

    return vector_store