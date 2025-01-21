from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from models.base import Base
from models.validators import UserValidator, handle_db_operation


ROLE = ['SUPPORT', 'COMMERCIAL', 'GESTION']


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String, nullable=False)

    clients = relationship('Client', back_populates='commercial')
    events_support = relationship('Event', back_populates='support_contact')

    def __repr__(self):
        return f'User {self.username}'
