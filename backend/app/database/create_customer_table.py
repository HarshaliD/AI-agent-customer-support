from backend.app.database.database import Base, engine
from backend.app.models.customer import Customer

Base.metadata.create_all(bind=engine)

print("Customer table created!")