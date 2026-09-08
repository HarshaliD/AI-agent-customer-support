from backend.app.tools.customer_tools import get_customer


result = get_customer.invoke({
    "customer_id": "CUS-001"
})

print("Customer result:")
print(result)