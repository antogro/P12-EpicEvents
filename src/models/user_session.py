from src.models.authentication import Token
from src.models.user import User


class UserSession:
    """Gestionnaire de session utilisateur"""
    _current_user = None

    @classmethod
    def get_current_user(cls, ctx):
        """Récupère l'utilisateur actuellement
        connecté en utilisant la session de `ctx.obj`
        """
        if cls._current_user is None:
            if not ctx.obj or "session" not in ctx.obj:
                print("❌ Erreur : La session SQLAlchemy n'est "
                      "pas disponible dans le contexte.")
                exit(1)

            session = ctx.obj["session"]  # Récupère la session SQLAlchemy

            token = Token.get_stored_token()
            if token:
                payload = Token.verify_token(token)
                if payload:
                    user_id = payload['sub'].split('_')[0]
                    cls._current_user = User.get_object(
                        session, id=int(user_id))

        return cls._current_user

    @classmethod
    def set_current_user(cls, user):
        """Définit l'utilisateur courant"""
        cls._current_user = user

    @classmethod
    def clear_current_user(cls):
        """Efface l'utilisateur courant"""
        cls._current_user = None
