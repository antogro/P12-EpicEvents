from src.models.user import User


def test_create_user_with_permission(mocker, session, make_user):
    """Test qu'un utilisateur avec la permission
    peut créer un nouvel utilisateur."""
    admin_fixture = make_user(role="GESTION")
    new_user_fixture = make_user(role="COMMERCIAL")

    admin = User(**admin_fixture)

    mocker.patch("src.models.user.User.get_object", return_value=admin)
    mocker.patch(
        "src.models.permission.PermissionManager.validate_permission",
        return_value=(True, None),
    )

    new_user = User.create_object(session, **new_user_fixture)

    assert new_user.username == new_user_fixture["username"]
    assert new_user.email == new_user_fixture["email"]
    assert new_user.role == new_user_fixture["role"]


def test_get_user(mocker, session, make_user):
    """Test que l'on peut récupérer un utilisateur existant."""
    user_fixture = make_user(role="COMMERCIAL")
    user = User(**user_fixture)

    mocker.patch("src.models.user.User.get_object", return_value=user)

    retrieved_user = User.get_object(session, id=user_fixture["id"])

    assert retrieved_user.username == user_fixture["username"]
    assert retrieved_user.email == user_fixture["email"]


def test_update_user_with_permission(mocker, session, make_user):
    """Test qu'un utilisateur avec la permission
    peut mettre à jour un utilisateur existant.
    """
    admin_fixture = make_user(role="GESTION")
    user_fixture = make_user(role="COMMERCIAL")

    admin = User(**admin_fixture)
    user = User(**user_fixture)

    mocker.patch(
        "src.models.user.User.get_object",
        side_effect=lambda session, id: user
        if id == user_fixture["id"] else admin,
    )
    mocker.patch(
        "src.models.permission.PermissionManager.validate_permission",
        return_value=(True, None),
    )

    updated_user = User.update_object(
        session, user_id=user_fixture["id"], username="NewUsername"
    )

    assert updated_user.username == "NewUsername"


def test_delete_user_with_permission(mocker, session, make_user):
    """Test qu'un utilisateur avec la permission
    peut supprimer un utilisateur."""
    admin_fixture = make_user(role="GESTION")
    user_fixture = make_user(role="COMMERCIAL")

    admin = User(**admin_fixture)
    user = User(**user_fixture)

    mocker.patch(
        "src.models.user.User.get_object",
        side_effect=lambda session, id: user
        if id == user_fixture["id"] else admin,
    )
    mocker.patch(
        "src.models.permission.PermissionManager.validate_permission",
        return_value=(True, None),
    )

    deleted_user = User.delete_object(session, user_id=user_fixture["id"])

    assert deleted_user.id == user_fixture["id"]
