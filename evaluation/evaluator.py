import json
import time
import builtins
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage

# Load SQLAlchemy models before importing workflow
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.agent_action import AgentAction

from backend.app.database.database import SessionLocal
from backend.app.agents.workflow import workflow


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TEST_CASES_FILE = BASE_DIR / "test_cases.json"
RESULTS_FILE = BASE_DIR / "results.json"


# ============================================================
# LOAD TEST CASES
# ============================================================

with open(TEST_CASES_FILE, "r", encoding="utf-8") as f:
    TEST_CASES = json.load(f)


# ============================================================
# CREATE REAL DATABASE CONVERSATION
# ============================================================

def create_test_conversation():
    """
    Create a real conversation row.

    agent_actions.conversation_id has a foreign key to
    conversations.id, so every evaluation run needs a
    valid conversation ID.
    """

    db = SessionLocal()

    try:
        conversation = Conversation()

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation.id

    finally:
        db.close()


# ============================================================
# INITIAL STATE
# ============================================================

def create_initial_state(
    user_message,
    conversation_id,
    chat_history=None,
    pending_action=None,
    pending_order_id=None,
    user_confirmation=None
):
    """
    Create the SupportState required by the workflow.
    """

    return {
        "conversation_id": conversation_id,

        "user_message": user_message,

        "chat_history": chat_history or [],

        "intent": "",
        "order_id": "",
        "order_result": {},

        "knowledge_result": "",

        "refund_amount": 0.0,
        "refund_valid": False,

        "approval_required": False,
        "approval_status": "",

        "pending_action": pending_action,
        "pending_order_id": pending_order_id,

        "user_confirmation": user_confirmation,

        "final_response": "",
    }


# ============================================================
# EXPECTATIONS
# ============================================================

def get_expected(test_case):
    """
    Read expectations for both single-turn and multi-turn
    test cases.
    """

    # --------------------------------------------------------
    # Multi-turn
    # --------------------------------------------------------

    if "conversation" in test_case:

        return {
            "intents": test_case.get(
                "expected_intents", []
            ),

            "tools": test_case.get(
                "expected_tools", []
            ),

            "behavior": test_case.get(
                "expected_behavior"
            )
        }

    # --------------------------------------------------------
    # Single-turn
    # --------------------------------------------------------

    return {
        "intents": [
            test_case.get("expected_intent")
        ],

        "tools": [
            test_case.get("expected_tool")
        ],

        "behavior": test_case.get(
            "expected_behavior"
        )
    }


# ============================================================
# TOOL DETECTION
# ============================================================

def get_tools_by_turn(nodes_by_turn):
    """
    Determine the business tool used during each turn.
    """

    tools = []

    for nodes in nodes_by_turn:

        if "execute_refund" in nodes:
            tools.append("request_refund")

        elif "execute_cancellation" in nodes:
            tools.append("cancel_order")

        elif (
            "order_flow" in nodes
            or "cancellation_flow" in nodes
            or "validate_refund_order" in nodes
        ):
            tools.append("get_order")

        elif "escalation_flow" in nodes:
            tools.append("create_ticket")

        elif "general_flow" in nodes:
            tools.append("search_knowledge_base")

        else:
            tools.append(None)

    return tools


# ============================================================
# SINGLE TOOL DETECTION
# ============================================================

def get_actual_tool(nodes):

    return get_tools_by_turn([nodes])[0]


# ============================================================
# BEHAVIOR EVALUATION
# ============================================================

