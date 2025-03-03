import jwt
from datetime import datetime, timedelta, timezone
from models.user import User
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


TOKEN_STORAGE_PATH = Path.home() / ".epic_token"
SECRET_KEY = os.getenv("SECRET_KEY", "my_secret_key_is_beautifull")
TOKEN_EXPIRATION = os.getenv("TOKEN_EXPIRATION", 3600)


class Token:
    def create_token(user):
        payload = {
            'exp': datetime.utcnow() + timedelta(
                seconds=int(TOKEN_EXPIRATION)),
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
        """Stocke le token JWT dans un fichier temporaire"""
        with open(TOKEN_STORAGE_PATH, "w") as file:
            file.write(token)

    def get_stored_token():
        """Récupère le token stocké, s'il existe"""
        if TOKEN_STORAGE_PATH.exists():
            with open(TOKEN_STORAGE_PATH, "r") as file:
                return file.read().strip()
        return None

    def verify_token(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            exp_timestamp = payload.get("exp")
            iat_timestamp = payload.get("iat")

            exp_time = datetime.fromtimestamp(
                exp_timestamp, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            iat_time = datetime.fromtimestamp(
                iat_timestamp, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

            if exp_timestamp and datetime.fromtimestamp(
                    exp_timestamp, timezone.utc) < datetime.now(timezone.utc):
                print("⚠️ Token expiré. Veuillez vous reconnecter.")
                Token.clear_stored_token()
                return False

            token_data = {
                "Utilisateur": payload["sub"],
                "Émis le": iat_time,
                "Expire le": exp_time
            }

            return payload, token_data

        except jwt.ExpiredSignatureError:
            print("⚠️ Token expiré. Veuillez vous reconnecter.")
            Token.clear_stored_token()
            return False
        except jwt.InvalidTokenError:
            print("❌ Token invalide. Veuillez vous reconnecter.")
            Token.clear_stored_token()
            return False

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
        if TOKEN_STORAGE_PATH.exists():
            TOKEN_STORAGE_PATH.unlink()

    def ensure_authenticated():
        """Vérifie que l'utilisateur est authentifié
        avant d'exécuter une commande"""
        token = Token.get_stored_token()
        if not token:
            print("❌ Accès refusé : vous devez être connecté.")
            exit(1)

        result = Token.verify_token(token)

        if not result or result is False:
            exit(1)

        payload, _ = result

        return payload['sub']

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
