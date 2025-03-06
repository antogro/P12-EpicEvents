import typer
from typing import Optional
from src.models.contract import Contract
from src.models.permission import requires_permission, requires_login
from src.view.display_view import Display
from src.models.common import get_session

display = Display()

contract_app = typer.Typer(
    name="Epic Events Contract Management",
    help="Application de Gestion des Contrats Epic Event"
)


@contract_app.command(name="create")
@requires_permission("manage_all_contracts")
def create(
    ctx: typer.Context,
    client_id: int = typer.Option(
        ..., prompt=True, help="ID du client"),
    commercial_id: int = typer.Option(
        ..., prompt=True, help="ID du commercial"),
    total_amount: float = typer.Option(
        ..., prompt=True, help="Montant total"),
    remaining_amount: float = typer.Option(
        ..., prompt=True, help="Montant restant"),
):
    """Crée un contrat dans la base de données."""
    session = get_session()
    try:
        is_signed = None
        if typer.confirm(
                "Le contrat est-il signé ?", default=False):
            is_signed = True
        contract = Contract.create_object(
            session,
            client_id=client_id,
            commercial_id=commercial_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            is_signed=is_signed
        )
        typer.secho(f"✅ Contrat n°{contract.client_id} créé avec succès !")
    except Exception as e:
        typer.secho(f"\n ❌ {str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@contract_app.command(name="report")
@requires_login()
def contract_list(
    ctx: typer.Context,
    id: Optional[int] = typer.Option(None, help="ID du contrat"),
    client_id: Optional[int] = typer.Option(None, help="ID du client"),
    contract_id: Optional[int] = typer.Option(None, help="ID du contrat"),
    is_signed: Optional[bool] = typer.Option(False, help="Contrats signés"),
    amount_left: Optional[bool] = typer.Option(
        False, help="Contrats non entièrement payés"
    ),
    unsigned_only: Optional[bool] = typer.Option(
        False, help="Afficher uniquement les contrats non signés"),
):
    """Récupère les contrats selon divers filtres."""
    contract_headers = [
        "ID du contrat",
        "ID du client",
        "ID du commercial",
        "Montant total",
        "Montant restant",
        "Signé"
    ]
    session = get_session()
    try:
        contracts = get_filtered_contracts(
            session, client_id, contract_id, is_signed, amount_left,
            unsigned_only
        )

        if not contracts:
            typer.secho("❌ Aucun contrat trouvé", fg=typer.colors.RED)
            return

        display.table(
            title="Liste des contrats",
            headers=contract_headers,
            items=[
                Contract.format_contract_data(session, contract) for
                contract in contracts]
        )
    except Exception as e:
        typer.secho(f"\n ❌ {str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@contract_app.command(name="sign")
@requires_permission("manage_all_contracts", "update_own_contracts")
def sign_contract(
    ctx: typer.Context,
    contract_id: int = typer.Option(
        ..., prompt=True, help="ID du contrat à signer"),
):
    """Signe un contrat."""
    session = get_session()

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["contract_id"] = contract_id

    try:
        if typer.confirm("Validation de la signature du contrat ✅"):
            Contract.sign_object(session, contract_id=contract_id)
            typer.secho(f"✅ Contrat n°{contract_id} signé avec succès !")
        else:
            typer.secho("❌ Signature annulée", fg=typer.colors
                        .RED)
    except Exception as e:
        typer.secho(f"\n ❌ {str(e)}", fg=typer.colors.RED)


@contract_app.command(name="payment")
@requires_permission("update_own_contracts", "manage_all_contracts")
def payment(
    ctx: typer.Context,
    contract_id: int = typer.Option(None, prompt=True, help="ID du contrat"),
    amount: float = typer.Option(None, help="Montant du paiement"),
    change_total_amount: Optional[float] = typer.Option(
        None, help="Nouveau montant total du contrat"
    ),
):
    """Effectue un paiement partiel ou total sur un contrat."""
    typer.confirm("Validation du paiement ✅")
    session = get_session()

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["contract_id"] = contract_id

    try:
        contract = Contract.get_object(session, id=contract_id)

        if amount is None:
            amount = contract.remaining_amount

        if change_total_amount is None:
            change_total_amount = contract.total_amount

        Contract.update_amount(
            session,
            contract_id=contract_id,
            remaining_amount=amount,
            total_amount=change_total_amount
        )
        typer.secho(f"✅ Paiement du contrat n°{contract_id} effectué")
    except Exception as e:
        typer.secho(f"\n ❌ {str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@contract_app.command(name="delete")
def delete(
    ctx: typer.Context,
    id: int = typer.Option(
        None, prompt=True, help="ID du contrat à supprimer"),
):
    """Supprime un contrat."""
    typer.confirm("❓ Êtes-vous sûr de vouloir supprimer ce contrat ?")
    session = get_session()

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["contract_id"] = id

    try:
        Contract.delete_object(session, id)
        typer.secho(
            f'✅ Contrat {id} supprimé avec succès',
            fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"❌ Erreur: {str(e)}", fg=typer.colors.RED)


def get_filtered_contracts(
    session,
    client_id=None,
    contract_id=None,
    is_signed=False,
    amount_left=False,
    unsigned_only=False
):
    """
    Récupère les contrats filtrés en fonction des paramètres fournis.
    """
    contracts = Contract.get_all_object(session)

    if client_id:
        contracts = [
            contract for contract in
            contracts if contract.client_id == client_id]
    if contract_id:
        contracts = [
            contract for contract in
            contracts if contract.id == contract_id]
    if is_signed:
        contracts = [contract for contract in contracts if contract.is_signed]
    if amount_left:
        contracts = [
            contract for contract in
            contracts if contract.remaining_amount > 0]
    if unsigned_only:
        contracts = [
            contract for contract in contracts if not contract.is_signed]

    return contracts
