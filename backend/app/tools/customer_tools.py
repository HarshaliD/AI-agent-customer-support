from langchain_core.tools import tool

from backend.app.database.database import SessionLocal
from backend.app.models.customer import Customer


@tool
def get_customer(customer_id: str):
    """Retrieve customer information using the customer ID."""

    db = SessionLocal()

    try:
        customer = (
            db.query(Customer)
            .filter(Customer.customer_id == customer_id)
            .first()
        )

        if customer is None:
            return {
                "error": f"Customer {customer_id} was not found."
            }

        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
        }

    finally:
        db.close()