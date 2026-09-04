from backend.app.rag.document_loader import load_documents
from backend.app.rag.chunker import split_documents
from backend.app.rag.vector_store import create_vector_store
from backend.app.rag.retrieval import retrieve_documents, build_context
from backend.app.rag.prompt import rag_prompt


# 1. Load documents
documents = load_documents()

# 2. Split into chunks
chunks = split_documents(documents)

# 3. Create vector store
vector_store = create_vector_store(chunks)

# 4. Customer question
question = "How long do I have to return a product?"

# 5. Retrieve relevant chunks
results = retrieve_documents(
    vector_store,
    question,
    k=2,
)

# 6. Build context from retrieved chunks
context = build_context(results)

# 7. Put context + question into prompt template
prompt = rag_prompt.invoke({
    "context": context,
    "question": question,
})

print("\n===== FINAL PROMPT =====\n")
print(prompt)