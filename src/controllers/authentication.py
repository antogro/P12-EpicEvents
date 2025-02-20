import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.authentication import Token
from view.display_view import Display


engine = create_engine('sqlite:///./epic_event.db')
Session = sessionmaker(bind=engine)
display = Display()

auth_app = typer.Typer(name='Epic Events authentication Management',
                       help=['Application de Gestion '
                             'de l\'authentification Epic Event']
                       )


def get_session():
    """Récupère une session de la base de données"""
    return Session()


@auth_app.command(name="login")
def login(
    username: str = typer.Option(
        ..., prompt=True, help="Username"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password",
    ),
):
    """Login to the application"""
    try:
        session = get_session()
        token = Token.login(session, username, password=password)
        if token:
            print(token)

    except Exception as e:
        print(f"Error: {e}")@auth_app.command(name="login")


@auth_app.command(name="verify-token")
def verify_token(
):
    """Login to the application"""
    try:
        token = Token.verify_token(Token.get_stored_token())
        if token:
            print(token)

    except Exception as e:
        print(f"Error: {e}")


@auth_app.command(name="logout")
def logout():
    """Login to the application"""
    try:
        Token.logout()
    except Exception as e:
        print(f"Error: {e}")