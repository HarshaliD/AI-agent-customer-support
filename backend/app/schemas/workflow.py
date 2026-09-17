from typing import Literal, TypedDict
from pydantic import BaseModel

class SupportState(TypedDict):
    # Information shared between the different nodes
    # of the workflow
    conversation_id: int

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

    # Used for multi-turn confirmation
    pending_action: str | None
    pending_order_id: str | None
    user_confirmation: bool | None

    final_response: str


class IntentResult(BaseModel):
    intent: Literal[
        "ORDER_STATUS",
        "ORDER_CANCELLATION",
        "ORDER_REFUND",
        "RETURN",
        "PAYMENT",
        "ACCOUNT",
        "PRODUCT_INFORMATION",
        "COMPLAINT",
        "TECHNICAL_SUPPORT",
        "HUMAN_ESCALATION",
        "GENERAL_QUERY",
    ]

    order_id: str = ""

    refund_amount: float = 0.0

    # None = not a confirmation / unclear
    # True = confirmed
    # False = declined
    user_confirmation: bool | None = None