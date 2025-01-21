from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from models.base import Base
from validators import ClientValidator, handle_db_operation


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.utcnow
    )
    commercial_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    commercial = relationship('User', back_populates='clients')
    contracts = relationship('Contract', back_populates='client')

    def __repr__(self):
        return f'Client {self.full_name}'
