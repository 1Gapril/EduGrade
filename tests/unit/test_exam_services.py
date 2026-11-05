from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from backend.app.core.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from backend.app.models.exam import ExamStatus, QuestionType, SubmissionStatus
from backend.app.models.user import UserRole
from backend.app.services.exam_service import (
    AnswerKeyService,
    ExamCopyService,
    ExamService,
    GradingRubricService,
    QuestionService,
    SubmissionService,
)


def _data(*, dump=None, **values):
    return SimpleNamespace(
        model_dump=dump or (lambda **_kwargs: values.copy()),
        **values,
    )


def _exam_service(exam=None):
    service = ExamService.__new__(ExamService)
    service.db = MagicMock()
    service.repo = MagicMock()
    service.question_repo = MagicMock()
    service.version_repo = MagicMock()
    service.audit_repo = MagicMock()
    service.get = MagicMock(return_value=exam)
    service._assert_can_manage = MagicMock()
    service._assert_can_manage_class = MagicMock()
    return service


def test_exam_service_permissions_update_cancel_and_score_validation():
    exam_id, user_id = uuid4(), uuid4()
    version = SimpleNamespace(is_active=True)
    exam = SimpleNamespace(
        id=exam_id,
        class_id=uuid4(),
        status=ExamStatus.DRAFT,
        title="Exam",
        versions=[version],
    )
    service = _exam_service(exam)
    service.repo.validate_total_score.return_value = (Decimal("10"), Decimal("10"), True)

    updated = service.update(exam_id, _data(dump=lambda **_kwargs: {"title": "Updated"}), user_id)
    assert updated.title == "Updated"
    assert updated.updated_at is not None
    assert service.validate_scores(exam_id) == (Decimal("10"), Decimal("10"), True)

    cancelled = service.cancel(exam_id, user_id)
    assert cancelled.status is ExamStatus.CANCELLED
    assert version.is_active is False
    assert service.cancel(exam_id, user_id) is exam

    exam.status = ExamStatus.PUBLISHED
    with pytest.raises(ValidationError, match="rascunho ou edição"):
        service.update(exam_id, _data(dump=lambda **_kwargs: {"title": "No"}), user_id)


def test_exam_service_authorization_and_not_found_paths():
    service = _exam_service()
    service.db.get.side_effect = [None]
    with pytest.raises(AuthorizationError, match="Usuário não encontrado"):
        ExamService._assert_can_manage(service, SimpleNamespace(class_id=uuid4()), uuid4())

    service.db.get.side_effect = [
        SimpleNamespace(role=UserRole.STUDENT),
    ]
    with pytest.raises(AuthorizationError, match="Permissão insuficiente"):
        ExamService._assert_can_manage(service, SimpleNamespace(class_id=uuid4()), uuid4())

    service.db.get.side_effect = [
        SimpleNamespace(role=UserRole.TEACHER, teacher_profile=None),
        None,
    ]
    with pytest.raises(AuthorizationError, match="Você não leciona"):
        ExamService._assert_can_manage(service, SimpleNamespace(class_id=uuid4()), uuid4())

    service.db.get.side_effect = [
        SimpleNamespace(role=UserRole.TEACHER, teacher_profile=None),
        None,
    ]
    with pytest.raises(NotFoundError, match="Turma não encontrada"):
        ExamService._assert_can_manage_class(service, uuid4(), uuid4())

    service.repo.get_with_questions.return_value = None
    with pytest.raises(NotFoundError, match="Prova não encontrada"):
        ExamService.get(service, uuid4())


