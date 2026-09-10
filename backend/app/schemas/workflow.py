from typing import Literal, TypedDict
from pydantic import BaseModel


class SupportState(TypedDict):
    user_message: str
    chat_history: list
    intent: str
    order_id: str
    order_result: dict
    knowledge_result: str
    final_response: str


class IntentResult(BaseModel):
    intent: Literal[
        "ORDER_STATUS",
        "ORDER_CANCELLATION",
        "GENERAL_QUERY"
    ]
    order_id: str