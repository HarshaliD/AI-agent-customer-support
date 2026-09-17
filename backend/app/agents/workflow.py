from langgraph.graph import StateGraph, START, END

from backend.app.services.chat_service import model
from backend.app.schemas.workflow import SupportState, IntentResult

from backend.app.tools.order_tools import get_order
from backend.app.tools.cancellation_tools import cancel_order
from backend.app.tools.knowledge_tools import search_knowledge_base
from backend.app.tools.refund_tools import request_refund
from backend.app.tools.ticket_tools import create_ticket

from backend.app.services.action_logger import execute_and_log_tool


# ============================================================
# 1. UNDERSTAND THE CUSTOMER REQUEST
# ============================================================

def understand_request(state: SupportState):

    structured_model = model.with_structured_output(IntentResult)

    history_text = "\n".join(
        f"{message.type}: {message.content}"
        for message in state["chat_history"]
    )

    response = structured_model.invoke(
        f"""
        You are the intent classifier for a customer support agent.

        Classify the customer's request into exactly ONE of these intents:

        ORDER_STATUS:
        Questions about order status, tracking, delivery,
        shipment location, or whether an order has arrived.

        ORDER_CANCELLATION:
        Requests to cancel an existing order.

        ORDER_REFUND:
        Requests for a refund for an existing order.

        HUMAN_ESCALATION:
        The customer explicitly wants to speak to a human,
        manager, supervisor, support representative,
        or asks for their issue to be escalated.

        GENERAL_QUERY:
        General customer support questions that do not specifically
        require order status, cancellation, refund, or escalation.

        --------------------------------------------------------
        ORDER ID
        --------------------------------------------------------

        Extract the order ID if the customer provides one.

        If the current message does not contain an order ID,
        use the conversation history to determine whether the
        customer is referring to an existing order.

        If no order ID can be determined, return an empty string.

        --------------------------------------------------------
        REFUND AMOUNT
        --------------------------------------------------------

        If this is a refund request, extract the requested refund amount.

        If no refund amount is mentioned, return 0.

        --------------------------------------------------------
        CANCELLATION CONFIRMATION
        --------------------------------------------------------

        There may be a pending action waiting for confirmation.

        Current pending action:
        {state["pending_action"]}

        Current pending order:
        {state["pending_order_id"]}

        If pending_action is CANCEL_ORDER:

        Confirmation examples:
        - yes
        - yes please
        - confirm
        - do it
        - go ahead
        - cancel it

        These mean:

        user_confirmation = True

        Rejection examples:
        - no
        - no thanks
        - don't do it
        - nevermind
        - leave it

        These mean:

        user_confirmation = False

        If the response is unclear:

        user_confirmation = None

        The confirmation is NOT a new business intent.
        It is a response to the pending cancellation action.

        --------------------------------------------------------
        CONVERSATION HISTORY
        --------------------------------------------------------

        {history_text}

        --------------------------------------------------------
        CURRENT CUSTOMER MESSAGE
        --------------------------------------------------------

        {state["user_message"]}
        """
    )

    # If the model did not extract an order ID from the
    # current message, preserve the pending order ID.
    order_id = response.order_id

    if not order_id and state["pending_order_id"]:
        order_id = state["pending_order_id"]

    return {
        **state,
        "intent": response.intent,
        "order_id": order_id,
        "refund_amount": response.refund_amount,
        "user_confirmation": response.user_confirmation,
    }


# ============================================================
# 2. ORDER STATUS FLOW
# ============================================================

def order_flow(state: SupportState):

    result = execute_and_log_tool(
        get_order,
        state["order_id"],
        state["conversation_id"]
    )

    return {
        **state,
        "order_result": result,
    }


# ============================================================
# 3. CANCELLATION FLOW
# ============================================================

def cancellation_flow(state: SupportState):

    result = execute_and_log_tool(
        get_order,
        state["order_id"],
        state["conversation_id"]
    )

    return {
        **state,
        "order_result": result,
    }


# ============================================================
# Cancellation is eligible
# ============================================================

