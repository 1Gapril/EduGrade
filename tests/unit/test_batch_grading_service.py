from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.app.core.exceptions import NotFoundError, ValidationError
from backend.app.models.exam import SubmissionStatus
from backend.app.models.grading_batch import (
    BatchStatus,
    FileStatus,
    IdentificationStatus,
    PageGroupStatus,
)
from backend.app.services.batch_grading_service import BatchGradingService


def _service(batch=None):
    service = BatchGradingService.__new__(BatchGradingService)
    service.db = MagicMock()
    service.student_repo = MagicMock()
    service._batch = None
    service.db.get.return_value = batch
    return service


def test_create_batch_validates_exam_and_version():
    service = _service()
    exam_id, version_id, user_id = uuid4(), uuid4(), uuid4()
    service.exam_repo = MagicMock()
    service.version_repo = MagicMock()
    exam = SimpleNamespace(id=exam_id)
    version = SimpleNamespace(id=version_id)
    service.exam_repo.get.return_value = exam
    service.version_repo.get.return_value = version

    batch = service.create_batch(exam_id, version_id, user_id)

    assert batch.exam_id == exam_id
    assert batch.version_id == version_id
    assert batch.uploaded_by == user_id
    assert batch.status is BatchStatus.UPLOADING
    service.db.add.assert_called_once_with(batch)

    service.exam_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Prova não encontrada"):
        service.create_batch(exam_id, version_id, user_id)
    service.exam_repo.get.return_value = exam
    service.version_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Versão não encontrada"):
        service.create_batch(exam_id, version_id, user_id)


def test_add_files_and_start_processing_record_status_and_audit():
    batch = SimpleNamespace(
        id=uuid4(),
        status=BatchStatus.UPLOADING,
        total_files=0,
        failed_files=0,
        updated_at=None,
    )
    service = _service(batch)
    files = [
        {
            "filename": "scan.png",
            "path": "storage/scan.png",
            "content_type": "image/png",
            "size": 20,
            "type": "image",
        },
        {
            "filename": "exam.pdf",
            "path": "storage/exam.pdf",
            "content_type": "application/pdf",
            "size": 40,
            "type": "pdf",
            "page_count": 3,
        },
    ]

    created = service.add_files(batch.id, files)

    assert len(created) == 2
    assert created[0].page_count == 1
    assert created[1].page_count == 3
    assert batch.total_files == 2
    assert batch.failed_files == 0
    assert batch.updated_at is not None
    assert service.db.add.call_count == 3

    service.add_files(batch.id, [{
        "filename": "invalid.txt",
        "path": "",
        "content_type": "text/plain",
        "size": 0,
        "type": "image",
        "status": FileStatus.FAILED,
        "error_message": "unsupported",
    }])
    assert batch.total_files == 3
    assert batch.failed_files == 1

    started = service.start_processing(batch.id)
    assert started.status is BatchStatus.PROCESSING
    assert started.processing_started_at is not None

    batch.status = BatchStatus.COMPLETED
    with pytest.raises(ValidationError, match="estado de upload"):
        service.add_files(batch.id, files)
    service.db.get.return_value = None
    with pytest.raises(NotFoundError, match="Lote não encontrado"):
        service.get_batch(batch.id)


def test_batch_details_and_progress_summarize_counts():
    batch = SimpleNamespace(
        id=uuid4(),
        status=BatchStatus.IDENTIFYING,
        total_files=4,
        processed_files=2,
        total_pages=7,
        identified_students=3,
        grouped_submissions=2,
        graded_submissions=1,
    )
    service = _service(batch)
    file_stats = [(FileStatus.PROCESSED, 2), (FileStatus.FAILED, 1)]
    submission_stats = [(SubmissionStatus.REVIEWED, 1)]
    service.db.execute.side_effect = [
        SimpleNamespace(all=lambda: file_stats),
        SimpleNamespace(all=lambda: submission_stats),
        SimpleNamespace(scalar_one=lambda: 2),
    ]

    result = service.get_batch_with_details(batch.id)

    assert result["file_stats"] == {"processed": 2, "failed": 1}
    assert result["submission_stats"] == {"reviewed": 1}
    assert result["pending_identifications"] == 2
    assert result["progress"] == {
        "percentage": 50,
        "stage": "identifying",
        "files_processed": "2/4",
        "pages_processed": 7,
        "students_identified": 3,
        "submissions_grouped": 2,
        "submissions_graded": 1,
    }

    empty = SimpleNamespace(total_files=0, status=BatchStatus.UPLOADING)
    assert service._calculate_progress(empty) == {"percentage": 0, "stage": "uploading"}
    unknown = SimpleNamespace(
        total_files=1,
        status=SimpleNamespace(value="unexpected"),
        processed_files=0,
        total_pages=0,
        identified_students=0,
        grouped_submissions=0,
        graded_submissions=0,
    )
    assert service._calculate_progress(unknown)["percentage"] == 0


