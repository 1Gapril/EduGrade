from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from backend.app.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.app.models.user import UserRole
from backend.app.schemas.user import UserProvisionCreate, UserUpdate
from backend.app.services.user_service import (
    AdministratorService,
    StudentService,
    TeacherService,
    UserService,
)


def _data(**values):
    return SimpleNamespace(
        model_dump=lambda **_kwargs: values.copy(),
        **values,
    )


def test_user_service_create_checks_conflicts_and_logs_audit():
    db = MagicMock()
    service = UserService(db)
    service.user_repo = MagicMock()
    service.audit_repo = MagicMock()
    data = _data(
        email="student@example.test",
        username="student",
        full_name="A Student",
        password="secure-password",
        role="student",
    )
    service.user_repo.get_by_email.return_value = None
    service.user_repo.get_by_username.return_value = None

    with patch("backend.app.services.user_service.get_password_hash", return_value="hashed"):
        user = service.create_user(data, uuid4())

    assert user.hashed_password == "hashed"
    assert user.role == UserRole.STUDENT
    db.add.assert_called_once_with(user)
    service.audit_repo.log.assert_called_once()

    service.user_repo.get_by_email.return_value = user
    with pytest.raises(ConflictError, match="Email já cadastrado"):
        service.create_user(data, uuid4())

    service.user_repo.get_by_email.return_value = None
    service.user_repo.get_by_username.return_value = user
    with pytest.raises(ConflictError, match="Username já cadastrado"):
        service.create_user(data, uuid4())


def test_user_service_update_delete_search_and_not_found():
    service = UserService(MagicMock())
    service.user_repo = MagicMock()
    service.audit_repo = MagicMock()
    user = SimpleNamespace(
        id=uuid4(),
        email="old@example.test",
        username="old",
        full_name="Old Name",
        is_active=True,
        role=UserRole.STUDENT,
    )
    service.user_repo.get.return_value = user

    updated = service.update_user(
        user.id,
        UserUpdate(full_name="New Name"),
        uuid4(),
    )
    assert updated.full_name == "New Name"
    assert updated.updated_at is not None
    service.audit_repo.log.assert_called_once()

    assert service.delete_user(user.id, uuid4())
    assert user.is_active is False
    assert service.list_users(role=UserRole.STUDENT, active_only=True) == (
        service.user_repo.get_all.return_value
    )
    service.user_repo.get_all.assert_called_with(
        skip=0,
        limit=100,
        filters={"role": UserRole.STUDENT, "is_active": True},
    )
    assert service.list_users(active_only=False) == service.user_repo.get_all.return_value
    assert service.search_users("student", UserRole.STUDENT) == service.user_repo.search.return_value

    service.user_repo.get_by_email.return_value = SimpleNamespace()
    with pytest.raises(ConflictError, match="Email já cadastrado"):
        service.update_user(user.id, UserUpdate(email="other@example.com"), uuid4())
    service.user_repo.get_by_email.return_value = None
    service.user_repo.get_by_username.return_value = SimpleNamespace()
    with pytest.raises(ConflictError, match="Username já cadastrado"):
        service.update_user(user.id, UserUpdate(username="other"), uuid4())
    service.user_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Usuário não encontrado"):
        service.get_user(uuid4())


def test_student_service_validates_profile_and_updates():
    db = MagicMock()
    service = StudentService(db)
    service.student_repo = MagicMock()
    service.user_repo = MagicMock()
    service.audit_repo = MagicMock()
    user_id = uuid4()
    data = _data(
        user_id=user_id,
        ra="RA-1",
        registration_number="MAT-1",
        course_id=uuid4(),
        class_id=None,
    )
    student_user = SimpleNamespace(role=UserRole.STUDENT)
    service.user_repo.get.return_value = student_user
    service.student_repo.get_by_ra.return_value = None
    service.student_repo.get_by_registration_number.return_value = None
    service.student_repo.get_by_user_id.return_value = None

    student = service.create_student(data, uuid4())
    assert student.ra == "RA-1"
    assert student.registration_number == "MAT-1"
    service.student_repo.get.return_value = student
    assert service.get_student(student.id) is student
    assert service.get_student_by_user(user_id) == service.student_repo.get_by_user_id.return_value
    updated = service.update_student(student.id, _data(status="inactive"), uuid4())
    assert updated.status == "inactive"
    service.audit_repo.log.assert_called()
    service.student_repo.get_by_registration_number.return_value = SimpleNamespace()
    with pytest.raises(ConflictError, match="Matrícula institucional já cadastrada"):
        service.update_student(
            student.id,
            _data(registration_number="MAT-2"),
            uuid4(),
        )
    service.student_repo.get_by_registration_number.return_value = None
    service.student_repo.get_by_ra.return_value = SimpleNamespace()
    with pytest.raises(ConflictError, match="RA já cadastrado"):
        service.update_student(student.id, _data(ra="RA-2"), uuid4())

    service.user_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Usuário não encontrado"):
        service.create_student(data, uuid4())
    service.user_repo.get.return_value = SimpleNamespace(role=UserRole.TEACHER)
    with pytest.raises(ValidationError, match="role de aluno"):
        service.create_student(data, uuid4())
    service.user_repo.get.return_value = student_user
    service.student_repo.get_by_ra.return_value = student
    with pytest.raises(ConflictError, match="RA já cadastrado"):
        service.create_student(data, uuid4())
    service.student_repo.get_by_ra.return_value = None
    service.student_repo.get_by_registration_number.return_value = student
    with pytest.raises(ConflictError, match="Matrícula institucional já cadastrada"):
        service.create_student(data, uuid4())
    service.student_repo.get_by_registration_number.return_value = None
    service.student_repo.get_by_user_id.return_value = student
    with pytest.raises(ConflictError, match="perfil de aluno"):
        service.create_student(data, uuid4())
    service.student_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Aluno não encontrado"):
        service.get_student(uuid4())


