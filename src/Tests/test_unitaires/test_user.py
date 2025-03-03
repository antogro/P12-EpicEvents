from models.user import User


def test_create_user_with_permission(mocker, session, make_user):
    """Test qu'un utilisateur avec la permission
    peut créer un nouvel utilisateur."""
    new_user_fixture = make_user(role="COMMERCIAL")
    mocker.patch("models.user.User.get_object", return_value=None)
    mocker.patch(
        "models.permission.PermissionManager.validate_permission",
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

    mocker.patch("models.user.User.get_object", return_value=user)

    retrieved_user = User.get_object(session, id=user_fixture["id"])

    assert retrieved_user.username == user_fixture["username"]
    assert retrieved_user.email == user_fixture["email"]


def test_update_user_with_permission(mocker, session, make_user):
    """Test qu'un utilisateur avec la permission
    peut mettre à jour un utilisateur existant.
    """
    user_fixture = make_user(role="COMMERCIAL",
                             email="email@testemail.f",
                             id=2)
    mocker.patch(
        "models.permission.PermissionManager.validate_permission",
        return_value=(True, None),
    )
    user = User(**user_fixture)
    mocker.patch("models.user.User.get_object", return_value=user)

    updated_user = User.update_object(
        session, user_id=user_fixture["id"], username="NewUsername"
    )

    assert updated_user.username == "NewUsername"


def test_delete_user_with_permission(mocker, session, make_user):
    """Test qu'un utilisateur avec la permission
    peut supprimer un utilisateur."""
    user_fixture = make_user(role="COMMERCIAL",
                             username="username2",
                             email="email2@testemail.f",
                             id=3)

    user = User(**user_fixture)
    session.add(user)
    session.commit()
    mocker.patch("models.user.User.get_object", return_value=user)

    deleted_user = User.delete_object(session, user_id=user_fixture["id"])

    assert deleted_user.id == user_fixture["id"]