def test_process_files_tracks_success_and_failure():
    batch = SimpleNamespace(
        id=uuid4(),
        status=BatchStatus.UPLOADING,
        processed_files=0,
        failed_files=0,
        total_pages=0,
    )
    successful = SimpleNamespace(
        id=uuid4(),
        original_filename="ok.png",
        status=FileStatus.PENDING,
        processed_pages=0,
        processed_at=None,
    )
    failed = SimpleNamespace(
        id=uuid4(),
        original_filename="bad.png",
        status=FileStatus.PENDING,
        processed_pages=0,
        processed_at=None,
    )
    query = MagicMock()
    query.filter.return_value.all.return_value = [successful, failed]
    service = _service(batch)
    service.db.query.return_value = query
    service._process_file = MagicMock(
        side_effect=[[object(), object()], RuntimeError("decode failed")]
    )

    result = service.process_batch_files(batch.id)

    assert result.status is BatchStatus.IDENTIFYING
    assert successful.status is FileStatus.PROCESSED
    assert successful.processed_pages == 2
    assert failed.status is FileStatus.FAILED
    assert failed.error_message == "decode failed"
    assert batch.processed_files == 1
    assert batch.failed_files == 1
    assert batch.total_pages == 2


def test_process_image_creates_a_page_and_dispatches_file_type():
    service = _service()
    service.ocr = SimpleNamespace(
        process_page=lambda _path: {
            "processed_path": "scan_processed.png",
            "rotation": 90,
            "perspective_corrected": True,
            "confidence": 95,
            "full_text": "RA: 12345678",
        }
    )
    file = SimpleNamespace(id=uuid4(), stored_path="scan.png", file_type="image")

    pages = service._process_file(file)

    assert len(pages) == 1
    assert pages[0].batch_file_id == file.id
    assert pages[0].original_image_path == "scan.png"
    assert pages[0].processed_image_path == "scan_processed.png"
    assert pages[0].rotation_angle == 90
    assert pages[0].perspective_corrected is True
    assert pages[0].ocr_confidence == 95
    assert pages[0].full_text == "RA: 12345678"
    assert service.db.add.call_args.args[0] is pages[0]


def test_process_pdf_extracts_each_page_and_closes_document(monkeypatch):
    pages = [MagicMock(), MagicMock()]
    document = MagicMock()
    document.__len__.return_value = 2
    document.__getitem__.side_effect = pages
    monkeypatch.setitem(
        __import__("sys").modules,
        "fitz",
        SimpleNamespace(open=lambda _path: document),
    )
    service = _service()
    service.ocr = SimpleNamespace(
        process_page=lambda path: {"processed_path": f"{path}.processed"}
    )
    file = SimpleNamespace(id=uuid4(), stored_path="exam.pdf")

    results = service._process_pdf(file)

    assert [page.page_number for page in results] == [1, 2]
    assert [page.original_image_path for page in results] == [
        "exam_page1.png",
        "exam_page2.png",
    ]
    assert all(page.processed_image_path.endswith(".processed") for page in results)
    document.close.assert_called_once()


