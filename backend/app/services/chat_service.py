import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

model = ChatGoogleGenerativeAI(
    model=model_name
)


def get_ai_response(messages) -> str:
    response = model.invoke(messages)
    return response.text