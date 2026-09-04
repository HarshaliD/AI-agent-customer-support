from backend.app.rag.document_loader import load_documents
from backend.app.rag.chunker import split_documents
from backend.app.rag.vector_store import create_vector_store


documents = load_documents()

chunks = split_documents(documents)

vector_store = create_vector_store(chunks)

print("Vector store ready!")

query = "How long do I have to return a product?"

print("Searching...")

results = vector_store.similarity_search(
    query,
    k=2,
)

print("\nRetrieved chunks:\n")

for i, result in enumerate(results, start=1):
    print(f"--- Result {i} ---")
    print(result.page_content)
    print("Source:", result.metadata.get("source"))