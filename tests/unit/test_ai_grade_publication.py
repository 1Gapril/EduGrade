from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from backend.app.core.exceptions import ValidationError
from backend.app.models.academic import EnrollmentStatus
from backend.app.models.ai_correction import ReviewStatus
from backend.app.models.exam import SubmissionStatus
from backend.app.services.ai_correction_service import AICorrectionService


def _service(*, matching_assessment=True):
    service = AICorrectionService.__new__(AICorrectionService)
    service.db = MagicMock()
    correction = SimpleNamespace(id=uuid4(), question_id=uuid4())
    review = SimpleNamespace(status=ReviewStatus.APPROVED, final_score=Decimal("8.50"))
    student_id = uuid4()
    exam = SimpleNamespace(
        class_id=uuid4(),
        subject_id=uuid4(),
        academic_period_id=uuid4(),
        title="Prova 1",
    )
    submission = SimpleNamespace(
        id=uuid4(),
        identified_student_id=student_id,
        status=SubmissionStatus.REVIEWED,
        version=SimpleNamespace(exam=exam),
    )
    service.submission_repo = MagicMock()
    service.submission_repo.get.return_value = submission
    service.correction_repo = MagicMock()
    service.correction_repo.get_by_submission.return_value = [correction]
    service.review_repo = MagicMock()
    service.review_repo.get_by_ai_correction.return_value = review
    service.general_audit_repo = MagicMock()
    assessment = SimpleNamespace(
        id=uuid4(),
        title=exam.title,
        subject_id=exam.subject_id,
        academic_period_id=exam.academic_period_id,
        max_score=Decimal("10.00"),
    )
    if not matching_assessment:
        assessment.title = "Different title"
    enrollment = SimpleNamespace(id=uuid4(), status=EnrollmentStatus.ACTIVE)
    grade = SimpleNamespace(id=uuid4())
    return service, submission, enrollment, assessment, grade


def test_publish_grades_creates_and_officially_publishes_reviewed_grade():
    service, submission, enrollment, assessment, grade = _service()
    grade_service = MagicMock()
    grade_service.repo.get_by_enrollment_assessment.return_value = None
    grade_service.create.return_value = grade
    published_by = uuid4()
    with (
        patch("backend.app.services.academic_service.GradeService", return_value=grade_service),
        patch("backend.app.repositories.academic_repository.EnrollmentRepository") as enrollment_repo,
        patch("backend.app.repositories.academic_repository.AssessmentRepository") as assessment_repo,
    ):
        enrollment_repo.return_value.get_by_student_class.return_value = enrollment
        assessment_repo.return_value.get_by_class.return_value = [assessment]
        result = service.publish_grades(submission.id, published_by)

    assert result.status == SubmissionStatus.PUBLISHED
    grade_service.create.assert_called_once()
    assert grade_service.create.call_args.args[0].score == Decimal("8.50")
    grade_service.publish.assert_called_once_with(grade.id, published_by)


def test_publish_grades_rejects_missing_matching_assessment():
    service, submission, enrollment, assessment, _ = _service(matching_assessment=False)
    grade_service = MagicMock()
    with (
        patch("backend.app.services.academic_service.GradeService", return_value=grade_service),
        patch("backend.app.repositories.academic_repository.EnrollmentRepository") as enrollment_repo,
        patch("backend.app.repositories.academic_repository.AssessmentRepository") as assessment_repo,
    ):
        enrollment_repo.return_value.get_by_student_class.return_value = enrollment
        assessment_repo.return_value.get_by_class.return_value = [assessment]
        with pytest.raises(ValidationError, match="exatamente uma avaliação"):
            service.publish_grades(submission.id, uuid4())

    assert submission.status == SubmissionStatus.REVIEWED
    grade_service.create.assert_not_called()
    grade_service.publish.assert_not_called()
