from models.user import User
import pytest


def test_create_user(mocker, session, make_user):
    user_fixture = make_user()
    # Mock la méthode get_user pour simuler un utilisateur non existant
    mocker.patch("src.models.base.BaseModel.get_object", return_value=None)
    # Crée l'utilisateur avec les données fournies
    user = User.create_object(session, **user_fixture)
    # Vérifie que l'utilisateur a bien été créé
    assert user.id is not None
    assert user.email == user_fixture["email"]
    assert user.username == user_fixture["username"]
    assert user.role == user_fixture["role"]
    assert User.verify_password(user.password, user_fixture["password"])

    # Vérifie que l'utilisateur est maintenant en base
    # de données via la méthode `get_user`
    retrieved_user = session.query(User).filter_by(email=user.email).first()
    assert retrieved_user.id == user.id


def test_create_user_should_raise_error_with_invalide_role(
    mocker,
    session,
):
    mocker.patch("src.models.base.BaseModel.get_object", return_value=None)
    incomplete_data = {
        "username": "test_user",
        "password": "password",
        "email": "test_user@example.com",
        "role": "COMERCIAL",
    }

    with pytest.raises(Exception) as e:
        User.create_object(session, **incomplete_data)
    assert ("Le rôle doit être l'un des suivants: COMMERCIAL, SUPPORT, GESTION"
            in str(e.value))


def test_create_user_should_raise_error_with_invalide_required_email(
    mocker,
    session,
):
    mocker.patch("src.models.base.BaseModel.get_object", return_value=None)
    incomplete_data = {
        "username": "test_user",
        "password": "password",
        "role": "COMMERCIAL",
    }

    with pytest.raises(Exception) as e:
        User.create_object(session, **incomplete_data)
    assert "Le champ email est requis" in str(e.value)


def test_creat_user_existing_email(mocker, session, make_user):
    user_fixture = make_user()
    mocker.patch(
        "src.models.base.BaseModel.get_object", return_value=make_user)
    with pytest.raises(Exception) as e:
        User.create_object(session, **user_fixture)
    assert "Un utilisateur avec cet email existe déjà" in str(e.value)


def test_hash_password():
    password = "password"
    hashed_password = User.hash_password(password)
    assert hashed_password != password


def test_verify_password():
    password = "password"
    hashed_password = User.hash_password(password)
    assert User.verify_password(hashed_password, password) is True


def test_get_user(mocker, session, make_user):
    user_fixture = make_user()
    expected_user = User(**user_fixture)

    # Prépare le mock pour session.query().filter_by().first()
    mock_query = mocker.Mock()
    mock_filter = mocker.Mock()
    mock_filter.first.return_value = expected_user

    session.query = mocker.Mock(return_value=mock_query)
    mock_query.filter_by = mocker.Mock(return_value=mock_filter)

    # Exécution
    result = User.get_object(session, email=user_fixture["email"])

    # Vérification
    assert result == expected_user
    session.query.assert_called_once_with(User)
    mock_query.filter_by.assert_called_once_with(email=user_fixture["email"])
    mock_filter.first.assert_called_once()


def test_get_user_invalide_data_raise_exception_error(
        mocker,
        session,
        make_user
):
    user_fixture = make_user()
    session.query = Exception("DB Error")
    # Exécution
    with pytest.raises(
        Exception, match="Erreur lors de la récupération:"
    ):
        User.get_object(session, email=user_fixture.email)


def test_delete_user(
        mocker,
        session,
        make_user
):
    # Prépare le mock pour session
    user_fixture = make_user()
    expected_user = User(**user_fixture)
    user_id = 1

    # Crée l'utilisateur avec les données fournies
    mock_get_user = mocker.patch(
        "src.models.user.User.get_object", return_value=expected_user
    )
    mock_session_delete = mocker.patch.object(session, "delete")
    mock_session_commit = mocker.patch.object(session, "commit")
    # Supprime l'utilisateur
    result = User.delete_object(session, user_id)
    # Vérifie que l'utilisateur a été supprimé
    assert result.email == expected_user.email
    assert result.username == expected_user.username
    mock_get_user.assert_called_once_with(session, id=user_id)
    mock_session_delete.assert_called_once_with(expected_user)
    mock_session_commit.assert_called_once()


def test_delete_user_raise_error_with_wrong_user(
        mocker,
        session
):
    user_id = 999
    mocker.patch("src.models.user.User.get_object", return_value="")
    with pytest.raises(Exception) as e:
        User.delete_object(session, user_id)
    assert "L'utilisateur n'existe pas" in str(e.value)


def test_delete_user_raise_exception_error(
        mocker,
        session,
        make_user
):
    user_id = 999
    mocker.patch("src.models.user.User.get_object", return_value=make_user)
    with pytest.raises(Exception) as e:
        User.delete_object(session, user_id)
    assert "Erreur lors de la suppression de l'utilisateur:" in str(e.value)


def test_update_user(
        mocker,
        session,
        make_user
):
    # Prépare le mock pour session.query().filter_by().first()
    user_fixture = make_user()
    initial_user = User(**user_fixture)
    user_id = 1
    update_data = {"email": "test2@example.com", "username": "update_username"}

    # Crée l'utilisateur avec les données fournies
    mock_get_user = mocker.patch(
        "src.models.user.User.get_object", side_effect=[initial_user, None]
    )
    mock_session_commit = mocker.patch.object(session, "commit")

    # Met à jour l'utilisateur
    result = User.update_object(session, user_id, **update_data)

    # Vérifie que l'utilisateur a été mis à jour
    assert result.username == update_data["username"]
    assert mock_get_user.call_count == 2
    mock_session_commit.assert_called_once()

    # Vérifie que la méthode update() a été appelée


def test_update_user_with_no_user(
        mocker,
        session,
):
    user_id = 1
    update_data = {"email": "test2@example.com", "username": "update_username"}
    # Crée l'utilisateur avec les données fournies
    mocker.patch(
        "src.models.user.User.get_object",
        return_value=None
    )
    with pytest.raises(Exception, match="L'utilisateur n'existe pas"):
        User.update_object(session, user_id, **update_data)


def test_update_user_with_existing_email(
        mocker,
        session,
        make_user
):
    initial_user = User(**make_user())
    existing_user = User(**make_user(email='existing@email.fr'))
    user_id = 1
    # Crée l'utilisateur avec les données fournies
    mock_session_rollback = mocker.patch.object(session, 'rollback')
    mock_get_user = mocker.patch(
        "src.models.user.User.get_object", side_effect=[
            initial_user, existing_user
        ]
        )
    with pytest.raises(
        Exception,
        match="Un utilisateur avec cet email existe déjà"
    ):
        User.update_object(session, user_id, email='existing@email.fr')

        mock_session_rollback.assert_called_once()
        assert mock_get_user.call_count == 2


def test_update_user_invalid_field(
        mocker,
        session,
        make_user
):
    """Test la mise à jour avec un champ invalide"""
    # Préparation
    initial_user = User(**make_user())
    mocker.patch('src.models.user.User.get_object', return_value=initial_user)
    mock_session_rollback = mocker.patch.object(session, 'rollback')

    # Mise à jour avec un champ qui n'existe pas
    with pytest.raises(
        Exception,
        match="Erreur lors de la mise à jour de l'utilisateur"
    ):
        result = User.update_object(session, 1, email="email.@email.fr")

        # Vérification que l'utilisateur n'a pas été modifié
        mock_session_rollback.assert_called_once()
        assert result == initial_user
