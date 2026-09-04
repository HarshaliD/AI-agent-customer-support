from backend.app.rag.document_loader import load_documents
from backend.app.rag.chunker import split_documents
from backend.app.rag.vector_store import create_vector_store
from backend.app.rag.retrieval import retrieve_documents, build_context
from backend.app.rag.prompt import rag_prompt
from backend.app.rag.generation import generate_answer


# 1. Load documents
documents = load_documents()

# 2. Split documents into chunks
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

# 6. Build context
context = build_context(results)

# 7. Create augmented prompt
prompt = rag_prompt.invoke({
    "context": context,
    "question": question,
})

# 8. Generate answer using Gemini
answer = generate_answer(prompt)

print("\n===== RAG ANSWER =====\n")
print(answer)