import typer
from sqlalchemy import create_engine
from typing import Optional
from sqlalchemy.orm import sessionmaker
from models.event import Event
from view.display_view import Display
from models.permission import requires_permission, requires_login
from models.contract import Contract
from models.user_session import UserSession


engine = create_engine("sqlite:///./epic_event.db")
Session = sessionmaker(bind=engine)
display = Display()

event_app = typer.Typer(
    name="Epic Events Events Management",
    help="Application de Gestion des Evenement Epic Events",
)


def get_session():
    """Récupère une session SQLAlchemy active"""
    try:
        session = Session()
        return session
    except Exception as e:
        typer.secho("❌ Erreur : Impossible d'initialiser"
                    f" la session SQLAlchemy : {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@event_app.command(name="create")
@requires_permission("create_event")
def create(
        ctx: typer.Context,
        name: str = typer.Option(
            ..., prompt=True, help="Nom de l'évenement"),
        client_id: int = typer.Option(
            None, prompt=True, help="ID de client"),
        contract_id: int = typer.Option(
            ..., prompt=True, help="ID du contrat"
        ),
        start_date: str = typer.Option(
            ..., prompt=True, help="date de début format:'aaaa-mm-dd'"
        ),
        end_date: str = typer.Option(
            ..., prompt=True, help="date de fin"),
        location: str = typer.Option(
            ..., prompt=True, help="Localisation"),
        attendees: int = typer.Option(
            ..., prompt=True, help="Nombre de participant"
        ),
        notes: str = typer.Option(
            None, prompt=True, help="Description de l'évènement"
        ),
):
    """Crée un contrat dans la base de données"""
    try:
        session = get_session()
        support_contact_id = None
        if typer.confirm(
            "Souhaitez-vous ajouter un support à cet événement ?",
                default=False):
            support_contact_id = typer.prompt("ID du support", type=int)
        # Vérifier que le contrat est bien récupéré
        contrat = Contract.get_object(session, id=contract_id)

        if not contrat:
            raise Exception(" Le contrat spécifié n'existe pas.")

        # Vérifier que le contrat a bien un commercial_id
        if contrat.commercial_id is None:
            raise Exception(" Le contrat ne possède "
                            "pas de commercial associé.")

        # Vérifier que le contrat appartient au commercial connecté
        current_user = UserSession.get_current_user(ctx)

        if contrat.commercial_id != current_user.id:
            raise Exception("\n Seul le commercial responsable du client "
                            "peut créer un événement.")

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
            f"✅ Evenement du contrat n°'{event.contract_id}' créé avec succès!"
        )
    except Exception as e:
        typer.secho(
            f"❌{str(e)}",
            fg=typer.colors.RED,
        )
    finally:
        session.close()


@event_app.command(name="report")
@requires_login()
def event_report(
        ctx: typer.Context,
        client_id: Optional[int] = typer.Option(
            None, help="ID du client associé"),
        id: Optional[int] = typer.Option(
            None, help="ID de l'événement"),
        support_contact_id: Optional[int] = typer.Option(
            None, help="ID du support associé"),
        contract_id: Optional[int] = typer.Option(
            None, help="ID du contrat associé"),
        unassigned_only: bool = typer.Option(
            False, help="Afficher uniquement les événements sans support")
):
    """
    Affiche les détails d'un événement avec
    option de filtrage pour événements non assignés.
    """
    event_headers = [
        "ID de l'Evènement",
        "ID du support",
        "ID du client",
        "ID du contrat",
        "Nom de l'évènement",
        "Date de début",
        "date de fin",
        "Localisation",
        "Nombre de participants",
        "Créé le",
        "Mise à jour le",
        "Notes",
    ]

    session = get_session()
    try:
        events = get_filtered_events(
            session, client_id, id, support_contact_id,
            contract_id, unassigned_only
        )

        if not events:
            typer.secho("❌ Aucun évènement trouvé", fg=typer.colors.RED)
            return

        # Affichage du tableau des événements
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
        id: int = typer.Option(..., prompt=True, help="ID de L'évènement"),
        name: Optional[str] = typer.Option(
            None, prompt=True, help="Nom de l'évenement"),
        start_date: Optional[str] = typer.Option(
            None,
            prompt=True,
            help="Date et heure de début "
            "(format: YYYY-MM-DD_HH:MM:SS, ex: 2025-12-20_14:30:00)",
        ),
        end_date: Optional[str] = typer.Option(
            None,
            prompt=True,
            help="Date et   heure de fin (format: YYYY-MM-DD_HH:MM:SS,"
            "ex: 2025-12-20_16:30:00)",
        ),
        location: Optional[str] = typer.Option(
            None, prompt=True, help="Localisation"),
        attendees: Optional[int] = typer.Option(
            None, prompt=True, help="Nombre de participant"
        ),
):
    """Mise à jour d'un Evènement"""
    session = get_session()
    try:
        event = Event.update_object(
            session,
            event_id=id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            location=location,
            attendees=attendees,
        )
        typer.secho(f"✅ Evènement '{event}' mise à jour")
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@event_app.command(name="delete")
@requires_permission("update_own_events")
def event_delete(
    ctx: typer.Context,
    id: int = typer.Option(
        ..., prompt=True, help="ID de L'évènement à supprimer")
):
    """Suppression d'un Evènement"""
    session = get_session()
    try:
        Event.delete_object(session, event_id=id)
        typer.secho(f"✅ L'évènement n°{id} a été supprimé")
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.color.RED)


def get_filtered_events(
    session,
    client_id=None,
    event_id=None,
    support_contact_id=None,
    contract_id=None,
    unassigned_only=False  # Ajout de l'option de filtrage
):
    """
    Récupère les événements filtrés en fonction des paramètres fournis.
    """
    events = Event.get_all_object(session)

    if client_id:
        events = [event for event in events if event.client_id == client_id]
    if event_id:
        events = [event for event in events if event.id == event_id]
    if support_contact_id:
        events = [
            event for event in events if
            event.support_contact_id == support_contact_id
        ]
    if contract_id:
        events = [
            event for event in events if
            event.contract_id == contract_id]
    if unassigned_only:
        events = [
            event for event in events if
            event.support_contact_id is None]

    return events
