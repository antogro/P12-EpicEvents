from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Text
)
from models.base import BaseModel


class DynamicPermission(BaseModel):
    """Modèles pour stocker les permissions dynamiques"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )
    category = Column(String(50))
    is_active = Column(Boolean, default=True)

    __tablename__ = 'dynamic_permissions'


class DynamicPermissionRule(BaseModel):
    """Modèles pour stocker les règles de permissions dynamiques"""
    id = Column(Integer, primary_key=True, autoincrement=True)
    permission_id = Column(
        Integer,
        ForeignKey('dynamic_permissions.id'),
        nullable=False
    )
    attribute = Column(String(150))
    value = Column(String(150))
    operator = Column(String(50))
    error_message = Column(String(250))

    __tablename__ = 'permission_rules'
