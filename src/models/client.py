from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from models.base import Base


class Client(Base):
    """
    Modele d'un client
        args: id (int),
              name (str),
              first_name (str),
              last_name (str),
              email (str),
              phone (str),
              company_name (str)
              commercial_id (int)
    """
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.utcnow
    )
    commercial_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'Client {self.full_name}'
