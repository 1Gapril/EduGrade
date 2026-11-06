from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from backend.app.core.exceptions import ConflictError, NotFoundError
from backend.app.models.academic import Class, Enrollment, EnrollmentStatus
from backend.app.services.academic_service import (
    AcademicPeriodService,
    AcademicRuleService,
    AssessmentService,
    AttendanceService,
    ClassService,
    CourseService,
    EnrollmentService,
    GradeService,
    SubjectService,
)


def _data(**values):
    return SimpleNamespace(
        model_dump=lambda **_kwargs: values.copy(),
        **values,
    )


def test_class_enrollment_count_includes_only_active_students():
    class_record = Class(
        enrollments=[
            Enrollment(status=EnrollmentStatus.ACTIVE),
            Enrollment(status=EnrollmentStatus.ACTIVE),
            Enrollment(status=EnrollmentStatus.INACTIVE),
        ]
    )

    assert class_record.enrollments_count == 2


def test_course_service_create_conflict_and_crud():
    db = MagicMock()
    service = CourseService(db)
    service.repo = MagicMock()
    service.audit_repo = MagicMock()
    data = _data(code="CS", name="Computer Science", duration_semesters=8)
    service.repo.get_by_code.return_value = None

    created = service.create(data, uuid4())

    assert created.code == "CS"
    db.add.assert_called_once_with(created)
    db.flush.assert_called_once()
    service.audit_repo.log.assert_called_once()

    service.repo.get_by_code.return_value = created
    with pytest.raises(ConflictError, match="Código do curso"):
        service.create(data, uuid4())

    service.repo.get.return_value = created
    updated = service.update(created.id, _data(name="Computing"), uuid4())
    assert updated.name == "Computing"
    assert service.list() == service.repo.get_active.return_value
    assert service.list(active_only=False) == service.repo.get_all.return_value

    service.repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Curso não encontrado"):
        service.get(uuid4())


def test_subject_service_create_lookup_update_and_conflict():
    db = MagicMock()
    service = SubjectService(db)
    service.repo = MagicMock()
    service.audit_repo = MagicMock()
    data = _data(code="MATH", name="Mathematics", course_id=uuid4())
    service.repo.get_by_code.return_value = None

    subject = service.create(data, uuid4())

    assert subject.code == "MATH"
    service.repo.get_by_course.return_value = [subject]
    assert service.get_by_course(subject.course_id) == [subject]
    service.repo.get.return_value = subject
    assert service.get(subject.id) is subject
    assert service.update(subject.id, _data(name="Algebra"), uuid4()).name == "Algebra"

    service.repo.get_by_code.return_value = subject
    with pytest.raises(ConflictError, match="Código da disciplina"):
        service.create(data, uuid4())
    service.repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Disciplina não encontrada"):
        service.get(uuid4())


def test_class_service_delegates_create_update_and_queries():
    db = MagicMock()
    service = ClassService(db)
    service.repo = MagicMock()
    service.audit_repo = MagicMock()
    data = _data(
        code="CLS",
        name="Class",
        course_id=uuid4(),
        subject_id=uuid4(),
        academic_period_id=uuid4(),
        semester=1,
        year=2026,
    )

    created = service.create(data, uuid4())
    service.repo.get_with_details.return_value = created
    assert service.get(created.id) is created
    assert service.get_by_teacher(uuid4()) == service.repo.get_by_teacher.return_value
    assert service.get_students_count(created.id) == service.repo.get_students_count.return_value
    updated = service.update(created.id, _data(name="Updated"), uuid4())
    assert updated.name == "Updated"

    service.repo.get_with_details.return_value = None
    with pytest.raises(NotFoundError, match="Turma não encontrada"):
        service.get(uuid4())


def test_academic_period_service_create_current_and_switch():
    db = MagicMock()
    service = AcademicPeriodService(db)
    service.repo = MagicMock()
    service.audit_repo = MagicMock()
    data = _data(
        name="2026",
        code="2026",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )
    service.repo.get_by_code.return_value = None
    period = service.create(data, uuid4())
    assert period.code == "2026"

    service.repo.get_current.return_value = period
    assert service.get_current() is period
    target = SimpleNamespace(id=uuid4(), code="2027", is_current=False)
    service.repo.get.return_value = target
    assert service.set_current(target.id, uuid4()) is target
    assert period.is_current is False
    assert target.is_current is True

    service.repo.get_by_code.return_value = period
    with pytest.raises(ConflictError, match="Código do período"):
        service.create(data, uuid4())
    service.repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Período não encontrado"):
        service.get(uuid4())


