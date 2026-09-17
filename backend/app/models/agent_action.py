from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.database import Base

class AgentAction(Base):
    __tablename__ = "agent_actions"

    id: Mapped[int] = mapped_column(primary_key=True)

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id")
    )

    tool_name: Mapped[str] = mapped_column(String(100))

    arguments: Mapped[str] = mapped_column(Text)

    result: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20))

    latency: Mapped[float] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )