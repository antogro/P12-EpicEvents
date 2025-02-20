import jwt
from datetime import datetime, timedelta, timezone
from src.models.user import User
import os


SECRET_KEY = 'beautifull-amazing-secret-key'


# 1 hour in seconds
TOKEN_EXPIRATION = 3600
TOKEN_FILE = "src/config/token.txt"


class Token:
    def create_token(user):
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION),
            'iat': datetime.utcnow(),
            'sub': f"{user.id}_{user.username}"
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token

    def login(session, username, password):
        user = User.get_object(session, username=username)
        if not user:
            return {'success': False, 'message': 'Utilisateur non trouvé.'}
        if User.verify_password(user.password, password):
            token = Token.create_token(user)
            Token.save_token(token)
            return {
                'success': True,
                'token': token
            }
        return {
            'success': False,
            'message': 'Invalid username or password.'
        }

    def save_token(token: str):
        """Stocke le token JWT dans un fichier"""
        with open(TOKEN_FILE, "w") as file:
            file.write(token)

    def get_stored_token():
        """Récupère le token stocké, s'il existe"""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as file:
                return file.read().strip()
        return None

    def verify_token(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(
                    exp, timezone.utc) < datetime.now(timezone.utc):
                print("⚠️ Token expiré. Veuillez vous reconnecter.")
                Token.clear_stored_token()
                return False
            return payload
        except jwt.ExpiredSignatureError:
            print("⚠️ Token expiré. Veuillez vous reconnecter.")
            Token.clear_stored_token()
            return False
        except jwt.InvalidTokenError:
            print("❌ Token invalide. Veuillez vous reconnecter.")
            Token.clear_stored_token()
            return False

    def clear_stored_token():
        """Supprime le token stocké si invalide ou expiré"""
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)

    def ensure_authenticated():
        """Vérifie que l'utilisateur est authentifié
        avant d'exécuter une commande
        """
        token = Token.get_stored_token()
        if not token:
            print("❌ Accès refusé : vous devez être connecté.")
            exit(1)
        playload = Token.verify_token(token)
        if not playload:
            exit(1)
        return playload['sub']

    def logout():
        Token.clear_stored_token()
        return {
            'success': True,
            'message': 'Déconnexion réussie',
        }

    def is_logged():
        token = Token.get_stored_token()
        if token and Token.verify_token(token):
            return True