def test_enrollment_create_bulk_update_and_lookup():
    db = MagicMock()
    service = EnrollmentService(db)
    service.repo = MagicMock()
    service.audit_repo = MagicMock()
    data = _data(student_id=uuid4(), class_id=uuid4(), academic_period_id=uuid4())
    service.repo.get_by_student_class.return_value = None

    enrollment = service.create(data, uuid4())
    enrollment.status = EnrollmentStatus.ACTIVE
    assert enrollment.student_id == data.student_id

    existing_student = uuid4()
    new_student = uuid4()
    service.repo.get_by_student_class.side_effect = [object(), None]
    bulk = service.bulk_create(
        data.class_id,
        [existing_student, new_student],
        data.academic_period_id,
        uuid4(),
    )
    assert len(bulk) == 1
    assert bulk[0].student_id == new_student
    assert bulk[0].status == EnrollmentStatus.ACTIVE

    service.repo.get_by_student_class.side_effect = None
    service.repo.get_by_student_class.return_value = object()
    with pytest.raises(ConflictError, match="Aluno já matriculado"):
        service.create(data, uuid4())

    service.repo.get.return_value = enrollment
    assert service.update(enrollment.id, _data(status="inactive"), uuid4()).status == "inactive"
    audit_call = service.audit_repo.log.call_args
    assert audit_call.args[1] == "Matrícula atualizada"
    assert audit_call.args[3] == "Enrollment"
    assert audit_call.kwargs["old_values"]["status"] == "active"
    assert audit_call.kwargs["new_values"] == {"status": "inactive"}
    service.repo.get_by_student_period.return_value = [enrollment]
    assert service.get_by_student(data.student_id, data.academic_period_id) == [enrollment]

    service.repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Matrícula não encontrada"):
        service.get(uuid4())


def test_assessment_service_publish_and_weighted_average():
    db = MagicMock()
    service = AssessmentService(db)
    service.repo = MagicMock()
    service.grade_repo = MagicMock()
    service.audit_repo = MagicMock()
    data = _data(
        title="Exam",
        type="a1",
        weight=Decimal("1"),
        max_score=Decimal("10"),
        class_id=uuid4(),
        subject_id=uuid4(),
        academic_period_id=uuid4(),
        scheduled_date=date(2026, 5, 1),
    )
    created = service.create(data, uuid4())
    service.repo.get.return_value = created
    assert service.get(created.id) is created
    assert service.publish(created.id, uuid4()).is_published is True
    enrollment_id = uuid4()
    assert service.calculate_final_grade(enrollment_id) == (
        service.grade_repo.calculate_weighted_average.return_value
    )
    service.grade_repo.calculate_weighted_average.assert_called_once_with(enrollment_id)

    service.repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Avaliação não encontrada"):
        service.get(uuid4())


def test_grade_service_create_update_and_publish():
    db = MagicMock()
    service = GradeService(db)
    service.repo = MagicMock()
    service.audit_repo = MagicMock()
    data = _data(enrollment_id=uuid4(), assessment_id=uuid4(), score=Decimal("8"))
    service.repo.get_by_enrollment_assessment.return_value = None

    grade = service.create(data, uuid4())
    assert grade.score == Decimal("8")
    assert grade.graded_by is not None
    service.repo.get.return_value = grade
    assert service.update(grade.id, _data(score=Decimal("9"), is_official=True), uuid4()).score == 9
    assert grade.published_at is not None
    assert service.publish(grade.id, uuid4()).is_official is True

    service.repo.get_by_enrollment_assessment.return_value = grade
    with pytest.raises(ConflictError, match="Nota já existe"):
        service.create(data, uuid4())
    service.repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Nota não encontrada"):
        service.update(uuid4(), _data(score=Decimal("1")), uuid4())
    with pytest.raises(NotFoundError, match="Nota não encontrada"):
        service.publish(uuid4(), uuid4())


def test_attendance_service_create_bulk_and_calculate():
    db = MagicMock()
    service = AttendanceService(db)
    service.repo = MagicMock()
    enrollment_id = uuid4()
    class_date = date(2026, 5, 1)
    data = _data(enrollment_id=enrollment_id, class_date=class_date, is_present=True)
    service.repo.get_by_enrollment.return_value = []

    attendance = service.create(data, uuid4())
    assert attendance.enrollment_id == enrollment_id
    service.repo.get_by_enrollment.side_effect = [
        [SimpleNamespace(class_date=class_date)],
        [],
    ]
    bulk = service.bulk_create(uuid4(), class_date, [data, data], uuid4())
    assert len(bulk) == 1
    assert service.calculate_percentage(enrollment_id) == service.repo.calculate_percentage.return_value

    service.repo.get_by_enrollment.side_effect = None
    service.repo.get_by_enrollment.return_value = [SimpleNamespace(class_date=class_date)]
    with pytest.raises(ConflictError, match="Frequência já registrada"):
        service.create(data, uuid4())


def test_academic_rule_service_rejects_duplicate_and_lists_by_type():
    db = MagicMock()
    service = AcademicRuleService(db)
    service.repo = MagicMock()
    rule_data = _data(name="Passing grade", rule_type="grade", config='{"minimum": 6}')
    service.repo.get_by_name.return_value = None

    rule = service.create(rule_data)

    assert rule.name == "Passing grade"
    service.repo.get_by_type.return_value = [rule]
    assert service.get_by_type("grade") == [rule]
    service.repo.get_by_name.return_value = rule
    with pytest.raises(ConflictError, match="Nome da regra"):
        service.create(rule_data)
