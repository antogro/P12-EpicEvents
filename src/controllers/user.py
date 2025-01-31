import typer
from sqlalchemy import create_engine
from typing import Optional
from sqlalchemy.orm import sessionmaker
import os
import sys
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)
from models.user import User, UserRole
from view.display_view import Display


engine = create_engine('sqlite:///./epic_events.db')
Session = sessionmaker(bind=engine)
display = Display()

user_app = typer.Typer(name='Epic Events User Management',
                       help='Application de Gestion des Utilisateurs Epic Event')


def get_session():
    """Récupère une session de la base de données"""
    return Session()


@user_app.command(name="create")
def create(
    username: str = typer.Option(..., help="Nom d'utilisateur"),
    email: str = typer.Option(..., help="Adresse e-mail"),
    password: str = typer.Option(
        ..., help="Mot de passe", prompt=True, hide_input=True),
    role: UserRole = typer.Option(
        ..., help="Rôle d'utilisateur"),
):
    """Crée un utilisateur dans la base de données"""
    try:
        session = get_session()
        user = User.create_object(
            session,
            username=username,
            email=email,
            password=password,
            role=role.value
        )
        typer.secho(
            f"✅ Utilisateur '{user.username}' créé avec succès !",
        )
    except Exception as e:
        typer.secho(f"❌ Erreur lors de la création de l'utilisateur : "
                    f"{str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@user_app.command(name='list')
def user_list(
    user_id: Optional[int] = typer.Option(
        None, help="ID d'un utilisateur spécifique"),
    role: Optional[UserRole] = typer.Option(None, help="Filtrer par rôle")
):
    """
    Lister les utilisateurs
    """
    session = get_session()
    headers = ["ID", "Username", "Email", "Role"]
    try:
        if user_id:
            user = User.get_object(session, id=user_id)
            if user:
                display.table(
                    title="Détails de l'utilisateur:",
                    headers=headers,
                    items=[User.format_user_data(session, user)],

                )

            else:
                typer.secho("❌ Utilisateur non trouvé", fg=typer.colors.RED)
        else:
            users = User.get_all_object(session, User)
            if role:
                users = [user for user in users if user.role == role.value]

            display.table(
                title="Liste des Utilisateurs",
                items=[User.format_user_data(session, user) for user in users],
                headers=headers,
            )
    except Exception as e:
        typer.secho(f"❌ Erreur: {str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@user_app.command(name='delete')
def delete(
        user_id: int = typer.Option(...,
                                    help="ID de l'utilisateur à supprimer"
                                    )):
    typer.confirm("❓Êtes vous sur de vouloir supprimer cet utilisateur ?")
    session = get_session()
    try:
        User.delete_object(session, user_id)
        typer.secho(
            f'✅ Utilisateur {user_id} supprimé avec succès',
            fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"❌ Erreur: {str(e)}", fg=typer.colors.RED)


if __name__ == "__main__":
    user_app()
