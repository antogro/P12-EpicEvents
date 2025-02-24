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
    def validate_required_fields(**kwargs):
        required_fields = ["username", "email", "role", "password"]
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

        if total_amount < 0:
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
    def validate_dates(start_date=None, end_date=None):
        if start_date and end_date:
            start_date = DateTimeUtils.parse_date(start_date)
            end_date = DateTimeUtils.parse_date(end_date)
            if start_date > end_date:
                raise Exception("La date de fin doit être "
                                "supérieure à la date de début")
        if start_date:
            if start_date < datetime.now():
                raise Exception("La date de début doit être dans le futur")
        return start_date, end_date

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


class DateTimeUtils:
    """Utilitaire pour la gestion des dates et heures"""

    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATETIME_CLI_FORMAT = "%Y-%m-%d_%H:%M:%S"

    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """
        Convertit une chaîne de caractères en objet datetime
        Accepte les formats:
        - YYYY-MM-DD
        - YYYY-MM-DD HH:MM:SS
        - YYYY-MM-DD_HH:MM:SS (format CLI)
        """
        formats_to_try = [
            DateTimeUtils.DATETIME_FORMAT,
            DateTimeUtils.DATE_FORMAT,
            DateTimeUtils.DATETIME_CLI_FORMAT
        ]

        for date_format in formats_to_try:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue

        raise ValueError(
            "Format de date invalide. Formats acceptés:\n"
            f"- {DateTimeUtils.DATE_FORMAT} (date simple)\n"
            f"- {DateTimeUtils.DATETIME_FORMAT} (date et heure)\n"
            f"- {DateTimeUtils.DATETIME_CLI_FORMAT} (CLI avec _)"
        )