def behavior_matches(
    expected_behavior,
    nodes_by_turn,
    states,
    responses
):
    """
    Evaluate behavior semantically.

    The test cases use descriptive labels while the workflow
    exposes concrete node names. We therefore evaluate the
    expected behavior against the actual workflow path.
    """

    if not expected_behavior:
        return True

    # Flatten nodes for sequence checks
    all_nodes = []

    for nodes in nodes_by_turn:
        all_nodes.extend(nodes)

    # ========================================================
    # GENERAL / RAG
    # ========================================================

    if expected_behavior in {
        "answer_return_policy",
        "answer_return_period",
        "answer_shipping_policy",
        "answer_warranty_policy",
        "provide_general_support_response",
        "stay_within_customer_support_scope",
        "avoid_inventing_novamart_information",
    }:

        return (
            "general_flow" in all_nodes
            and
            "search_knowledge_base"
            in get_tools_by_turn(nodes_by_turn)
        )

    # ========================================================
    # ORDER STATUS
    # ========================================================

    if expected_behavior in {
        "return_order_status",
        "return_tracking_information",
        "report_cancelled_status",
    }:

        return (
            "order_flow" in all_nodes
            and
            "get_order"
            in get_tools_by_turn(nodes_by_turn)
        )

    # ========================================================
    # CANCELLATION: ELIGIBLE + CONFIRMATION
    # ========================================================

    if expected_behavior in {
        "check_cancellation_eligibility_then_ask_confirmation",
        "eligible_cancellation_requires_confirmation",
    }:

        return (
            "cancellation_flow" in all_nodes
            and
            "cancellation_eligible" in all_nodes
            and
            "ask_cancellation_confirmation"
            in all_nodes
            and
            "execute_cancellation"
            not in all_nodes
        )

    # ========================================================
    # CANCELLATION: INELIGIBLE
    # ========================================================

    if expected_behavior in {
        "reject_cancellation_as_ineligible",
        "do_not_cancel_shipped_order",
        "reject_already_cancelled_order",
    }:

        return (
            "cancellation_flow" in all_nodes
            and
            "cancellation_not_eligible"
            in all_nodes
            and
            "cancel_order"
            not in get_tools_by_turn(nodes_by_turn)
        )

    # ========================================================
    # CANCELLATION: CONFIRMED
    # ========================================================

    if expected_behavior in {
        "check_eligibility_then_cancel_after_explicit_confirmation",
        "retain_order_context_and_require_confirmation",
    }:

        return (
            "cancellation_flow" in all_nodes
            and
            "execute_cancellation" in all_nodes
            and
            "cancel_order"
            in get_tools_by_turn(nodes_by_turn)
        )

    # ========================================================
    # CANCELLATION: DON'T CANCEL
    # ========================================================

    if expected_behavior == "ask_confirmation_then_leave_order_unchanged":
        return (
            "check_cancellation_confirmation" in all_nodes
            and "cancellation_not_requested" in all_nodes
            and "execute_cancellation" not in all_nodes
        )

    if expected_behavior == "do_not_cancel_until_explicit_confirmation":
        # Temporal safety check for multi-turn cancellation.
        # Cancellation must not happen before the final explicit
        # confirmation, and must happen only after that confirmation.
        if len(nodes_by_turn) < 2:
            return False

        earlier_turns = nodes_by_turn[:-1]
        final_turn = nodes_by_turn[-1]

        cancelled_early = any(
            "execute_cancellation" in nodes
            or "cancel_order" in get_tools_by_turn([nodes])[0:1]
            for nodes in earlier_turns
        )

        cancelled_after_confirmation = (
            "execute_cancellation" in final_turn
            and "cancel_order" in get_tools_by_turn([final_turn])
        )

        return (
            "check_cancellation_confirmation" in all_nodes
            and not cancelled_early
            and cancelled_after_confirmation
        )

    # ========================================================
    # ORDER NOT FOUND
    # ========================================================

    if expected_behavior in {
        "report_order_not_found",
        "report_order_not_found_without_cancelling",
        "report_order_not_found_without_refund",
        "handle_tool_error_without_hallucinating",
        "stop_after_tool_error_without_cancelling",
        "stop_after_tool_error_without_refund",
    }:

        return (
            "order_not_found" in all_nodes
            and
            "cancel_order"
            not in get_tools_by_turn(nodes_by_turn)
            and
            "request_refund"
            not in get_tools_by_turn(nodes_by_turn)
        )

    # ========================================================
    # REFUND: MANAGER APPROVAL
    # ========================================================

    if expected_behavior in {
        "validate_order_then_require_manager_approval",
        "validate_order_then_require_approval",
        "require_manager_approval_before_refund",
    }:

        return (
            "validate_refund_order" in all_nodes
            and
            "check_refund_amount" in all_nodes
            and
            "refund_requires_approval"
            in all_nodes
            and
            "check_human_approval"
            in all_nodes
        )

    # ========================================================
    # MISSING REFUND INFORMATION
    # ========================================================

    if expected_behavior in {
        "request_missing_order_id",
        "request_order_id_or_refund_details",
    }:

        # Current workflow does not have a dedicated
        # missing-information node.
        #
        # Therefore we explicitly return False instead
        # of pretending that refund_rejected is equivalent.

        return False

    # ========================================================
    # HUMAN ESCALATION
    # ========================================================

    if expected_behavior == (
        "create_high_priority_escalation_ticket"
    ):

        return (
            "escalation_flow" in all_nodes
            and
            "create_ticket"
            in get_tools_by_turn(nodes_by_turn)
        )

    # ========================================================
    # INVALID TOOL ARGUMENTS
    # ========================================================

    if expected_behavior == (
        "do_not_execute_invalid_order_identifier"
    ):

        # A correctly guarded implementation should reject
        # the invalid identifier BEFORE get_order executes.

        tools = get_tools_by_turn(nodes_by_turn)

        return "get_order" not in tools

    # ========================================================
    # DESTRUCTIVE ACTION VALIDATION
    # ========================================================

    if expected_behavior == (
        "validate_order_before_destructive_action"
    ):

        return (
            "cancellation_flow" in all_nodes
            and
            "get_order"
            in get_tools_by_turn(nodes_by_turn)
        )

    # ========================================================
    # UNKNOWN
    # ========================================================

    return False


