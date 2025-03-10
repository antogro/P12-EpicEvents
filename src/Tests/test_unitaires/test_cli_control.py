from typer.testing import CliRunner
from src.controllers.authentication import auth_app
from src.controllers.user import user_app
from src.controllers.client import client_app
from src.controllers.contract import contract_app
from src.controllers.event import event_app
from src.models.user import User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event


runner = CliRunner()


def test_login(mocker):
    """Test de la connexion d'un utilisateur"""
    mocker.patch(
        "src.models.authentication.Token.login",
        return_value={"success": True, "token": "fake-token"},
    )

    result = runner.invoke(
        auth_app, ["login"], input="testuser\ntestpassword\n")
    print('result: ', result)
    assert result.exit_code == 0
    assert "testuser connecté avec succ" in result.output


def test_verify_token(mocker):
    """Test de la vérification d'un token"""
    mocker.patch(
        "src.models.authentication.Token.get_stored_token",
        return_value="fake-token"
    )
    mocker.patch(
        "src.models.authentication.Token.verify_token",
        return_value=(
            {"sub": "3_commercial"},  # payload
            {
                "Utilisateur": "3_commercial",
                "Émis le": "2025-01-01 00:00:00 UTC",
                "Expire le": "2025-01-02 00:00:00 UTC",
            },
        ),
    )

    result = runner.invoke(auth_app, ["verify-token"], obj={})
    assert result.exit_code == 0
    assert "Token '3_commercial' valide" in result.output


def test_logout(mocker):
    """Test de la déconnexion"""
    mocker.patch(
        "src.models.authentication.Token.logout",
        return_value={"success": True, "message": "Déconnexion réussie"},
    )

    result = runner.invoke(auth_app, ["logout"])
    assert result.exit_code == 0
    assert "Déconnexion réussie" in result.output


def test_create_user(mocker, session, ctx_with_session, make_user):
    mocker.patch("src.controllers.user.get_session", return_value=session)

    mock_user = User(**make_user())

    mocker.patch("src.models.user.User.create_object", return_value=mock_user)

    mocker.patch(
        "src.models.user_session.UserSession.get_current_user",
        return_value=User(**make_user(role="GESTION", id=1)),
    )

    result = runner.invoke(
        user_app,
        ["create"],
        obj=ctx_with_session,
        input="testuser\ntest@example.com\ntestpassword\nCOMMERCIAL\n",
    )

    print('result.output: ', result.output)
    assert result.exit_code == 0
    assert "✅ Utilisateur 'testuser' créé avec succès" in result.output


def test_delete_user(mocker, session, ctx_with_session, make_user):
    """Test de la suppression d'un utilisateur"""
    # Make sure the real DB delete is never called
    mocker.patch("src.models.user.User.delete_object", return_value=True)

    mocker.patch(
        "src.models.user_session.UserSession.get_current_user",
        return_value=User(**make_user(role="GESTION", id=1)),
    )

    result = runner.invoke(
        user_app,
        ["delete", "--id", "2"],
        obj=ctx_with_session,
        input="y",  # confirm the deletion
    )
    print('result.output: ', result.output)

    assert result.exit_code == 0
    assert "Utilisateur 2 supprimé avec succès" in result.output


def test_create_client(mocker, session, make_user, make_client):
    """Test de la création d'un client"""
    mocker.patch(
        "src.models.user_session.UserSession.get_current_user",
        return_value=User(**make_user(role="COMMERCIAL", id=1)),
    )
    mocker.patch(
        "src.models.client.Client.create_object",
        return_value=Client(**make_client(commercial_id=1)),
    )

    result = runner.invoke(
        client_app,
        ["create"],
        obj={"session": session},
        input="John\nDoe\njohn@example.com\n0101010101\nJD Corp\n1\n",
    )
    print('result.output: ', result.output)

    assert result.exit_code == 0
    assert "Client 'John Doe' créé avec succès" in result.output


