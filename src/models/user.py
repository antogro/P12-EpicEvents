from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from models.base import Base
from models.validators import UserValidator
import hashlib
import os


class User(Base):
    """
    Modele d'un utilisateur,
    contenant les informations de
    base et les informations de connexion.
        args: id (int),
              username (str),
              email (str),
              password (str),
              role (str)
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    role = Column(String, nullable=False)

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'User {self.username}'

    def get_user(session, **kwargs) -> 'User':
        """
        Récupère un utilisateur selon differents critères
        Utilisation: get_user(session, email='email')
        """
        try:
            return session.query(User).filter_by(**kwargs).first()
        except Exception as e:
            raise Exception(
                f"Erreur lors de la récupération de l'utilisateur: {str(e)}"
            )

    def hash_password(password):
        """
        Hashage du mot de passe
        """
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt, 100000
        )
        return salt + key

    @staticmethod
    def verify_password(stored_password, password):
        """
        Vérification du mot de passe
        """
        salt = stored_password[:32]
        key = stored_password[32:]
        new_key = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt, 100000
        )
        return new_key == key

    def create_user(session, **kwargs) -> 'User':
        """
        Crée un utilisateur
        **kwargs: email, username, password, role
        Utilisation : create_user(
            session,
            email='email',
            username='username',
            password='password',
            role='role'
        )
        """
        try:
            UserValidator.validate_role(kwargs['role'])
            UserValidator.validate_required_fields(kwargs)
            if User.get_user(session, email=kwargs['email']):
                raise Exception("Un utilisateur avec cet email existe déjà")
            user = User(**kwargs)
            user.password = User.hash_password(kwargs['password'])
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise Exception(
                f"Erreur lors de la création de l'utilisateur: {str(e)}"
            )

    def update_user(session, user_id, **kwargs):
        """
        Met à jour un utilisateur
        **kwargs: email, username, password, role
        Utilisation : update_user(session, user_id, email='email')
        """
        try:
            user = User.get_user(session, id=user_id)

            if not user:
                raise Exception("L'utilisateur n'existe pas")
            if 'email' in kwargs and user.email != kwargs['email']:
                if User.get_user(session, email=kwargs['email']):
                    raise Exception(
                        "Un utilisateur avec cet email existe déjà"
                    )

            for key, value in kwargs.items():

                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise Exception(
                f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}"
            )

    def delete_user(session, user_id):
        """
        Supprime un utilisateur
        Utilisation : delete_user(session, user_id)
        """
        try:
            user = User.get_user(session, id=user_id)

            if not user:
                raise Exception("L'utilisateur n'existe pas")
            session.delete(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise Exception(
                f"Erreur lors de la suppression de l'utilisateur: {str(e)}"
            )
