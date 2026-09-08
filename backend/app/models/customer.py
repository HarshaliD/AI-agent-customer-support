from sqlalchemy import Column, Integer, String

from backend.app.database.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)