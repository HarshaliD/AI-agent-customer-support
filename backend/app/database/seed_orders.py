from backend.app.database.database import SessionLocal
from backend.app.models.order import Order


db = SessionLocal()

orders = [
    Order(
        order_id="ORD-10245",
        status="shipped",
        tracking_number="TRK123",
    ),
    Order(
        order_id="ORD-10246",
        status="processing",
        tracking_number=None,
    ),
]

db.add_all(orders)
db.commit()
db.close()

print("Orders inserted!")