def test_delete_client(
        mocker, session, ctx_with_session, make_client, make_user):
    """Test de la suppression d'un client"""
    mocker.patch(
        "src.models.client.Client.get_object",
        return_value=Client(**make_client(commercial_id=1))
    )
    mocker.patch("src.models.client.Client.delete_object", return_value=True)

    mocker.patch(
        "src.models.user_session.UserSession.get_current_user",
        return_value=User(**make_user(role="COMMERCIAL", id=1)))

    result = runner.invoke(
        client_app, ["delete", "--id", "1"],
        obj={"session": session}, input="y"
    )

    assert result.exit_code == 0
    assert "Client 1 supprimé avec succès" in result.output


def test_create_contract(mocker, session, make_user):
    """Test de la création d'un contrat"""

    mocker.patch("src.controllers.contract.get_session", return_value=session)
    mocker.patch(
        "src.models.user_session.UserSession.get_current_user",
        return_value=User(**make_user(role="GESTION", id=2)),
    )
    mocker.patch(
        "src.models.user.User.get_object",
        return_value=User(**make_user(role="COMMERCIAL", id=1)),
    )
    mocker.patch(
        "src.models.contract.Contract.create_object",
        return_value=Contract(
            id=1,
            client_id=1,
            commercial_id=1,
            total_amount=1000.0,
            remaining_amount=500.0,
            is_signed=False,
        ),
    )

    result = runner.invoke(
        contract_app,
        ["create"],
        obj={"session": session},
        input="1\n1\n1500.0\n500.0\n",
    )
    print('result.output: ', result.output)

    assert result.exit_code == 0
    assert "✅ Contrat n°1 créé avec succès !" in result.output


def test_sign_contract(mocker, session, make_user):
    """Test de la signature d'un contrat avec confirmation 'y'."""
    mocker.patch("src.controllers.contract.get_session", return_value=session)
    mocker.patch(
        "src.models.user_session.UserSession.get_current_user",
        return_value=User(**make_user(role="GESTION", id=2)),
    )
    mocker.patch(
        "src.models.user.User.get_object",
        return_value=User(**make_user(role="COMMERCIAL", id=1)),
    )

    mocker.patch("src.models.contract.Contract.sign_object", return_value=True)

    result = runner.invoke(
        contract_app, ["sign", "--id", "1"],
        obj={"session": session}, input="y"
    )

    assert result.exit_code == 0
    assert "Contrat n°1 signé avec succès" in result.output


def test_delete_contract(mocker, session, make_user):
    """Test de la suppression d'un contrat avec confirmation 'y'."""

    mocker.patch("src.models.user_session.UserSession.get_current_user",
                 return_value=User(**make_user(role="GESTION", id=2)))

    mock_contract = Contract(
        id=1, client_id=1, commercial_id=2,
        total_amount=1500.0, remaining_amount=500.0, is_signed=True)

    mocker.patch("src.models.contract.Contract.get_object",
                 return_value=mock_contract)

    mocker.patch(
        "src.models.contract.Contract.delete_object", return_value=True)

    result = runner.invoke(contract_app, ["delete", "--id", "1"],
                           obj={"session": session}, input="y")

    assert result.exit_code == 0
    assert "✅ Contrat 1 supprimé avec succès" in result.output


def test_create_event(mocker, session, make_user, make_event):
    """Test de la création d'un événement avec confirmation 'n'."""
    mocker.patch(
        "src.models.user_session.UserSession.get_current_user",
        return_value=User(**make_user(role="COMMERCIAL", id=2)),
    )

    mocker.patch(
        "src.models.client.Client.get_object",
        return_value=Client(id=1, commercial_id=2)
    )
    mocker.patch(
        "src.models.contract.Contract.get_object",
        return_value=Contract(
            id=1, client_id=1, commercial_id=2, is_signed=True),
    )
    mocker.patch(
        "src.models.event.Event.create_object",
        return_value=Event(**make_event()))

    result = runner.invoke(
        event_app,
        [
            "create",
            "--client-id",
            "1",
            "--contract-id",
            "1",
            "--name",
            "Conférence annuelle",
            "--start-date",
            "2027-09-15_09:00:00",
            "--end-date",
            "2027-09-15_12:00:00",
            "--location",
            "Paris",
            "--attendees",
            "50",
            "--notes",
            "Événement VIP",
        ],
        obj={"session": session},
        input="n",
    )
    print("result: ", result.output)

    assert result.exit_code == 0
    assert "✅ Événement du contrat n°1 créé avec succès!" in result.output
