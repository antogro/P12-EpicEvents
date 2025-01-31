from models.contract import Contract
from models.user import User
import pytest


def test_create_contract(mocker, session, make_contract, make_user):
    user_fixture = make_user(role="COMMERCIAL")
    contract_fixture = make_contract()

    user = User(**user_fixture)
    mocker.patch(
        "models.validators.ContractValidator.validate_required_fields",
        return_value=None
    )
    mocker.patch(
        "models.validators.ContractValidator.validate_amounts",
        return_value=None
    )
    mocker.patch("models.contract.Contract.get_object", return_value=None)
    mocker.patch("models.contract.User.get_object", return_value=user)

    contract = Contract.create_object(session, **contract_fixture)

    assert contract.total_amount == contract_fixture["total_amount"]
    assert contract.remaining_amount == contract_fixture["remaining_amount"]
    assert contract.client_id == contract_fixture["client_id"]
    assert contract.commercial_id == contract_fixture["commercial_id"]


def test_create_contract_should_raise_error_with_invalide_required_fields(
    mocker,
    session,
):
    mocker.patch.object(Contract, 'get_object', return_value=None)
    incomplete_data = {
        "client_id": 1,
        "commercial_id": 1,
        "total_amount": 1000,
    }

    with pytest.raises(Exception) as e:
        Contract.create_object(session, **incomplete_data)
    assert ("Le champ remaining_amount est requis"
            in str(e.value))


def test_create_contract_should_raise_error_invalide_amount(
    mocker,
    session,
    make_contract,
    make_user
):
    user_fixture = make_user(role="COMMERCIAL")
    contract_fixture = make_contract(remaining_amount=1100)
    mocker.patch.object(User, 'get_object', return_value=user_fixture)

    mocker.patch.object(Contract, 'get_object', return_value=None)

    with pytest.raises(Exception) as e:
        Contract.create_object(session, **contract_fixture)
    assert (
        "Le montant restant ne peut pas être supérieur au montant total"
        in str(e.value)
    )


def test_create_contract_should_raise_error_negative_amount(
    mocker,
    session,
    make_contract
):
    contract_fixture = make_contract(remaining_amount=-100)
    mocker.patch.object(Contract, 'get_object', return_value=None)

    with pytest.raises(Exception) as e:
        Contract.create_object(session, **contract_fixture)
    assert "Les montants ne peuvent pas être négatifs" in str(e.value)


def test_get_contract(mocker, session, make_contract):
    contract_fixture = make_contract()
    expected_contract = Contract(**contract_fixture)

    # Prépare le mock pour session.query().filter_by().first()
    mock_query = mocker.Mock()
    mock_filter = mocker.Mock()
    mock_filter.first.return_value = expected_contract

    session.query = mocker.Mock(return_value=mock_query)
    mock_query.filter_by = mocker.Mock(return_value=mock_filter)

    # Exécution
    result = Contract.get_object(
        session, client_id=contract_fixture["client_id"]
    )

    # Vérification
    assert result == expected_contract
    session.query.assert_called_once_with(Contract)
    mock_query.filter_by.assert_called_once_with(
        client_id=contract_fixture["client_id"]
    )
    mock_filter.first.assert_called_once()


def test_get_contract_invalide_data_raise_exception_error(
        mocker,
        session,
        make_contract
):
    contract_fixture = make_contract()
    mock_query = mocker.Mock()
    mock_query.filter_by.side_effect = Exception("DB Error")

    mocker.patch.object(session, "query", return_value=mock_query)
    # Exécution
    with pytest.raises(
        Exception, match="Erreur lors de la récupération:"
    ):
        Contract.get_object(session, client_id=contract_fixture["client_id"])