# ============================================================
# UPDATE LANGCHAIN HISTORY
# ============================================================

def update_chat_history(
    chat_history,
    user_message,
    assistant_response
):
    """
    Convert conversation history into proper LangChain
    message objects.
    """

    updated_history = list(chat_history)

    updated_history.append(
        HumanMessage(
            content=user_message
        )
    )

    if assistant_response:

        updated_history.append(
            AIMessage(
                content=assistant_response
            )
        )

    return updated_history


# ============================================================
# RUN ONE WORKFLOW TURN
# ============================================================

def run_single_turn(
    user_message,
    conversation_id,
    chat_history,
    pending_action=None,
    pending_order_id=None,
    user_confirmation=None,
    auto_approve=False
):

    state = create_initial_state(
        user_message=user_message,
        conversation_id=conversation_id,
        chat_history=chat_history,
        pending_action=pending_action,
        pending_order_id=pending_order_id,
        user_confirmation=user_confirmation
    )

    nodes = []

    start_time = time.perf_counter()

    original_input = builtins.input

    try:

        # ----------------------------------------------------
        # HITL APPROVAL
        # ----------------------------------------------------

        if auto_approve:

            builtins.input = (
                lambda prompt="": "yes"
            )

        else:

            builtins.input = (
                lambda prompt="": "no"
            )

        # ----------------------------------------------------
        # RUN WORKFLOW
        # ----------------------------------------------------

        final_state = None

        for event in workflow.stream(state):

            if not isinstance(event, dict):
                continue

            for node_name, node_state in event.items():

                nodes.append(node_name)

                if isinstance(
                    node_state,
                    dict
                ):

                    final_state = node_state

        latency = (
            time.perf_counter()
            - start_time
        )

        if final_state is None:

            final_state = state

        response = final_state.get(
            "final_response",
            ""
        )

        # ----------------------------------------------------
        # UPDATE HISTORY
        # ----------------------------------------------------

        updated_history = update_chat_history(
            chat_history,
            user_message,
            response
        )

        return {
            "state": final_state,
            "nodes": nodes,
            "response": response,
            "latency": latency,
            "chat_history": updated_history,
            "error": None
        }

    except Exception as e:

        latency = (
            time.perf_counter()
            - start_time
        )

        return {
            "state": state,
            "nodes": nodes,
            "response": "",
            "latency": latency,
            "chat_history": chat_history,
            "error": str(e)
        }

    finally:

        builtins.input = original_input


# ============================================================
# CHECK INTENTS
# ============================================================

def intents_match(
    expected_intents,
    actual_intents
):

    if not expected_intents:
        return True

    return expected_intents == actual_intents


# ============================================================
# CHECK TOOLS
# ============================================================

def tools_match(
    expected_tools,
    actual_tools
):

    # --------------------------------------------------------
    # Single turn
    # --------------------------------------------------------

    if len(expected_tools) == 1:

        expected = expected_tools[0]

        if expected is None:

            return (
                len(actual_tools) == 1
                and actual_tools[0] is None
            )

        return (
            expected
            == actual_tools[0]
        )

    # --------------------------------------------------------
    # Multi-turn
    # --------------------------------------------------------

    # The expected tool list describes the meaningful
    # tool sequence. Compare it against the actual sequence,
    # ignoring turns where no business tool was called.

    actual_non_null = [
        tool
        for tool in actual_tools
        if tool is not None
    ]

    expected_non_null = [
        tool
        for tool in expected_tools
        if tool is not None
    ]

    return (
        actual_non_null
        == expected_non_null
    )


# ============================================================
# RUN TEST CASE
# ============================================================

