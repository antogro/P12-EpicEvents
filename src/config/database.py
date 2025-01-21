from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base


DATA_BASE_URL = 'sqlite:///./epic_event.db'
engine = create_engine(DATA_BASE_URL, echo=True)
Session = sessionmaker(bind=engine)


def create_database():
    Base.metadata.create_all(engine)


def get_session():
    try:
        return Session()
    except Exception as e:
        raise Exception(f"Erreur de connexion à la base de données : {str(e)}")
