from src.controllers.client import client_app
from src.controllers.user import user_app
from src.controllers.contract import contract_app
from sqlalchemy import create_engine
from src.controllers.event import event_app
from src.controllers.authentication import auth_app
from src.models.authentication import Token
from sqlalchemy.orm import sessionmaker
import typer


app = typer.Typer()

Session = sessionmaker(bind=create_engine("sqlite:///epic_event.db"))


@app.callback()
def main(ctx: typer.Context):
    """Initialise le contexte global pour l'application"""
    if ctx.obj is None:
        ctx.obj = {}  # On initialise un dictionnaire vide si ctx.obj est None
    ctx.obj["session"] = Session()  # Stocke la session SQLAlchemy


app.add_typer(user_app, name='user', callback=Token.get_auth)
app.add_typer(client_app, name='client', callback=Token.get_auth)
app.add_typer(contract_app, name='contract', callback=Token.get_auth)
app.add_typer(event_app, name='event', callback=Token.get_auth)
app.add_typer(auth_app, name='auth', callback=Token.get_auth)


if __name__ == '__main__':
    app()