def test_publish_exam_creates_immutable_question_answer_and_rubric_snapshots():
    question_id = uuid4()
    question = SimpleNamespace(
        id=question_id,
        question_order=1,
        type=QuestionType.ESSAY,
        statement="Explain.",
        score=Decimal("10"),
        config={"answer_lines": 4},
        answer_key=SimpleNamespace(
            correct_answer=None,
            expected_answer="Expected",
            accepted_alternatives=[],
            keywords=["key"],
            required_concepts=["concept"],
            justification="Reason",
            partial_scoring=None,
        ),
        grading_rubric=SimpleNamespace(
            criteria=[{"name": "Clarity"}],
            max_score=Decimal("10"),
        ),
    )
    exam = SimpleNamespace(
        id=uuid4(),
        class_id=uuid4(),
        title="Essay exam",
        description="Description",
        instructions="Instructions",
        total_score=Decimal("10"),
        version=2,
        status=ExamStatus.DRAFT,
        published_at=None,
    )
    service = _exam_service(exam)
    service.validate_scores = MagicMock(return_value=(Decimal("10"), Decimal("10"), True))
    service.question_repo.get_by_exam.return_value = [question]
    service.question_repo.get_with_answer_key.return_value = question

    version = service.publish(exam.id, uuid4())

    assert version.version_number == 3
    assert version.questions_snapshot[0]["id"] == str(question_id)
    assert version.answer_key_snapshot[str(question_id)]["expected_answer"] == "Expected"
    assert version.rubrics_snapshot[str(question_id)]["criteria"] == [{"name": "Clarity"}]
    assert exam.status is ExamStatus.PUBLISHED
    assert exam.version == 3
    assert exam.published_at is not None

    service.validate_scores.return_value = (Decimal("8"), Decimal("10"), False)
    with pytest.raises(ValidationError, match="difere do total"):
        service.publish(exam.id, uuid4())
    service.validate_scores.return_value = (Decimal("10"), Decimal("10"), True)
    service.question_repo.get_by_exam.return_value = []
    with pytest.raises(ValidationError, match="pelo menos uma questão"):
        service.publish(exam.id, uuid4())
    service.question_repo.get_by_exam.return_value = [question]
    service.question_repo.get_with_answer_key.return_value = None
    with pytest.raises(ValidationError, match="não possui gabarito"):
        service.publish(exam.id, uuid4())


def test_update_exam_questions_reorders_creates_keys_and_removes_omitted():
    exam_id, question_id, omitted_id = uuid4(), uuid4(), uuid4()
    existing = SimpleNamespace(
        id=question_id,
        question_order=1,
        answer_key=SimpleNamespace(),
    )
    omitted = SimpleNamespace(id=omitted_id, question_order=2, answer_key=None)
    exam = SimpleNamespace(
        id=exam_id,
        class_id=uuid4(),
        status=ExamStatus.DRAFT,
        title="Exam",
    )
    service = _exam_service(exam)
    service.question_repo.get_by_exam.return_value = [existing, omitted]
    update_data = _data(
        class_id=exam.class_id,
        title="Updated",
        dump=lambda **_kwargs: {"title": "Updated"},
        questions=[
            SimpleNamespace(
                id=question_id,
                type="essay",
                statement="Updated question",
                score=Decimal("5"),
                config={},
                correct_answer=None,
                expected_answer="Expected",
                accepted_alternatives=[],
                keywords=[],
                required_concepts=[],
                justification=None,
            ),
            SimpleNamespace(
                id=None,
                type="short_answer",
                statement="New question",
                score=Decimal("5"),
                config={},
                correct_answer=None,
                expected_answer="Another answer",
                accepted_alternatives=[],
                keywords=[],
                required_concepts=[],
                justification=None,
            ),
        ],
    )

    result = service.update_with_questions(exam_id, update_data, uuid4())

    assert result.title == "Updated"
    assert existing.question_order == 1
    service.db.delete.assert_called_once_with(omitted)
    assert service.db.add.call_count == 2
    assert existing.answer_key.expected_answer == "Expected"

    duplicate = _data(
        class_id=exam.class_id,
        questions=[SimpleNamespace(id=question_id), SimpleNamespace(id=question_id)],
        dump=lambda **_kwargs: {},
    )
    with pytest.raises(ValidationError, match="mais de uma vez"):
        service.update_with_questions(exam_id, duplicate, uuid4())

    foreign = _data(
        class_id=exam.class_id,
        questions=[SimpleNamespace(id=uuid4())],
        dump=lambda **_kwargs: {},
    )
    with pytest.raises(ValidationError, match="não pertence"):
        service.update_with_questions(exam_id, foreign, uuid4())


