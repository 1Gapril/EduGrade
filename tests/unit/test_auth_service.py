from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from backend.app.core.exceptions import AuthenticationError, ValidationError
from backend.app.models.user import UserRole
from backend.app.services.auth_service import AuthService, PermissionService


def _service(user=None):
    service = AuthService(MagicMock())
    service.user_repo = MagicMock()
    service.user_repo.get_by_email_or_username.return_value = user
    return service


def test_authenticate_rejects_unknown_or_inactive_users():
    service = _service()
    with pytest.raises(AuthenticationError, match="Credenciais inválidas"):
        service.authenticate(SimpleNamespace(username="missing", password="secret"))

    inactive = SimpleNamespace(is_active=False)
    service = _service(inactive)
    with pytest.raises(AuthenticationError, match="Usuário inativo"):
        service.authenticate(SimpleNamespace(username="inactive", password="secret"))


def test_authenticate_rejects_wrong_password_and_records_attempt():
    user = SimpleNamespace(id=uuid4(), is_active=True, hashed_password="hash")
    service = _service(user)
    with (
        patch("backend.app.services.auth_service.verify_password", return_value=False),
        pytest.raises(AuthenticationError, match="Credenciais inválidas"),
    ):
        service.authenticate(SimpleNamespace(username="teacher", password="wrong"))

    service.db.flush.assert_called_once()


def test_authenticate_updates_last_login_and_returns_tokens():
    user = SimpleNamespace(
        id=uuid4(),
        email="teacher@example.test",
        is_active=True,
        hashed_password="hash",
        role=UserRole.TEACHER,
    )
    service = _service(user)
    expected = object()
    service._create_token_response = MagicMock(return_value=expected)
    with patch("backend.app.services.auth_service.verify_password", return_value=True):
        result = service.authenticate(SimpleNamespace(username="teacher", password="secret"))

    assert result is expected
    assert user.last_login is not None
    assert service.db.flush.call_count == 2


def test_refresh_token_validates_type_and_active_user():
    service = _service()
    user = SimpleNamespace(is_active=True)
    service.user_repo.get.return_value = user
    service._create_token_response = MagicMock(return_value="tokens")
    payload = SimpleNamespace(type="refresh", user_id=str(uuid4()))
    with patch("backend.app.services.auth_service.decode_token", return_value=payload):
        assert service.refresh_token("refresh") == "tokens"

    with (
        patch(
            "backend.app.services.auth_service.decode_token",
            return_value=SimpleNamespace(type="access", user_id=str(uuid4())),
        ),
        pytest.raises(AuthenticationError, match="Refresh token inválido"),
    ):
        service.refresh_token("access")


def test_refresh_token_rejects_unknown_user():
    service = _service()
    service.user_repo.get.return_value = None
    with (
        patch(
            "backend.app.services.auth_service.decode_token",
            return_value=SimpleNamespace(type="refresh", user_id=str(uuid4())),
        ),
        pytest.raises(AuthenticationError, match="Usuário não encontrado"),
    ):
        service.refresh_token("refresh")


def test_change_password_validates_user_and_current_password():
    service = _service()
    service.user_repo.get.return_value = None
    with pytest.raises(ValidationError, match="Usuário não encontrado"):
        service.change_password(uuid4(), "old", "new-password")

    user = SimpleNamespace(hashed_password="hash", email="person@example.test", id=uuid4())
    service.user_repo.get.return_value = user
    with (
        patch("backend.app.services.auth_service.verify_password", return_value=False),
        pytest.raises(AuthenticationError, match="Senha atual incorreta"),
    ):
        service.change_password(user.id, "wrong", "new-password")


def test_change_password_updates_hash():
    user = SimpleNamespace(hashed_password="old-hash", email="person@example.test", id=uuid4())
    service = _service()
    service.user_repo.get.return_value = user
    with (
        patch("backend.app.services.auth_service.verify_password", return_value=True),
        patch("backend.app.services.auth_service.get_password_hash", return_value="new-hash"),
    ):
        assert service.change_password(user.id, "old-password", "new-password")

    assert user.hashed_password == "new-hash"
    assert service.db.flush.call_count == 2


def test_validate_token_delegates_to_decoder():
    service = _service()
    payload = object()
    with patch("backend.app.services.auth_service.decode_token", return_value=payload) as decode:
        assert service.validate_token("token") is payload
    decode.assert_called_once_with("token")


@pytest.mark.parametrize(
    ("role", "profile_method", "profile", "expected"),
    [
        (UserRole.ADMIN, None, None, True),
        (UserRole.TEACHER, "get_teacher_profile", SimpleNamespace(id=uuid4()), True),
        (UserRole.TEACHER, "get_teacher_profile", None, False),
        (UserRole.STUDENT, "get_student_profile", SimpleNamespace(id=uuid4()), True),
        (UserRole.STUDENT, "get_student_profile", None, False),
    ],
)
def test_permission_service_class_access(role, profile_method, profile, expected):
    service = PermissionService(MagicMock())
    if profile_method:
        repo = service.teacher_repo if role == UserRole.TEACHER else service.student_repo
        if role == UserRole.TEACHER:
            service.teacher_repo = repo = MagicMock()
        else:
            service.student_repo = repo = MagicMock()
        repo.get_by_user_id.return_value = profile
    if role == UserRole.TEACHER and profile:
        with patch("backend.app.repositories.academic_repository.ClassRepository") as repo_type:
            repo_type.return_value.get.return_value = SimpleNamespace(teacher_id=profile.id)
            assert service.can_access_class(SimpleNamespace(role=role, id=uuid4()), uuid4()) is expected
    elif role == UserRole.STUDENT and profile:
        enrollment = SimpleNamespace(status=SimpleNamespace(value="active"))
        with patch("backend.app.repositories.academic_repository.EnrollmentRepository") as repo_type:
            repo_type.return_value.get_by_student_class.return_value = enrollment
            assert service.can_access_class(SimpleNamespace(role=role, id=uuid4()), uuid4()) is expected
    else:
        assert service.can_access_class(SimpleNamespace(role=role, id=uuid4()), uuid4()) is expected
