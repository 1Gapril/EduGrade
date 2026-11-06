from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.repositories.academic_repository import TeacherSubjectRepository
from backend.app.schemas.academic import TeacherSubjectCreate
from backend.app.services.academic_service import TeacherSubjectService


def test_create_teacher_subject_duplicate_raises_conflict():
    service = TeacherSubjectService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_by_teacher_subject.return_value = object()

    data = SimpleNamespace(
        teacher_id=uuid4(),
        subject_id=uuid4(),
        academic_period_id=None,
        is_coordinator=False,
    )

    with pytest.raises(ConflictError, match="Associação já existe"):
        service.create(data)
    service.repo.get_by_teacher_subject.assert_called_once_with(
        data.teacher_id,
        data.subject_id,
        data.academic_period_id,
    )


def test_create_teacher_subject_passes_academic_period_to_duplicate_lookup():
    db = MagicMock()
    service = TeacherSubjectService(db)
    service.repo = MagicMock()
    service.repo.get_by_teacher_subject.return_value = None
    period_id = uuid4()
    data = TeacherSubjectCreate(
        teacher_id=uuid4(),
        subject_id=uuid4(),
        academic_period_id=period_id,
    )

    association = service.create(data)

    assert association.academic_period_id == period_id
    service.repo.get_by_teacher_subject.assert_called_once_with(
        data.teacher_id,
        data.subject_id,
        period_id,
    )
    db.add.assert_called_once_with(association)
    db.flush.assert_called_once()


def test_teacher_subject_service_update_and_delete():
    db = MagicMock()
    service = TeacherSubjectService(db)
    association = SimpleNamespace(id=uuid4(), is_coordinator=False)
    service.repo = MagicMock()
    service.repo.get.return_value = association

    updated = service.update(association.id, is_coordinator=True)
    assert updated.is_coordinator is True
    db.flush.assert_called_once()

    service.delete(association.id)
    db.delete.assert_called_once_with(association)


def test_teacher_subject_service_list_by_teacher():
    service = TeacherSubjectService(MagicMock())
    teacher_id = uuid4()
    expected = [SimpleNamespace(id=uuid4(), teacher_id=teacher_id)]
    service.repo = MagicMock()
    service.repo.get_by_teacher.return_value = expected

    assert service.list_by_teacher(teacher_id) == expected


def test_teacher_subject_service_get_not_found():
    service = TeacherSubjectService(MagicMock())
    service.repo = MagicMock()
    service.repo.get.return_value = None

    with pytest.raises(NotFoundError, match="Associação professor-disciplina não encontrada"):
        service.get(uuid4())


@pytest.mark.parametrize(
    ("period_id", "expected_clause"),
    [(None, "academic_period_id IS NULL"), (uuid4(), "academic_period_id =")],
)
def test_teacher_subject_duplicate_lookup_is_period_specific(period_id, expected_clause):
    db = MagicMock()
    repository = TeacherSubjectRepository(db)
    db.execute.return_value.scalar_one_or_none.return_value = None

    repository.get_by_teacher_subject(uuid4(), uuid4(), period_id)

    statement = str(db.execute.call_args.args[0])
    assert expected_clause in statement