@pytest.mark.parametrize(
    (
        "text",
        "ra_student",
        "registration_student",
        "enrolled",
        "expected_status",
        "expected_match",
    ),
    [
        ("RA: RA-123", "student", None, True, IdentificationStatus.IDENTIFIED, "ra_only"),
        (
            "RA: RA-123 Matrícula: MAT-456",
            "student",
            "student",
            True,
            IdentificationStatus.IDENTIFIED,
            "ra_and_registration_number",
        ),
        (
            "RA: RA-123 Matrícula: MAT-456",
            "student",
            "other",
            True,
            IdentificationStatus.CONFLICT,
            "none",
        ),
        (
            "RA: RA-123 Matrícula: MAT-456",
            "student",
            None,
            True,
            IdentificationStatus.CONFLICT,
            "none",
        ),
        (
            "Matrícula: MAT-456",
            None,
            "student",
            True,
            IdentificationStatus.IDENTIFIED,
            "registration_number_only",
        ),
        (
            "Matrícula: MAT-456",
            None,
            None,
            True,
            IdentificationStatus.NOT_FOUND,
            "none",
        ),
        ("RA: RA-123", "student", None, False, IdentificationStatus.NOT_FOUND, "none"),
        ("sem identificação", None, None, True, IdentificationStatus.PENDING, "none"),
    ],
)
def test_identify_page_resolves_supported_identifier_cases(
    text,
    ra_student,
    registration_student,
    enrolled,
    expected_status,
    expected_match,
):
    service = _service()
    students = {
        "student": SimpleNamespace(id=uuid4()),
        "other": SimpleNamespace(id=uuid4()),
    }
    service.student_repo.get_by_ra.return_value = students.get(ra_student)
    service.student_repo.get_by_registration_number.return_value = students.get(
        registration_student
    )
    service._student_is_enrolled_for_page = MagicMock(return_value=enrolled)
    page = SimpleNamespace(id=uuid4(), full_text=text, batch_file_id=uuid4())

    result = service._identify_page(page)

    assert result.page_id == page.id
    assert result.status is expected_status
    assert result.match_type == expected_match
    assert result.raw_response["ocr_text"] == text
    assert result.ra_confidence == (Decimal("95") if "RA:" in text else None)
    if expected_status is IdentificationStatus.IDENTIFIED:
        assert result.matched_student_id is not None
    else:
        assert result.matched_student_id is None


def test_identify_students_counts_success_and_audits_page_errors():
    batch = SimpleNamespace(id=uuid4(), status=BatchStatus.PROCESSING, identified_students=0)
    service = _service(batch)
    first, second = SimpleNamespace(id=uuid4()), SimpleNamespace(id=uuid4())
    service.db.query.return_value.join.return_value.filter.return_value.all.return_value = [
        first,
        second,
    ]
    service._identify_page = MagicMock(
        side_effect=[
            SimpleNamespace(status=IdentificationStatus.IDENTIFIED),
            RuntimeError("bad OCR"),
        ]
    )

    result = service.identify_students(batch.id)

    assert result.identified_students == 1
    assert result.status is BatchStatus.GROUPING
    assert service.db.add.call_count == 1


def test_group_pages_groups_identifications_by_student():
    batch = SimpleNamespace(
        id=uuid4(),
        exam_id=uuid4(),
        version_id=uuid4(),
        status=BatchStatus.IDENTIFYING,
        grouped_submissions=0,
    )
    student_id = uuid4()
    page_ids = [uuid4(), uuid4()]
    identifications = [
        SimpleNamespace(matched_student_id=student_id, page_id=page_id)
        for page_id in page_ids
    ]
    service = _service(batch)
    service.exam_repo = MagicMock()
    service.exam_repo.get.return_value = SimpleNamespace(
        class_id=uuid4(), academic_period_id=uuid4()
    )
    service._student_is_enrolled_for_exam = MagicMock(return_value=True)
    service.db.get.side_effect = [
        batch,
        *[SimpleNamespace(id=page_id) for page_id in page_ids],
    ]
    service.db.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = (
        identifications
    )

    result = service.group_pages(batch.id)

    group = service.db.add.call_args.args[0]
    assert group.page_ids == [str(page_id) for page_id in page_ids]
    assert group.student_id == student_id
    assert group.status is PageGroupStatus.GROUPED
    assert group.confidence == Decimal("90")
    assert result.grouped_submissions == 1
    assert result.status is BatchStatus.GRADING


def test_create_submissions_from_groups_associates_available_pages():
    batch = SimpleNamespace(id=uuid4(), exam_id=uuid4())
    exam = SimpleNamespace(class_id=uuid4(), academic_period_id=uuid4())
    page_id = uuid4()
    page = SimpleNamespace(id=page_id, original_image_path="scan.png", submission_id=None)
    missing_page_id = uuid4()
    group = SimpleNamespace(
        version_id=uuid4(),
        student_id=uuid4(),
        page_ids=[str(page_id), str(missing_page_id)],
        created_submission_id=None,
    )
    service = _service(batch)
    service.exam_repo = MagicMock()
    service.exam_repo.get.return_value = exam
    service._student_is_enrolled_for_exam = MagicMock(return_value=True)
    service.db.query.return_value.filter.return_value.all.return_value = [group]
    service.db.get.side_effect = [batch, page, None]

    submissions = service.create_submissions_from_groups(batch.id)

    assert len(submissions) == 1
    submission = submissions[0]
    assert submission.status is SubmissionStatus.AWAITING_CORRECTION
    assert submission.identified_student_id == group.student_id
    assert submission.original_files == ["scan.png"]
    assert page.submission_id == submission.id
    assert group.created_submission_id == submission.id


