from backend.app.rag.document_loader import load_documents
from backend.app.rag.chunker import split_documents
from backend.app.rag.vector_store import create_vector_store
from backend.app.rag.rag_service import get_rag_response


# 1. Load documents
documents = load_documents()

# 2. Split documents into chunks
chunks = split_documents(documents)

# 3. Create vector store
vector_store = create_vector_store(chunks)

# 4. Ask a question
question = "How long do I have to return a product?"

# 5. Get RAG response
answer = get_rag_response(
    vector_store,
    question,
)

print("\n===== RAG SERVICE ANSWER =====\n")
print(answer)