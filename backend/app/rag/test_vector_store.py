from backend.app.rag.vector_store import load_vector_store


vector_store = load_vector_store()

print("Vector store loaded successfully!")

results = vector_store.similarity_search(
    "How long do I have to return a product?",
    k=2,
)

print("\nRetrieved chunks:\n")

for i, result in enumerate(results, start=1):
    print(f"--- Result {i} ---")
    print(result.page_content)
    print("Source:", result.metadata.get("source"))