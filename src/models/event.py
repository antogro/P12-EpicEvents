from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from models.base import Base
from models import User, Contract, EventValidator, handle_db_operation


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    name = Column(String)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    support_contact_id = Column(Integer, ForeignKey('users.id'))
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.utcnow
    )

    contract = relationship('Contract', back_populates='events')
    support_contact = relationship('User', back_populates='events_support')

    def __repr__(self):
        return f'<Event {self.name}>'
