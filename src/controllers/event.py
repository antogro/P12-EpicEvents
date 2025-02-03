import typer
from sqlalchemy import create_engine
from typing import Optional
from sqlalchemy.orm import sessionmaker
import os
import sys
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)
from models.contract import Contract
from models.user import User
from models.client import Client
from models.event import Event

from view.display_view import Display

engine = create_engine('sqlite:///./epic_event.db')
Session = sessionmaker(bind=engine)
display = Display()

event_app = typer.Typer(name='Epic Events Events Management',
                        help='Application de Gestion des Evenement Epic Events'
                        )


def get_session():
    """Récupère une session de la base de données"""
    return Session()


@event_app.command(name="create")
def create(
    client_id: int = typer.Option(..., help="ID de client"),
    support_contact_id: int = typer.Option(..., help="ID du support"),
    contract_id: int = typer.Option(..., help="ID du contrat"),
    name: str = typer.Option(..., help="Nom de l'évenement"),
    start_date: str = typer.Option(
        ..., help="date de début format:'aaaa-mm-dd'"),
    end_date: str = typer.Option(..., help="date de fin"),
    location: str = typer.Option(..., help="Localisation"),
    attendees: int = typer.Option(
        ..., help="Nombre de participant"),
):
    """Crée un contrat dans la base de données"""
    try:
        session = get_session()
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
        )
        typer.secho(
            f"✅ Evenement du contrat n°'{event.contract_id}' créé avec succès!"
        )
    except Exception as e:
        typer.secho(f"❌ Erreur lors de la création de l'évènement : "
                    f"{str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@event_app.command(name="repport")
def event_repport(
    client_id: Optional[int] = typer.Option(None, help="ID du client associé"),
    id: Optional[int] = typer.Option(None, help="ID de l'évenement"),
    support_contact_id: Optional[int] = typer.Option(
        None, help="ID du support associé"),
    contract_id: Optional[int] = typer.Option(
        None, help="ID du contrat associé"),
):
    """Affiche les détails d'un événement"""
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
    ]
    session = get_session()
    try:
        events = get_filtered_events(
            session,
            client_id,
            id,
            support_contact_id,
            contract_id
        )
        if not events:
            typer.secho("❌ Aucun évènement trouvé", fg=typer.colors.RED)
            return

        # Affichage du tableau des contrats
        display.table(
            title="Liste des Evènement",
            headers=event_headers,
            items=[
                Event.format_event_data(
                    session, event) for event in events
                ]
        )
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@event_app.command(name="update")
def event_update(
    id: int = typer.Option(..., help="ID de L'évènement"),
    name: Optional[str] = typer.Option(None, help="Nom de l'évenement"),
    start_date: Optional[str] = typer.Option(
        None,
        help="Date et heure de début (format: YYYY-MM-DD_HH:MM:SS,"
             "ex: 2025-12-20_14:30:00)"
    ),
    end_date: Optional[str] = typer.Option(
        None,
        help="Date et heure de fin (format: YYYY-MM-DD_HH:MM:SS,"
             "ex: 2025-12-20_16:30:00)"
    ),
    location: Optional[str] = typer.Option(None, help="Localisation"),
    attendees: Optional[int] = typer.Option(
        None, help="Nombre de participant"),
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
            attendees=attendees
        )
        typer.secho(f"✅ Evènement '{event}' mise à jour")
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@event_app.command(name="delete")
def event_delete(
        id: int = typer.Option(..., help="ID de L'évènement à supprimer")
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
):
    """
    Récupère les contrats filtrés en fonction des paramètres fournis.
    """
    events = Event.get_all_object(session, Event)
    if client_id:
        events = [event for event in events if event.client_id == client_id]
    elif event_id:
        events = [event for event in events if event.id == event_id]
    elif support_contact_id:
        events = [
            event for event in events
            if event.support_contact_id == support_contact_id]
    elif contract_id:
        events = [
            event for event in events if event.contract_id == contract_id]
    else:
        events = Event.get_all_object(session, Event)
    return events
