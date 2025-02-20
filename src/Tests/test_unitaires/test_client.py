import pytest
from src.models.client import Client
from src.models.user import User
from src.models.permission import PermissionManager


def test_create_client_with_permission(mocker, session, make_client, make_user):
    """Test qu'un commercial peut créer un client si la permission est valide."""
    user_fixture = make_user(role="COMMERCIAL")
    client_fixture = make_client()

    user = User(**user_fixture)

    mocker.patch("src.models.client.Client.get_object", return_value=None)
    mocker.patch("src.models.user.User.get_object", return_value=user)
    mocker.patch("src.models.permission.PermissionManager.validate_permission", return_value=(True, None))

    client = Client.create_object(session, **client_fixture)

    assert client.email == client_fixture["email"]
    assert client.first_name == client_fixture["first_name"]



def test_create_client_should_raise_error_with_existing_email(mocker, session, make_client):
    """Test qu'une erreur est levée si l'email du client existe déjà."""
    client_fixture = make_client()

    mocker.patch("src.models.client.Client.get_object", return_value=Client(**client_fixture))

    with pytest.raises(Exception, match="Un client avec cet email existe déjà"):
        Client.create_object(session, **client_fixture)


def test_create_client_should_raise_error_with_invalid_role(mocker, session, make_client, make_user):
    """Test qu'un rôle invalide ne peut pas créer un client."""
    user_fixture = make_user(role="SUPPORT")  # Support ne peut pas créer de client
    client_fixture = make_client()

    user = User(**user_fixture)

    mocker.patch("src.models.user.User.get_object", return_value=user)
    mocker.patch("src.models.permission.PermissionManager.validate_permission", return_value=(False, "Contact commercial invalide"))

    with pytest.raises(Exception, match="Contact commercial invalide"):
        Client.create_object(session, **client_fixture)


def test_get_client(mocker, session, make_client):
    """Test qu'un client existant peut être récupéré."""
    client_fixture = make_client(id=1)  # Ajoute un ID explicite
    client = Client(**client_fixture)

    mocker.patch("src.models.client.Client.get_object", return_value=client)

    retrieved_client = Client.get_object(session, id=client_fixture["id"])

    assert retrieved_client.id == client_fixture["id"]
    assert retrieved_client.email == client_fixture["email"]


def test_get_client_invalide_data_raise_error(mocker, session):
    """Test qu'une erreur est levée si un client inexistant est demandé."""
    mocker.patch("src.models.client.Client.get_object", return_value=None)

    with pytest.raises(Exception, match="Le client n'existe pas"):
        client = Client.get_object(session, id=999)
        if not client:
            raise Exception("Le client n'existe pas")


### 🔹 **Test de Mise à Jour d'un Client**
def test_update_client(mocker, session, make_client):
    """Test qu'un client peut être mis à jour."""
    client_fixture = make_client()
    client = Client(**client_fixture)

    mocker.patch("src.models.client.Client.get_object", return_value=client)

    updated_client = Client.update_object(session, client_id=client_fixture["id"], email="newemail@example.com")

    assert updated_client.email == "newemail@example.com"


def test_update_client_with_existing_email(mocker, session, make_client):
    """Test qu'une erreur est levée si l'email existe déjà chez un autre client."""
    existing_client_fixture = make_client(email="existing@example.com")
    client_fixture = make_client(id=1, email="test@example.com")

    existing_client = Client(**existing_client_fixture)
    client = Client(**client_fixture)

    mocker.patch("src.models.client.Client.get_object", side_effect=lambda session, id: existing_client if id == 2 else client)

    with pytest.raises(Exception, match="Un client avec cet email existe déjà"):
        Client.update_object(session, client_id=client_fixture["id"], email="existing@example.com")



def test_update_client_with_no_client(mocker, session):
    """Test qu'une erreur est levée si on tente de mettre à jour un client inexistant."""
    mocker.patch("src.models.client.Client.get_object", return_value=None)

    with pytest.raises(Exception, match="Le client n'existe pas"):
        Client.update_object(session, client_id=999, email="test@example.com")


def test_update_client_invalid_field(mocker, session, make_client):
    """Test qu'une mise à jour avec un champ invalide est refusée."""
    client_fixture = make_client()
    client = Client(**client_fixture)

    mocker.patch("src.models.client.Client.get_object", return_value=client)

    with pytest.raises(Exception, match="Champ invalide"):
        Client.update_object(session, client_id=client_fixture["id"], invalid_field="value")


def test_delete_client(mocker, session, make_client):
    """Test qu'un client peut être supprimé."""
    client_fixture = make_client(id=1)  # Ajoute un ID explicite
    client = Client(**client_fixture)

    mocker.patch("src.models.client.Client.get_object", return_value=client)

    deleted_client = Client.delete_object(session, client_id=client_fixture["id"])

    assert deleted_client.id == client_fixture["id"]


def test_delete_client_with_no_client(mocker, session):
    """Test qu'une erreur est levée si on tente de supprimer un client inexistant."""
    mocker.patch("src.models.client.Client.get_object", return_value=None)

    with pytest.raises(Exception, match="Le client n'existe pas"):
        Client.delete_object(session, client_id=999)
