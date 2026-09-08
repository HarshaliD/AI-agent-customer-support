from langchain_core.tools import tool

from backend.app.database.database import SessionLocal
from backend.app.models.order import Order


@tool
def get_order(order_id: str):
    """Retrieve information about an order using its order ID."""

    db = SessionLocal()

    try:
        order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if order is None:
            return {
                "error": f"Order {order_id} was not found."
            }

        return {
            "order_id": order.order_id,
            "status": order.status,
            "tracking_number": order.tracking_number,
        }

    finally:
        db.close()