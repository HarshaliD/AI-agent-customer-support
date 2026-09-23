RAG_DISTANCE_THRESHOLD = 0.70


def retrieve_documents(vector_store, question, k=2):
    results = vector_store.similarity_search_with_score(
        question,
        k=k,
    )

    print("\n--- RAG Retrieval ---")

    for document, score in results:
        print("Source:", document.metadata.get("source"))
        print("Distance:", score)
        print("Content:", document.page_content[:200])

    # Best result = lowest distance
    if results:
        best_document, best_score = min(
            results,
            key=lambda item: item[1]
        )

        print("Best Distance:", best_score)
        print("Threshold:", RAG_DISTANCE_THRESHOLD)

        if best_score > RAG_DISTANCE_THRESHOLD:
            print("Relevant: False")
            print("No sufficiently relevant knowledge found.")

            return []

        print("Relevant: True")

    return results


def build_context(results):
    context = "\n\n".join(
        document.page_content
        for document, score in results
    )

    return context