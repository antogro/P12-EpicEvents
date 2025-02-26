from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from models.base import BaseModel
from models.contract import Contract
from models.user import User
from models.client import Client
from models.validators import EventValidator, DateTimeUtils


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

            kwargs['start_date'] = DateTimeUtils.parse_date(
                kwargs['start_date'])
            kwargs['end_date'] = DateTimeUtils.parse_date(kwargs['end_date'])

            contract = Contract.get_object(session, id=kwargs['contract_id'])
            if not contract:
                raise Exception("Le contrat n'existe pas.")
            if not contract.is_signed:
                raise Exception("Le contrat n'est pas signé.")

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
    def update_object(cls, session, event_id: int, **kwargs):
        """
        Met à jour un événement en ne modifiant que les champs fournis.
        """
        try:
            event = cls.get_object(session, id=event_id)
            if not event:
                raise Exception("L'événement n'existe pas")

            # Filtrer les champs non None
            updates = {
                key: value for key, value in kwargs.items()
                if value is not None}

            # Validation spécifique
            if 'start_date' in updates or 'end_date' in updates:
                start_date = updates.get('start_date', event.start_date)
                end_date = updates.get('end_date', event.end_date)
                updates['start_date'], updates['end_date'] = [
                    EventValidator.validate_dates(start_date, end_date)
                ]

            if 'attendees' in updates:
                EventValidator.validate_attendees(updates['attendees'])

            if 'support_contact_id' in updates:
                support = User.get_object(
                    session, id=updates['support_contact_id']
                )
                if not support or support.role != 'SUPPORT':
                    raise Exception("Contact support invalide")

            # Mise à jour des attributs valides
            for key, value in updates.items():
                setattr(event, key, value)

            return cls._save_object(session, event)

        except Exception as e:
            raise Exception(f"Une erreur lors de la mise "
                            f"à jour de l'événement: {str(e)}")

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

    def format_event_data(session, event):
        """
        Format les données de l'événement pour la mise en page.
        Gère correctement la conversion des dates datetime en chaînes.
        """
        def format_datetime(dt):
            if isinstance(dt, datetime):
                return dt.strftime(DateTimeUtils.DATETIME_FORMAT)
            return str(dt)
        notes = ''
        if event.notes is not None:
            notes = event.notes or ''

        return {
            'ID de l\'Événement': event.id,
            "ID du support": event.support_contact_id,
            "ID du client": event.client_id,
            "ID du contrat": event.contract_id,
            "Nom de l'événement": event.name,
            "Date de début": format_datetime(event.start_date),
            "Date de fin": format_datetime(event.end_date),
            "Localisation": event.location,
            "Nombre de participants": event.attendees,
            "Créé le": format_datetime(event.created_at),
            "Mise à jour le": format_datetime(event.updated_at),
            "Notes": notes
        }
