from langchain_core.tools import tool

from backend.app.database.database import SessionLocal
from backend.app.models.order import Order


@tool
def cancel_order(order_id: str):
    """Cancel an order if it is still in processing status."""

    db = SessionLocal()

    try:
        order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if order is None:
            return {
                "success": False,
                "error": f"Order {order_id} was not found."
            }

        if order.status != "processing":
            return {
                "success": False,
                "error": (
                    f"Order {order_id} cannot be cancelled "
                    f"because its status is '{order.status}'."
                )
            }

        order.status = "cancelled"
        db.commit()

        return {
            "success": True,
            "order_id": order.order_id,
            "status": order.status,
        }

    finally:
        db.close() 