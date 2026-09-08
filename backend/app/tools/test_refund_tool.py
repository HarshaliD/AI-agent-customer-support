from backend.app.tools.refund_tools import request_refund


result = request_refund.invoke({
    "order_id": "ORD-10245",
    "reason": "Product arrived damaged.",
    "amount": 500.0,
})

print("Refund result:")
print(result)