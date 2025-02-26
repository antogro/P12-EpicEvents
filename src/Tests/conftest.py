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


@pytest.fixture
def mock_session(mocker):
    session_mock = mocker.MagicMock()
    mocker.patch("src.controllers.user.get_session", return_value=session_mock)
    return session_mock


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
        "id": 1,
        "email": "test_user@test.fr",
        "username": "usernam",
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
        "id": 1,
        "first_name": "full_name",
        "last_name": "full_name",
        "email": "email@email.fr",
        "phone": "0101010101",
        "company_name": "compagny_name",
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
        "id": 1,
        "client_id": 1,
        "commercial_id": 1,
        "total_amount": 1000,
        "remaining_amount": 1000,
        "is_signed": True
    }


@pytest.fixture
def make_contract(contract_data):
    """Fixture pour créer un club."""
    def _make_contract(**kwargs):
        contract = contract_data.copy()
        contract.update(kwargs)
        return contract
    return _make_contract


@pytest.fixture
def event_data():
    """
    Fixture pour les données de test d'un évènement
    """
    return {
        "support_contact_id": 1,
        "client_id": 1,
        "contract_id": 1,
        "name": "name",
        "start_date":  (
            datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
        "end_date":  (
            datetime.now() + timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S'),
        "location": "location",
        "attendees": 10,
    }


@pytest.fixture
def make_event(event_data):
    """Fixture pour créer un club."""
    def _make_event(**kwargs):
        event = event_data.copy()
        event.update(kwargs)
        return event
    return _make_event
