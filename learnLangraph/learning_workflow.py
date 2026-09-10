from typing import TypedDict, Literal

from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

from backend.app.services.chat_service import model


class SupportState(TypedDict):
    user_message: str
    intent: str


class IntentResult(BaseModel):
    intent: Literal["ORDER_STATUS", "GENERAL_QUERY"]


def understand_request(state: SupportState):
    structured_model = model.with_structured_output(IntentResult)

    response = structured_model.invoke(
        state["user_message"]
    )

    return {
        "user_message": state["user_message"],
        "intent": response.intent
    }


def order_flow(state: SupportState):
    print("→ Entered ORDER workflow")
    return state


def general_flow(state: SupportState):
    print("→ Entered GENERAL workflow")
    return state


def route_by_intent(state: SupportState):
    if state["intent"] == "ORDER_STATUS":
        return "order_flow"

    return "general_flow"


graph = StateGraph(SupportState)

graph.add_node("understand_request", understand_request)
graph.add_node("order_flow", order_flow)
graph.add_node("general_flow", general_flow)

graph.add_edge(START, "understand_request")

graph.add_conditional_edges(
    "understand_request",
    route_by_intent
)

graph.add_edge("order_flow", END)
graph.add_edge("general_flow", END)

workflow = graph.compile()


initial_state = {
    "user_message": "Where is my order?",
    "intent": ""
}

result = workflow.invoke(initial_state)

print("\nFinal State:")
print(result)