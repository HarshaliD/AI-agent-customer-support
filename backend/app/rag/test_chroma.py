import chromadb

from backend.app.rag.embeddings import embeddings

print("1. Creating Gemini embedding...")

text = "Customers can return products within 30 days."

vector = embeddings.embed_query(text)

print("2. Embedding created!")
print("Vector length:", len(vector))

print("3. Creating in-memory Chroma client...")

client = chromadb.Client(
    settings=chromadb.Settings(
        chroma_api_impl="chromadb.api.segment.SegmentAPI"
    )
)

print("4. Creating collection...")

collection = client.create_collection(
    name="gemini_test",
    embedding_function=None,
)

print("5. Collection created!")

print("6. Adding Gemini vector directly...")

try:
    collection.add(
        ids=["test_1"],
        embeddings=[vector],
        documents=[text],
    )

    print("7. Vector added!")

except BaseException as e:
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR MESSAGE:", e)

print("8. Collection count:", collection.count())

print("9. Searching for similar text...")

query_vector = embeddings.embed_query(
    "How long do I have to return something?"
)

results = collection.query(
    query_embeddings=[query_vector],
    n_results=1,
)

print("10. Search completed!")
print("Result:", results["documents"][0][0])