import typer
from typing import Optional
from src.models.client import Client
from src.view.display_view import Display
from src.models.permission import requires_permission, requires_login
from src.models.common import get_session
from src.models.user_session import UserSession

display = Display()

client_app = typer.Typer(
    name="Epic Events client Management",
    help="Application de Gestion des clients Epic Event",
)


@client_app.command(name="create")
@requires_permission("create_clients")
def create_client(
        ctx: typer.Context,
        first_name: str = typer.Option(
            ..., prompt=True, help="Prénom du client"),
        last_name: str = typer.Option(
            ..., prompt=True, help="Nom de Famille du client"),
        email: str = typer.Option(
            ..., prompt=True, help="Adresse e-mail du client"),
        phone: str = typer.Option(
            ..., prompt=True, help="Numéro de téléphone du client"),
        company_name: str = typer.Option(
            ..., prompt=True, help="Nom de la compagnie"),
):
    """Crée un utilisateur dans la base de données"""
    try:
        commercial_id = UserSession.get_current_user(ctx).id
        session = get_session()
        client = Client.create_object(
            session,
            first_name=first_name.replace("-", " "),
            last_name=last_name.replace("-", " "),
            email=email,
            phone=phone,
            company_name=company_name.replace("-", " "),
            commercial_id=commercial_id,
        )
        typer.secho(
            f"✅ Client '{client.first_name} {client.last_name}' "
            f"créé avec succès !",
            fg=typer.colors.GREEN,
        )
    except Exception as e:
        typer.secho(
            f"❌ {str(e)}",
            fg=typer.colors.RED
        )
    finally:
        session.close()


@client_app.command(name="report")
@requires_login()
def client_list(
        ctx: typer.Context,
        id: Optional[int] = typer.Option(
            None,
            help="ID du client pour afficher les détails"
        ),
        commercial_id: Optional[int] = typer.Option(
            None,
            help="ID du commercial pour afficher les clients",
        ),
):
    """Affiche la liste des clients"""
    session = get_session()
    headers = [
        "ID",
        "Prènom",
        "Nom",
        "Email",
        "Phone",
        "Company name",
        "Commercial ID",
        "Commercial Name",
    ]
    try:
        if id:
            client = Client.get_object(session, id=id)
            if client:
                display.table(
                    title="Détails du client",
                    headers=headers,
                    items=[Client.format_client_data(session, client)],
                )
            else:
                typer.secho("❌ Client non trouvé", fg=typer.colors.RED)
        else:
            clients = Client.get_all_object(session)
            if commercial_id is not None:
                clients = [
                    client
                    for client in clients
                    if client.commercial_id == commercial_id
                ]
                display.table(
                    title="Liste des clients pour ce commercial",
                    headers=headers,
                    items=[
                        Client.format_client_data(session, client)
                        for client in clients
                    ],
                    exclude_headers=["Commercial Name", "Company name"],
                )
            else:
                display.table(
                    title="Liste des clients",
                    headers=headers,
                    items=[
                        Client.format_client_data(session, client)
                        for client in clients
                    ],
                    exclude_headers=["Commercial Name", "Company name"],
                )

    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@client_app.command(name="update")
@requires_permission("update_own_clients")
def update_client(
        ctx: typer.Context,
        id: Optional[int] = typer.Option(
            None, help="ID du client pour afficher les détails"
        ),
        first_name: Optional[str] = typer.Option(
            None, help="Prénom du client"),
        last_name: Optional[str] = typer.Option(
            None, help="Nom de Famille du client"),
        email: Optional[str] = typer.Option(
            None, help="Adresse e-mail du client"),
        phone: Optional[str] = typer.Option(
            None, help="Numéro de téléphone du client"),
        company_name: Optional[str] = typer.Option(
            None, help="Nom de la compagnie"),
        commercial_id: Optional[int] = typer.Option(
            None, help="ID du commercial"),
):
    """Mise à jour d'un client"""
    session = get_session()
    try:
        client = Client.update_object(
            session,
            client_id=id,
            first_name=first_name.replace("-", " ") if first_name else None,
            last_name=last_name.replace("-", " ") if last_name else None,
            email=email,
            phone=phone,
            company_name=company_name.replace(
                "-", " ") if company_name else None,
            commercial_id=commercial_id,
        )
        typer.secho(
            f"✅ Evenement du contrat n°'{client.id}' créé avec succès!")
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)


@client_app.command()
@requires_permission("update_own_clients")
def delete(
        ctx: typer.Context,
        id: Optional[int] = typer.Option(
        None, prompt=True, help="ID du client à supprimer")):
    typer.confirm("❓Êtes vous sur de vouloir supprimer cet utilisateur ?")
    session = get_session()
    try:
        Client.delete_object(session, id)
        typer.secho(f"Client {id} supprimé avec succès", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"❌{str(e)}", fg=typer.colors.RED)


if __name__ == "__main__":
    client_app()
