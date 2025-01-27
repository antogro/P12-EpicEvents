from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, Boolean
from models.base import Base


class Contract(Base):
    """
    Modele d'un contrat
        args: - id (int),
              - client_id (int),
              - commercial_id (int),
              - total_amout (float),
              - remaining-amount (float),
              - is_signed (bool),
    """
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_signed = Column(Boolean, default=False)

    __table_args__ = {'extend_existing': True}
