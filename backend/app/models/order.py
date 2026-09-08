from sqlalchemy import Column, Integer, String

from backend.app.database.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False)
    tracking_number = Column(String(100), nullable=True)