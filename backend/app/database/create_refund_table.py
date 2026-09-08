from backend.app.database.database import Base, engine
from backend.app.models.refund import Refund

Base.metadata.create_all(bind=engine)

print("Refund table created!")