from langchain_core.tools import tool

from backend.app.database.database import SessionLocal
from backend.app.models.ticket import Ticket


@tool
def create_ticket(
    customer_id: str,
    category: str,
    description: str,
    priority: str,
):
    """Create a customer support ticket."""

    db = SessionLocal()

    try:
        # Generate a simple ticket ID
        ticket_count = db.query(Ticket).count()
        ticket_id = f"TKT-{ticket_count + 1:05d}"

        ticket = Ticket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            category=category,
            description=description,
            priority=priority,
            status="open",
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "customer_id": ticket.customer_id,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
        }

    finally:
        db.close()