import typer
from sqlalchemy import create_engine
from typing import Optional
from sqlalchemy.orm import sessionmaker
from models.user import User, UserRole
from view.display_view import Display
from sentry_sdk import capture_exception
from models.permission import requires_permission, requires_login


engine = create_engine('sqlite:///./epic_event.db')
Session = sessionmaker(bind=engine)
display = Display()

user_app = typer.Typer(name='Epic Events User Management',
                       help='Application de Gestion '
                            'des Utilisateurs Epic Event')


def get_session():
    """Récupère une session SQLAlchemy active"""
    try:
        session = Session()
        print("⚠️ get_session() appelé")
        print(f"get_session() called in {__name__}")  # ✅ Voir l'import réel
        return session
    except Exception as e:
        typer.secho("❌ Erreur : Impossible d'initialiser "
                    f"la session SQLAlchemy : {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@user_app.command(name="create")
@requires_permission("manage_users")
def create(
    ctx: typer.Context,
    username: str = typer.Option(..., prompt=True, help="Nom d'utilisateur"),
    email: str = typer.Option(..., prompt=True, help="Adresse e-mail"),
    password: str = typer.Option(
        ..., help="Mot de passe", prompt=True, hide_input=True),
    role: UserRole = typer.Option(
        ..., prompt=True, help="Rôle d'utilisateur"),
):
    """Crée un utilisateur dans la base de données"""
    session = get_session()
    try:
        # Vérifie les permissions de l'utilisateur-
        user = User.create_object(
            session,
            username=username.replace("-", " "),
            email=email,
            password=password,
            role=role.value
        )
        typer.secho(f"✅ Utilisateur '{user.username}' créé avec succès !")
    except Exception as e:
        typer.secho(
            f"❌ Erreur lors de la création de l'utilisateur : {str(e)}",
            fg=typer.colors.RED
        )
        raise typer.Exit(code=1)
    finally:
        session.close()


@user_app.command(name='report')
@requires_login()
def user_repport(
    ctx: typer.Context,
    user_id: Optional[int] = typer.Option(
        None, help="ID d'un utilisateur spécifique"),
    role: Optional[UserRole] = typer.Option(None, help="Filtrer par rôle")
):
    """Lister les utilisateurs"""
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
        typer.secho(
                    f"\n ❌ {str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@user_app.command(name='update')
@requires_permission("manage_users")
def user_update(
    ctx: typer.Context,
    id: int = typer.Option(
        ..., prompt=True, help="ID de l'utilisateur à modifier"
    ),
    username: str = typer.Option(None, help="Nom d'utilisateur"),
    email: str = typer.Option(None, help="Adresse email"),
    role: Optional[UserRole] = typer.Option(None, help="Nouveau rôle"),
    password: Optional[str] = typer.Option(None, help="Nouveau mot de passe")
):
    """Mettre à jour les informations d'un utilisateur"""
    session = get_session()
    try:
        # Vérifie les permissions de l'utilisateur

        user = User.update_object(
            session,
            user_id=id,
            username=username,
            email=email,
            role=role,
            password=password
        )
        typer.secho(f"✅ Utilisateur '{user}' mis à jour")
    except Exception as e:
        typer.secho(
                    f"\n ❌ {str(e)}", fg=typer.colors.RED)
    finally:
        session.close()


@user_app.command(name='delete')
@requires_permission("manage_users")
def delete(
    ctx: typer.Context,
    user_id: int = typer.Option(..., help="ID de l'utilisateur à supprimer")
):
    """Supprimer un utilisateur"""
    try:
        # Vérifie les permissions de l'utilisateur

        typer.confirm(
            "❓Êtes-vous sûr de vouloir supprimer cet utilisateur ?",
            abort=True)
        session = get_session()
        User.delete_object(session, user_id)
        typer.secho(
            f'✅ Utilisateur {user_id} supprimé avec succès',
            fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(
                    f"\n ❌ {str(e)}", fg=typer.colors.RED)
        capture_exception(e)
    finally:
        session.close()


if __name__ == "__main__":
    user_app()
