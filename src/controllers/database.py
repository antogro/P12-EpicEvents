from sqlalchemy import create_engine
import os
import sys
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)
from models.relationships import setup_relationships
from models.base import Base


def init_database(database_url='sqlite:///epic_events.db'):
    """Initialise la base de données et crée toutes les tables"""
    engine = create_engine(database_url)

    setup_relationships()

    Base.metadata.create_all(engine)


if __name__ == "__main__":
    try:
        init_database()
        print("✅ Base de données initialisée avec succès!")
    except Exception as e:
        print(
            f"❌ Erreur lors de l'initialisation de la base de données: {str(e)}"
        )
