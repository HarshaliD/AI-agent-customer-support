def retrieve_documents(vector_store, question, k=2):
    results = vector_store.similarity_search(
        question,
        k=k,
    )

    return results


def build_context(results):
    context = "\n\n".join(
        document.page_content
        for document in results
    )

    return context