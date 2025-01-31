from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, Boolean
from models.base import BaseModel
from models.validators import ContractValidator
from models.user import User


class Contract(BaseModel):
    """
    Modele d'un contrat
        args: - id (int),
              - client_id (int),
              - commercial_id (int),
              - total_amout (float),
              - remaining-amount (float),
              - is_signed (bool),
    """
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    is_signed = Column(Boolean, default=False)

    __table_args__ = {'extend_existing': True}

    @classmethod
    def create_object(cls, session, **kwargs):
        """
        Crée un contrat
        Utilisation : create_contract(
            session,
            client_id='client_id',
            commercial_id='commercial_id',
            total_amount='total_amount',
            remaining_amount='remaining_amount'
        )
        """
        try:
            ContractValidator.validate_required_fields(**kwargs)
            ContractValidator.validate_amounts(
                kwargs["total_amount"], kwargs["remaining_amount"]
            )
            if 'commercial_id' in kwargs and kwargs['commercial_id']:
                commercial = User.get_object(
                    session, id=kwargs['commercial_id']
                )
                if not commercial or commercial.role != 'COMMERCIAL':
                    raise ValueError("Le commercial n'existe pas")
            return cls._save_object(session, cls(**kwargs))
        except Exception as e:
            raise Exception(
                f"Une erreur lors de la mise à jour du contrat: {str(e)}")

    @classmethod
    def update_object(cls, session, contract_id, **kwargs):
        """
        Met à jour un contrat
        Utilisation : update_contract(
            session,
            contract_id,
            total_amount='total_amount',
            remaining_amount='remaining_amount'
        )
        """
        try:
            contract = cls.get_object(session, id=contract_id)
            if not contract:
                raise Exception("Le contrat n'existe pas")

            ContractValidator.validate_amounts(
                kwargs["total_amount"], kwargs["remaining_amount"]
            )
            for key, value in kwargs.items():

                if hasattr(contract, key):
                    setattr(contract, key, value)
            return cls._save_object(session, contract)
        except Exception as e:
            session.rollback()
            raise Exception(
                f"Une erreur lors de la mise à jour du contrat: {str(e)}")

    @classmethod
    def update_amount(cls, session, contract_id, **kwargs):
        try:
            contract = cls.get_object(session, id=contract_id)
            if not contract:
                raise Exception("Le contrat n'existe pas")

            ContractValidator.validate_amounts(
                kwargs["total_amount"], kwargs["remaining_amount"]
            )
            contract.remaining_amount = kwargs["remaining_amount"]
            if kwargs['total_amount']:
                contract.total_amount = kwargs['total_amount']
            return cls._save_object(session, contract)
        except Exception as e:
            raise Exception(
                f"Une erreur lors de la mise à jour du contrat: {str(e)}")

    @classmethod
    def sign_object(cls, session, contract_id):
        """
        Signe un contrat
        Utilisation : sign_contract(session, contract_id)
        """
        try:
            contract = cls.get_object(session, id=contract_id)
            if not contract:
                raise Exception("Le contrat n'existe pas")

            contract.is_signed = True
            return cls._save_object(session, contract)
        except Exception as e:
            raise Exception(
                f"Une erreur lors de la mise à jour du contrat: {str(e)}")

    @classmethod
    def delete_object(cls, session, contract_id):
        """
        Supprime un contrat
        Utilisation : delete_contract(session, contract_id)
        """
        try:
            contract = Contract.get_object(session, id=contract_id)
            if not contract:
                raise Exception("Le contrat n'existe pas")
            return cls._delete_object(session, contract)
        except Exception as e:
            raise Exception(
                f"Une erreur lors de la suppression du contrat: {str(e)}"
            )

    def format_contract_data(session, contract):
        return {
            "ID du client": contract.client_id,
            "ID du commercial": contract.commercial_id,
            "Somme total à payer": contract.total_amount,
            "Somme restante": contract.remaining_amount,
            "Signé": contract.is_signed,
        }
