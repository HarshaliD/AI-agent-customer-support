from pathlib import Path

from langchain_chroma import Chroma
from backend.app.rag.embeddings import embeddings


# --------------------------------------------------
# Configuration
# --------------------------------------------------

VECTOR_STORE_PATH = "chroma_db"

TEST_CASES = [
    # Known knowledge-base questions
    {
        "id": 1,
        "query": "What is NovaMart's return policy?",
        "label": "KNOWN",
    },
    {
        "id": 2,
        "query": "How many days do I have to return a product?",
        "label": "KNOWN",
    },
    {
        "id": 3,
        "query": "How long does NovaMart shipping take?",
        "label": "KNOWN",
    },
    {
        "id": 4,
        "query": "What is NovaMart's warranty policy?",
        "label": "KNOWN",
    },

    # Questions outside the knowledge base
    {
        "id": 30,
        "query": "Who is the Prime Minister of India?",
        "label": "UNKNOWN",
    },
    {
        "id": 31,
        "query": "What is the capital of France?",
        "label": "UNKNOWN",
    },
    {
        "id": 32,
        "query": "Tell me a joke.",
        "label": "UNKNOWN",
    },
]


# --------------------------------------------------
# Load existing Chroma vector store
# --------------------------------------------------

def load_vector_store():
    print("Loading Chroma vector store...")

    vector_store = Chroma(
        persist_directory=VECTOR_STORE_PATH,
        embedding_function=embeddings,
    )

    print("Vector store loaded.\n")

    return vector_store


# --------------------------------------------------
# Run calibration queries
# --------------------------------------------------

def run_calibration(vector_store):

    results = []

    for test_case in TEST_CASES:

        query = test_case["query"]
        label = test_case["label"]

        retrieved = vector_store.similarity_search_with_score(
            query,
            k=2,
        )

        # Lowest distance = most relevant result
        best_document, best_score = min(
            retrieved,
            key=lambda item: item[1]
        )

        source = best_document.metadata.get(
            "source",
            "unknown"
        )

        results.append({
            "id": test_case["id"],
            "query": query,
            "label": label,
            "distance": best_score,
            "source": source,
        })

    return results


# --------------------------------------------------
# Display results
# --------------------------------------------------

def print_results(results):

    print("\n" + "=" * 100)
    print("RAG CALIBRATION RESULTS")
    print("=" * 100)

    for result in results:

        print(f"\nID       : {result['id']}")
        print(f"Query    : {result['query']}")
        print(f"Label    : {result['label']}")
        print(f"Distance : {result['distance']:.6f}")
        print(f"Source   : {result['source']}")

    print("\n" + "=" * 100)


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    vector_store = load_vector_store()

    results = run_calibration(vector_store)

    print_results(results)