def test_student_provision_requires_institutional_registration_number():
    user = {
        "email": "student@example.org",
        "username": "student",
        "full_name": "A Student",
        "password": "secure-initial-password",
        "role": "student",
    }

    with pytest.raises(ValueError, match="Matrícula institucional obrigatória"):
        UserProvisionCreate(user=user, student_ra="RA-1")

    data = UserProvisionCreate(
        user=user,
        student_ra="RA-1",
        student_registration_number="MAT-1",
    )
    assert data.student_registration_number == "MAT-1"


def test_teacher_service_validates_profile_and_updates():
    db = MagicMock()
    service = TeacherService(db)
    service.teacher_repo = MagicMock()
    service.user_repo = MagicMock()
    service.audit_repo = MagicMock()
    user_id = uuid4()
    data = _data(user_id=user_id, employee_id="EMP-1", department="Science")
    teacher_user = SimpleNamespace(role=UserRole.TEACHER)
    service.user_repo.get.return_value = teacher_user
    service.teacher_repo.get_by_employee_id.return_value = None
    service.teacher_repo.get_by_user_id.return_value = None

    teacher = service.create_teacher(data, uuid4())
    assert teacher.employee_id == "EMP-1"
    service.teacher_repo.get.return_value = teacher
    assert service.get_teacher(teacher.id) is teacher
    service.teacher_repo.get_by_user_id.return_value = teacher
    assert service.get_teacher_by_user(user_id) is teacher
    updated = service.update_teacher(teacher.id, _data(department="Math"), uuid4())
    assert updated.department == "Math"
    service.audit_repo.log.assert_called()
    service.teacher_repo.get_by_employee_id.return_value = SimpleNamespace()
    with pytest.raises(ConflictError, match="ID do funcionário já cadastrado"):
        service.update_teacher(
            teacher.id,
            _data(employee_id="EMP-OTHER"),
            uuid4(),
        )

    service.user_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Usuário não encontrado"):
        service.create_teacher(data, uuid4())
    service.user_repo.get.return_value = SimpleNamespace(role=UserRole.STUDENT)
    with pytest.raises(ValidationError, match="role de professor"):
        service.create_teacher(data, uuid4())
    service.user_repo.get.return_value = teacher_user
    service.teacher_repo.get_by_employee_id.return_value = teacher
    with pytest.raises(ConflictError, match="ID do funcionário"):
        service.create_teacher(data, uuid4())
    service.teacher_repo.get_by_employee_id.return_value = None
    service.teacher_repo.get_by_user_id.return_value = teacher
    with pytest.raises(ConflictError, match="perfil de professor"):
        service.create_teacher(data, uuid4())
    service.teacher_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Professor não encontrado"):
        service.get_teacher(uuid4())


def test_administrator_service_validates_profile_and_updates():
    db = MagicMock()
    service = AdministratorService(db)
    service.admin_repo = MagicMock()
    service.user_repo = MagicMock()
    service.audit_repo = MagicMock()
    user_id = uuid4()
    data = _data(
        user_id=user_id,
        employee_id="ADMIN-1",
        department="IT",
        permissions="full",
    )
    admin_user = SimpleNamespace(role=UserRole.ADMIN)
    service.user_repo.get.return_value = admin_user
    service.admin_repo.get_by_employee_id.return_value = None
    service.admin_repo.get_by_user_id.return_value = None

    admin = service.create_administrator(data, uuid4())
    assert admin.employee_id == "ADMIN-1"
    service.admin_repo.get.return_value = admin
    assert service.get_administrator(admin.id) is admin
    service.admin_repo.get_by_user_id.return_value = admin
    assert service.get_administrator_by_user(user_id) is admin
    updated = service.update_administrator(admin.id, _data(department="Operations"), uuid4())
    assert updated.department == "Operations"
    service.audit_repo.log.assert_called()

    service.user_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Usuário não encontrado"):
        service.create_administrator(data, uuid4())
    service.user_repo.get.return_value = SimpleNamespace(role=UserRole.TEACHER)
    with pytest.raises(ValidationError, match="role de administrador"):
        service.create_administrator(data, uuid4())
    service.user_repo.get.return_value = admin_user
    service.admin_repo.get_by_employee_id.return_value = admin
    with pytest.raises(ConflictError, match="ID do funcionário"):
        service.create_administrator(data, uuid4())
    service.admin_repo.get_by_employee_id.return_value = None
    service.admin_repo.get_by_user_id.return_value = admin
    with pytest.raises(ConflictError, match="perfil de administrador"):
        service.create_administrator(data, uuid4())
    service.admin_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Administrador não encontrado"):
        service.get_administrator(uuid4())
