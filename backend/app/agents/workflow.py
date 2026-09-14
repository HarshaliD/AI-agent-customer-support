from langgraph.graph import StateGraph, START, END

from backend.app.services.chat_service import model
from backend.app.schemas.workflow import SupportState, IntentResult

from backend.app.tools.order_tools import get_order
from backend.app.tools.cancellation_tools import cancel_order
from backend.app.tools.knowledge_tools import search_knowledge_base
from backend.app.tools.refund_tools import request_refund


# ============================================================
# 1. UNDERSTAND THE CUSTOMER REQUEST
# ============================================================

def understand_request(state: SupportState):

    structured_model = model.with_structured_output(IntentResult)

    history_text = "\n".join(
        f"{message.type}: {message.content}"
        for message in state["chat_history"]
    )
    # message is Langchain Object
    # message.type → who sent it (e.g. "human" or "ai")
    # message.content → the actual message text

    response = structured_model.invoke(
        f"""
        Classify the customer's request into exactly one of these intents.

        ORDER_STATUS:
        Questions about the status, location, tracking, or delivery
        of an existing order.

        ORDER_CANCELLATION:
        Requests to cancel an existing order.

        ORDER_REFUND:
        Requests for a refund for an existing order.

        GENERAL_QUERY:
        A general question that is not specifically about an existing
        order, cancellation, or refund.

        Also extract the order ID if the customer provides one.

        For refund requests, extract the requested refund amount.

        If the current message does not contain an order ID,
        use the conversation history to determine whether an
        order ID is being referred to.

        If no order ID can be determined, return an empty string
        for order_id.

        If no refund amount is mentioned, return 0.

        Previous conversation:
        {history_text}

        Current customer message:
        {state["user_message"]}
        """
    )

    return {
        **state,                                     #unwrap the state and owerite the content mentioned below in the state
        "intent": response.intent,
        "order_id": response.order_id,
        "refund_amount": response.refund_amount,
    }


# ============================================================
# 2. ORDER STATUS FLOW
# ============================================================

def order_flow(state: SupportState):

    result = get_order.invoke(state["order_id"])

    return {
        **state,
        "order_result": result,
    }


# ============================================================
# 3. CANCELLATION FLOW
# ============================================================

def cancellation_flow(state: SupportState):

    result = get_order.invoke(state["order_id"])

    return {
        **state,
        "order_result": result,
    }


def cancellation_eligible(state: SupportState):

    result = cancel_order.invoke(state["order_id"])

    return {
        **state,
        "order_result": result,
    }


def cancellation_completed(state: SupportState):

    return {
        **state,
        "final_response": (
            f"Your order {state['order_id']} has been "
            f"cancelled successfully."
        ),
    }


def cancellation_not_eligible(state: SupportState):

    return {
        **state,
        "final_response": (
            f"Order {state['order_id']} cannot be cancelled "
            f"because its current status is "
            f"'{state['order_result'].get('status')}'."
        ),
    }


# ============================================================
# 4. REFUND VALIDATION
# ============================================================

def validate_refund_order(state: SupportState):

    result = get_order.invoke(state["order_id"])

    if "error" in result:
        return {
            **state,
            "order_result": result,
            "refund_valid": False,
        }

    return {
        **state,
        "order_result": result,
        "refund_valid": True,
    }


def route_refund_validation(state: SupportState):

    if not state["refund_valid"]:
        return "refund_rejected"

    return "check_refund_amount"


def refund_rejected(state: SupportState):

    return {
        **state,
        "final_response": (
            f"I couldn't find order {state['order_id']}. "
            "Please check the order ID and try again."
        ),
    }


# ============================================================
# 5. REFUND AMOUNT GUARDRAIL
# ============================================================

def check_refund_amount(state: SupportState):

    if state["refund_amount"] > 50000:

        return {
            **state,
            "approval_required": True,
        }

    return {
        **state,
        "approval_required": False,
        "approval_status": "not_required",
    }


def route_refund_amount(state: SupportState):

    if state["approval_required"]:
        return "refund_requires_approval"

    return "refund_can_continue"