def run_test_case(test_case):

    test_id = test_case["id"]

    expected = get_expected(
        test_case
    )

    # --------------------------------------------------------
    # REAL DATABASE CONVERSATION
    # --------------------------------------------------------

    conversation_id = (
        create_test_conversation()
    )

    # ========================================================
    # MULTI-TURN
    # ========================================================

    if "conversation" in test_case:

        chat_history = []

        nodes_by_turn = []
        states = []
        responses = []

        total_latency = 0

        pending_action = None
        pending_order_id = None
        user_confirmation = None

        error = None

        actual_intents = []

        for turn_index, user_message in enumerate(
            test_case["conversation"],
            start=1
        ):

            result = run_single_turn(
                user_message=user_message,

                conversation_id=conversation_id,

                chat_history=chat_history,

                pending_action=pending_action,

                pending_order_id=pending_order_id,

                user_confirmation=user_confirmation,

                auto_approve=test_case.get(
                    "auto_approve",
                    False
                )
            )

            total_latency += result[
                "latency"
            ]

            nodes_by_turn.append(
                result["nodes"]
            )

            states.append(
                result["state"]
            )

            responses.append({
                "turn": turn_index,
                "input": user_message,
                "response": result["response"],
                "nodes": result["nodes"],
                "latency": result["latency"]
            })

            actual_intents.append(
                result["state"].get(
                    "intent"
                )
            )

            # ------------------------------------------------
            # Preserve workflow state
            # ------------------------------------------------

            pending_action = result[
                "state"
            ].get(
                "pending_action"
            )

            pending_order_id = result[
                "state"
            ].get(
                "pending_order_id"
            )

            user_confirmation = result[
                "state"
            ].get(
                "user_confirmation"
            )

            # ------------------------------------------------
            # Preserve conversation history
            # ------------------------------------------------

            chat_history = result[
                "chat_history"
            ]

            if result["error"]:

                error = result["error"]

                break

        actual_tools = get_tools_by_turn(
            nodes_by_turn
        )

        behavior_correct = behavior_matches(
            expected["behavior"],
            nodes_by_turn,
            states,
            responses
        )

        return {
            "id": test_id,

            "input": test_case[
                "conversation"
            ],

            "expected_intents":
                expected["intents"],

            "actual_intents":
                actual_intents,

            "expected_tools":
                expected["tools"],

            "actual_tools":
                actual_tools,

            "expected_behavior":
                expected["behavior"],

            "actual_behavior_nodes":
                [
                    node
                    for nodes in nodes_by_turn
                    for node in nodes
                ],

            "intent_correct":
                intents_match(
                    expected["intents"],
                    actual_intents
                ),

            "tool_correct":
                tools_match(
                    expected["tools"],
                    actual_tools
                ),

            "behavior_correct":
                behavior_correct,

            "successful_run":
                error is None,

            "response":
                (
                    responses[-1]["response"]
                    if responses
                    else ""
                ),

            "responses":
                responses,

            "latency":
                total_latency,

            "nodes_by_turn":
                nodes_by_turn,

            "conversation_id":
                conversation_id,

            "error":
                error
        }

    # ========================================================
    # SINGLE TURN
    # ========================================================

    user_message = test_case[
        "input"
    ]

    result = run_single_turn(
        user_message=user_message,

        conversation_id=conversation_id,

        chat_history=[],

        auto_approve=test_case.get(
            "auto_approve",
            False
        )
    )

    final_state = result[
        "state"
    ]

    nodes = result[
        "nodes"
    ]

    actual_intent = final_state.get(
        "intent"
    )

    actual_tool = get_actual_tool(
        nodes
    )

    behavior_correct = behavior_matches(
        expected["behavior"],
        [nodes],
        [final_state],
        [result["response"]]
    )

    return {
        "id": test_id,

        "input": user_message,

        "expected_intent":
            expected["intents"][0],

        "actual_intent":
            actual_intent,

        "expected_tool":
            expected["tools"][0],

        "actual_tool":
            actual_tool,

        "expected_behavior":
            expected["behavior"],

        "actual_behavior_nodes":
            nodes,

        "intent_correct":
            (
                actual_intent
                == expected["intents"][0]
            ),

        "tool_correct":
            (
                actual_tool
                == expected["tools"][0]
            ),

        "behavior_correct":
            behavior_correct,

        "successful_run":
            result["error"] is None,

        "response":
            result["response"],

        "responses": [
            {
                "turn": 1,
                "input": user_message,
                "response":
                    result["response"],
                "nodes": nodes,
                "latency":
                    result["latency"]
            }
        ],

        "latency":
            result["latency"],

        "nodes":
            nodes,

        "conversation_id":
            conversation_id,

        "error":
            result["error"]
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 60)
    print(
        "AI CUSTOMER SUPPORT AGENT EVALUATION"
    )
    print("=" * 60)

    results = []

    for test_case in TEST_CASES:

        print(
            f"\nRunning Test "
            f"{test_case['id']}..."
        )

        result = run_test_case(
            test_case
        )

        results.append(result)

        print(
            "Intent:   "
            + (
                "PASS"
                if result["intent_correct"]
                else "FAIL"
            )
        )

        print(
            "Tool:     "
            + (
                "PASS"
                if result["tool_correct"]
                else "FAIL"
            )
        )

        print(
            "Behavior: "
            + (
                "PASS"
                if result["behavior_correct"]
                else "FAIL"
            )
        )

        print(
            "Execution:"
            + (
                " PASS"
                if result["successful_run"]
                else " FAIL"
            )
        )

        print(
            f"Latency: "
            f"{result['latency']:.2f}s"
        )

        if result["error"]:

            print(
                f"Error: "
                f"{result['error']}"
            )

    # ========================================================
    # METRICS
    # ========================================================

    total = len(results)

    intent_correct = sum(
        r["intent_correct"]
        for r in results
    )

    tool_correct = sum(
        r["tool_correct"]
        for r in results
    )

    behavior_correct = sum(
        r["behavior_correct"]
        for r in results
    )

    successful_runs = sum(
        r["successful_run"]
        for r in results
    )

    total_latency = sum(
        r["latency"]
        for r in results
    )

    average_latency = (
        total_latency / total
        if total
        else 0
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print(
        "EVALUATION SUMMARY"
    )
    print("=" * 60)

    print(
        f"Total Test Cases:       "
        f"{total}"
    )

    print(
        f"Intent Accuracy:        "
        f"{intent_correct / total * 100:.2f}%"
    )

    print(
        f"Tool Selection Accuracy:"
        f" {tool_correct / total * 100:.2f}%"
    )

    print(
        f"Behavior Accuracy:      "
        f"{behavior_correct / total * 100:.2f}%"
    )

    print(
        f"Execution Success:      "
        f"{successful_runs / total * 100:.2f}%"
    )

    print(
        f"Average Latency:        "
        f"{average_latency:.2f}s"
    )

    # ========================================================
    # FAILED TESTS
    # ========================================================

    failed = [
        r
        for r in results
        if (
            not r["intent_correct"]
            or not r["tool_correct"]
            or not r["behavior_correct"]
            or not r["successful_run"]
        )
    ]

    print("\n" + "=" * 60)
    print(
        "FAILED TEST CASES"
    )
    print("=" * 60)

    if not failed:

        print(
            "All test cases passed! 🎉"
        )

    else:

        for result in failed:

            print(
                f"\nTest {result['id']}"
            )

            print(
                f"Input: "
                f"{result['input']}"
            )

            print(
                f"Expected intent: "
                f"{result.get('expected_intent', result.get('expected_intents'))}"
            )

            print(
                f"Actual intent:   "
                f"{result.get('actual_intent', result.get('actual_intents'))}"
            )

            print(
                f"Expected tool:   "
                f"{result.get('expected_tool', result.get('expected_tools'))}"
            )

            print(
                f"Actual tool:     "
                f"{result.get('actual_tool', result.get('actual_tools'))}"
            )

            print(
                f"Expected behavior:"
                f" {result['expected_behavior']}"
            )

            print(
                "Actual workflow nodes:"
            )

            print(
                result[
                    "actual_behavior_nodes"
                ]
            )

            if result["error"]:

                print(
                    f"Error: "
                    f"{result['error']}"
                )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    report = {

        "summary": {

            "total_test_cases":
                total,

            "intent_accuracy":
                (
                    intent_correct
                    / total
                    * 100
                    if total
                    else 0
                ),

            "tool_selection_accuracy":
                (
                    tool_correct
                    / total
                    * 100
                    if total
                    else 0
                ),

            "behavior_accuracy":
                (
                    behavior_correct
                    / total
                    * 100
                    if total
                    else 0
                ),

            "execution_success":
                (
                    successful_runs
                    / total
                    * 100
                    if total
                    else 0
                ),

            "average_latency_seconds":
                average_latency
        },

        "failed_tests":
            failed,

        "results":
            results
    }

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    print(
        f"\nDetailed results saved to:"
        f" {RESULTS_FILE}"
    )

    print("\n" + "=" * 60)
    print(
        "Evaluation complete."
    )
    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()