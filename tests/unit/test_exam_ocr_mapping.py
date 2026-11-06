from types import SimpleNamespace
from uuid import uuid4

import pytest

from backend.app.core.config import settings
from backend.app.core.exceptions import ExternalServiceError
from backend.app.integrations.ocr import processor as ocr_processor
from backend.app.models.grading_batch import IdentificationStatus
from backend.app.schemas.ai_correction import BatchCorrectionRequest
from backend.app.services import exam_service
from backend.app.services.ai_correction_service import AICorrectionService
from backend.app.services.batch_grading_service import BatchGradingService


def test_process_ocr_maps_processor_fields_to_question(monkeypatch):
    question_id = uuid4()
    page = SimpleNamespace(
        id=uuid4(),
        extracted_answers=[],
        original_image_path="scan.png",
        processed_image_path=None,
        rotation_angle=0,
        perspective_corrected=False,
        ocr_confidence=None,
    )
    submission = SimpleNamespace(
        id=uuid4(),
        version=SimpleNamespace(exam_id=uuid4()),
        pages=[page],
        processed_files=[],
        status=None,
        processed_at=None,
    )

    class FakeDatabase:
        def flush(self):
            pass

    class FakeSubmissionRepository:
        def get_with_pages(self, _submission_id):
            return submission

    class FakeQuestionRepository:
        def __init__(self, _db):
            pass

        def get_by_exam(self, _exam_id):
            return [SimpleNamespace(id=question_id, question_order=1)]

    class FakeOCRProcessor:
        def process_page(self, _image_path):
            return {
                "processed_path": "scan_processed.png",
                "extracted_answers": [
                    {
                        "question_order": 1,
                        "extracted_text": "Resposta lida",
                        "ocr_confidence": 94.5,
                        "bounding_box": {"x": 1},
                    }
                ],
            }

    monkeypatch.setattr(exam_service, "ExamQuestionRepository", FakeQuestionRepository)
    monkeypatch.setattr(
        "backend.app.integrations.ocr.processor.OCRProcessor",
        FakeOCRProcessor,
    )
    service = exam_service.SubmissionService.__new__(exam_service.SubmissionService)
    service.db = FakeDatabase()
    service.repo = FakeSubmissionRepository()

    service.process_ocr(submission.id)

    assert len(page.extracted_answers) == 1
    answer = page.extracted_answers[0]
    assert answer.question_id == question_id
    assert answer.extracted_text == "Resposta lida"
    assert answer.ocr_confidence == 94.5
    assert answer.bounding_box == {"x": 1}
    assert submission.processed_files == ["scan_processed.png"]


@pytest.mark.asyncio
async def test_batch_correction_skips_questions_without_ocr_answers():
    class FakeSubmissionRepository:
        def get(self, _submission_id):
            return SimpleNamespace(version=SimpleNamespace(exam_id=uuid4()))

    class FakeQuestionRepository:
        def get_by_exam(self, _exam_id):
            return [SimpleNamespace(id=uuid4())]

    class FakeAnswerRepository:
        def get_all_by_submission_question(self, _submission_id, _question_id):
            return []

    service = AICorrectionService.__new__(AICorrectionService)
    service.submission_repo = FakeSubmissionRepository()
    service.question_repo = FakeQuestionRepository()
    service.answer_repo = FakeAnswerRepository()

    result = await service.batch_correct(BatchCorrectionRequest(submission_id=uuid4()))

    assert result.total_processed == 0
    assert result.failed == 0
    assert result.skipped == 1


def test_ocr_processor_uses_configured_tesseract_path(monkeypatch):
    configured_path = r"C:\OCR\tesseract.exe"
    monkeypatch.setattr(settings, "tesseract_path", configured_path)

    processor = ocr_processor.OCRProcessor()

    assert processor.tesseract_path == configured_path
    assert ocr_processor.pytesseract.pytesseract.tesseract_cmd == configured_path


def test_ocr_processor_reports_missing_language_data(monkeypatch):
    def missing_language(*_args, **_kwargs):
        raise ocr_processor.pytesseract.TesseractError(
            1,
            "Error opening data file por.traineddata; Failed loading language 'por'",
        )

    monkeypatch.setattr(ocr_processor.pytesseract, "image_to_data", missing_language)
    processor = ocr_processor.OCRProcessor(tesseract_path="tesseract")

    with pytest.raises(ExternalServiceError, match="Modelo de idioma 'por'.*não encontrado"):
        processor._run_ocr(None)


def test_identification_with_unregistered_matricula_requires_manual_review():
    student = SimpleNamespace(id=uuid4())
    page = SimpleNamespace(
        id=uuid4(),
        full_text="RA: 12345678 Matrícula: 87654321",
    )
    service = BatchGradingService.__new__(BatchGradingService)
    service.student_repo = SimpleNamespace(
        get_by_ra=lambda ra: student if ra == "12345678" else None,
        get_by_registration_number=lambda _registration_number: None,
    )
    service.db = SimpleNamespace(add=lambda _result: None, flush=lambda: None)

    result = service._identify_page(page)

    assert result.status == IdentificationStatus.CONFLICT
    assert result.matched_student_id is None
    assert result.conflict_details["registration_number_not_found"] == "87654321"
