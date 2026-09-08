from langchain_core.tools import tool

from backend.app.database.database import SessionLocal
from backend.app.models.refund import Refund


@tool
def request_refund(
    order_id: str,
    reason: str,
    amount: float,
):
    """Create a refund request for an order."""

    db = SessionLocal()

    try:
        refund_count = db.query(Refund).count()
        refund_id = f"REF-{refund_count + 1:05d}"

        refund = Refund(
            refund_id=refund_id,
            order_id=order_id,
            reason=reason,
            amount=amount,
            status="pending",
        )

        db.add(refund)
        db.commit()
        db.refresh(refund)

        return {
            "success": True,
            "refund_id": refund.refund_id,
            "order_id": refund.order_id,
            "amount": refund.amount,
            "status": refund.status,
        }

    finally:
        db.close()