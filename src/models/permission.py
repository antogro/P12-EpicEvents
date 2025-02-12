from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from src.models.base import BaseModel


class DynamicPermission(BaseModel):
    """Modèles pour stocker les permissions dynamiques"""

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    __tablename__ = "dynamic_permissions"


class DynamicPermissionRule(BaseModel):
    """Modèles pour stocker les règles de permissions dynamiques"""

    id = Column(Integer, primary_key=True, autoincrement=True)
    permission_id = Column(
        Integer, ForeignKey("dynamic_permissions.id"), nullable=False
    )
    attribute = Column(String(150))
    value = Column(String(150))
    operator = Column(String(50))
    error_message = Column(String(250))

    __tablename__ = "permission_rules"


class PermissionManager:
    """Gestionnaire de permission"""

    @classmethod
    def validate_permission(
        cls, session, user, permission_name, context=None, return_error=False
    ):
        """Vérifie si un utilisateur a une permission sur un objet donné"""
        permission = DynamicPermission.get_object(
            session, name=permission_name)
        if not permission:
            return (False, "Permission non trouvée") if return_error else False

        rules = DynamicPermissionRule.get_object(
            session, permission_id=permission.id
        )
        
        context = context or {}

        if not cls._evaluate_rule(rules, user, context):
            return (False, rules.error_message) if return_error else False

        return (True, None) if return_error else True

    @classmethod
    def _evaluate_rule(cls, rule, user, context):
        """Évalue une règle de permission"""
        actual_value = cls._get_value(rule.attribute, user, context)
        print(actual_value)
        expected_value = rule.value
        print(expected_value)

        if expected_value.startswith("user."):
            expected_value = cls._get_value(expected_value, user, context)

        return cls._apply_operator(rule.operator, actual_value, expected_value)

    @classmethod
    def _get_value(cls, attribute_path, user, context):
        """Récupère la valeur d'un attribut d'un objet donné"""
        if attribute_path.startswith("user."):
            _, attr = attribute_path.split(".")
            return getattr(user, attr, None)
        return context.get(attribute_path)

    @classmethod
    def _apply_operator(cls, operator, actual_value, expected_value):
        """Applique un opérateur de comparaison entre deux valeurs"""
        if operator == "==":
            return actual_value == expected_value
        if operator == "!=":
            return actual_value != expected_value
        if operator == ">":
            return actual_value > expected_value
        if operator == "<":
            return actual_value < expected_value
        if operator == "in":
            return actual_value in expected_value.split(",")
        return False
