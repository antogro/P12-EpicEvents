import typer
from sqlalchemy import create_engine
from typing import Optional
from sqlalchemy.orm import sessionmaker
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)

from models.client import Client
from models.user import User
from view.display_view import Display

engine = create_engine('sqlite:///./epic_events.db')
Session = sessionmaker(bind=engine)
display = Display()

client_app = typer.Typer(name='Epic Events client Management',
                         help='Application de Gestion des clients Epic Event')


def get_session():
    """Récupère une session de la base de données"""
    return Session()


@client_app.command(name="create")
def create_client(
    first_name: str = typer.Option(..., help="Prénom du client"),
    last_name: str = typer.Option(..., help="Nom de Famille du client"),
    email: str = typer.Option(..., help="Adresse e-mail du client"),
    phone: str = typer.Option(..., help="Numéro de téléphone du client"),
    company_name: str = typer.Option(..., help="Nom de la compagnie"),
    commercial_id: int = typer.Option(..., help="ID du commercial"),
):
    """Crée un utilisateur dans la base de données"""
    try:
        session = get_session()
        client = Client.create_object(
            session,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
            commercial_id=commercial_id,
        )
        typer.secho(
            f"✅ Client '{client.first_name} {client.last_name}' créé avec succès !",
            fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(f"❌ Erreur lors de la création du client : {str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@client_app.command(name="list")
def client_list(
    client_id: Optional[int] = typer.Option(
        None,
        help="ID du client pour afficher les détails"),
    commercial_id: Optional[int] = typer.Option(
        None,
        help="ID du commercial pour afficher les clients",
    )
):
    """Affiche la liste des clients"""
    session = get_session()
    headers = ["ID", "First name", "Last_name", "Email", "Phone", "Company name", "Commercial Id", "Commercial Name"]
    try:
        if client_id:
            client = Client.get_object(session, id=client_id)
            if client:
                display.table(
                    title="Détails du client",
                    headers=headers,
                    items=[Client.format_client_data(session, client)]
                )
            else:
                typer.secho("❌ Client non trouvé", fg=typer.colors.RED)
        else:
            clients = Client.get_all_object(session, Client)
            if commercial_id:
                clients = [client for client in clients if client.commercial_id == commercial_id]
                display.table(
                    title="Liste des clients pour ce commercial",
                    headers=headers,
                    items=[Client.format_client_data(session, client) for client in clients],
                    exclude_headers=['Commercial Name', 'Company name']

                )
            else:
                display.table(
                    title="Liste des clients",
                    headers=headers,
                    items=[Client.format_client_data(session, client) for client in clients],
                    exclude_headers=['Commercial Name', 'Company name']

                )

    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@client_app.command()
def delete(
        client_id: Optional[int] = typer.Option(
        None, help="ID du client à supprimer")
):
    typer.confirm("❓Êtes vous sur de vouloir supprimer cet utilisateur ?")
    session = get_session()
    try:
        Client.delete_object(session, client_id)
        typer.secho(
            f'Client {client_id} supprimé avec succès',
            fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"❌ Erreur: {str(e)}", fg=typer.colors.RED)


if __name__ == "__main__":
    client_app()
