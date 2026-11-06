import pymupdf
import pytest

from backend.app.core.exceptions import ExternalServiceError, FileProcessingError
from backend.app.services import exam_import_service


@pytest.mark.asyncio
async def test_analyze_pdfs_returns_reviewable_question_draft(monkeypatch):
    class FakeProvider:
        model = "fcc-model"

        async def generate_text(self, prompt, model, **kwargs):
            assert model == "fcc-model"
            assert "PROVA:" in prompt
            assert "GABARITO:" in prompt
            return """```json
            {
              "title": "Banco de Dados",
              "description": "Avaliação",
              "instructions": "Responda às questões.",
              "total_score": 10,
              "questions": [{
                "type": "multiple_choice",
                "statement": "O que é uma chave primária?",
                "score": 10,
                "alternatives": ["Identificador único", "Uma tabela"],
                "correct_answer": "A",
                "answer_needs_review": false
              }],
              "review_notes": []
            }
            ```"""

    monkeypatch.setattr(
        exam_import_service.ExamPDFImportService,
        "_extract_pdf_text",
        staticmethod(lambda _content: "Documento de prova"),
    )
    def get_fcc_provider(**kwargs):
        assert kwargs["provider_type"] == "fcc_claude"
        assert kwargs["db"] is None
        return FakeProvider()

    monkeypatch.setattr(
        exam_import_service.AIProviderFactory,
        "get_provider",
        get_fcc_provider,
    )

    result = await exam_import_service.ExamPDFImportService(None).analyze(
        b"exam", b"answer key"
    )

    assert result.title == "Banco de Dados"
    assert result.questions[0].statement == "O que é uma chave primária?"
    assert result.questions[0].correct_answer == "A"
    assert result.questions[0].answer_needs_review is False


@pytest.mark.asyncio
async def test_analyze_pdfs_does_not_invent_answer_key_when_absent(monkeypatch):
    captured_prompt = {}

    class FakeProvider:
        model = "fcc-model"

        async def generate_text(self, prompt, _model, **_kwargs):
            captured_prompt["value"] = prompt
            return """{
              "title": "Banco de Dados",
              "total_score": 1,
              "questions": [{
                "type": "short_answer",
                "statement": "Defina tabela.",
                "score": 1,
                "answer_needs_review": true
              }]
            }"""

    monkeypatch.setattr(
        exam_import_service.ExamPDFImportService,
        "_extract_pdf_text",
        staticmethod(lambda _content: "Texto do documento"),
    )
    monkeypatch.setattr(
        exam_import_service.AIProviderFactory,
        "get_provider",
        lambda **_kwargs: FakeProvider(),
    )

    result = await exam_import_service.ExamPDFImportService(None).analyze(b"exam", None)

    assert "Gabarito não enviado" in captured_prompt["value"]
    assert result.questions[0].answer_needs_review is True
    assert result.questions[0].expected_answer is None


def test_extract_pdf_text_reads_text_pdf():
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Questão 1: Explique uma chave primária.")
    content = document.tobytes()
    document.close()

    extracted = exam_import_service.ExamPDFImportService._extract_pdf_text(content)

    assert "Questão 1: Explique uma chave primária." in extracted


@pytest.mark.asyncio
async def test_analyze_pdfs_reports_invalid_ai_response(monkeypatch):
    class FakeProvider:
        model = "fcc-model"

        async def generate_text(self, *_args, **_kwargs):
            return "Não consegui extrair as questões."

    monkeypatch.setattr(
        exam_import_service.ExamPDFImportService,
        "_extract_pdf_text",
        staticmethod(lambda _content: "Texto do documento"),
    )
    monkeypatch.setattr(
        exam_import_service.AIProviderFactory,
        "get_provider",
        lambda **_kwargs: FakeProvider(),
    )

    with pytest.raises(ExternalServiceError, match="formato válido") as error:
        await exam_import_service.ExamPDFImportService(None).analyze(b"exam", None)
    assert error.value.detail == "A resposta da IA não contém um objeto JSON válido."


@pytest.mark.asyncio
async def test_analyze_pdfs_reports_invalid_fields_from_ai_response(monkeypatch):
    class FakeProvider:
        model = "fcc-model"

        async def generate_text(self, *_args, **_kwargs):
            return '{"title":"X","total_score":10,"questions":[]}'

    monkeypatch.setattr(
        exam_import_service.ExamPDFImportService,
        "_extract_pdf_text",
        staticmethod(lambda _content: "Texto do documento"),
    )
    monkeypatch.setattr(
        exam_import_service.AIProviderFactory,
        "get_provider",
        lambda **_kwargs: FakeProvider(),
    )

    with pytest.raises(ExternalServiceError) as error:
        await exam_import_service.ExamPDFImportService(None).analyze(b"exam", None)

    assert "title: String should have at least 2 characters" in error.value.detail
    assert "questions: List should have at least 1 item" in error.value.detail


