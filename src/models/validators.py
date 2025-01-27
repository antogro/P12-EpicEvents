from datetime import datetime


class UserValidator:
    @staticmethod
    def validate_role(role):
        valid_roles = ["COMMERCIAL", "SUPPORT", "GESTION"]
        if role not in valid_roles:
            raise Exception(
                f"Le rôle doit être l'un des suivants: "
                f"{', '.join(valid_roles)}"
            )

    @staticmethod
    def validate_required_fields(kwargs, for_creation=False):
        required_fields = ["username", "email", "role", "password"]
        if for_creation:
            required_fields.append("password")

        for field in required_fields:
            if field not in kwargs:
                raise Exception(f"Le champ {field} est requis")
