from src.controllers.client import client_app
from src.controllers.user import user_app
from src.controllers.contract import contract_app
from src.controllers.event import event_app

import typer


app = typer.Typer()

app.add_typer(user_app, name='user')
app.add_typer(client_app, name='client')
app.add_typer(contract_app, name='contract')
app.add_typer(event_app, name='event')


if __name__ == '__main__':
    app()
