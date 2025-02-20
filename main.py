from src.controllers.client import client_app
from src.controllers.user import user_app
from src.controllers.contract import contract_app
from sqlalchemy import create_engine
from src.controllers.event import event_app
from src.controllers.authentication import auth_app
from sqlalchemy.orm import sessionmaker
import typer


app = typer.Typer()

Session = sessionmaker(bind=create_engine("sqlite:///epic_event.db"))


@app.callback()
def main(ctx: typer.Context):
    """Initialise le contexte global pour l'application"""
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj["session"] = Session()


app.add_typer(user_app, name='user')
app.add_typer(client_app, name='client')
app.add_typer(contract_app, name='contract')
app.add_typer(event_app, name='event')
app.add_typer(auth_app, name='auth')


if __name__ == '__main__':
    app()
