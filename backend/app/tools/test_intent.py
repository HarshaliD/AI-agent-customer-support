from backend.app.services.chat_service import model
from backend.app.schemas.workflow import IntentResult


structured_model = model.with_structured_output(IntentResult)


messages = [
    "Can I cancel my order ORD-10249?",
    "I want to cancel my order ORD-10249.",
    "Please cancel my order ORD-10249.",
    "Is my order eligible for cancellation?",
]


for message in messages:

    result = structured_model.invoke(
        f"""
        Classify the customer's request into exactly one of these intents.

        ORDER_STATUS:
        Questions about the status, location, tracking, or delivery
        of an existing order.

        ORDER_CANCELLATION:
        Requests or questions about cancelling an existing order.

        ORDER_REFUND:
        Requests for a refund for an existing order.

        GENERAL_QUERY:
        A general question that is not specifically about an existing
        order, cancellation, or refund.

        Current customer message:
        {message}
        """
    )

    print("\n" + "=" * 60)
    print("Customer:", message)
    print("Intent:", result.intent)
    print("Order ID:", result.order_id)
    print("Refund amount:", result.refund_amount)