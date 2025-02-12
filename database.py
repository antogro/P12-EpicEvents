from sqlalchemy import create_engine
from src.models.relationships import setup_relationships
from src.models.base import Base
from sqlalchemy.orm import sessionmaker
from src.models.permission import PermissionManager


def init_database(database_url="sqlite:///epic_event.db"):
    """Initialise la base de données et crée toutes les tables"""
    # Création du moteur de base de données
    engine = create_engine(database_url)

    # Configuration des relations
    setup_relationships()

    # Création de toutes les tables
    Base.metadata.create_all(engine)


def init_permissions_and_rules(database_url="sqlite:///epic_event.db"):
    """Initialize permissions and rules in the database"""
    # Create database engine
    engine = create_engine(database_url)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Initialize permissions
        print("Initializing permissions...")
        PermissionManager.initialize_permission(session)
        session.commit()
        print("✅ Permissions initialized successfully!")

        # Initialize rules
        print("Initializing permission rules...")
        PermissionManager.initialize_rules(session)
        session.commit()
        print("✅ Base de données initialisée avec succès!!")

    except Exception as e:
        session.rollback()
        print(f"❌ Error during initialization: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    try:
        init_database()
        print("✅ Base de données initialisée avec succès!")
        init_permissions_and_rules()
    except Exception as e:
        print(
            "❌ Erreur lors de l'initialisation "
            f"de la base de données: {str(e)}")
