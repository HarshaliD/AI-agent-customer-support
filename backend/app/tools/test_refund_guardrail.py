from backend.app.agents.workflow import workflow


def run_test(message, approval_status="not_required"):
    initial_state = {
        "user_message": message,
        "chat_history": [],
        "intent": "",
        "order_id": "",
        "order_result": {},
        "knowledge_result": "",
        "refund_amount": 0.0,
        "refund_valid": False,
        "approval_required": False,
        "approval_status": approval_status,
        "final_response": "",
    }

    result = workflow.invoke(initial_state)

    print("\n" + "=" * 60)
    print("USER:", message)
    print("MANAGER DECISION:", approval_status)
    print("=" * 60)

    print("Intent:", result["intent"])
    print("Order ID:", result["order_id"])
    print("Refund amount:", result["refund_amount"])
    print("Refund valid:", result["refund_valid"])
    print("Approval required:", result["approval_required"])
    print("Approval status:", result["approval_status"])
    print("Response:", result["final_response"])

    print("\nOrder/Refund Result:")
    print(result["order_result"])


if __name__ == "__main__":

    # ========================================================
    # TEST 1: High-value refund + PENDING
    # Expected: refund should NOT be created
    # ========================================================

    run_test(
        "I want a refund of ₹60000 for order ORD-10245",
        approval_status="pending"
    )


    # ========================================================
    # TEST 2: High-value refund + APPROVED
    # Expected: request_refund() should execute
    # ========================================================

    run_test(
        "I want a refund of ₹60000 for order ORD-10245",
        approval_status="approved"
    )


    # ========================================================
    # TEST 3: High-value refund + REJECTED
    # Expected: refund should NOT be created
    # ========================================================

    run_test(
        "I want a refund of ₹60000 for order ORD-10245",
        approval_status="rejected"
    )


    # ========================================================
    # TEST 4: Normal refund
    # Expected: no manager approval required
    # ========================================================

    run_test(
        "I want a refund of ₹40000 for order ORD-10245",
        approval_status="not_required"
    )


    # ========================================================
    # TEST 5: Non-existent order
    # Expected: rejected before approval logic
    # ========================================================

    run_test(
        "I want a refund of ₹60000 for order ORD-99999",
        approval_status="pending"
    )