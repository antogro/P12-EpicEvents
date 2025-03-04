from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from src.models.base import BaseModel
from src.models.user_session import UserSession
from src.models.contract import Contract
from src.models.client import Client
import typer
from functools import wraps


class DynamicPermission(BaseModel):
    """Modèle des permissions dynamiques"""

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    __tablename__ = "dynamic_permissions"
    __table_args__ = {"extend_existing": True}


class DynamicPermissionRule(BaseModel):
    """Modèle des règles de permissions"""

    id = Column(Integer, primary_key=True, autoincrement=True)
    permission_id = Column(
        Integer, ForeignKey("dynamic_permissions.id"), nullable=False
    )
    attribute = Column(String(150))
    value = Column(String(150))
    operator = Column(String(50))
    error_message = Column(String(250))

    __tablename__ = "permission_rules"
    __table_args__ = {"extend_existing": True}


class PermissionManager:
    """Gestionnaire des permissions dynamiques"""

    @classmethod
    def validate_permission(
        cls, session, user, permission_name, context=None, return_error=False
    ):
        """Vérifie si un utilisateur a une permission spécifique."""
        permission = DynamicPermission.get_object(
            session, name=permission_name)
        if not permission:
            return (False, "Permission non trouvée") if return_error else False

        rules = DynamicPermissionRule.get_all_object(
            session, permission_id=permission.id
        )
        context = context or {}

        errors = []

        for rule in rules:
            actual_value = cls._get_value(rule.attribute, user, context)
            expected_value = cls._get_value(rule.value, user, context)

            if cls._apply_operator(
                    rule.operator, actual_value, expected_value):
                return (True, None)

            errors.append(rule.error_message)

        return (
            (False, errors[0])
            if return_error and errors
            else (False, "Permission refusée")
        )

    @classmethod
    def _get_value(cls, attribute_path, user, context):
        """Récupère une valeur d'un objet en fonction du chemin"""

        if not attribute_path or attribute_path == "None":
            return None
        session = context.get("session")
        if attribute_path.startswith("user."):
            value = getattr(user, attribute_path.split(".")[1], None)
            return value if value is not None else ""
        if "." not in attribute_path:
            return attribute_path
        obj_type, attr = attribute_path.split(".")
        obj = context.get(obj_type)
        if isinstance(obj, int) and session:
            obj = cls._get_object_by_type(session, obj_type, obj)
        return getattr(obj, attr, attribute_path) if obj else attribute_path

    @classmethod
    def _get_object_by_type(cls, session, obj_type, obj_id):
        """Récupère un objet en fonction de son type"""
        if obj_type == "contract":
            return Contract.get_object(session, id=obj_id)
        if obj_type == "client":
            return Client.get_object(session, id=obj_id)
        return None

    @classmethod
    def _apply_operator(cls, operator, actual_value, expected_value):
        """Applique un opérateur de comparaison entre deux valeurs"""
        operations = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            "in": lambda a, b: a in b.split(",") if
            isinstance(b, str) else False,
        }
        return operations.get(operator, lambda a, b: False)(
            actual_value, expected_value
        )

    # @classmethod
    # def check_user_permission(cls, ctx: typer.Context, permission_name: str):
    #     """Vérifie si l'utilisateur actuel a la permission spécifiée"""
    #     session = ctx.obj.get("session") if ctx.obj else None
    #     if not session:
    #         typer.secho(
    #             "❌ Erreur : Session SQLAlchemy non disponible.",
    #             fg=typer.colors.RED
    #         )
    #         exit(1)

    #     current_user = UserSession.get_current_user(ctx)
    #     if not current_user:
    #         typer.secho("❌ Vous devez être connecté.", fg=typer.colors.RED)
    #         exit(1)
    #     has_permission, error_message = cls.validate_permission(
    #         session, current_user, permission_name, return_error=True
    #     )
    #     if not has_permission:
    #         typer.secho(f"❌ {error_message}", fg=typer.colors.RED)
    #         exit(1)

    #     return True


def requires_login():
    """
    Vérifie qu'un utilisateur est connecté avant d'accéder à une commande.
    Utilise la permission `view_reports` définie dans `permission_rules.py`.
    """
    return requires_permission("view_reports")


def requires_permission(*permission_names):
    """
    Vérifie qu'un utilisateur possède AU MOINS UNE des permissions.
    Affiche uniquement l'erreur qui lui est directement liée.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(ctx: typer.Context, *args, **kwargs):
            session = ctx.obj.get("session") if ctx.obj else None
            if not session:
                typer.secho(
                    "❌ Erreur : Session SQLAlchemy non initialisée.",
                    fg=typer.colors.RED,
                )
                exit(1)

            user = UserSession.get_current_user(ctx)
            if not user:
                typer.secho(
                    "❌ Vous devez être connecté.", fg=typer.colors.RED)
                exit(1)

            contract_id = kwargs.get("contract_id")
            client_id = kwargs.get("id")

            contract = (
                Contract.get_object(session, id=contract_id)
                if contract_id
                else None
            )
            client = Client.get_object(
                session, id=client_id) if client_id else None

            context = {
                "contract": contract, "client": client,
                "session": session, "contract_id": contract_id,
                "client_id": client_id,
            }

            for perm in permission_names:
                has_permission, error_message = (
                    PermissionManager.validate_permission(
                        session,
                        user,
                        perm,
                        context=context,
                        return_error=True
                    )
                )

                if has_permission:
                    return func(ctx, *args, **kwargs)

            typer.secho(f"❌ {error_message}", fg=typer.colors.RED)
            exit(1)

        return wrapper

    return decorator
