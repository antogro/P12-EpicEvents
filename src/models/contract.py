from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, Boolean
from models.base import Base
from validators import ContractValidator, handle_db_operation


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_signed = Column(Boolean, default=False)

    client = relationship("Client", back_populates="contracts")
    events = relationship("Event", back_populates="contract")
