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

from view.display_view import Display

engine = create_engine('sqlite:///./epic_event.db')
Session = sessionmaker(bind=engine)
display = Display()

contract_app = typer.Typer(name='Epic Events contract Management',
                           help='Application de Gestion des Contrats Epic Event')


def get_session():
    """Récupère une session de la base de données"""
    return Session()


@contract_app.command(name="create")
def create(
    client_id: int = typer.Option(..., help="ID de client"),
    commercial_id: int = typer.Option(..., help="ID du commercial"),
    total_amount: float = typer.Option(..., help="Montant Total"),
    remaining_amount: float = typer.Option(
        ..., help="Montant restant"),
):
    """Crée un contrat dans la base de données"""
    try:
        session = get_session()
        contract = Contract.create_object(
            session,
            client_id=client_id,
            commercial_id=commercial_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount
        )
        typer.secho(
            f"✅ Contrat n°'{contract.client_id}' créé avec succès !",
        )
    except Exception as e:
        typer.secho(f"❌ Erreur lors de la création du contrat : "
                    f"{str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@contract_app.command(name="repport")
def contract_list(
    client_id: Optional[int] = typer.Option(None, help="ID de client"),
    id: Optional[int] = typer.Option(None, help="ID du contrat"),
    is_signed: Optional[bool] = typer.Option(None, help="Contrats signés"),
    contract_amount_left: Optional[bool] = typer.Option(
        None, help="Contrat pas entièrement payés"),
):
    """Recupere les contrats de la base de données:
        signé
        /non signé
        /pas entièrement payés
        /ID du client
        /ID du contrat
    """
    contract_headers = [
        "ID du client",
        "ID du commercial",
        "Somme total à payer",
        "Somme restante",
        "Signé"
    ]
    session = get_session()
    try:
        # Récupération des contrats en fonction des filtres
        contracts = get_filtered_contracts(
            session, client_id, id, is_signed, contract_amount_left)

        # Vérification si aucun contrat trouvé
        if not contracts:
            typer.secho("❌ Aucun contrat trouvé", fg=typer.colors.RED)
            return

        # Affichage du tableau des contrats
        display.table(
            title="Liste des contrats",
            headers=contract_headers,
            items=[
                Contract.format_contract_data(
                    session, contract) for contract in contracts
                ]
        )
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@contract_app.command(name="sign-contract")
def sign_contract(
        id: int = typer.Option(None, help="ID du contrat à signer"),
):
    typer.confirm("Validation de la signature du contrat ✅")
    session = get_session()
    try:
        Contract.sign_object(session, contract_id=id)
        typer.secho(
            f"✅ Contrat n°'{id}' signé avec succès !",
        )
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)


@contract_app.command(name="payment")
def payment(
    id: int = typer.Option(
        None, help="ID du contrat pour lequel effectuer le paiement"),
    amount: float = typer.Option(
        None, help="Montant du paiment pour le contrat"),
    change_total_amount: Optional[float] = typer.Option(
        None, help="Montant total à payer pour le contrat"),
):
    typer.confirm("Validation de l'entrée du paiments  ✅")
    session = get_session()
    try:
        Contract.update_amount(
            session,
            contract_id=id,
            remaining_amount=amount,
            total_amount=change_total_amount
        )
        typer.secho(f"✅ Paiement du contrat n°'{id}' effect")
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()


@contract_app.command()
def delete(
    id: int = typer.Option(None, help="ID du contrat à supprimer")
):
    typer.confirm("❓Êtes vous sur de vouloir supprimer cet utilisateur ?")
    session = get_session()
    try:
        Contract.delete_object(session, id)
        typer.secho(
            f'✅ Utilisateur {id} supprimé avec succès',
            fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"❌ Erreur: {str(e)}", fg=typer.colors.RED)


def get_filtered_contracts(
        session,
        client_id=None,
        id=None,
        is_signed=False,
        contract_amount_left=False
):
    """
    Récupère les contrats filtrés en fonction des paramètres fournis.
    """
    contracts = Contract.get_all_object(session, Contract)
    if client_id:
        contracts = [contract for contract in contracts if contract.client_id]
    elif id:
        contracts = [contract for contract in contracts if contract.id]
    elif is_signed:
        contracts = [contract for contract in contracts if contract.is_signed]
    if contract_amount_left:
        contracts = [
            contract for contract in contracts if contract.remaining_amount > 0
        ]
    return contracts