def cancellation_eligible(state: SupportState):

    # This node ONLY determines that the order is eligible.
    #
    # It does NOT perform the cancellation.
    #
    # The customer must explicitly confirm first.

    return {
        **state,
        "final_response": "",
    }


# ============================================================
# Ask customer for confirmation
# ============================================================

def ask_cancellation_confirmation(state: SupportState):

    return {
        **state,

        # Remember the action waiting for confirmation.
        "pending_action": "CANCEL_ORDER",

        # Remember the exact order being cancelled.
        "pending_order_id": state["order_id"],

        "final_response": (
            f"Your order {state['order_id']} is eligible for "
            "cancellation. Would you like me to cancel it?"
        ),
    }


# ============================================================
# Check cancellation confirmation
# ============================================================

def check_cancellation_confirmation(state: SupportState):

    if state["user_confirmation"] is True:

        return {
            **state,
            "final_response": "",
        }

    if state["user_confirmation"] is False:

        return {
            **state,
            "pending_action": None,
            "pending_order_id": None,
            "final_response": (
                "No problem. I won't cancel your order."
            ),
        }

    return {
        **state,
        "final_response": (
            "Please confirm whether you want me to "
            "cancel your order."
        ),
    }


# ============================================================
# Route cancellation confirmation
# ============================================================

def route_cancellation_confirmation(state: SupportState):

    if state["user_confirmation"] is True:
        return "cancel"

    if state["user_confirmation"] is False:
        return "decline"

    return "unclear"


# ============================================================
# Actually cancel the order
# ============================================================

def execute_cancellation(state: SupportState):

    # Safety check:
    # Cancellation must NEVER happen without explicit
    # customer confirmation.

    if state["user_confirmation"] is not True:

        return {
            **state,
            "final_response": (
                "I need your confirmation before cancelling "
                "the order."
            ),
        }

    result = execute_and_log_tool(
        cancel_order,
        state["order_id"],
        state["conversation_id"]
    )

    return {
        **state,
        "order_result": result,
        "pending_action": None,
        "pending_order_id": None,
    }


# ============================================================
# Cancellation completed
# ============================================================

def cancellation_completed(state: SupportState):

    # Never claim cancellation succeeded if the tool failed.

    if "error" in state["order_result"]:

        return {
            **state,
            "final_response": (
                f"I couldn't cancel order "
                f"{state['order_id']}. "
                f"{state['order_result']['error']}"
            ),
        }

    return {
        **state,
        "final_response": (
            f"Your order {state['order_id']} has been "
            "cancelled successfully."
        ),
    }


# ============================================================
# Customer declined cancellation
# ============================================================

def cancellation_not_requested(state: SupportState):

    return {
        **state,
        "pending_action": None,
        "pending_order_id": None,
        "final_response": (
            "No problem. I won't cancel your order."
        ),
    }


# ============================================================
# Cancellation not eligible
# ============================================================

def cancellation_not_eligible(state: SupportState):

    return {
        **state,
        "pending_action": None,
        "pending_order_id": None,
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

    result = execute_and_log_tool(
        get_order,
        state["order_id"],
        state["conversation_id"]
    )

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
# 5. REFUND APPROVAL GUARDRAIL
# ============================================================

def check_refund_amount(state: SupportState):

    # For the current HITL demonstration,
    # every valid refund requires manager approval.
    #
    # Later this can become:
    #
    # if state["refund_amount"] >= 50000:
    #     approval_required = True
    #
    # For now, we keep the demonstration simple.

    return {
        **state,
        "approval_required": True,
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
            "Manager approval is required before the refund "
            "can proceed."
        ),
    }


# ============================================================
# Manager approval through CMD
# ============================================================

