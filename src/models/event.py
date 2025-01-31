from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from models.base import BaseModel
from models import Contract, User, Client
from models.validators import EventValidator


class Event(BaseModel):
    """
    Modele d'un Event
    args: - id (int),
          - contract_id (int),
          - support_contact_id (int),
          - name (str),
          - start_date (int),
          - end_date (int),
          - location (str),
          - attendees (int),
          - note (str)
    """
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    support_contact_id = Column(Integer, ForeignKey('users.id'))
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    name = Column(String)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(Text)
    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'<Event {self.name}>'

    @classmethod
    def create_object(cls, session, **kwargs):
        """
        Crée un événement
        Utilisation : create_event(
            session,
            name='name',
            support_contact_id='support_contact_id'
            client_id='client_id',
            contract_id='contract_id',
            start_date='start_date',
            end_date='end_date',
            location='location',
            attendees='attendees',
            notes='notes',
        )
        """
        try:
            EventValidator.validate_required_fields(**kwargs)
            EventValidator.validate_dates(
                kwargs['start_date'], kwargs['end_date']
            )
            EventValidator.validate_attendees(kwargs['attendees'])

            kwargs['start_date'] = datetime.strptime(
                kwargs['start_date'], "%Y-%m-%d %H:%M:%S")
            kwargs['end_date'] = datetime.strptime(
                kwargs['end_date'], "%Y-%m-%d %H:%M:%S")

            contrat = Contract.get_object(session, id=kwargs['contract_id'])
            if not contrat:
                raise Exception("Le contrat n'existe pas")

            if 'support_contact_id' in kwargs and kwargs['support_contact_id']:
                support_contact = User.get_object(
                    session, id=kwargs['support_contact_id']
                )
                if not support_contact or support_contact.role != 'SUPPORT':
                    raise ValueError("Le SUPPORT n'existe pas")

            if 'client_id' in kwargs and kwargs['client_id']:
                if not Client.get_object(
                        session, id=kwargs['client_id']):
                    raise ValueError("Le client n'existe pas")

            return cls._save_object(session, cls(**kwargs))
        except Exception as e:
            raise Exception(f"Erreur création événement: {str(e)}")

    @classmethod
    def update_object(cls, session, event_id, **kwargs):
        try:
            event = cls.get_object(session, id=event_id)
            if not event:
                raise Exception("L'événement n'existe pas")

            if 'start_date' in kwargs:
                if isinstance(kwargs['start_date'], str):
                    kwargs['start_date'] = datetime.fromisoformat(
                        kwargs['start_date'])
            if 'end_date' in kwargs:
                if isinstance(kwargs['end_date'], str):
                    kwargs['end_date'] = datetime.fromisoformat(
                        kwargs['end_date'])

            if 'start_date' in kwargs and 'end_date' in kwargs:
                EventValidator.validate_dates(
                    kwargs['start_date'], kwargs['end_date'])
            if 'attendees' in kwargs:
                EventValidator.validate_attendees(kwargs['attendees'])

            if 'support_contact_id' in kwargs:
                support = User.get_object(
                    session, id=kwargs['support_contact_id'])
                if not support or support.role != 'SUPPORT':
                    raise Exception("Contact support invalide")

            for key, value in kwargs.items():
                if hasattr(event, key):
                    setattr(event, key, value)

            return cls._save_object(session, event)
        except Exception as e:
            raise Exception(
                f"Une erreur lors de la mise à jour de l'événement: {str(e)}"
            )

    @classmethod
    def delete_object(cls, session, event_id):
        """
        Supprime un événement
        Utilisation : delete_event(session, event_id)
        """
        try:
            event = cls.get_object(session, id=event_id)
            if not event:
                raise Exception("L'événement n'existe pas")
            return cls._delete_object(session, event)
        except Exception as e:
            raise Exception(
                f"Erreur lors de la suppression de l'événement: {str(e)}"
            )
