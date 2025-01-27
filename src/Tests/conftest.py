import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)
from models.base import Base


@pytest.fixture(scope='module')
def engine():
    return create_engine('sqlite:///:memory:')


@pytest.fixture(scope='module')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def user_data_commercial():
    """
    Fixture pour les données de test d'un utilisateur
    retourne un utilisateur:
        role: Gestion
    """
    return {
        "email": "test_user@test.fr",
        "username": "username",
        "password": "password",
        "role": "COMMERCIAL",
    }


@pytest.fixture
def make_user(user_data_commercial):
    """Fixture pour créer un club."""
    def _make_user(**kwargs):
        user = user_data_commercial.copy()
        user.update(kwargs)
        return user
    return _make_user


@pytest.fixture
def client_data():
    """
    Fixture pour les données de test d'un utilisateur
    retourne un utilisateur:
        role: Commercial
    """
    return {
        "full_name": "full_name",
        "email": "email@email.fr",
        "phone": "0101010101",
        "company": "compagny_name",
        "commercial_id": 1,
    }


@pytest.fixture
def make_client(client_data):
    """Fixture pour créer un club."""
    def _make_client(**kwargs):
        client = client_data.copy()
        client.update(kwargs)
        return client
    return _make_client


@pytest.fixture
def contract_data():
    """
    Fixture pour les données de test d'un contrat
    """
    return {
        "client_id": 1,
        "commercial_id": 1,
        "total_amount": 1000,
        "remaining_amount": 1000,
    }


@pytest.fixture
def event_data():
    """
    Fixture pour les données de test d'un évènement
    """
    return {
        "contract_id": 1,
        "name": "name",
        "start_date":  (
            datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
        "end_date":  (
            datetime.now() + timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S'),
        "location": "location",
        "attendees": 10,
    }
