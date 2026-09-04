import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


def embed_documents(documents):
    texts = [document.page_content for document in documents]

    vectors = embeddings.embed_documents(texts)

    return vectors