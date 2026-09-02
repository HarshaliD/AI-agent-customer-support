import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


def get_ai_response(messages) -> str:
    response = model.invoke(messages)
    return response.text