def test_question_answer_key_and_rubric_services_validate_and_update():
    db = MagicMock()
    question_service = QuestionService(db)
    question_service.repo = MagicMock()
    question_service.answer_key_repo = MagicMock()
    question_service.rubric_repo = MagicMock()
    question = SimpleNamespace(
        id=uuid4(),
        question_order=1,
        exam=SimpleNamespace(status=ExamStatus.DRAFT),
    )
    question_service.repo.get_by_exam.return_value = []

    question_service.create(
        _data(
            exam_id=uuid4(),
            question_order=1,
            type=QuestionType.ESSAY,
            statement="Explain",
            score=Decimal("5"),
        )
    )
    question_service.repo.get_with_answer_key.return_value = question
    assert question_service.get(question.id) is question
    assert question_service.update(question.id, _data(statement="Updated")).statement == "Updated"
    question_service.repo.get_by_exam.return_value = [question]
    with pytest.raises(ConflictError, match="Ordem 1"):
        question_service.create(
            _data(
                exam_id=uuid4(),
                question_order=1,
                type=QuestionType.ESSAY,
                statement="Duplicate",
                score=Decimal("1"),
            )
        )
    question_service.repo.get_by_exam.return_value = [question]
    assert question_service.reorder(
        uuid4(), [{"id": str(question.id), "order": 4}, {"id": str(uuid4()), "order": 3}]
    )[0].question_order == 4
    question.exam.status = ExamStatus.PUBLISHED
    with pytest.raises(ValidationError, match="prova publicada"):
        question_service.update(question.id, _data(statement="No"))

    ak_service = AnswerKeyService(db)
    ak_service.question_repo = MagicMock()
    ak_service.repo = MagicMock()
    ak_service.question_repo.get.return_value = question
    ak_service.repo.get_by_question.return_value = None
    answer_key = ak_service.create(_data(question_id=question.id, correct_answer="A"))
    assert answer_key.correct_answer == "A"
    ak_service.repo.get_by_question.return_value = answer_key
    assert ak_service.update(question.id, _data(correct_answer="B")).correct_answer == "B"
    with pytest.raises(ConflictError, match="Gabarito já existe"):
        ak_service.create(_data(question_id=question.id, correct_answer="A"))
    ak_service.question_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Questão não encontrada"):
        ak_service.create(_data(question_id=question.id, correct_answer="A"))

    rubric_service = GradingRubricService(db)
    rubric_service.question_repo = MagicMock()
    rubric_service.repo = MagicMock()
    rubric_service.question_repo.get.return_value = question
    rubric_service.repo.get_by_question.return_value = None
    rubric = rubric_service.create(
        _data(question_id=question.id, criteria=[{"name": "Clarity"}], max_score=Decimal("5"))
    )
    assert rubric.max_score == Decimal("5")
    rubric_service.repo.get_by_question.return_value = rubric
    assert rubric_service.update(question.id, _data(max_score=Decimal("4"))).max_score == 4
    with pytest.raises(ConflictError, match="Rubrica já existe"):
        rubric_service.create(
            _data(question_id=question.id, criteria=[], max_score=Decimal("5"))
        )
    rubric_service.question_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Questão não encontrada"):
        rubric_service.create(
            _data(question_id=question.id, criteria=[], max_score=Decimal("5"))
        )


