import pytest
from models.client import Client
from models.user import User


def test_create_client(mocker, session, make_client, make_user):
    """Test qu'un commercial peut créer un client."""
    user_fixture = make_user(role="COMMERCIAL")
    user = User(**user_fixture)

    session.add(user)
    session.commit()

    client_fixture = make_client(commercial_id=user.id)

    mocker.patch("models.client.Client.get_object", return_value=None)
    mocker.patch("models.user.User.get_object", return_value=user)
    mocker.patch(
        "models.permission.PermissionManager.validate_permission",
        return_value=(True, None),
    )

    client = Client.create_object(session, **client_fixture)

    assert client.email == client_fixture["email"]
    assert client.first_name == client_fixture["first_name"]


def test_create_client_should_raise_error(mocker, session, make_client):
    """Test qu'on ne peut pas créer un client si
    l'email existe déjà ou si le rôle est invalide."""
    client_fixture = make_client()

    mocker.patch(
        "models.client.Client.get_object",
        return_value=Client(**client_fixture)
    )

    with pytest.raises(
        Exception,
        match="Un client avec cet email existe déjà|Email déjà utilisé"
    ):
        Client.create_object(session, **client_fixture)


def test_get_client(mocker, session, make_client):
    """
    Test que la récupération d'un client fonctionne.
    """
    expected_contract = Client(**make_client(id=1))

    mocker.patch.object(
        Client, "get_object", return_value=Client(**make_client(id=1)))

    retrieved_client = Client.get_object(session, id=1)

    assert retrieved_client.first_name == expected_contract.first_name
    assert retrieved_client.last_name == expected_contract.last_name
    assert retrieved_client.email == expected_contract.email


def test_update_user_with_permission(mocker, session, make_client):
    """Test qu'un utilisateur avec la permission
    peut mettre à jour un utilisateur existant.
    """
    client_fixture = make_client(id=2, email="emailtest3@email.f")
    mocker.patch(
        "models.permission.PermissionManager.validate_permission",
        return_value=(True, None),
    )
    client = Client(**client_fixture)
    mocker.patch("models.client.Client.get_object", return_value=client)

    updated_client = client.update_object(
        session, client_id=client_fixture["id"], first_name="Newclientname"
    )

    assert updated_client.first_name == "Newclientname"

    with pytest.raises(
            Exception, match="Un client avec cet email existe déjà"):
        Client.update_object(
            session, client_id=client.id, email="existing@example.com")

    mocker.patch("models.client.Client.get_object", return_value=None)
    with pytest.raises(Exception, match="Le client n'existe pas"):
        Client.update_object(
            session, client_id=999, email="test25@example.com")


def test_delete_client_with_permission(mocker, session, make_client):
    """Test qu'un utilisateur avec la permission
    peut supprimer un utilisateur."""
    client_fixture = make_client(id=4, email="emailtest2@email.f")

    client = Client(**client_fixture)
    session.add(client)
    session.commit()
    mocker.patch("models.client.Client.get_object", return_value=client)

    deleted_client = client.delete_object(
        session, client_id=client_fixture["id"])

    assert deleted_client.id == client_fixture["id"]
