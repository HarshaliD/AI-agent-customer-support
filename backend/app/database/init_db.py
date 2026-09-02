from backend.app.database.database import Base, engine
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")