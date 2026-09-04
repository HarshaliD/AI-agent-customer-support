from backend.app.rag.embeddings import embeddings


text = "Customers can return products within 30 days."

print("Starting embedding...")

vector = embeddings.embed_query(text)

print("Embedding completed!")
print("Vector type:", type(vector))
print("Vector length:", len(vector))
print("First 5 values:", vector[:5])