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


class ContractValidator:
    @staticmethod
    def validate_required_fields(**kwargs):
        required_fields = [
            "client_id",
            "commercial_id",
            "total_amount",
            "remaining_amount",
        ]
        for field in required_fields:
            if field not in kwargs:
                raise Exception(f"Le champ {field} est requis")

    @staticmethod
    def validate_amounts(total_amount=None, remaining_amount=None):
        if remaining_amount:
            if remaining_amount < 0:
                raise Exception("Les montants ne peuvent pas être négatifs")
        else:
            if remaining_amount < 0 or total_amount < 0:
                raise Exception("Les montants ne peuvent pas être négatifs")
            if remaining_amount > total_amount:
                raise Exception(
                    "Le montant restant ne peut pas être "
                    "supérieur au montant total"
                )


class EventValidator:
    @staticmethod
    def validate_required_fields(**kwargs):
        required_fields = [
            "contract_id",
            "client_id",
            "support_contact_id",
            "name",
            "start_date",
            "end_date",
            "location",
            "attendees",
        ]
        for field in required_fields:
            if field not in kwargs:
                raise Exception(f"Le champ {field} est requis")

    @staticmethod
    def validate_dates(start_date, end_date):
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        if start_date > end_date:
            raise Exception("La date de fin doit être "
                            "supérieure à la date de début")
        if start_date < datetime.now():
            raise Exception("La date de début doit être dans le futur")

    @staticmethod
    def validate_attendees(attendees):
        if attendees <= 0:
            raise Exception("Le nombre de participants doit être positif")


class ClientValidator:
    @staticmethod
    def validate_required_fields(**kwargs):
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "company_name",
            "commercial_id",
        ]
        for field in required_fields:
            if field not in kwargs:
                raise Exception(f"Le champ {field} est requis")

    @staticmethod
    def validate_email(email):
        if "@" not in email:
            raise Exception("L'email doit être valide")
