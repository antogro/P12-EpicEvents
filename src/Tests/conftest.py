import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)
from config.permission_rules import PermissionRule
from models.base import Base


@pytest.fixture(scope="module")
def engine():
    """Crée un moteur SQLite en mémoire pour les tests."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def tables(engine):
    """Crée et supprime les tables pour chaque module de test."""
    connection = engine.connect()
    session = sessionmaker(bind=engine)()

    Base.metadata.create_all(engine)

    PermissionRule.initialize_permission(session)
    PermissionRule.initialize_rules(session)
    session.commit()

    yield  # Laisse le test s'exécuter

    Base.metadata.drop_all(engine)
    connection.close()


@pytest.fixture
def session(engine, tables):
    """Fournit une session SQLAlchemy transactionnelle pour chaque test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def ctx_with_session(session):
    """
    Fixture qui fournit un contexte `ctx`
    avec une session SQLAlchemy valide.
    """
    return {"session": session}


@pytest.fixture
def mock_session(mocker):
    """
    Mocke une session SQLAlchemy pour
    éviter l'accès à la base de données.
    """
    session_mock = mocker.MagicMock()
    mocker.patch("src.controllers.user.get_session", return_value=session_mock)
    return session_mock


@pytest.fixture
def make_user():
    """Fixture pour générer un utilisateur de test."""
    def _make_user(**kwargs):
        user = {
            "id": 1,
            "username": "testuser",
            "email": "test_user@test.fr",
            "password": "password",
            "role": "COMMERCIAL",
        }
        user.update(kwargs)
        return user
    return _make_user


@pytest.fixture
def make_client():
    """Fixture pour générer un client de test."""
    def _make_client(**kwargs):
        client = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "0101010101",
            "company_name": "JD Corp",
            "commercial_id": 1,
        }
        client.update(kwargs)
        return client
    return _make_client


@pytest.fixture
def make_contract():
    """Fixture pour générer un contrat de test."""
    def _make_contract(**kwargs):
        contract = {
            "id": 1,
            "client_id": 1,
            "commercial_id": 1,
            "total_amount": 1000,
            "remaining_amount": 500,
            "is_signed": True,
        }
        contract.update(kwargs)
        return contract
    return _make_contract


@pytest.fixture
def make_event():
    """Fixture pour générer un événement de test."""
    def _make_event(**kwargs):
        event = {
            "id": 1,
            "support_contact_id": 1,
            "client_id": 1,
            "contract_id": 1,
            "name": "Événement Test",
            "start_date": (datetime.now() + timedelta(days=30)).strftime(
                "%Y-%m-%d %H:%M:%S"),
            "end_date": (datetime.now() + timedelta(days=40)).strftime(
                "%Y-%m-%d %H:%M:%S"),
            "location": "Paris",
            "attendees": 100,
        }
        event.update(kwargs)
        return event
    return _make_event