@pytest.mark.asyncio
async def test_analyze_pdfs_reports_root_keys_when_exam_fields_are_nested(monkeypatch):
    class FakeProvider:
        model = "fcc-model"

        async def generate_text(self, *_args, **_kwargs):
            return '{"payload":{"message":"resposta sem campos da prova"}}'

    monkeypatch.setattr(
        exam_import_service.ExamPDFImportService,
        "_extract_pdf_text",
        staticmethod(lambda _content: "Texto do documento"),
    )
    monkeypatch.setattr(
        exam_import_service.AIProviderFactory,
        "get_provider",
        lambda **_kwargs: FakeProvider(),
    )

    with pytest.raises(ExternalServiceError) as error:
        await exam_import_service.ExamPDFImportService(None).analyze(b"exam", None)

    assert "title: Field required" in error.value.detail
    assert "total_score: Field required" in error.value.detail
    assert "questions: Field required" in error.value.detail
    assert "Campos no objeto recebido: payload." in error.value.detail


@pytest.mark.parametrize(
    "response",
    [
        '{"title":"Prova"}',
        'Resposta: {"title":"Prova"} fim.',
        '```json\n{"title":"Prova"}\n```',
        '```JSON\n{"title":"Prova"}\n```',
    ],
)
def test_decode_json_accepts_fenced_and_embedded_objects(response):
    assert exam_import_service.ExamPDFImportService._decode_json(response) == {
        "title": "Prova"
    }


@pytest.mark.parametrize(
    "response",
    [
        '{"data":{"title":"Prova","total_score":1,"questions":[{"statement":"Questão"}]}}',
        '{"result":"{\\"title\\":\\"Prova\\",\\"total_score\\":1,\\"questions\\":[{\\"statement\\":\\"Questão\\"}]}"}',
    ],
)
def test_decode_json_extracts_exam_from_response_envelopes(response):
    assert exam_import_service.ExamPDFImportService._decode_json(response) == {
        "title": "Prova",
        "total_score": 1,
        "questions": [{"statement": "Questão"}],
    }


@pytest.mark.parametrize("response", ["[]", "sem objeto", '{"incompleto": }'])
def test_decode_json_rejects_non_object_and_malformed_text(response):
    with pytest.raises(ValueError):
        exam_import_service.ExamPDFImportService._decode_json(response)


def _create_pdf(*page_texts):
    document = pymupdf.open()
    for text in page_texts:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_extract_pdf_text_rejects_invalid_pdf():
    with pytest.raises(FileProcessingError, match="Não foi possível ler"):
        exam_import_service.ExamPDFImportService._extract_pdf_text(b"not a pdf")


def test_extract_pdf_text_ocr_reads_pages_without_text(monkeypatch):
    from backend.app.integrations.ocr.processor import OCRProcessor

    monkeypatch.setattr(
        OCRProcessor,
        "_run_ocr",
        lambda _self, _image: {"text": "Texto reconhecido pelo OCR"},
    )

    extracted = exam_import_service.ExamPDFImportService._extract_pdf_text(
        _create_pdf("Página com texto", "")
    )

    assert "Página com texto" in extracted
    assert "Texto reconhecido pelo OCR" in extracted


def test_extract_pdf_text_rejects_document_without_text(monkeypatch):
    monkeypatch.setattr(
        exam_import_service.ExamPDFImportService,
        "_ocr_empty_pages",
        staticmethod(lambda _document, _page_texts: [""]),
    )

    with pytest.raises(FileProcessingError, match="Não foi possível extrair texto"):
        exam_import_service.ExamPDFImportService._extract_pdf_text(_create_pdf(""))


def test_extract_pdf_text_enforces_page_limit(monkeypatch):
    monkeypatch.setattr(exam_import_service.ExamPDFImportService, "MAX_PDF_PAGES", 1)

    with pytest.raises(FileProcessingError, match="no máximo 1 páginas"):
        exam_import_service.ExamPDFImportService._extract_pdf_text(
            _create_pdf("Página 1", "Página 2")
        )


def test_extract_pdf_text_enforces_character_limit(monkeypatch):
    monkeypatch.setattr(
        exam_import_service.ExamPDFImportService,
        "MAX_EXTRACTED_CHARACTERS",
        5,
    )

    with pytest.raises(FileProcessingError, match="muito extenso"):
        exam_import_service.ExamPDFImportService._extract_pdf_text(_create_pdf("Texto"))