# ============================================================
# 6. HUMAN-IN-THE-LOOP
# ============================================================

def refund_requires_approval(state: SupportState):

    return {
        **state,
        "final_response": (
            f"Your refund request for order "
            f"{state['order_id']} is for "
            f"₹{state['refund_amount']:.2f}. "
            "Because the refund amount exceeds ₹50,000, "
            "manager approval is required before the refund "
            "can proceed."
        ),
    }


def check_human_approval(state: SupportState):

    if state["approval_status"] == "approved":

        return {
            **state,
            "final_response": (
                "Manager approval received. "
                "The refund can proceed."
            ),
        }

    if state["approval_status"] == "rejected":

        return {
            **state,
            "final_response": (
                f"Your refund request for order "
                f"{state['order_id']} was rejected by the manager."
            ),
        }

    return {
        **state,
        "final_response": (
            f"Your refund request for order "
            f"{state['order_id']} is awaiting manager approval."
        ),
    }


def route_human_approval(state: SupportState):

    if state["approval_status"] == "approved":
        return "execute_refund"

    if state["approval_status"] == "rejected":
        return "refund_rejected_by_manager"

    return "refund_pending"


def execute_refund(state: SupportState):

    result = request_refund.invoke(
        {
            "order_id": state["order_id"],
            "reason": state["user_message"],
            "amount": state["refund_amount"],
        }
    )

    return {
        **state,
        "order_result": result,
        "final_response": (
            f"Your refund request for order "
            f"{state['order_id']} has been submitted successfully."
        ),
    }


def refund_rejected_by_manager(state: SupportState):

    return {
        **state,
        "final_response": (
            f"Your refund request for order "
            f"{state['order_id']} was rejected by the manager."
        ),
    }


def refund_pending(state: SupportState):

    return {
        **state,
        "final_response": (
            f"Your refund request for order "
            f"{state['order_id']} is awaiting manager approval."
        ),
    }


# ============================================================
# 7. REFUND WITHOUT ADDITIONAL APPROVAL
# ============================================================

def refund_can_continue(state: SupportState):

    return {
        **state,
        "final_response": (
            f"Order {state['order_id']} exists and the requested "
            f"refund amount of ₹{state['refund_amount']:.2f} "
            "does not require additional manager approval."
        ),
    }


# ============================================================
# 8. GENERAL KNOWLEDGE FLOW
# ============================================================

def general_flow(state: SupportState):

    result = search_knowledge_base.invoke(
        state["user_message"]
    )

    return {
        **state,
        "knowledge_result": result,
    }


# ============================================================
# 9. GENERATE FINAL RESPONSE
# ============================================================

def generate_response(state: SupportState):

    response = model.invoke(
        f"""
        You are a customer support assistant for NovaMart.

        Respond to the customer's message using only the
        information available in the workflow state.

        Customer message:
        {state["user_message"]}

        Order information:
        {state["order_result"]}

        Knowledge base information:
        {state["knowledge_result"]}

        Give a clear and concise response.

        Do not invent information.
        """
    )

    return {
        **state,
        "final_response": response.text,
    }


# ============================================================
# 10. ROUTING FUNCTIONS
# ============================================================

def route_by_intent(state: SupportState):

    if state["intent"] == "ORDER_STATUS":
        return "order_flow"

    if state["intent"] == "ORDER_CANCELLATION":
        return "cancellation_flow"

    if state["intent"] == "ORDER_REFUND":
        return "validate_refund_order"

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


def order_not_found(state: SupportState):

    return {
        **state,
        "final_response": (
            "I'm sorry, but I couldn't find that order. "
            "Please check the order ID and try again."
        ),
    }


# ============================================================
# 11. BUILD LANGGRAPH WORKFLOW
# ============================================================

graph = StateGraph(SupportState)


# ------------------------------------------------------------
# Nodes
# ------------------------------------------------------------

graph.add_node(
    "understand_request",
    understand_request
)

graph.add_node(
    "order_flow",
    order_flow
)

graph.add_node(
    "order_not_found",
    order_not_found
)

graph.add_node(
    "cancellation_flow",
    cancellation_flow
)

