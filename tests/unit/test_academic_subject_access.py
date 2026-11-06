from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from backend.app.api.routes.academic import (
    _assert_class_access,
    get_subject,
    list_classes,
    require_class_permission,
)
from backend.app.models.user import UserRole
from backend.app.schemas.common import PaginationParams


def test_teacher_cannot_get_unassigned_subject():
    class QueryStub:
        def filter(self, *conditions):
            return self

        def first(self):
            return None

    class DatabaseStub:
        def query(self, *models):
            return QueryStub()

    user = SimpleNamespace(
        role=UserRole.TEACHER,
        teacher_profile=SimpleNamespace(id=uuid4()),
    )

    with pytest.raises(HTTPException) as error:
        get_subject(uuid4(), current_user=user, db=DatabaseStub())

    assert error.value.status_code == 403


def test_teacher_cannot_access_class_without_matching_subject_assignment():
    class QueryStub:
        def filter(self, *conditions):
            return self

        def first(self):
            return None

    class DatabaseStub:
        def query(self, *models):
            return QueryStub()

    teacher_id = uuid4()
    user = SimpleNamespace(
        role=UserRole.TEACHER,
        teacher_profile=SimpleNamespace(id=teacher_id),
    )
    class_record = SimpleNamespace(
        id=uuid4(),
        teacher_id=teacher_id,
        subject_id=uuid4(),
        academic_period_id=uuid4(),
    )

    with pytest.raises(HTTPException) as error:
        _assert_class_access(DatabaseStub(), user, class_record)

    assert error.value.status_code == 403


def test_teacher_class_list_is_scoped_to_profile_and_assignment():
    class QueryStub:
        def __init__(self):
            self.conditions = []

        def filter(self, *conditions):
            self.conditions.extend(conditions)
            return self

        def distinct(self):
            return self

        def count(self):
            return 0

        def offset(self, value):
            return self

        def limit(self, value):
            return self

        def all(self):
            return []

    query = QueryStub()

    class DatabaseStub:
        def query(self, *models):
            return query

    user = SimpleNamespace(
        role=UserRole.TEACHER,
        teacher_profile=SimpleNamespace(id=uuid4()),
    )

    result = list_classes(
        params=PaginationParams(page=1, page_size=20),
        current_user=user,
        db=DatabaseStub(),
    )

    assert result.items == []
    assert len(query.conditions) == 1
    condition = str(query.conditions[0]).upper()
    assert "EXISTS" in condition
    assert "TEACHER_ID" in condition


@pytest.mark.parametrize(
    ("permission", "enabled", "allowed"),
    [
        ("publish_grades", True, True),
        ("publish_grades", False, False),
        ("edit_grades", False, False),
    ],
)
def test_contextual_assignment_checks_each_permission(permission, enabled, allowed):
    teacher_id = uuid4()
    class_record = SimpleNamespace(
        id=uuid4(),
        teacher_id=None,
        subject_id=uuid4(),
        academic_period_id=uuid4(),
    )
    assignment = SimpleNamespace(
        teacher_id=teacher_id,
        class_id=class_record.id,
        subject_id=class_record.subject_id,
        academic_period_id=class_record.academic_period_id,
        is_active=True,
        permissions={permission: enabled},
    )

    class QueryStub:
        def filter(self, *conditions):
            return self

        def first(self):
            return assignment

    class DatabaseStub:
        def get(self, model, item_id):
            return class_record

        def query(self, *models):
            return QueryStub()

    user = SimpleNamespace(
        role=UserRole.TEACHER,
        teacher_profile=SimpleNamespace(id=teacher_id),
    )
    db = DatabaseStub()

    if allowed:
        assert require_class_permission(db, user, class_record.id, permission) is class_record
    else:
        with pytest.raises(HTTPException) as error:
            require_class_permission(db, user, class_record.id, permission)
        assert error.value.status_code == 403