def check_human_approval(state: SupportState):

    print("\n")
    print("==============================================")
    print("          MANAGER APPROVAL REQUIRED")
    print("==============================================")
    print(f"Order ID      : {state['order_id']}")
    print(f"Refund Amount : ₹{state['refund_amount']:.2f}")
    print(f"Reason        : {state['user_message']}")
    print("==============================================")

    while True:

        decision = input(
            "Approve refund? (yes/no): "
        ).strip().lower()

        if decision == "yes":

            print("Manager decision: APPROVED")

            return {
                **state,
                "approval_status": "approved",
            }

        if decision == "no":

            print("Manager decision: REJECTED")

            return {
                **state,
                "approval_status": "rejected",
            }

        print(
            "Invalid input. Please enter only 'yes' or 'no'."
        )


# ============================================================
# Route manager decision
# ============================================================

def route_human_approval(state: SupportState):

    if state["approval_status"] == "approved":
        return "execute_refund"

    if state["approval_status"] == "rejected":
        return "refund_rejected_by_manager"

    return "refund_pending"


# ============================================================
# Execute refund
# ============================================================

def execute_refund(state: SupportState):

    result = execute_and_log_tool(
        request_refund,
        {
            "order_id": state["order_id"],
            "reason": state["user_message"],
            "amount": state["refund_amount"],
        },
        state["conversation_id"]
    )

    # Never claim success if the refund tool failed.

    if "error" in result:

        return {
            **state,
            "order_result": result,
            "final_response": (
                f"I couldn't submit the refund request "
                f"for order {state['order_id']}. "
                f"{result['error']}"
            ),
        }

    return {
        **state,
        "order_result": result,
        "final_response": (
            f"Your refund request for order "
            f"{state['order_id']} has been submitted successfully."
        ),
    }


# ============================================================
# Refund rejected by manager
# ============================================================

def refund_rejected_by_manager(state: SupportState):

    return {
        **state,
        "final_response": (
            f"Your refund request for order "
            f"{state['order_id']} was rejected by the manager."
        ),
    }


# ============================================================
# Refund pending
# ============================================================

def refund_pending(state: SupportState):

    return {
        **state,
        "final_response": (
            f"Your refund request for order "
            f"{state['order_id']} is awaiting manager approval."
        ),
    }


# ============================================================
# Refund without additional approval
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
# 7. HUMAN ESCALATION FLOW
# ============================================================

def escalation_flow(state: SupportState):

    # --------------------------------------------------------
    # Current project limitation:
    #
    # SupportState does not yet contain customer_id.
    # Therefore we use a demo customer for escalation.
    #
    # Later we can add customer lookup and obtain the
    # customer ID dynamically.
    # --------------------------------------------------------

    customer_id = "CUS-001"

    result = execute_and_log_tool(
        create_ticket,
        {
            "customer_id": customer_id,
            "category": "HUMAN_ESCALATION",
            "description": state["user_message"],
            "priority": "high",
        },
        state["conversation_id"]
    )

    # Never claim that a ticket was created if the
    # ticket tool failed.

    if "error" in result:

        return {
            **state,
            "final_response": (
                "I couldn't create the escalation ticket right now. "
                "Please try again."
            ),
        }

    ticket_id = result.get(
        "ticket_id",
        "created"
    )

    return {
        **state,
        "final_response": (
            "I've escalated your request to our support team. "
            f"Your high-priority ticket is {ticket_id}."
        ),
    }


# ============================================================
# 8. GENERAL KNOWLEDGE FLOW
# ============================================================

def general_flow(state: SupportState):

    result = execute_and_log_tool(
        search_knowledge_base,
        state["user_message"],
        state["conversation_id"]
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

        Respond to the customer's message using ONLY the
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

    if state["intent"] == "HUMAN_ESCALATION":
        return "escalation_flow"

    return "general_flow"


def route_pending_action(state: SupportState):

    # Pending cancellation has priority over normal intent routing.

    if state["pending_action"] == "CANCEL_ORDER":
        return "check_cancellation_confirmation"

    return route_by_intent(state)


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


# ============================================================
# Nodes
# ============================================================

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
    "ask_cancellation_confirmation",
    ask_cancellation_confirmation
)

graph.add_node(
    "check_cancellation_confirmation",
    check_cancellation_confirmation
)

graph.add_node(
    "execute_cancellation",
    execute_cancellation
)

graph.add_node(
    "cancellation_completed",
    cancellation_completed
)

