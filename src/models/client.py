from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from models.base import BaseModel
from models.validators import ClientValidator
from models.user import User


class Client(BaseModel):
    """
    Modele d'un client
        args: id (int),
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
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now(timezone.utc)
    )
    commercial_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'Client {self.first_name} {self.last_name}'

    @classmethod
    def create_object(cls, session, **kwargs) -> 'Client':
        """
        Crée un client
        Utilisation : create_client(
            session,
            first_name (str),
            last_name (str),
            email='email',
            phone='phone',
            company_name='compagny_name',
            commercial_id='commercial_id'
        )
        """
        try:
            ClientValidator.validate_required_fields(**kwargs)
            ClientValidator.validate_email(kwargs['email'])

            if cls.get_object(session, email=kwargs['email']):
                raise Exception("Un client avec cet email existe déjà")

            if 'commercial_id' in kwargs:
                commercial = User.get_object(
                    session, id=kwargs['commercial_id']
                )
                if not commercial or commercial.role != 'COMMERCIAL':
                    raise Exception("Contact commercial invalide")

            return cls._save_object(session, cls(**kwargs))
        except Exception as e:
            raise Exception(f"Erreur lors de la création du client : {str(e)}")

    @classmethod
    def update_object(cls, session, client_id: int, **kwargs) -> 'Client':
        """
        Met à jour un client sans écraser les valeurs existantes par None.
        """
        try:
            client = cls.get_object(session, id=client_id)
            if not client:
                raise Exception("Le client n'existe pas")

            updates = {
                key: value for key, value in kwargs.items()
                if value is not None
            }

            # Vérification de l'email si fourni
            if 'email' in updates:
                ClientValidator.validate_email(updates['email'])
                if cls.get_object(session, email=updates['email']):
                    raise Exception("Un client avec cet email existe déjà")

            # Vérification du commercial_id si fourni
            if 'commercial_id' in updates:
                commercial = User.get_object(
                    session, id=updates['commercial_id']
                )
                if not commercial or commercial.role != 'COMMERCIAL':
                    raise Exception("Contact commercial invalide")

            # Mise à jour des attributs valides
            for key, value in updates.items():
                setattr(client, key, value)

            return cls._save_object(session, client)

        except Exception as e:
            raise Exception(f"Une erreur lors de la mise à jour du client: "
                            f"{str(e)}")

    @classmethod
    def delete_object(cls, session, client_id: int):
        """
        Supprime un client
        Utilisation : delete_client(session, client_id)
        """
        try:
            client = cls.get_object(session, id=client_id)
            if not client:
                raise Exception("Le client n'existe pas")
            return cls._delete_object(session, client)
        except Exception as e:
            raise Exception(
                f"Une erreur lors de la suppression du client: {str(e)}"
            )

    def format_client_data(session, client):
        """
        Format les données du client pour la mise en page
        """
        commercial = User.get_object(session, id=client.commercial_id)
        return {
                "ID": client.id,
                "First name": client.first_name,
                "Last_name": client.last_name,
                "Email": client.email,
                "Phone": client.phone,
                "Company name": client.phone,
                "Commercial ID": client.commercial_id,
                "Commercial Name": commercial.username
        }
