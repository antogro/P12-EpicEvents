import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///epic_event.db")
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)


def get_session():
    """Retourne une session SQLAlchemy"""
    try:
        session = Session()
        return session
    except Exception as e:
        print(f"❌ Erreur lors de la création de la session: {e}")
        raise