graph.add_node(
    "cancellation_not_requested",
    cancellation_not_requested
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
    "escalation_flow",
    escalation_flow
)

graph.add_node(
    "general_flow",
    general_flow
)

graph.add_node(
    "generate_response",
    generate_response
)


# ============================================================
# Main routing
# ============================================================

graph.add_edge(
    START,
    "understand_request"
)


# First check whether the conversation is waiting
# for confirmation of an existing action.

graph.add_conditional_edges(
    "understand_request",
    route_pending_action,
    {
        "check_cancellation_confirmation":
            "check_cancellation_confirmation",

        "order_flow":
            "order_flow",

        "cancellation_flow":
            "cancellation_flow",

        "validate_refund_order":
            "validate_refund_order",

        "escalation_flow":
            "escalation_flow",

        "general_flow":
            "general_flow",
    }
)


# ============================================================
# Order status
# ============================================================

graph.add_conditional_edges(
    "order_flow",
    route_order_result,
    {
        "order_not_found":
            "order_not_found",

        "generate_response":
            "generate_response",
    }
)


# ============================================================
# Cancellation
# ============================================================

graph.add_conditional_edges(
    "cancellation_flow",
    route_cancellation_result,
    {
        "order_not_found":
            "order_not_found",

        "cancellation_eligible":
            "cancellation_eligible",

        "cancellation_not_eligible":
            "cancellation_not_eligible",
    }
)


# Eligible does NOT cancel.
# It first asks the customer for confirmation.

graph.add_edge(
    "cancellation_eligible",
    "ask_cancellation_confirmation"
)


# Finish this invocation after asking for confirmation.

graph.add_edge(
    "ask_cancellation_confirmation",
    END
)


# ============================================================
# Cancellation confirmation
# ============================================================

graph.add_conditional_edges(
    "check_cancellation_confirmation",
    route_cancellation_confirmation,
    {
        "cancel":
            "execute_cancellation",

        "decline":
            "cancellation_not_requested",

        "unclear":
            END,
    }
)


graph.add_edge(
    "execute_cancellation",
    "cancellation_completed"
)


graph.add_edge(
    "cancellation_completed",
    END
)


graph.add_edge(
    "cancellation_not_requested",
    END
)


graph.add_edge(
    "cancellation_not_eligible",
    END
)


# ============================================================
# General query
# ============================================================

graph.add_edge(
    "general_flow",
    "generate_response"
)


# ============================================================
# Refund validation
# ============================================================

graph.add_conditional_edges(
    "validate_refund_order",
    route_refund_validation,
    {
        "refund_rejected":
            "refund_rejected",

        "check_refund_amount":
            "check_refund_amount",
    }
)


# ============================================================
# Refund approval guardrail
# ============================================================

graph.add_conditional_edges(
    "check_refund_amount",
    route_refund_amount,
    {
        "refund_requires_approval":
            "refund_requires_approval",

        "refund_can_continue":
            "refund_can_continue",
    }
)


# ============================================================
# Human approval
# ============================================================

graph.add_edge(
    "refund_requires_approval",
    "check_human_approval"
)


graph.add_conditional_edges(
    "check_human_approval",
    route_human_approval,
    {
        "execute_refund":
            "execute_refund",

        "refund_rejected_by_manager":
            "refund_rejected_by_manager",

        "refund_pending":
            "refund_pending",
    }
)


# ============================================================
# Human escalation
# ============================================================

graph.add_edge(
    "escalation_flow",
    END
)


# ============================================================
# Endpoints
# ============================================================

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
    "order_not_found",
    END
)


graph.add_edge(
    "generate_response",
    END
)


# ============================================================
# 12. COMPILE WORKFLOW
# ============================================================

workflow = graph.compile()


# ============================================================
# 13. VISUALIZE WORKFLOW
# ============================================================

print(
    workflow.get_graph().draw_mermaid()
)

png_bytes = (
    workflow
    .get_graph()
    .draw_mermaid_png()
)

with open("workflow.png", "wb") as f:
    f.write(png_bytes)