def test_delete_contract(
        mocker,
        session,
        make_contract
):
    # Prépare le mock pour session
    contract_fixture = make_contract()
    expected_contract = Contract(**contract_fixture)
    contract_id = 1

    # Crée l'utilisateur avec les données fournies
    mock_get_contract = mocker.patch.object(
        Contract, 'get_object', return_value=expected_contract
    )
    mock_session_delete = mocker.patch.object(session, "delete")
    mock_session_commit = mocker.patch.object(session, "commit")
    # Supprime l'utilisateur
    result = Contract.delete_object(session, contract_id)
    # Vérifie que l'utilisateur a été supprimé
    assert result.commercial_id == expected_contract.commercial_id
    assert result.client_id == expected_contract.client_id
    mock_get_contract.assert_called_once_with(session, id=contract_id)
    mock_session_delete.assert_called_once_with(expected_contract)
    mock_session_commit.assert_called_once()


def test_delete_contract_raise_error_with_wrong_contract_id(
        mocker,
        session
):
    contract_id = 999
    mocker.patch.object(Contract, 'get_object', return_value="")
    with pytest.raises(Exception) as e:
        Contract.delete_object(session, contract_id)
    assert "Le contrat n'existe pas" in str(e.value)


def test_delete_contract_raise_exception_error(
        mocker,
        session,
        make_contract
):
    contract_id = 999
    mocker.patch.object(
        Contract, 'get_object', return_value=make_contract)
    with pytest.raises(Exception) as e:
        Contract.delete_object(session, contract_id)
    assert "Erreur lors de la suppression de l'objet Contract" in str(e.value)


def test_update_contract(
        mocker,
        session,
        make_contract
):
    contract_fixture = make_contract()
    initial_contract = Contract(**contract_fixture)
    contract_id = 1
    update_data = {
        "total_amount": 1500,
        "remaining_amount": 1200
    }
    mock_get_contract = mocker.patch.object(
        Contract, 'get_object', side_effect=[initial_contract]
    )
    mock_session_commit = mocker.patch.object(session, "commit")

    result = Contract.update_object(session, contract_id, **update_data)

    assert result.total_amount == update_data["total_amount"]
    assert mock_get_contract.call_count == 1
    mock_session_commit.assert_called_once()


def test_update_contract_with_no_contract(
        mocker,
        session,
):
    contract_id = 1
    update_data = {
        "total_amount": 1500,
        "remaining_amount": 1200
    }
    mocker.patch.object(
        Contract, 'get_object', side_effect=None
    )

    with pytest.raises(Exception, match="Le contrat n'existe pas"):
        Contract.update_object(session, contract_id, **update_data)


def test_update_contract_with_wrong_amount(
    mocker,
    session,
    make_contract,
    make_user
):
    update_data = make_contract(remaining_amount=1100)
    mocker.patch.object(User, 'get_object', return_value=make_user())

    mocker.patch.object(Contract, 'get_object', return_value=make_contract())
    with pytest.raises(Exception) as e:
        Contract.update_object(session, 1, **update_data)
    assert (
        "Le montant restant ne peut pas être supérieur au montant total"
        in str(e.value)
    )


def test_sign_contract(mocker, session):
    # Créer un mock de contrat avec is_signed = False
    mock_contract = mocker.MagicMock()
    mock_contract.is_signed = False

    # Mock get_object pour retourner notre mock_contract
    mocker.patch.object(Contract, 'get_object', return_value=mock_contract)

    # Mock _save_object pour retourner le contrat modifié
    mocker.patch.object(Contract, '_save_object', return_value=mock_contract)

    # Appeler la méthode
    result = Contract.sign_object(session, contract_id=1)

    # Vérifications
    assert result.is_signed is True
    Contract.get_object.assert_called_once_with(session, id=1)
    Contract._save_object.assert_called_once_with(session, mock_contract)


def test_sign_contract_with_no_contract(mocker, session):
    # Mock get_object pour retourner None
    mocker.patch.object(Contract, 'get_object', return_value=None)
    with pytest.raises(Exception, match="Le contrat n'existe pas"):
        Contract.sign_object(session, contract_id=1)
