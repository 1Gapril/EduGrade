import json
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.app.core.exceptions import ExternalServiceError, NotFoundError, ValidationError
from backend.app.models.ai_correction import AICorrectionStatus, ReviewStatus
from backend.app.models.exam import QuestionType, SubmissionStatus
from backend.app.schemas.ai_correction import BatchCorrectionRequest
from backend.app.services.ai_correction_service import AICorrectionService


def _service(response=None):
    service = AICorrectionService.__new__(AICorrectionService)
    service.db = MagicMock()
    service.correction_repo = MagicMock()
    service.review_repo = MagicMock()
    service.audit_repo = MagicMock()
    service.general_audit_repo = MagicMock()
    service.question_repo = MagicMock()
    service.submission_repo = MagicMock()
    service.answer_repo = MagicMock()
    service.provider = AsyncMock()
    service.provider.provider_id = "test-provider"
    service.provider.model = "text-model"
    service.provider.vision_model = "vision-model"
    service.provider.generate_text.return_value = json.dumps(response or {
        "recognized_text": "student answer",
        "interpretation": "correct",
        "suggested_score": 8,
        "max_score": 10,
        "justification": "Matches the rubric",
        "criteria_met": ["concept"],
        "criteria_not_met": [],
        "conceptual_errors": [],
        "ocr_confidence": 90,
        "evaluation_confidence": 85,
        "requires_review": False,
    })
    service.provider.analyze_image.return_value = service.provider.generate_text.return_value
    return service


def _submission(question_id, status=SubmissionStatus.UPLOADED):
    exam = SimpleNamespace(
        class_id=uuid4(),
        subject_id=uuid4(),
        academic_period_id=uuid4(),
        title="Assessment 1",
    )
    version = SimpleNamespace(
        exam=exam,
        answer_key_snapshot={str(question_id): {"expected_answer": "expected"}},
        rubrics_snapshot={str(question_id): {"criteria": []}},
    )
    return SimpleNamespace(
        id=uuid4(),
        status=status,
        identified_student_id=uuid4(),
        version=version,
    )


def _question(question_id):
    return SimpleNamespace(
        id=question_id,
        type=QuestionType.ESSAY,
        statement="Explain the concept",
        score=Decimal("10"),
        question_order=1,
    )


def _correction_result(requires_review=False):
    return SimpleNamespace(
        id=uuid4(),
        submission_id=uuid4(),
        question_id=uuid4(),
        provider="test-provider",
        model="text-model",
        status=AICorrectionStatus.COMPLETED,
        max_score=Decimal("10"),
        criteria_met=[],
        criteria_not_met=[],
        conceptual_errors=[],
        requires_review=requires_review,
        raw_response={},
        created_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_correct_question_uses_extracted_text_and_marks_review_status():
    service = _service()
    question_id = uuid4()
    submission = _submission(question_id)
    service.submission_repo.get_with_pages.return_value = submission
    service.question_repo.get_with_answer_key.return_value = _question(question_id)
    service.answer_repo.get_all_by_submission_question.return_value = [
        SimpleNamespace(
            id=uuid4(),
            extracted_text=" student answer ",
            extracted_image_path=None,
            ocr_confidence=Decimal("80"),
        ),
        SimpleNamespace(
            id=uuid4(),
            extracted_text="",
            extracted_image_path=None,
            ocr_confidence=Decimal("100"),
        ),
    ]

    correction = await service.correct_question(submission.id, question_id)

    assert correction.status is AICorrectionStatus.COMPLETED
    assert correction.recognized_text == "student answer"
    assert correction.suggested_score == Decimal("8")
    assert correction.ocr_confidence == Decimal("90")
    assert submission.status is SubmissionStatus.IN_CORRECTION
    service.provider.generate_text.assert_awaited_once()
    service.general_audit_repo.log.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response", "submission_status"),
    [
        (
            {"suggested_score": 7, "evaluation_confidence": 69, "requires_review": False},
            SubmissionStatus.AWAITING_REVIEW,
        ),
        (
            {"suggested_score": 7, "evaluation_confidence": 90, "requires_review": True},
            SubmissionStatus.AWAITING_REVIEW,
        ),
    ],
)
async def test_correct_question_requires_human_review_when_requested(response, submission_status):
    service = _service(response)
    question_id = uuid4()
    submission = _submission(question_id)
    service.submission_repo.get_with_pages.return_value = submission
    service.question_repo.get_with_answer_key.return_value = _question(question_id)
    service.answer_repo.get_all_by_submission_question.return_value = []

    correction = await service.correct_question(submission.id, question_id)

    assert correction.status is AICorrectionStatus.REQUIRES_REVIEW
    assert submission.status is submission_status


@pytest.mark.asyncio
async def test_correct_question_sends_answer_image_to_vision_provider(tmp_path):
    service = _service()
    question_id = uuid4()
    submission = _submission(question_id)
    image_path = tmp_path / "answer.png"
    image_path.write_bytes(b"synthetic-image")
    service.submission_repo.get_with_pages.return_value = submission
    service.question_repo.get_with_answer_key.return_value = _question(question_id)
    service.answer_repo.get_all_by_submission_question.return_value = [
        SimpleNamespace(
            id=uuid4(),
            extracted_text=None,
            extracted_image_path=str(image_path),
            ocr_confidence=None,
        ),
    ]

    correction = await service.correct_question(submission.id, question_id)

    assert correction.model == "vision-model"
    service.provider.analyze_image.assert_awaited_once()
    service.provider.generate_text.assert_not_awaited()


