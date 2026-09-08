from backend.app.tools.cancellation_tools import cancel_order


# Test 1: processing order → should cancel
result = cancel_order.invoke({
    "order_id": "ORD-10246"
})

print("Processing order result:")
print(result)


# Test 2: shipped order → should be rejected
result = cancel_order.invoke({
    "order_id": "ORD-10245"
})

print("\nShipped order result:")
print(result)