def test_create_submissions_blocks_student_without_active_enrollment():
    batch = SimpleNamespace(id=uuid4(), exam_id=uuid4())
    group = SimpleNamespace(
        id=uuid4(),
        version_id=uuid4(),
        student_id=uuid4(),
        page_ids=[],
        created_submission_id=None,
        status=PageGroupStatus.GROUPED,
        conflict_details={},
    )
    service = _service(batch)
    service.exam_repo = MagicMock()
    service.exam_repo.get.return_value = SimpleNamespace(
        class_id=uuid4(), academic_period_id=uuid4()
    )
    service._student_is_enrolled_for_exam = MagicMock(return_value=False)
    service.db.query.return_value.filter.return_value.all.return_value = [group]

    submissions = service.create_submissions_from_groups(batch.id)

    assert submissions == []
    assert group.status is PageGroupStatus.CONFLICT
    assert group.conflict_details["student_not_enrolled_in_exam_class"] is True
    assert group.created_submission_id is None


@pytest.mark.asyncio
async def test_grade_all_submissions_sets_completed_or_partial_status():
    batch = SimpleNamespace(
        id=uuid4(),
        status=BatchStatus.GROUPING,
        graded_submissions=0,
        pending_review=0,
    )
    submissions = [SimpleNamespace(id=uuid4()), SimpleNamespace(id=uuid4())]
    service = _service(batch)
    service.db.query.return_value.filter.return_value.all.return_value = submissions
    service.ai_service = SimpleNamespace(
        batch_correct=AsyncMock(
            side_effect=[
                SimpleNamespace(total_processed=3, requires_review_count=1),
                SimpleNamespace(total_processed=2, requires_review_count=0),
            ]
        )
    )

    result = await service.grade_all_submissions(batch.id)

    assert result.graded_submissions == 5
    assert result.pending_review == 1
    assert result.status is BatchStatus.PARTIAL

    service.ai_service.batch_correct = AsyncMock(
        return_value=SimpleNamespace(total_processed=1, requires_review_count=0)
    )
    batch.pending_review = 0
    result = await service.grade_all_submissions(batch.id)
    assert result.status is BatchStatus.COMPLETED
    assert result.processing_completed_at is not None


def test_manual_identification_updates_record_and_missing_entities_raise():
    service = _service()
    student_id, teacher_id, identification_id = uuid4(), uuid4(), uuid4()
    page_id, file_id, batch_id = uuid4(), uuid4(), uuid4()
    period_id, class_id = uuid4(), uuid4()
    ident = SimpleNamespace(
        id=identification_id,
        page_id=page_id,
        submission_id=uuid4(),
        status=IdentificationStatus.PENDING,
        matched_student_id=None,
        manual_override=False,
    )
    student = SimpleNamespace(id=student_id)
    page = SimpleNamespace(batch_file_id=file_id)
    batch_file = SimpleNamespace(batch_id=batch_id)
    batch = SimpleNamespace(id=batch_id, exam_id=uuid4())
    exam = SimpleNamespace(class_id=class_id, academic_period_id=period_id)
    service.exam_repo = MagicMock()
    service.exam_repo.get.return_value = exam
    service.db.get.side_effect = [
        ident,
        page,
        batch_file,
        batch,
        batch_file,
        batch,
    ]
    service.db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
        id=uuid4()
    )
    service.student_repo.get.return_value = student

    updated = service.manual_identify(identification_id, student_id, teacher_id)

    assert updated.status is IdentificationStatus.MANUAL
    assert updated.manual_override is True
    assert updated.overridden_by == teacher_id
    assert updated.overridden_at is not None

    service.db.get.side_effect = [None]
    with pytest.raises(NotFoundError, match="Identificação não encontrada"):
        service.manual_identify(identification_id, student_id, teacher_id)
    service.db.get.side_effect = [ident]
    service.student_repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Aluno não encontrado"):
        service.manual_identify(identification_id, student_id, teacher_id)


def test_pending_identifications_query_and_audit_log():
    service = _service()
    expected = [SimpleNamespace(status=IdentificationStatus.CONFLICT)]
    service.db.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = (
        expected
    )

    assert service.get_pending_identifications(uuid4()) == expected

    service._log_audit(uuid4(), "test", "Batch", uuid4(), "description")
    audit = service.db.add.call_args.args[0]
    assert audit.action == "test"
    assert audit.description == "description"
