from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from src.models.base import BaseModel
from src.models.validators import UserValidator
import hashlib
import os
from sentry_sdk import capture_message, capture_exception
from src.config.sentry_base import logger
from enum import Enum


class UserRole(str, Enum):
    """Enumération des rôles d'utilisateur"""
    COMMERCIAL = "COMMERCIAL"
    SUPPORT = "SUPPORT"
    GESTION = "GESTION"


class User(BaseModel):
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

    @classmethod
    def create_object(cls, session, **kwargs) -> 'User':
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
            UserValidator.validate_required_fields(**kwargs)
            if cls.get_object(session, email=kwargs['email']):
                raise Exception("Un utilisateur avec cet email existe déjà")
            kwargs['password'] = cls.hash_password(kwargs['password'])
            success_message = f"Utilisateur '{kwargs['username']}' créé"
            logger.info(success_message)
            capture_message(success_message)
            return cls._save_object(session, cls(**kwargs))
        except Exception as e:
            logger.error("Erreur lors de la création de l'utilisateur "
                         f"'{kwargs["username"]}': {str(e)}")
            capture_exception(e)
            raise Exception(f'Erreur lors de la création'
                            f' de l\'utilisateur : {str(e)}')

    @classmethod
    def update_object(cls, session, user_id, **kwargs):
        """
        Met à jour un utilisateur
        **kwargs: email, username, password, role
        Utilisation : update_user(session, user_id, email='email')
        """
        try:
            user = cls.get_object(session, id=user_id)

            updates = {
                key: value for key, value in kwargs.items()
                if value is not None
            }

            if not user:
                raise Exception("L'utilisateur n'existe pas")
            if 'email' in updates and user.email != updates['email']:
                if cls.get_object(session, email=updates['email']):
                    raise Exception(
                        "Un utilisateur avec cet email existe déjà"
                    )
            if 'role' in updates:
                UserValidator.validate_role(updates['role'])

            if 'password' in updates:
                updates['password'] = cls.hash_password(updates['password'])

            for key, value in updates.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            success_message = f"Utilisateur '{user.username}' mis à jour"
            logger.info(success_message)
            capture_message(success_message)
            return cls._save_object(session, user)
        except Exception as e:
            session.rollback()
            logger.error("Erreur lors de la mise à jour de l'utilisateur "
                         f"'{id}': {str(e)}")
            capture_exception(e)
            raise Exception(
                f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}"
            )

    @classmethod
    def delete_object(cls, session, user_id):
        """
        Supprime un utilisateur
        Utilisation : delete_user(session, user_id)
        """
        try:
            user = cls.get_object(session, id=user_id)

            if not user:
                raise Exception("L'utilisateur n'existe pas")

            return cls._delete_object(session, user)
        except Exception as e:
            session.rollback()
            raise Exception(
                f"Erreur lors de la suppression de l'utilisateur: {str(e)}"
            )

    def format_user_data(session, user):
        """
        Format les données de l'utilisateur pour la mise en page
        """
        return {
                "ID": str(user.id),
                "Username": user.username,
                "Email": user.email,
                "Role": str(user.role)
        }
