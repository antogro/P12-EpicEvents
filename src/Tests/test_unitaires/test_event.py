from models.event import Event
from models.user import User
from models.contract import Contract
from models.client import Client
import pytest
from datetime import datetime


def test_create_event(mocker, session, make_event, make_user, make_client):
    commercial_user_fixture = make_user(role='SUPPORT')
    client_fixture = make_client()
    event_fixture = make_event()
    mocker.patch.object(Contract, 'get_object', return_value=True)
    mocker.patch(
        "models.validators.EventValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.EventValidator.validate_dates",
        return_value=None
    )
    mocker.patch(
        "models.user.User.get_object",
        return_value=User(**commercial_user_fixture)
    )
    mocker.patch(
        "models.client.Client.get_object",
        return_value=Client(**client_fixture)
    )

    event = Event.create_object(session, **event_fixture)
    assert event.name == event_fixture['name']
    assert event.location == event_fixture['location']


def test_create_event_raise_error_invalid_required_field(
        mocker,
        session,
        make_client,
        make_user
):
    commercial_user_fixture = make_user(role='SUPPORT')
    client_fixture = make_client()
    mocker.patch.object(Event, 'get_object', return_value=None)
    incomplete_data = {
        "support_contact_id": 1,
        "client_id": 1,
        "contract_id": 1,
        "name": "name",
        "location": "location",
        "attendees": 10,
    }
    mocker.patch(
        "models.validators.EventValidator.validate_dates",
        return_value=None
    )
    mocker.patch(
        "models.contract.User.get_object",
        return_value=User(**commercial_user_fixture)
    )
    mocker.patch(
        "models.client.Client.get_object",
        return_value=Client(**client_fixture)
    )

    with pytest.raises(Exception) as e:
        Event.create_object(session, **incomplete_data)
    assert ("Le champ start_date est requis"
            in str(e.value))


def test_create_event_should_raise_error_invalide_date(
    mocker,
    session,
    make_event
):
    event_fixture = make_event(start_date=datetime.now())
    mocker.patch.object(Contract, 'get_object', return_value=None)

    with pytest.raises(Exception) as e:
        Event.create_object(session, **event_fixture)
    assert (
        "La date de début doit être dans le futur"
        in str(e.value)
    )


def test_create_event_should_raise_error_end_date(
    mocker,
    session,
    make_event
):
    event_fixture = make_event(end_date=datetime.now())

    with pytest.raises(Exception) as e:
        Event.create_object(session, **event_fixture)
    assert (
        "La date de fin doit être supérieure à la date de début"
        in str(e.value)
    )


def test_create_event_should_raise_error_with_no_contract(
    mocker,
    session,
    make_event
):
    event_fixture = make_event()
    mocker.patch.object(Contract, 'get_object', return_value=None)

    with pytest.raises(Exception) as e:
        Event.create_object(session, **event_fixture)
    assert (
        "Le contrat n'existe pas"
        in str(e.value)
    )


def test_create_event_should_raise_error_with_no_support_role(
    mocker,
    session,
    make_event,
    make_user
):
    commercial_user_fixture = make_user(role='COMMERCIAL')
    event_fixture = make_event()
    mocker.patch.object(Contract, 'get_object', return_value=True)
    mocker.patch(
        "models.validators.EventValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.EventValidator.validate_dates",
        return_value=None
    )
    mocker.patch(
        "models.contract.User.get_object",
        return_value=User(**commercial_user_fixture)
    )

    with pytest.raises(Exception) as e:
        Event.create_object(session, **event_fixture)
    assert (
        "Le SUPPORT n'existe pas"
        in str(e.value)
    )


def test_create_event_should_raise_error_with_no_client(
    mocker,
    session,
    make_event,
    make_user
):
    commercial_user_fixture = make_user(role='SUPPORT')
    event_fixture = make_event()
    mocker.patch.object(Contract, 'get_object', return_value=True)
    mocker.patch(
        "models.validators.EventValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.EventValidator.validate_dates",
        return_value=None
    )
    mocker.patch(
        "models.user.User.get_object",
        return_value=User(**commercial_user_fixture)
    )
    mocker.patch(
        "models.client.Client.get_object",
        return_value=None
    )

    with pytest.raises(Exception) as e:
        Event.create_object(session, **event_fixture)
    assert (
        "Le client n'existe pas"
        in str(e.value)
    )


