import typer
from typing import Optional
from src.models.event import Event
from src.view.display_view import Display
from src.models.permission import requires_permission, requires_login
from src.models.contract import Contract
from src.models.user_session import UserSession
from src.models.common import get_session

display = Display()

event_app = typer.Typer(
    name="Epic Events Management",
    help="Application de Gestion des Événements Epic Events"
)


@event_app.command(name="create")
@requires_permission("create_event")
def create(
    ctx: typer.Context,
    name: str = typer.Option(..., prompt=True, help="Nom de l'événement"),
    client_id: int = typer.Option(..., prompt=True, help="ID du client"),
    contract_id: int = typer.Option(..., prompt=True, help="ID du contrat"),
    start_date: str = typer.Option(
        ..., prompt=True, help="Date de début (AAAA-MM-JJ)"),
    end_date: str = typer.Option(
        ..., prompt=True, help="Date de fin (AAAA-MM-JJ)"),
    location: str = typer.Option(..., prompt=True, help="Localisation"),
    attendees: int = typer.Option(
        ..., prompt=True, help="Nombre de participants"),
    notes: str = typer.Option(
        None, prompt=True, help="Description de l'événement"),
):
    """Crée un événement dans la base de données."""
    session = get_session()
    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["contract_id"] = contract_id
    try:
        support_contact_id = None
        if typer.confirm(
            "Souhaitez-vous ajouter un support à cet événement ?",
                default=False):
            support_contact_id = typer.prompt("ID du support", type=int)

        contrat = Contract.get_object(session, id=contract_id)
        if not contrat:
            raise Exception("Le contrat spécifié n'existe pas.")

        if contrat.commercial_id is None:
            raise Exception("Le contrat ne possède pas de commercial associé.")

        current_user = UserSession.get_current_user(ctx)
        if contrat.commercial_id != current_user.id:
            raise Exception(
                "Seul le commercial responsable "
                "du client peut créer un événement.")

        event = Event.create_object(
            session,
            client_id=client_id,
            support_contact_id=support_contact_id,
            contract_id=contract_id,
            name=name.replace("-", " "),
            start_date=start_date,
            end_date=end_date,
            location=location,
            attendees=attendees,
            notes=notes.replace("-", " "),
        )
        typer.secho(
            f"✅ Événement du contrat n°{event.contract_id} créé avec succès!")
    except Exception as e:
        typer.secho(f"❌ {str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@event_app.command(name="report")
@requires_login()
def event_report(
    ctx: typer.Context,
    client_id: Optional[int] = typer.Option(None, help="ID du client associé"),
    event_id: Optional[int] = typer.Option(None, help="ID de l'événement"),
    support_contact_id: Optional[int] = typer.Option(
        None, help="ID du support"),
    contract_id: Optional[int] = typer.Option(None, help="ID du contrat"),
    unassigned_only: bool = typer.Option(
        False, help="Afficher uniquement les événements sans support"),
):
    """Affiche les détails des événements avec option de filtrage."""
    event_headers = [
        "ID de l'Événement", "ID du support", "ID du client", "ID du contrat",
        "Nom de l'événement", "Date de début", "Date de fin", "Localisation",
        "Nombre de participants", "Créé le", "Mise à jour le", "Notes",
    ]

    session = get_session()
    try:
        events = get_filtered_events(
            session, client_id, event_id,
            support_contact_id, contract_id, unassigned_only
        )

        if not events:
            typer.secho("❌ Aucun événement trouvé", fg=typer.colors.RED)
            return

        display.table(
            title="Liste des Événements",
            headers=event_headers,
            items=[Event.format_event_data(session, event) for event in events]
        )
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@event_app.command(name="update")
@requires_permission("update_own_events")
def event_update(
    ctx: typer.Context,
    event_id: int = typer.Option(..., prompt=True, help="ID de l'événement"),
    name: Optional[str] = typer.Option(None, help="Nom de l'événement"),
    start_date: Optional[str] = typer.Option(
        None, help="Date et heure de début (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = typer.Option(
        None, help="Date et heure de fin (YYYY-MM-DD HH:MM:SS)"),
    location: Optional[str] = typer.Option(
        None, help="Localisation"),
    attendees: Optional[int] = typer.Option(
        None, help="Nombre de participants"),
):
    """Met à jour un événement."""
    session = get_session()

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["event_id"] = event_id

    try:
        event = Event.update_object(
            session,
            event_id=event_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            location=location,
            attendees=attendees,
        )
        typer.secho(f"✅ Événement '{event}' mis à jour avec succès!")
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@event_app.command(name="assign-support")
@requires_permission("update_own_events")
def assign_support(
    ctx: typer.Context,
    event_id: int = typer.Option(..., prompt=True, help="ID de l'événement"),
    support_id: Optional[int] = typer.Option(
        ..., prompt=True, help="ID du support à assigner"),
):
    """Met à jour un événement."""
    session = get_session()

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["event_id"] = event_id

    try:
        Event.update_object(
            session,
            event_id=event_id,
            support_contact_id=support_id,
        )
        typer.secho(
            f"✅ Support {support_id} assigné à "
            f"l'événement n°{event_id} avec succès!")
    except Exception as e:
        typer.secho(f"❌{e}", fg=typer.colors.RED)
    finally:
        session.close()


@event_app.command(name="delete")
@requires_permission("update_own_events")
def event_delete(
    ctx: typer.Context,
    id: int = typer.Option(
        ..., prompt=True, help="ID de l'événement à supprimer"),
):
    """Supprime un événement."""
    session = get_session()

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["event_id"] = id

    try:
        Event.delete_object(session, event_id=id)
        typer.secho(f"✅ L'événement n°{id} a été supprimé")
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)


def get_filtered_events(
    session,
    client_id=None,
    event_id=None,
    support_contact_id=None,
    contract_id=None,
    unassigned_only=False
):
    """Récupère les événements filtrés selon divers critères."""
    events = Event.get_all_object(session)

    if client_id:
        events = [event for event in events if event.client_id == client_id]
    if event_id:
        events = [event for event in events if event.id == event_id]
    if support_contact_id:
        events = [
            event for event in events if
            event.support_contact_id == support_contact_id]
    if contract_id:
        events = [
            event for event in events if
            event.contract_id == contract_id]
    if unassigned_only:
        events = [
            event for event in events if event.support_contact_id is None]

    return events
