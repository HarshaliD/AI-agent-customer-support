from sqlalchemy import Column, Integer, String, Text

from backend.app.database.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="open")