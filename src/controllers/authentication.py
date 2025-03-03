import typer
from models.authentication import Token
from view.display_view import Display
from models.common import get_session

display = Display()

auth_app = typer.Typer(name='Epic Events authentication Management',
                       help=['Application de Gestion '
                             'de l\'authentification Epic Event']
                       )


@auth_app.command(name="login")
def login(
        username: str = typer.Option(
            ..., prompt=True, help="Username"),
        password: str = typer.Option(
            ..., prompt=True, hide_input=True, help="Password"),
):
    """Connexion à l'application"""
    try:
        session = get_session()
        token = Token.login(session, username, password=password)
        if token['success'] is True:
            typer.secho(
                f"✅ {username} connecté avec succès", fg=typer.colors.GREEN)
        else:
            typer.secho("❌ Identifiants invalides", fg=typer.colors.RED)
            raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"{str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@auth_app.command(name="verify-token")
def verify_token():
    """Vérifie le token de l'utilisateur"""
    try:
        result = Token.verify_token(Token.get_stored_token())

        if result and result is not False:
            payload, token_data = result
            typer.secho(
                f"✅ Token '{payload['sub']}' valide !", fg=typer.colors.GREEN)
            typer.secho(f"📆 Émis le : {token_data['Émis le']}")
            typer.secho(f"⏳ Expire le : {token_data['Expire le']}")

    except Exception as e:
        typer.secho(f"❌ Erreur: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@auth_app.command(name="logout")
def logout():
    """Login to the application"""
    try:
        Token.logout()
        typer.secho("✅ Déconnexion réussie", fg=typer.colors.GREEN)
    except Exception as e:
        print(f"Error: {e}")
