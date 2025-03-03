import pytest
from models.event import Event
from models.user import User
from models.contract import Contract
from models.client import Client
from datetime import datetime


def test_create_event(
    mocker, session, make_event, make_user, make_client, make_contract
):
    """Test qu'un événement peut être créé avec succès."""
    support_user = make_user(role="SUPPORT")
    client_fixture = make_client()
    event_fixture = make_event()
    contract_fixture = Contract(**make_contract())

    mocker.patch(
        "models.contract.Contract.get_object", return_value=contract_fixture)
    mocker.patch(
        "models.user.User.get_object", return_value=User(**support_user))
    mocker.patch(
        "models.client.Client.get_object",
        return_value=Client(**client_fixture)
    )

    event = Event.create_object(session, **event_fixture)
    assert event.name == event_fixture["name"]
    assert event.location == event_fixture["location"]


def test_create_event_should_raise_error_missing_required_fields(
    mocker, session, make_client, make_user
):
    """Test qu'une erreur est levée si des
    champs obligatoires sont manquants."""
    support_user = make_user(role="SUPPORT")
    client_fixture = make_client()

    incomplete_data = {
        "support_contact_id": 1,
        "client_id": 1,
        "contract_id": 1,
        "name": "Event Name",
        "location": "Event Location",
        "attendees": 10,
    }

    mocker.patch(
        "models.validators.EventValidator.validate_dates", return_value=None)
    mocker.patch(
        "models.user.User.get_object", return_value=User(**support_user))
    mocker.patch(
        "models.client.Client.get_object",
        return_value=Client(**client_fixture)
    )

    with pytest.raises(Exception, match="Le champ start_date est requis"):
        Event.create_object(session, **incomplete_data)


def test_create_event_should_raise_error_invalid_dates(
        mocker, session, make_event):
    """Test qu'une erreur est levée si la date de début est dans le passé."""
    past_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_fixture = make_event(start_date=past_date)
    mocker.patch.object(Contract, "get_object", return_value=None)

    with pytest.raises(
            Exception, match="La date de début doit être dans le futur"):
        Event.create_object(session, **event_fixture)


def test_create_event_should_raise_error_end_date(mocker, session, make_event):
    """Test qu'une erreur est levée si la date
    de fin est avant la date de début."""
    invalide_end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_fixture = make_event(end_date=invalide_end_date)

    with pytest.raises(
        Exception,
        match="La date de fin doit être supérieure à la date de début"
    ):
        Event.create_object(session, **event_fixture)


def test_create_event_should_raise_error_no_contract(
        mocker, session, make_event):
    """Test qu'une erreur est levée si le contrat n'existe pas."""
    event_fixture = make_event()
    mocker.patch.object(Contract, "get_object", return_value=None)

    with pytest.raises(Exception, match="Le contrat n'existe pas"):
        Event.create_object(session, **event_fixture)


def test_create_event_should_raise_error_no_support_role(
    mocker, session, make_event, make_contract, make_user
):
    """Test qu'une erreur est levée si le support contact n'est pas valide."""
    commercial_user = make_user(role="COMMERCIAL")
    event_fixture = make_event()
    contract_fixture = Contract(**make_contract())

    mocker.patch(
        "models.contract.Contract.get_object",
        return_value=contract_fixture
    )
    mocker.patch(
        "models.validators.EventValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.EventValidator.validate_dates",
        return_value=None)
    mocker.patch(
        "models.user.User.get_object",
        return_value=User(**commercial_user))

    with pytest.raises(Exception, match="Le SUPPORT n'existe pas"):
        Event.create_object(session, **event_fixture)


def test_create_event_should_raise_error_no_client(
    mocker, session, make_event, make_user, make_contract
):
    """Test qu'une erreur est levée si le client n'existe pas."""
    support_user = make_user(role="SUPPORT")
    event_fixture = make_event()
    contract_fixture = Contract(**make_contract())

    mocker.patch(
        "models.contract.Contract.get_object",
        return_value=contract_fixture)
    mocker.patch(
        "models.user.User.get_object",
        return_value=User(**support_user))
    mocker.patch("models.client.Client.get_object", return_value=None)

    with pytest.raises(Exception, match="Le client n'existe pas"):
        Event.create_object(session, **event_fixture)


def test_update_event(mocker, session, make_event):
    """Test qu'un événement peut être mis à jour."""
    initial_event = Event(**make_event())
    event_id = 1
    update_data = {"location": "Updated Location", "attendees": 20}

    mock_get_event = mocker.patch.object(
        Event, "get_object", return_value=initial_event
    )
    mock_session_commit = mocker.patch.object(session, "commit")

    result = Event.update_object(session, event_id, **update_data)

    assert result.location == update_data["location"]
    assert result.attendees == update_data["attendees"]
    mock_get_event.assert_called_once()
    mock_session_commit.assert_called_once()


def test_update_event_should_raise_error_no_event(mocker, session):
    """Test qu'une erreur est levée si l'événement n'existe pas."""
    event_id = 1
    update_data = {"location": "Updated Location", "attendees": 20}

    mocker.patch("models.event.Event.get_object", return_value=None)

    with pytest.raises(Exception, match="L'événement n'existe pas"):
        Event.update_object(session, event_id, **update_data)


def test_delete_event(mocker, session, make_event):
    """Test qu'un événement peut être supprimé."""
    event_fixture = make_event()
    expected_event = Event(**event_fixture)
    event_id = 1

    mock_get_event = mocker.patch.object(
        Event, "get_object", return_value=expected_event
    )
    mock_session_delete = mocker.patch.object(session, "delete")
    mock_session_commit = mocker.patch.object(session, "commit")

    result = Event.delete_object(session, event_id)

    assert result.contract_id == expected_event.contract_id
    assert result.support_contact_id == expected_event.support_contact_id
    mock_get_event.assert_called_once_with(session, id=event_id)
    mock_session_delete.assert_called_once_with(expected_event)
    mock_session_commit.assert_called_once()


def test_delete_event_should_raise_error_no_event(mocker, session):
    """Test qu'une erreur est levée si l'événement n'existe pas."""
    event_id = 999
    mocker.patch.object(Event, "get_object", return_value=None)

    with pytest.raises(Exception, match="L'événement n'existe pas"):
        Event.delete_object(session, event_id)
