from src.models.permission import DynamicPermission, DynamicPermissionRule


class PermissionRule:
    @staticmethod
    def initialize_permission(session):
        """Initialise toutes les permissions dans la session"""
        permissions = [
            # Permissions de lecture globales (tous les rôles)
            {
                "name": "view_reports",
                "description": "Voir tous les rapports"
            },
            # Permissions équipe de gestion
            {
                "name": "manage_users",
                "description": "Gérer les collaborateurs (CRUD)"
            },
            {
                "name": "manage_all_contracts",
                "description": "Gérer tous les contrats"
            },
            {
                "name": "view_unassigned_events",
                "description": "Voir les événements sans support assigné",
            },
            {
                "name": "assign_support",
                "description": "Assigner un support aux événements",
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
                "name": "view_filtered_contracts",
                "description":
                    "Filtrer les contrats par statut (non signés/non payés)",
            },
            {
                "name": "create_event",
                "description":
                    "Créer des événements pour les clients avec contrat signé",
            },
            # Permissions équipe support
            {
                "name": "view_own_events",
                "description": "Voir ses propres événements assignés",
            },
            {
                "name": "update_own_events",
                "description": "Modifier ses propres événements",
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
        """Initialise les règles de permissions dans la session"""
        rules = [
            # Règles pour l'équipe de gestion
            {
                "permission_name": "manage_users",
                "attribute": "user.role",
                "operator": "==",
                "value": "GESTION",
                "error_message":
                    "Seule l'équipe de gestion peut gérer les collaborateurs",
            },
            {
                "permission_name": "manage_all_contracts",
                "attribute": "user.role",
                "operator": "==",
                "value": "GESTION",
                "error_message":
                    "Seule l'équipe de gestion peut gérer tous les contrats",
            },
            {
                "permission_name": "view_unassigned_events",
                "attribute": "user.role",
                "operator": "==",
                "value": "GESTION",
                "error_message":
                    "Seule l'équipe de gestion peut "
                    "voir les événements non assignés",
            },
            {
                "permission_name": "assign_support",
                "attribute": "user.role",
                "operator": "==",
                "value": "GESTION",
                "error_message":
                    "Seule l'équipe de gestion peut assigner un support",
            },
            # Règles pour l'équipe commerciale
            {
                "permission_name": "create_clients",
                "attribute": "user.role",
                "operator": "==",
                "value": "COMMERCIAL",
                "error_message":
                    "Seuls les commerciaux peuvent créer des clients",
            },
            {
                "permission_name": "update_own_clients",
                "attribute": "client.commercial_id",
                "operator": "==",
                "value": "user.id",
                "error_message":
                    "Vous ne pouvez modifier que vos propres clients",
            },
            {
                "permission_name": "update_own_contracts",
                "attribute": "contract.commercial_id",
                "operator": "==",
                "value": "user.id",
                "error_message":
                    "Vous ne pouvez modifier que les contrats de vos clients",
            },
            # Règles pour l'équipe support

            {
                "permission_name": "update_own_events",
                "attribute": "event.support_contact_id",
                "operator": "==",
                "value": "user.id",
                "error_message":
                    "Vous ne pouvez modifier que les "
                    "événements qui vous sont assignés",
            },
            {
                "permission_name": "create_event",
                "attribute": "user.role",
                "operator": "==",
                "value": "COMMERCIAL",
                "error_message":
                    "Seul un commercial peut créer un "
                    "événement pour un contrat dument signé.",
            },
            # Un commercial peut créer un événement UNIQUEMENT pour ses
            # propres clients avec un contrat signé
            {
                "permission_name": "create_event",
                "attribute": "contract.commercial_id",
                "operator": "==",
                "value": "user.id",
                "error_message": "Vous ne pouvez créer des événements"
                " que pour vos propres clients ayant un contrat signé.",
            },
            {
                "permission_name": "create_event",
                "attribute": "contract.is_signed",
                "operator": "==",
                "value": "True",
                "error_message": "Vous ne pouvez créer un événement"
                " que si le contrat est signé.",
            },
            {
                "permission_name": "view_reports",
                "attribute": "user.id",
                "operator": "!=",
                "value": "None",
                "error_message":
                    "Vous devez être connecté pour voir les rapports."
            }

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