@pytest.mark.asyncio
async def test_correct_question_records_provider_failure_and_surfaces_error():
    service = _service()
    question_id = uuid4()
    submission = _submission(question_id)
    service.submission_repo.get_with_pages.return_value = submission
    service.question_repo.get_with_answer_key.return_value = _question(question_id)
    service.answer_repo.get_all_by_submission_question.return_value = []
    service.provider.generate_text.side_effect = RuntimeError("provider unavailable")

    with pytest.raises(ExternalServiceError, match="Falha na correção por IA"):
        await service.correct_question(submission.id, question_id)

    correction = service.db.add.call_args.args[0]
    assert correction.status is AICorrectionStatus.FAILED
    assert correction.error_message == "provider unavailable"


@pytest.mark.asyncio
async def test_correct_question_rejects_missing_submission_or_question():
    service = _service()
    service.submission_repo.get_with_pages.return_value = None
    with pytest.raises(NotFoundError, match="Submissão não encontrada"):
        await service.correct_question(uuid4(), uuid4())

    service.submission_repo.get_with_pages.return_value = SimpleNamespace()
    service.question_repo.get_with_answer_key.return_value = None
    with pytest.raises(NotFoundError, match="Questão não encontrada"):
        await service.correct_question(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_batch_correct_counts_successes_failures_and_unanswered_questions():
    service = _service()
    submission_id = uuid4()
    questions = [_question(uuid4()) for _ in range(3)]
    service.submission_repo.get.return_value = SimpleNamespace(
        version=SimpleNamespace(exam_id=uuid4()),
    )
    service.question_repo.get_by_exam.return_value = questions
    service.answer_repo.get_all_by_submission_question.side_effect = [
        [SimpleNamespace(extracted_text="answer", extracted_image_path=None)],
        [SimpleNamespace(extracted_text="answer", extracted_image_path=None)],
        [],
    ]
    service.correct_question = AsyncMock(side_effect=[
        _correction_result(requires_review=True),
        ExternalServiceError("provider failed"),
    ])

    result = await service.batch_correct(BatchCorrectionRequest(submission_id=submission_id))

    assert result.total_processed == 1
    assert result.failed == 1
    assert result.skipped == 1
    assert result.requires_review_count == 1


def test_create_review_rejects_missing_or_duplicate_review():
    service = _service()
    service.correction_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Correção não encontrada"):
        service.create_review(uuid4(), uuid4())

    service.correction_repo.get.return_value = SimpleNamespace(id=uuid4())
    service.review_repo.get_by_ai_correction.return_value = SimpleNamespace(id=uuid4())
    with pytest.raises(ValidationError, match="Revisão já existe"):
        service.create_review(uuid4(), uuid4())


def test_create_review_records_audit_for_new_review():
    service = _service()
    service.correction_repo.get.return_value = SimpleNamespace(
        id=uuid4(),
        suggested_score=Decimal("8"),
    )
    service.review_repo.get_by_ai_correction.return_value = None
    reviewer_id = uuid4()

    review = service.create_review(uuid4(), reviewer_id)

    assert review.status is ReviewStatus.IN_REVIEW
    assert review.original_suggested_score == Decimal("8")
    service.db.add.assert_called_once_with(review)
    service.general_audit_repo.log.assert_called_once()


def test_update_review_marks_approved_and_audits_score_changes():
    service = _service()
    review_id = uuid4()
    correction = SimpleNamespace(
        id=uuid4(),
        submission_id=uuid4(),
        suggested_score=Decimal("8"),
    )
    review = SimpleNamespace(
        id=review_id,
        ai_correction_id=correction.id,
        final_score=Decimal("7"),
        status=ReviewStatus.IN_REVIEW,
    )
    submission = SimpleNamespace(id=correction.submission_id, status=SubmissionStatus.AWAITING_REVIEW)
    service.review_repo.get.return_value = review
    service.review_repo.get_by_ai_correction.return_value = review
    service.correction_repo.get.return_value = correction
    service.correction_repo.get_by_submission.return_value = [correction]
    service.submission_repo.get.return_value = submission

    updated = service.update_review(
        review_id,
        Decimal("8"),
        corrected_text="Reviewed answer",
        reviewer_id=uuid4(),
    )

    assert updated.status is ReviewStatus.APPROVED
    assert updated.final_score == Decimal("8")
    assert submission.status is SubmissionStatus.REVIEWED
    service.audit_repo.create.assert_called_once()
    service.general_audit_repo.log.assert_called_once()


def test_update_review_rejects_missing_review():
    service = _service()
    service.review_repo.get.return_value = None

    with pytest.raises(NotFoundError, match="Revisão não encontrada"):
        service.update_review(uuid4(), Decimal("8"))
