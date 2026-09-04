from backend.app.rag.retrieval import retrieve_documents, build_context
from backend.app.rag.prompt import rag_prompt
from backend.app.rag.generation import generate_answer


def get_rag_response(vector_store, question):
    results = retrieve_documents(
        vector_store,
        question,
        k=2,
    )

    context = build_context(results)

    prompt = rag_prompt.invoke({
        "context": context,
        "question": question,
    })

    answer = generate_answer(prompt)

    return answer