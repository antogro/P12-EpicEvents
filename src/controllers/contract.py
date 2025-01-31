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

engine = create_engine('sqlite:///./epic_events.db')
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
    """Crée un utilisateur dans la base de données"""
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


@contract_app.command(name="list")
def contract_list(
    client_id: int = typer.Option(None, help="ID de client"),
    contract_id: int = typer.Option(None, help="ID du contrat"),
    is_signed: bool = typer.Option(None, help="Contrats signés"),
    contract_amount_left: bool = typer.Option(
        None, help="Contrat pas entièrement payés"),
):
    contract_headers = [
        "ID du client", "ID du commercial", "Somme total à payer", "Somme restante", "Signé"]
    session = get_session()
    try:
        contracts = []
        if client_id:
            contracts = Contract.get_object(session, client_id=client_id)
            if not contracts:
                typer.secho(f"❌ Aucun contrat trouvé pour le client n°'"
                            f"{client_id}'", fg=typer.colors.RED)
        elif contract_id:
            contracts = Contract.get_object(session, commercial_id=contract_id)
            if not contracts:
                typer.secho(f"❌ Aucun contrat trouvé pour le contrat n°'"
                            f"{contract_id}'", fg=typer.colors.RED)
        elif is_signed:
            contracts = Contract.get_all_object(session, Contract)
            print(contracts.is_signed)
            if not contracts:
                typer.secho("❌ Aucun contrat signé",
                            fg=typer.colors.RED)
            contracts = [contract for contract in contracts if contract.is_signed]
        elif contract_amount_left:
            contracts = Contract.get_all_object(session, Contract)
            for contract in contracts:
                if contract.remaining_amount > 0:
                    contract_amount_left.append(contract)
        else:
            contracts = Contract.get_all_object(session, Contract)

        contracts = [contracts]
        display.table(
            title="Liste des clients",
            headers=contract_headers,
            items=[Contract.format_contract_data(session, contract) for contract in contracts],
        )
    except Exception as e:
        typer.secho(f"❌ Une erreur est survenue : {e}", fg=typer.colors.RED)
    finally:
        session.close()



