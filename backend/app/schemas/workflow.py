from typing import Literal, TypedDict
from pydantic import BaseModel

# It is the info we need to share within the workflow
class SupportState(TypedDict):
    user_message: str
    chat_history: list
    intent: str
    order_id: str
    order_result: dict
    knowledge_result: str
    refund_amount: float
    refund_valid: bool
    approval_required: bool
    approval_status: str
    final_response: str

# Defines the information Gemini should extract from the user message
class IntentResult(BaseModel):
    intent: Literal[
        "ORDER_STATUS",
        "ORDER_CANCELLATION",
        "ORDER_REFUND",
        "GENERAL_QUERY"
    ]
    order_id: str = ""
    refund_amount: float = 0.0