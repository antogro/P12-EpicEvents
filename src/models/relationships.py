from sqlalchemy.orm import relationship


def setup_relationships():
    from models.user import User
    from models.client import Client
    from models.contract import Contract
    from models.event import Event
    from moels.permissions import DynamicPermission, DynamicPermissionRule

    # Relation entre un User et un client
    User.clients = relationship("Client", back_populates="commercial")
    Client.commercial = relationship("User", back_populates="clients")

    # Relation entre un client et un contrat
    Client.contracts = relationship("Contract", back_populates="client")
    Contract.client = relationship("Client", back_populates="contracts")

    # Relation entre un Event et un contrat
    Contract.events = relationship("Event", back_populates="contract")
    Event.contract = relationship("Contract", back_populates="events")

    # Relation entre un Event et un Support
    User.events_support = relationship(
        "Event", back_populates="support_contact"
    )
    Event.support_contact = relationship(
        "User", back_populates="events_support"
    )

    Client.event_id = relationship(
        "Event", back_populates="client_id"
    )
    Event.client_id = relationship(
        "Client", back_populates="event_id"
    )

    DynamicPermission.rules = relationship(
        "DynamicPermissionRule",
        back_populates="permission",
        cascade="all, delete-orphan"
    )

    DynamicPermissionRule.permission = relationship(
        "DynamicPermission",
        back_populates="rules",
    )
