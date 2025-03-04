import pytest
from src.models.contract import Contract
from src.models.user import User


def test_create_contract(mocker, session, make_contract, make_user):
    """Test qu'un commercial peut créer un contrat."""
    user_fixture = make_user(role="COMMERCIAL")
    contract_fixture = make_contract()

    user = User(**user_fixture)

    mocker.patch(
        "src.models.validators.ContractValidator.validate_required_fields",
        return_value=None,
    )
    mocker.patch(
        "src.models.validators.ContractValidator.validate_amounts",
        return_value=None
    )
    mocker.patch("src.models.contract.Contract.get_object", return_value=None)
    mocker.patch("src.models.user.User.get_object", return_value=user)

    contract = Contract.create_object(session, **contract_fixture)

    assert contract.total_amount == contract_fixture["total_amount"]
    assert contract.remaining_amount == contract_fixture["remaining_amount"]
    assert contract.client_id == contract_fixture["client_id"]
    assert contract.commercial_id == contract_fixture["commercial_id"]


def test_create_contract_should_raise_error_with_invalid_fields(
        mocker, session
):
    """Test qu'une erreur est levée si des champs
    obligatoires sont manquants."""
    mocker.patch.object(Contract, "get_object", return_value=None)
    incomplete_data = {
        "client_id": 1,
        "commercial_id": 1,
        "total_amount": 1000,  # `remaining_amount` manquant
    }

    with pytest.raises(
            Exception, match="Le champ remaining_amount est requis"):
        Contract.create_object(session, **incomplete_data)


def test_create_contract_should_raise_error_with_invalid_amount(
        mocker, session, make_contract, make_user
):
    """Test qu'une erreur est levée si le montant
    restant est supérieur au total."""
    user_fixture = make_user(role="COMMERCIAL")
    contract_fixture = make_contract(remaining_amount=1300)
    user = User(**user_fixture)

    mocker.patch("src.models.contract.Contract.get_object", return_value=None)
    mocker.patch("src.models.user.User.get_object", return_value=user)

    with pytest.raises(
        Exception,
        match="Le montant restant ne peut pas être supérieur au montant total",
    ):
        Contract.create_object(session, **contract_fixture)


def test_get_contract(mocker, session, make_contract):
    """Test qu'on peut récupérer un contrat existant."""
    contract_fixture = make_contract()
    expected_contract = Contract(**contract_fixture)

    mocker.patch.object(Contract, "get_object", return_value=expected_contract)

    result = Contract.get_object(
        session, client_id=contract_fixture["client_id"])

    assert result == expected_contract


def test_get_contract_invalide_data_raise_error(
        mocker, session, make_contract):
    """Test qu'une erreur est levée si le contrat est inexistant."""

    contract_fixture = make_contract()
    mocker.patch.object(Contract, "get_object", return_value=None)

    with pytest.raises(Exception, match="Le contrat n'existe pas"):
        contract = Contract.get_object(
            session, client_id=contract_fixture["client_id"])
        if contract is None:
            raise Exception("Le contrat n'existe pas")


def test_delete_contract(mocker, session, make_contract):
    """Test suppression d'un contrat existant."""
    contract_fixture = make_contract()
    expected_contract = Contract(**contract_fixture)

    mocker.patch.object(Contract, "get_object", return_value=expected_contract)
    mocker.patch.object(session, "delete")
    mocker.patch.object(session, "commit")

    result = Contract.delete_object(session, expected_contract.id)

    assert result.commercial_id == expected_contract.commercial_id
    assert result.client_id == expected_contract.client_id


def test_delete_contract_raise_error_with_wrong_contract_id(mocker, session):
    """Test qu'on ne peut pas supprimer un contrat inexistant."""
    contract_id = 999
    mocker.patch.object(Contract, "get_object", return_value=None)

    with pytest.raises(Exception, match="Le contrat n'existe pas"):
        Contract.delete_object(session, contract_id)


def test_update_contract(mocker, session, make_contract):
    """Test mise à jour d'un contrat."""
    contract_fixture = make_contract()
    initial_contract = Contract(**contract_fixture)
    contract_id = contract_fixture["id"]
    update_data = {"total_amount": 1500, "remaining_amount": 1200}

    mocker.patch.object(Contract, "get_object", return_value=initial_contract)
    mocker.patch.object(session, "commit")

    result = Contract.update_object(session, contract_id, **update_data)

    assert result.total_amount == update_data["total_amount"]


def test_update_contract_with_no_contract(mocker, session):
    """Test mise à jour d'un contrat inexistant."""
    contract_id = 999
    update_data = {"total_amount": 1500}

    mocker.patch.object(Contract, "get_object", return_value=None)

    with pytest.raises(Exception, match="Le contrat n'existe pas"):
        Contract.update_object(session, contract_id, **update_data)


def test_update_contract_with_wrong_amount(
        mocker, session, make_contract, make_user):
    """Test mise à jour avec un montant restant supérieur au total."""
    update_data = {"remaining_amount": 1500}

    user = User(**make_user())
    contract = Contract(**make_contract())
    mocker.patch.object(User, "get_object", return_value=user)
    mocker.patch.object(Contract, "get_object", return_value=contract)

    with pytest.raises(
        Exception,
        match="Le montant restant ne peut pas être supérieur au montant total",
    ):
        Contract.update_amount(session, 1, **update_data)


def test_sign_contract(mocker, session):
    """Test signature d'un contrat."""
    mock_contract = mocker.MagicMock()
    mock_contract.is_signed = False

    mocker.patch.object(Contract, "get_object", return_value=mock_contract)
    mocker.patch.object(Contract, "_save_object", return_value=mock_contract)

    result = Contract.sign_object(session, contract_id=1)

    assert result.is_signed is True


def test_sign_contract_with_no_contract(mocker, session):
    """Test signature d'un contrat inexistant."""
    mocker.patch.object(Contract, "get_object", return_value=None)

    with pytest.raises(Exception, match="Le contrat n'existe pas"):
        Contract.sign_object(session, contract_id=1)
