from backend.app.tools.ticket_tools import create_ticket


result = create_ticket.invoke({
    "customer_id": "CUS-001",
    "category": "delivery",
    "description": "My order has been delayed.",
    "priority": "medium",
})

print("Ticket result:")
print(result)