def test_update_event(
        mocker,
        session,
        make_event
):
    initial_event = Event(**make_event())
    event_id = 1
    update_data = {
        "location": "update_location",
        "attendees": 15,
    }
    mock_get_event = mocker.patch.object(
        Event, 'get_object', return_value=initial_event
    )
    mock_session_commit = mocker.patch.object(session, "commit")

    result = Event.update_object(session, event_id, **update_data)

    assert result.location == update_data["location"]
    assert result.attendees == update_data["attendees"]
    assert mock_get_event.call_count == 1
    mock_session_commit.assert_called_once()


def test_update_event_raise_error_with_no_event(
        mocker,
        session,
):
    event_id = 1
    update_data = {
        "location": "update_location",
        "attendees": 15,
    }
    mocker.patch(
        "models.event.Event.get_object",
        return_value=None
    )
    with pytest.raises(Exception, match="L'événement n'existe pas"):
        Event.update_object(session, event_id, **update_data)


def test_update_event_raise_error_with_wrong_start_date(
        mocker,
        session,
        make_event
):
    initial_event = Event(**make_event())
    event_id = 1
    update_data = make_event(start_date=datetime.now())

    mocker.patch(
        "models.event.Event.get_object",
        return_value=initial_event
    )
    with pytest.raises(
            Exception, match="La date de début doit être dans le futur"
    ):
        Event.update_object(session, event_id, **update_data)


def test_update_event_raise_error_with_wrong_end_date(
        mocker,
        session,
        make_event
):
    initial_event = Event(**make_event())
    event_id = 1
    update_data = make_event(end_date=datetime.now())

    mocker.patch(
        "models.event.Event.get_object",
        return_value=initial_event
    )
    with pytest.raises(
        Exception,
        match="La date de fin doit être supérieure à la date de début"
    ):
        Event.update_object(session, event_id, **update_data)


def test_update_event_raise_error_with_no_attendees(
        mocker,
        session,
        make_event
):
    initial_event = Event(**make_event())
    event_id = 1
    update_data = make_event(attendees=0)

    mocker.patch(
        "models.event.Event.get_object",
        return_value=initial_event
    )
    with pytest.raises(
        Exception,
        match="Le nombre de participants doit être positif"
    ):
        Event.update_object(session, event_id, **update_data)


def test_update_event_raise_error_wrong_commercial_id(
        mocker,
        session,
        make_event,
        make_user
):
    # Créer un event avec des dates valides
    event_data = make_event()
    initial_event = Event(**event_data)

    # Mock des objets et méthodes
    mock_user = mocker.MagicMock()
    mock_user.role = "COMMERCIAL"

    mocker.patch.object(Contract, 'get_object', return_value=mock_user)
    mocker.patch.object(Contract, '_save_object', return_value=mock_user)
    mocker.patch.object(Event, 'get_object', return_value=initial_event)
    # Mock _save_object pour éviter l'interaction avec la DB
    mocker.patch.object(Event, '_save_object', return_value=initial_event)

    event_id = 1
    update_data = {
        "location": "update_location",
        "support_contact_id": 1
    }

    # Exécuter la mise à jour
    with pytest.raises(
        Exception,
        match="Contact support invalide"
    ):
        Event.update_object(session, event_id, **update_data)


def test_delete_event(
        mocker,
        session,
        make_event
):
    # Prépare le mock pour session
    event_fixture = make_event()
    expected_event = Event(**event_fixture)
    event_id = 1

    # Crée l'utilisateur avec les données fournies
    mock_get_event = mocker.patch.object(
        Event, 'get_object', return_value=expected_event
    )
    mock_session_delete = mocker.patch.object(session, "delete")
    mock_session_commit = mocker.patch.object(session, "commit")
    # Supprime l'utilisateur
    result = Event.delete_object(session, event_id)
    # Vérifie que l'utilisateur a été supprimé
    assert result.contract_id == expected_event.contract_id
    assert result.support_contact_id == expected_event.support_contact_id
    mock_get_event.assert_called_once_with(session, id=event_id)
    mock_session_delete.assert_called_once_with(expected_event)
    mock_session_commit.assert_called_once()


def test_delete_event_raise_error_with_wrong_event_id(
        mocker,
        session
):
    event_id = 999
    mocker.patch.object(Event, 'get_object', return_value="")
    with pytest.raises(Exception) as e:
        Event.delete_object(session, event_id)
    assert "L'événement n'existe pas" in str(e.value)


def test_delete_event_raise_exception_error(
        mocker,
        session,
        make_event
):
    event_id = 999
    mocker.patch.object(
        Event, 'get_object', return_value=make_event)
    with pytest.raises(Exception) as e:
        Event.delete_object(session, event_id)
    assert "Erreur lors de la suppression de l'événement" in str(e.value)
