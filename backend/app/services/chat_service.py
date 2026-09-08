import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.tools.available_tools import AVAILABLE_TOOLS


load_dotenv()


model_name = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


# Plain Gemini model
model = ChatGoogleGenerativeAI(
    model=model_name
)


# Gemini model with all approved tools
model_with_tools = model.bind_tools(AVAILABLE_TOOLS)


def get_ai_response(messages) -> str:
    response = model.invoke(messages)
    return response.text