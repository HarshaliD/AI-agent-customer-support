from backend.app.database.database import Base, engine
from backend.app.models.order import Order

Base.metadata.create_all(bind=engine)

print("Tables created!")