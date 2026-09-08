from backend.app.database.database import Base, engine
from backend.app.models.ticket import Ticket

Base.metadata.create_all(bind=engine)

print("Ticket table created!")
