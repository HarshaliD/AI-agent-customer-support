from langchain_core.tools import tool

from backend.app.rag.retrieval import retrieve_documents, build_context
from backend.app.rag.vector_store import load_vector_store


@tool
def search_knowledge_base(query: str):
    """Search NovaMart's knowledge base for customer support information."""

    vector_store = load_vector_store()

    results = retrieve_documents(
        vector_store,
        query,
        k=2,
    )

    return build_context(results)