from src.models.permission import DynamicPermission, DynamicPermissionRule


@staticmethod
def initialize_permission(session):
    """Initialise la permission dans la session"""
    permissions = [
        # Permissions de lecture globales (tous les rôles)
        {"name": "view_clients", "description": "Voir tous les clients"},
        {"name": "view_contracts", "description": "Voir tous les contrats"},
        {"name": "view_events", "description": "Voir tous les événements"},
        # Permissions équipe de gestion
        {
            "name": "manage_users",
            "description": "Gérer les collaborateurs (CRUD)"},
        {
            "name": "manage_all_contracts",
            "description": "Gérer tous les contrats"},
        {
            "name": "assign_support",
            "description": "Assigner un support aux événements",
        },
        {
            "name": "filter_events_support",
            "description": "Filtrer les événements par support",
        },
        # Permissions équipe commerciale
        {"name": "create_clients", "description": "Créer des clients"},
        {
            "name": "update_own_clients",
            "description": "Modifier ses propres clients",
        },
        {
            "name": "update_own_contracts",
            "description": "Modifier les contrats de ses clients",
        },
        {
            "name": "create_events",
            "description": "Créer des événements pour ses clients",
        },
        {
            "name": "filter_contracts_status",
            "description": "Filtrer les contrats par statut",
        },
        # Permissions équipe support
        {
            "name": "update_own_events",
            "description": "Modifier ses propres événements",
        },
        {
            "name": "filter_own_events",
            "description": "Filtrer ses propres événements",
        },
    ]

    for permission_data in permissions:
        existing_permission = DynamicPermission.get_object(
            session, name=permission_data["name"]
        )
        if not existing_permission:
            new_permission = DynamicPermission(**permission_data)
            DynamicPermission._save_object(session, new_permission)


@staticmethod
def initialize_rules(session):
    """Initialise les règles des permissions dans la session"""
    rules = [
        # Règles pour l'équipe de gestion
        {
            "permission_name": "manage_users",
            "attribute": "user.role",
            "operator": "==",
            "value": "GESTION",
            "error_message": "Seule l'équipe de gestion "
            "peut gérer les collaborateurs",
        },
        {
            "permission_name": "manage_all_contracts",
            "attribute": "user.role",
            "operator": "==",
            "value": "GESTION",
            "error_message": "Seule l'équipe de gestion "
            "peut gérer tous les contrats",
        },
        {
            "permission_name": "assign_support",
            "attribute": "user.role",
            "operator": "==",
            "value": "GESTION",
            "error_message": "Seule l'équipe de gestion"
                             " peut assigner un support",
        },
        # Règles pour l'équipe commerciale
        {
            "permission_name": "create_clients",
            "attribute": "user.role",
            "operator": "==",
            "value": "COMMERCIAL",
            "error_message": "Seuls les commerciaux "
                             "peuvent créer des clients",
        },
        {
            "permission_name": "update_own_clients",
            "attribute": "client.commercial_id",
            "operator": "==",
            "value": "user.id",
            "error_message": "Vous ne pouvez modifier "
                             "que vos propres clients",
        },
        {
            "permission_name": "update_own_contracts",
            "attribute": "contract.commercial_id",
            "operator": "==",
            "value": "user.id",
            "error_message": "Vous ne pouvez modifier "
            "que les contrats de vos clients",
        },
        {
            "permission_name": "create_events",
            "attribute": "contract.commercial_id",
            "operator": "==",
            "value": "user.id",
            "error_message": "Vous ne pouvez créer des événements "
            "que pour vos clients",
        },
        # Règles pour l'équipe support
        {
            "permission_name": "update_own_events",
            "attribute": "event.support_contact_id",
            "operator": "==",
            "value": "user.id",
            "error_message": "Vous ne pouvez modifier que les événements "
            "qui vous sont assignés",
        },
    ]

    for rule_data in rules:
        permission = DynamicPermission.get_object(
            session, name=rule_data["permission_name"]
        )
        if permission:
            rule_create_data = {
                "permission_id": permission.id,
                "attribute": rule_data["attribute"],
                "operator": rule_data["operator"],
                "value": rule_data["value"],
                "error_message": rule_data["error_message"],
            }

            existing_rule = DynamicPermissionRule.get_object(
                session,
                permission_id=permission.id,
                attribute=rule_data["attribute"],
            )

            if not existing_rule:
                new_rule = DynamicPermissionRule(**rule_create_data)
                DynamicPermissionRule._save_object(session, new_rule)
