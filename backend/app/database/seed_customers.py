from backend.app.database.database import SessionLocal
from backend.app.models.customer import Customer


db = SessionLocal()

customers = [
    Customer(
        customer_id="CUS-001",
        name="Rahul",
        email="rahul@example.com",
    ),
    Customer(
        customer_id="CUS-002",
        name="Priya",
        email="priya@example.com",
    ),
]

db.add_all(customers)
db.commit()
db.close()

print("Customers inserted!")