graph.add_node(
    "cancellation_eligible",
    cancellation_eligible
)

graph.add_node(
    "cancellation_completed",
    cancellation_completed
)

graph.add_node(
    "cancellation_not_eligible",
    cancellation_not_eligible
)

graph.add_node(
    "validate_refund_order",
    validate_refund_order
)

graph.add_node(
    "refund_rejected",
    refund_rejected 
)

graph.add_node(
    "check_refund_amount",
    check_refund_amount
)

graph.add_node(
    "refund_requires_approval",
    refund_requires_approval
)

graph.add_node(
    "check_human_approval",
    check_human_approval
)

graph.add_node(
    "execute_refund",
    execute_refund
)

graph.add_node(
    "refund_rejected_by_manager",
    refund_rejected_by_manager
)

graph.add_node(
    "refund_pending",
    refund_pending
)

graph.add_node(
    "refund_can_continue",
    refund_can_continue
)

graph.add_node(
    "general_flow",
    general_flow
)

graph.add_node(
    "generate_response",
    generate_response
)


# ------------------------------------------------------------
# Main routing
# ------------------------------------------------------------

graph.add_edge(
    START,
    "understand_request"
)

graph.add_conditional_edges(
    "understand_request",
    route_by_intent,
    {
        "order_flow": "order_flow",
        "cancellation_flow": "cancellation_flow",
        "validate_refund_order": "validate_refund_order",
        "general_flow": "general_flow",
    }
)


# ------------------------------------------------------------
# Order status
# ------------------------------------------------------------

graph.add_conditional_edges(
    "order_flow",
    route_order_result,
    {
        "order_not_found": "order_not_found",
        "generate_response": "generate_response",
    }
)


# ------------------------------------------------------------
# Cancellation
# ------------------------------------------------------------

graph.add_conditional_edges(
    "cancellation_flow",
    route_cancellation_result,
    {
        "order_not_found": "order_not_found",
        "cancellation_eligible": "cancellation_eligible",
        "cancellation_not_eligible": "cancellation_not_eligible",
    }
)

graph.add_edge(
    "cancellation_eligible",
    "cancellation_completed"
)


# ------------------------------------------------------------
# General query
# ------------------------------------------------------------

graph.add_edge(
    "general_flow",
    "generate_response"
)
  

# ------------------------------------------------------------
# Refund validation
# ------------------------------------------------------------

graph.add_conditional_edges(
    "validate_refund_order",
    route_refund_validation,
    {
        "refund_rejected": "refund_rejected",
        "check_refund_amount": "check_refund_amount",
    }
)


# ------------------------------------------------------------
# Refund amount guardrail
# ------------------------------------------------------------

graph.add_conditional_edges(
    "check_refund_amount",
    route_refund_amount,
    {
        "refund_requires_approval": "refund_requires_approval",
        "refund_can_continue": "refund_can_continue",
    }
)

 
# ------------------------------------------------------------
# Human approval
# ------------------------------------------------------------

graph.add_edge(
    "refund_requires_approval",
    "check_human_approval"
)

graph.add_conditional_edges(
    "check_human_approval",
    route_human_approval,
    {
        "execute_refund": "execute_refund",
        "refund_rejected_by_manager": "refund_rejected_by_manager",
        "refund_pending": "refund_pending",
    }
)


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------

graph.add_edge(
    "execute_refund",
    END
)

graph.add_edge(
    "refund_rejected_by_manager",
    END
)

graph.add_edge(
    "refund_pending",
    END
)

graph.add_edge(
    "refund_rejected",
    END
)

graph.add_edge(
    "refund_can_continue",
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

graph.add_edge(
    "order_not_found",
    END
)

graph.add_edge(
    "generate_response",
    END
)


# ------------------------------------------------------------
# Compile
# ------------------------------------------------------------


workflow = graph.compile()


# ------------------------------------------------------------
# Visualize workflow
# ------------------------------------------------------------

print(workflow.get_graph().draw_mermaid())
png_bytes = workflow.get_graph().draw_mermaid_png()

with open("workflow.png", "wb") as f:
    f.write(png_bytes)