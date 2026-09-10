from backend.app.services.chat_service import model
from backend.app.schemas.workflow import SupportState, IntentResult
from backend.app.tools.order_tools import get_order
from backend.app.tools.cancellation_tools import cancel_order
from backend.app.tools.knowledge_tools import search_knowledge_base

from langgraph.graph import StateGraph, START, END


def understand_request(state: SupportState):
    structured_model = model.with_structured_output(IntentResult)

    history_text = "\n".join(
        f"{message.type}: {message.content}"
        for message in state["chat_history"]
    )

    response = structured_model.invoke(
        f"""
        Classify the customer's request into exactly one of these intents.

        ORDER_STATUS:
        Questions about the status, location, tracking, or delivery
        of an existing order.

        ORDER_CANCELLATION:
        Requests to cancel an existing order.

        GENERAL_QUERY:
        A general question that is not specifically about an existing order.

        Also extract the order ID if the customer provides one.

        If the current message does not contain an order ID,
        use the conversation history to determine whether an
        order ID is being referred to.

        If no order ID can be determined, return an empty string
        for order_id.

        Previous conversation:
        {history_text}

        Current customer message:
        {state["user_message"]}
        """
    )

    return {
        **state,
        "intent": response.intent,
        "order_id": response.order_id
    }


def order_flow(state: SupportState):
    result = get_order.invoke(state["order_id"])

    return {
        **state,
        "order_result": result
    }


def cancellation_flow(state: SupportState):
    result = get_order.invoke(state["order_id"])

    return {
        **state,
        "order_result": result
    }


def generate_response(state: SupportState):
    response = model.invoke(
        f"""
        You are a customer support assistant for NovaMart.

        Respond to the customer's message using the information
        available in the workflow state.

        Customer message:
        {state["user_message"]}

        Order information:
        {state["order_result"]}

        Knowledge base information:
        {state["knowledge_result"]}

        Give a clear and concise response to the customer.

        Do not invent information that is not present in the
        available information.
        """
    )

    return {
        **state,
        "final_response": response.text
    }


def order_not_found(state: SupportState):
    return {
        **state,
        "final_response": (
            "I'm sorry, but I couldn't find that order. "
            "Please check the order ID and try again."
        )
    }


def cancellation_eligible(state: SupportState):
    result = cancel_order.invoke(state["order_id"])

    return {
        **state,
        "order_result": result
    }


def cancellation_completed(state: SupportState):
    return {
        **state,
        "final_response": (
            f"Your order {state['order_id']} has been "
            f"cancelled successfully."
        )
    }


def cancellation_not_eligible(state: SupportState):
    return {
        **state,
        "final_response": (
            f"Order {state['order_id']} cannot be cancelled "
            f"because its current status is "
            f"'{state['order_result'].get('status')}'."
        )
    }


def general_flow(state: SupportState):
    result = search_knowledge_base.invoke(
        state["user_message"]
    )

    return {
        **state,
        "knowledge_result": result
    }


def route_by_intent(state: SupportState):
    if state["intent"] == "ORDER_STATUS":
        return "order_flow"

    if state["intent"] == "ORDER_CANCELLATION":
        return "cancellation_flow"

    return "general_flow"


def route_order_result(state: SupportState):
    if "error" in state["order_result"]:
        return "order_not_found"

    return "generate_response"


def route_cancellation_result(state: SupportState):
    if "error" in state["order_result"]:
        return "order_not_found"

    if state["order_result"].get("status") == "processing":
        return "cancellation_eligible"

    return "cancellation_not_eligible"


# --------------------------------------------------
# Build LangGraph workflow
# --------------------------------------------------

graph = StateGraph(SupportState)

graph.add_node("understand_request", understand_request)
graph.add_node("order_flow", order_flow)
graph.add_node("cancellation_flow", cancellation_flow)
graph.add_node("generate_response", generate_response)
graph.add_node("order_not_found", order_not_found)
graph.add_node("cancellation_eligible", cancellation_eligible)
graph.add_node("cancellation_completed", cancellation_completed)
graph.add_node("cancellation_not_eligible", cancellation_not_eligible)
graph.add_node("general_flow", general_flow)

graph.add_edge(START, "understand_request")

graph.add_conditional_edges(
    "understand_request",
    route_by_intent
)

graph.add_conditional_edges(
    "order_flow",
    route_order_result
)

graph.add_conditional_edges(
    "cancellation_flow",
    route_cancellation_result
)

graph.add_edge(
    "general_flow",
    "generate_response"
)

graph.add_edge(
    "cancellation_eligible",
    "cancellation_completed"
)

graph.add_edge(
    "generate_response",
    END
)

graph.add_edge(
    "order_not_found",
    END
)

graph.add_edge(
    "cancellation_completed",
    END
)

graph.add_edge(
    "cancellation_not_eligible",
    END
)

workflow = graph.compile()


# --------------------------------------------------
# Direct test
# --------------------------------------------------

if __name__ == "__main__":

    initial_state: SupportState = {
        "user_message": "Can I cancel my order ORD-99999?",
        "chat_history": [],
        "intent": "",
        "order_id": "",
        "order_result": {},
        "knowledge_result": "",
        "final_response": ""
    }

    result = workflow.invoke(initial_state)

    print("\nFinal State:")
    print(result)

    print("\nCustomer Response:")
    print(result["final_response"])