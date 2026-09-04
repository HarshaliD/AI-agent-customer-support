from backend.app.rag.document_loader import load_documents
from backend.app.rag.chunker import split_documents
from backend.app.rag.vector_store import create_vector_store


documents = load_documents()

print(f"Loaded documents: {len(documents)}")

chunks = split_documents(documents)

print(f"Created chunks: {len(chunks)}")

print("3. About to create vector store")

vector_store = create_vector_store(chunks)

print("4. Returned from create_vector_store()")

print("Documents stored in Chroma successfully!")