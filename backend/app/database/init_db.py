from backend.app.database.database import Base, engine

from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.agent_action import AgentAction

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")