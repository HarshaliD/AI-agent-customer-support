from sqlalchemy import Column, Integer, String, Float, Text

from backend.app.database.database import Base


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    refund_id = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="pending")