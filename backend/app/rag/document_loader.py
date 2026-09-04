from pathlib import Path
from langchain_community.document_loaders import TextLoader


KNOWLEDGE_BASE_PATH = Path("knowledge_base")


def load_documents():
    documents = []

    for file_path in KNOWLEDGE_BASE_PATH.glob("*.txt"):
        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

        documents.extend(loader.load())

    return documents