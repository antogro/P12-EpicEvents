from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base
from src.models.user import User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.permission import DynamicPermission, DynamicPermissionRule
from src.models.relationships import setup_relationships
from src.config.permission_rules import PermissionRule
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///epic_event.db")
engine = create_engine(DATABASE_URL)


def create_core_tables(engine):
    """Créer les tables principales (User, Client, Contract, Event)"""
    Base.metadata.create_all(engine, tables=[
        User.__table__,
        Client.__table__,
        Contract.__table__,
        Event.__table__,
    ])


def create_permission_tables(engine):
    """Créer les tables des permissions après les autres"""
    Base.metadata.create_all(engine, tables=[
        DynamicPermission.__table__,
        DynamicPermissionRule.__table__,
    ])


def init_database(database_url=DATABASE_URL):
    """Initialisation en deux étapes : core tables puis permissions"""
    engine = create_engine(database_url)
    setup_relationships()

    create_core_tables(engine)
    create_permission_tables(engine)

    return engine


def init_permissions_and_rules(engine):
    """Initialise les permissions et les règles dans la base de données"""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        PermissionRule.initialize_permission(session)
        PermissionRule.initialize_rules(session)
        session.commit()
    except Exception as e:
        session.rollback()
        print("❌ Erreur lors de l'initialisation"
              f" des permissions et règles: {str(e)}")
        raise
    finally:
        session.close()


def main():
    try:
        print("🔄 Initialisation de la base de données et des permissions...")
        engine = init_database()
        init_permissions_and_rules(engine)
        print("✅ Base de données et permissions initialisées avec succès!")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise


if __name__ == "__main__":
    main()
