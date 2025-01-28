from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from models.base import Base


class Event(Base):
    """
    Modele d'un Event
    args: - id (int),
          - contract_id (int),
          - support_contact_id (int),
          - name (str),
          - start_date (int),
          - end_date (int),
          - location (str),
          - attendees (int),
          - note (str)
    """
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    support_contact_id = Column(Integer, ForeignKey('users.id'))
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    name = Column(String)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.utcnow
    )

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'<Event {self.name}>'
