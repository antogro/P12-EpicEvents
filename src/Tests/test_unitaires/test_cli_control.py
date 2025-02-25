from typer.testing import CliRunner
from src.controllers.authentication import auth_app
from src.controllers.user import user_app
from src.controllers.client import client_app
from src.controllers.contract import contract_app
from src.controllers.event import event_app


runner = CliRunner()


def test_login(mocker):
    """Test de la connexion d'un utilisateur"""
    mocker.patch(
        "src.models.authentication.Token.login",
        return_value={"success": True, "token": "fake-token"},
    )

    result = runner.invoke(
        auth_app, ["login"], input="testuser\ntestpassword\n")
    assert result.exit_code == 0
    assert "testuser connecté avec succ" in result.output


def test_verify_token(mocker):
    """Test de la vérification du token"""
    mocker.patch(
        "models.authentication.Token.get_stored_token",
        return_value="fake-token"
    )
    mocker.patch(
        "models.authentication.Token.verify_token",
        return_value={"sub": "3_commercial"}
    )

    result = runner.invoke(auth_app, ["verify-token"])
    assert result.exit_code == 0
    assert (
        "Token '3_commercial' valide" in result.output
    )


def test_logout(mocker):
    """Test de la déconnexion"""
    mocker.patch(
        "models.authentication.Token.logout",
        return_value={"success": True, "message": "Déconnexion réussie"},
    )

    result = runner.invoke(auth_app, ["logout"])
    assert result.exit_code == 0
    assert "Déconnexion réussie" in result.output


def test_create_user(mocker, mock_session):
    """Test de la création d'un utilisateur"""

    mocker.patch("src.controllers.user.get_session", return_value=mock_session)
    mocker.patch("src.models.user.User.create_object", return_value=True)

    mock_session.add.return_value = None
    mock_session.commit.return_value = None

    result = runner.invoke(
        user_app,
        ["create"],
        input="testuser\ntest@example.com\ntestpassword\nCOMMERCIAL\n",
    )

    print("output :", result.output)

    assert result.exit_code == 0
    assert "✅ Utilisateur 'testuser' créé avec succès" in result.output


def test_delete_user(mocker):
    """Test de la suppression d'un utilisateur"""
    mocker.patch("models.user.User.delete_object", return_value=True)

    result = runner.invoke(user_app, ["delete", "--user-id", "1"])
    print(result.output)
    assert result.exit_code == 0
    assert "Utilisateur 1 supprimé avec succès" in result.output


def test_create_client(mocker):
    """Test de la création d'un client"""
    mocker.patch("src.models.client.Client.create_object", return_value=True)

    result = runner.invoke(
        client_app,
        ["create"],
        input="John\nDoe\njohn@example.com\n0123456789\nJD Corp\n1\n",
    )
    print(result.output)
    assert result.exit_code == 0
    assert "Client 'John Doe' créé avec succès" in result.output


def test_delete_client(mocker):
    """Test de la suppression d'un client"""
    mocker.patch("src.models.client.Client.delete_object", return_value=True)

    result = runner.invoke(client_app, ["delete", "--id", "1"])
    print(result.output)
    assert result.exit_code == 0
    assert "Client 1 supprimé avec succès" in result.output


def test_create_contract(mocker):
    """Test de la création d'un contrat"""
    mocker.patch(
        "src.models.contract.Contract.create_object", return_value=True)

    result = runner.invoke(
        contract_app, ["create"], input="1\n1\n1000.0\n500.0\n")
    assert result.exit_code == 0
    assert "Contrat n°'1' créé avec succès" in result.output


def test_sign_contract(mocker):
    """Test de la signature d'un contrat"""
    mocker.patch("src.models.contract.Contract.sign_object", return_value=True)

    result = runner.invoke(contract_app, ["sign", "--id", "1"])
    assert result.exit_code == 0
    assert "Contrat n°'1' signé avec succès" in result.output


def test_delete_contract(mocker):
    """Test de la suppression d'un contrat"""
    mocker.patch(
        "src.models.contract.Contract.delete_object", return_value=True)

    result = runner.invoke(contract_app, ["delete", "--id", "1"])
    assert result.exit_code == 0
    assert "Utilisateur 1 supprimé avec succès" in result.output


def test_create_event(mocker):
    """Test de la création d'un événement"""
    mocker.patch(
        "src.models.event.Event.create_object", return_value=True)

    result = runner.invoke(
        event_app,
        ["create"],
        input="Événement test\n1\n1\n2025-01-01\n2025-01-02\nParis\n100\nDescription\n",
    )
    assert result.exit_code == 0
    assert "Evenement du contrat n°'1' créé avec succès" in result.output


def test_delete_event(mocker):
    """Test de la suppression d'un événement"""
    mocker.patch("src.models.event.Event.delete_object", return_value=True)

    result = runner.invoke(event_app, ["delete", "--id", "1"])
    assert result.exit_code == 0
    assert "L'évènement n°1 a été supprimé" in result.output
