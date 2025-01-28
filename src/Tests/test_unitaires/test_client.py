from src.models.client import Client
from src.models.user import User
import pytest


def test_create_client(mocker, session, make_client, make_user):
    user_fixture = make_user(role="COMMERCIAL")
    client_fixture = make_client()

    user = User(**user_fixture)
    mocker.patch(
        "models.validators.ClientValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )
    mocker.patch("models.client.Client.get_object", return_value=None)
    mocker.patch("models.client.User.get_object", return_value=user)

    client = Client.create_object(session, **client_fixture)

    assert client.email == client_fixture["email"]
    assert client.first_name == client_fixture["first_name"]
    assert client.last_name == client_fixture["last_name"]
    assert client.commercial_id == client_fixture["commercial_id"]


def test_create_client_should_raise_error_with_invalide_role(
        mocker,
        session,
        make_user,
        make_client
):
    user_fixture = make_user(role='SUPPORT')
    client_fixture = make_client()
    user = User(**user_fixture)

    mocker.patch(
        "models.validators.ClientValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )

    mocker.patch("src.models.client.Client.get_object", return_value=None)
    mocker.patch("src.models.user.User.get_object", return_value=user)

    # Vérifie que l'exception levée concerne un rôle commercial invalide
    with pytest.raises(Exception) as e:
        Client.create_object(session, **client_fixture)

    # Assertion : le message doit correspondre à l'erreur de rôle invalide
    assert "Contact commercial invalide" in str(e.value)


def test_create_client_should_raise_error_with_invalide_required_field(
        mocker,
        session,
        make_user
):
    user_fixture = make_user(role="COMMERCIAL")

    user = User(**user_fixture)
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )
    mocker.patch("src.models.client.Client.get_object", return_value=None)
    mocker.patch("src.models.client.User.get_object", return_value=user)
    incomplete_data = {
        "first_name": "full_name",
        "last_name": "full_name",
        "email": "email@email.fr",
        "phone": "0101010101",
        "commercial_id": 1,
    }

    with pytest.raises(Exception) as e:
        Client.create_object(session, **incomplete_data)
    assert ("Le champ company_name est requis"
            in str(e.value))


def test_create_client_should_raise_error_with_invalide_email(
        make_client,
        mocker,
        session,
):
    mocker.patch(
        "models.validators.ClientValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch("src.models.client.Client.get_object", return_value=None)
    client_fixture = make_client(email='email.email.fr')

    with pytest.raises(Exception) as e:
        Client.create_object(session, **client_fixture)
    assert ("L'email doit être valide"
            in str(e.value))


def test_creat_client_existing_email(mocker, session, make_client):
    client_fixture = make_client()
    mocker.patch(
        "models.validators.ClientValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )
    mocker.patch(
        "src.models.client.Client.get_object", return_value=client_fixture)
    with pytest.raises(Exception) as e:
        Client.create_object(session, **client_fixture)
    assert "Un client avec cet email existe déjà" in str(e.value)


def test_get_client(mocker, session, make_client):
    client_fixture = make_client()
    expected_client = Client(**client_fixture)

    # Prépare le mock pour session.query().filter_by().first()
    mock_query = mocker.Mock()
    mock_filter = mocker.Mock()
    mock_filter.first.return_value = expected_client

    session.query = mocker.Mock(return_value=mock_query)
    mock_query.filter_by = mocker.Mock(return_value=mock_filter)

    # Exécution
    result = Client.get_object(session, email=client_fixture["email"])

    # Vérification
    assert result == expected_client
    session.query.assert_called_once_with(Client)
    mock_query.filter_by.assert_called_once_with(email=client_fixture["email"])
    mock_filter.first.assert_called_once()


def test_get_client_invalide_data_raise_error(
        mocker,
        session,
        make_client
):
    client_fixture = make_client()
    expected_client = Client(**client_fixture)

    # Prépare le mock pour session.query().filter_by().first()
    mock_query = mocker.Mock()
    mock_filter = mocker.Mock()
    mock_filter.first.return_value = expected_client

    session.query = mocker.Mock(return_value=mock_query)
    mock_query.filter_by = mocker.Mock(return_value=mock_filter)

    # Exécution
    mock_query.filter_by = mocker.Mock(return_value=mock_filter)
    with pytest.raises(Exception, match='Erreur lors de la récupération:'):
        Client.get_object(session, emil="invalid_data")


def test_delete_client(
        mocker,
        session,
        make_client
):
    # Prépare le mock pour session
    client_fixture = make_client()
    expected_client = Client(**client_fixture)
    client_id = 1

    # Crée l'utilisateur avec les données fournies
    mock_get_client = mocker.patch(
        "src.models.client.Client.get_object", return_value=expected_client
    )
    mock_session_delete = mocker.patch.object(session, "delete")
    mock_session_commit = mocker.patch.object(session, "commit")
    # Supprime l'utilisateur
    result = Client.delete_object(session, client_id)
    # Vérifie que l'utilisateur a été supprimé
    assert result.email == expected_client.email
    assert result.first_name == expected_client.first_name
    mock_get_client.assert_called_once_with(session, id=client_id)
    mock_session_delete.assert_called_once_with(expected_client)
    mock_session_commit.assert_called_once()


def test_delete_client_raise_error_with_wrong_client(
        mocker,
        session
):
    client_id = 999
    mocker.patch("src.models.client.Client.get_object", return_value="")
    with pytest.raises(Exception) as e:
        Client.delete_object(session, client_id)
    assert ("Une erreur lors de la suppression "
            "du client: Le client n'existe pas" in str(e.value))


def test_delete_client_raise_exception_error(
        mocker,
        session,
        make_client
):
    client_id = 999
    mocker.patch(
        "src.models.client.Client.get_object", return_value=make_client()
    )
    with pytest.raises(Exception) as e:
        Client.delete_object(session, client_id)
    assert "Une erreur lors de la suppression du client: " in str(e.value)


def test_update_client(
        mocker,
        session,
        make_client
):
    client_fixture = make_client()
    initial_client = Client(**client_fixture)
    client_id = 1
    update_data = {
        "email": "test2@example.com",
        "first_name": "update_client_name"
    }
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )
    mock_get_client = mocker.patch(
        "src.models.client.Client.get_object",
        side_effect=[initial_client, None]
    )
    mock_session_commit = mocker.patch.object(session, "commit")

    result = Client.update_object(session, client_id, **update_data)

    assert result.first_name == update_data["first_name"]
    assert mock_get_client.call_count == 2
    mock_session_commit.assert_called_once()


def test_update_client_with_no_client(
        mocker,
        session,
):
    client_id = 1
    update_data = {
        "email": "test2@example.com",
        "first_name": "update_client_name"}
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )
    mocker.patch(
        "src.models.client.Client.get_object",
        return_value=None
    )
    with pytest.raises(Exception, match="Le client n'existe pas"):
        Client.update_object(session, client_id, **update_data)


def test_update_client_with_existing_email(
        mocker,
        session,
        make_client
):
    initial_client = Client(**make_client())
    existing_client = Client(**make_client(email='existing@email.fr'))
    client_id = 1
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )
    mock_get_client = mocker.patch(
        "src.models.client.Client.get_object",
        side_effect=[initial_client, existing_client]
    )
    mock_session_rollback = mocker.patch.object(session, 'rollback')
    with pytest.raises(
        Exception,
        match=("Une erreur lors de la mise à jour du "
               "client: Un client avec cet email existe déjà")
    ):
        Client.update_object(session, client_id, email='existing@email.fr')

        mock_session_rollback.assert_called_once()
        assert mock_get_client.call_count == 2


