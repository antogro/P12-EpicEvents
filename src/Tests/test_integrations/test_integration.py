import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from src.models.base import Base
from src.models.user import User, UserRole
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event


@pytest.fixture(scope="function")
def db_session():
    """Fixture pour créer une base de données en mémoire
    et une session SQLAlchemy."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_client_contract_event(db_session):
    """Test d'intégration pour la création d'un
    client, d'un contrat et d'un événement.
    """

    # 1. Créer un utilisateur commercial
    commercial = User.create_object(
        db_session,
        username="commercial_user",
        email="commercial@example.com",
        password="securepassword",
        role=UserRole.COMMERCIAL.value,
    )

    assert commercial is not None
    assert commercial.role == UserRole.COMMERCIAL.value

    # 2. Créer un utilisateur support
    support_user = User.create_object(
        db_session,
        username="support_user",
        email="support@example.com",
        password="securepassword",
        role=UserRole.SUPPORT.value,
    )

    assert support_user is not None
    assert support_user.role == UserRole.SUPPORT.value

    # 3. Créer un client associé au commercial
    client = Client.create_object(
        db_session,
        first_name="Jean",
        last_name="Dupont",
        email="jean.dupont@example.com",
        phone="0601020304",
        company_name="Dupont Entreprise",
        commercial_id=commercial.id,
    )

    assert client is not None
    assert client.commercial_id == commercial.id

    # 4. Créer un contrat signé pour ce client
    contract = Contract.create_object(
        db_session,
        client_id=client.id,
        commercial_id=commercial.id,
        total_amount=5000.0,
        remaining_amount=2000.0
    )

    assert contract is not None
    assert contract.client_id == client.id

    # Signer le contrat pour permettre la création d'un événement
    contract = Contract.sign_object(db_session, contract.id)
    assert contract.is_signed is True

    start_date = (
        datetime.now(timezone.utc) + timedelta(days=5)).strftime(
            "%Y-%m-%d %H:%M:%S")
    end_date = (
        datetime.now(timezone.utc) + timedelta(
            days=5, hours=2)).strftime("%Y-%m-%d %H:%M:%S")

    event = Event.create_object(
        db_session,
        name="Réunion stratégique",
        client_id=client.id,
        contract_id=contract.id,
        support_contact_id=support_user.id,
        start_date=start_date,
        end_date=end_date,
        location="Paris",
        attendees=10,
        notes="Planification stratégique pour Q2"
    )

    assert event is not None
    assert event.client_id == client.id
    assert event.contract_id == contract.id
    assert event.support_contact_id == support_user.id
