from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import User, UserRole

DATABASE_URL = "sqlite:///epic_event.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def create_admin():
    """Créer un premier utilisateur de gestion si aucun n'existe."""
    existing_admin = session.query(
        User).filter_by(role=UserRole.GESTION.value).first()

    if existing_admin:
        print("✅ Un utilisateur de gestion existe déjà.")
        return

    admin = User.create_object(
        session,
        username="admin",
        email="admin@example.com",
        password="AdminSecure123!",
        role=UserRole.GESTION.value
    )

    print(f"✅ Utilisateur admin '{admin.username}' créé avec succès !")


if __name__ == "__main__":
    create_admin()