def test_exam_copy_generation_pdf_and_print_logging(monkeypatch):
    db = MagicMock()
    service = ExamCopyService(db)
    service.repo = MagicMock()
    service.version_repo = MagicMock()
    service.exam_repo = MagicMock()
    service.print_repo = MagicMock()
    service.audit_repo = MagicMock()
    version = SimpleNamespace(id=uuid4(), exam_id=uuid4(), version_number=2)
    service.version_repo.get.return_value = version
    service.repo.get_by_version.return_value = [object()]
    student_ids = [uuid4()]

    copies = service.generate_copies(version.id, 2, student_ids, uuid4())

    assert [copy.copy_identifier.rsplit("-", 1)[-1] for copy in copies] == ["0002", "0003"]
    assert copies[0].student_id == student_ids[0]
    assert copies[0].is_personalized
    assert copies[1].student_id is None
    assert not copies[1].is_personalized

    copy = SimpleNamespace(
        id=uuid4(),
        version_id=version.id,
        copy_identifier="copy-1",
        pdf_path=None,
        printed_at=None,
        printed_by=None,
    )
    service.repo.get.return_value = copy
    service.exam_repo.get.return_value = SimpleNamespace(id=version.exam_id)
    service.pdf_gen = SimpleNamespace(
        generate_student_exam=lambda **_kwargs: "storage/exams/pdfs/student.pdf",
        generate_teacher_answer_key=lambda **_kwargs: "storage/exams/pdfs/teacher.pdf",
    )
    assert service.generate_pdf_student(copy.id, uuid4()).endswith("student.pdf")
    assert copy.pdf_path.endswith("student.pdf")
    assert copy.printed_at is not None
    assert service.generate_pdf_teacher(version.id, uuid4()).endswith("teacher.pdf")

    service.version_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Versão não encontrada"):
        service.generate_pdf_teacher(version.id, uuid4())
    service.repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Cópia não encontrada"):
        service.generate_pdf_student(uuid4(), uuid4())

    log_data = _data(
        dump=lambda **_kwargs: {
            "exam_id": version.exam_id,
            "version_id": version.id,
            "printed_by": uuid4(),
            "copy_count": 2,
            "copy_identifiers": ["copy-1", "copy-2"],
        },
        copy_count=2,
        printed_by=uuid4(),
    )
    assert service.log_print(log_data).copy_count == 2
    service.version_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Versão não encontrada"):
        service.generate_copies(version.id, 1)


def test_submission_service_create_pages_identification_and_correction():
    db = MagicMock()
    service = SubmissionService(db)
    service.repo = MagicMock()
    service.copy_repo = MagicMock()
    service.version_repo = MagicMock()
    service.page_repo = MagicMock()
    service.answer_repo = MagicMock()
    service.audit_repo = MagicMock()
    copy = SimpleNamespace(id=uuid4(), version_id=uuid4(), student_id=uuid4(), copy_identifier="copy")
    service.copy_repo.get.return_value = copy
    service.repo.get_by_copy.return_value = None
    data = _data(
        copy_id=copy.id,
        version_id=uuid4(),
        student_id=None,
        original_files=["scan.png"],
    )

    submission = service.create(data, uuid4())
    assert submission.version_id == copy.version_id
    assert submission.student_id == copy.student_id
    pages = service.add_pages(
        submission.id,
        [_data(submission_id=uuid4(), page_number=1, original_image_path="scan.png")],
    )
    assert pages[0].submission_id == submission.id
    assert pages[0].page_number == 1

    service.repo.get.return_value = submission
    assert service.identify_student(
        submission.id,
        uuid4(),
        Decimal("95"),
        manual=True,
    ).manual_identification
    assert service.request_ai_correction(submission.id).status is SubmissionStatus.AWAITING_CORRECTION

    service.copy_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Cópia não encontrada"):
        service.create(data, uuid4())
    service.copy_repo.get.return_value = copy
    service.repo.get_by_copy.return_value = submission
    with pytest.raises(ConflictError, match="Submissão já existe"):
        service.create(data, uuid4())
    service.repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Submissão não encontrada"):
        service.add_pages(uuid4(), [])
    with pytest.raises(NotFoundError, match="Submissão não encontrada"):
        service.identify_student(uuid4(), uuid4(), Decimal("10"))
    with pytest.raises(NotFoundError, match="Submissão não encontrada"):
        service.request_ai_correction(uuid4())