def test_update_client_invalid_field(
        mocker,
        session,
        make_client
):
    """Test la mise à jour avec un champ invalide"""
    initial_client = Client(**make_client())
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )
    mocker.patch(
        'src.models.client.Client.get_object', return_value=initial_client)
    mock_session_rollback = mocker.patch.object(session, 'rollback')

    with pytest.raises(
        Exception,
        match="Une erreur lors de la mise à jour du client"
    ):
        result = Client.update_object(session, 1, eail="email.@email.fr")

        mock_session_rollback.assert_called_once()
        assert result == initial_client


def test_update_client_invalid_role(
        mocker,
        session,
        make_client,
        make_user
):
    user_fixture = make_user(role='SUPPORT')
    update_data = {"email": "test2@example.com", "commercial_id": 1}
    user = User(**user_fixture)

    mocker.patch(
        "models.validators.ClientValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.ClientValidator.validate_email",
        return_value=None
    )

    mocker.patch(
        "src.models.client.Client.get_object", return_value=make_client())
    mocker.patch("src.models.user.User.get_object", return_value=user)
    mock_session_rollback = mocker.patch.object(session, 'rollback')

    with pytest.raises(
        Exception,
        match="Une erreur lors de la mise à jour du client"
    ):
        result = Client.update_object(session, 1, **update_data)

        mock_session_rollback.assert_called_once()
        assert result == make_client()
