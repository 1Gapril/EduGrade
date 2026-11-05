import builtins
from unittest.mock import Mock

import numpy as np
import pytesseract
import pytest

from backend.app.core.exceptions import ExternalServiceError
from backend.app.integrations.ocr.processor import OCRProcessor, PaddleOCRProcessor


def test_process_page_runs_pipeline_and_returns_extracted_answers(monkeypatch, tmp_path):
    processor = OCRProcessor()
    image = np.zeros((20, 20, 3), dtype=np.uint8)
    ocr_data = {
        "text": "1. resposta",
        "confidence": 92,
        "data": {
            "text": ["1.", "resposta"],
            "conf": [90, 94],
            "left": [1, 15],
            "top": [2, 2],
            "width": [10, 20],
            "height": [5, 5],
        },
    }
    monkeypatch.setattr("backend.app.integrations.ocr.processor.cv2.imread", lambda _path: image)
    monkeypatch.setattr("backend.app.integrations.ocr.processor.cv2.imwrite", lambda *_args: True)
    monkeypatch.setattr(processor, "_detect_rotation", lambda _image: 90)
    monkeypatch.setattr(processor, "_rotate_image", lambda current, _angle: current)
    monkeypatch.setattr(processor, "_correct_perspective", lambda current: (current, True))
    monkeypatch.setattr(processor, "_preprocess_for_ocr", lambda current: current)
    monkeypatch.setattr(processor, "_run_ocr", lambda _image: ocr_data)

    result = processor.process_page(str(tmp_path / "exam.png"))

    assert result["rotation"] == 90
    assert result["perspective_corrected"]
    assert result["confidence"] == 92
    assert result["extracted_answers"][0]["question_order"] == 1
    assert result["extracted_answers"][0]["extracted_text"] == "resposta"
    assert result["extracted_answers"][0]["bounding_box"] == {
        "x": 1,
        "y": 2,
        "width": 34,
        "height": 5,
    }


def test_process_page_rejects_unreadable_image(monkeypatch):
    monkeypatch.setattr("backend.app.integrations.ocr.processor.cv2.imread", lambda _path: None)

    with pytest.raises(ValueError, match="Não foi possível carregar imagem"):
        OCRProcessor().process_page("missing.png")


def test_rotation_detection_and_point_ordering():
    processor = OCRProcessor()
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    monkeypatch_result = Mock(return_value="Rotate: 270\n")
    original = pytesseract.image_to_osd
    pytesseract.image_to_osd = monkeypatch_result
    try:
        assert processor._detect_rotation(image) == 270
    finally:
        pytesseract.image_to_osd = original

    ordered = processor._order_points(
        np.array([[10, 10], [0, 0], [10, 0], [0, 10]], dtype=np.float32)
    )
    assert ordered.tolist() == [[0, 0], [10, 0], [10, 10], [0, 10]]


def test_rotation_detection_returns_zero_when_osd_fails(monkeypatch):
    monkeypatch.setattr(
        pytesseract,
        "image_to_osd",
        Mock(side_effect=pytesseract.TesseractNotFoundError()),
    )
    assert OCRProcessor()._detect_rotation(np.zeros((10, 10, 3), dtype=np.uint8)) == 0


def test_preprocess_and_perspective_detection_on_blank_image():
    processor = OCRProcessor()
    image = np.full((100, 100, 3), 255, dtype=np.uint8)

    processed = processor._preprocess_for_ocr(image)
    unchanged, corrected = processor._correct_perspective(image)

    assert processed.shape == (100, 100)
    assert unchanged is image
    assert not corrected


def test_run_ocr_calculates_average_confidence(monkeypatch):
    monkeypatch.setattr(
        pytesseract,
        "image_to_data",
        lambda *_args, **_kwargs: {"conf": ["90", "-1", "70"], "text": ["one", "", "two"]},
    )
    monkeypatch.setattr(pytesseract, "image_to_string", lambda *_args, **_kwargs: " answer \n")

    result = OCRProcessor()._run_ocr(np.zeros((5, 5), dtype=np.uint8))

    assert result["text"] == "answer"
    assert result["confidence"] == 80
    assert result["word_count"] == 2


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (pytesseract.TesseractNotFoundError(), "Tesseract não encontrado"),
        (pytesseract.TesseractError(1, "traineddata missing"), "Modelo de idioma"),
        (pytesseract.TesseractError(1, "processing error"), "não conseguiu processar"),
    ],
)
def test_run_ocr_translates_tesseract_errors(monkeypatch, error, message):
    monkeypatch.setattr(pytesseract, "image_to_data", Mock(side_effect=error))

    with pytest.raises(ExternalServiceError, match=message):
        OCRProcessor()._run_ocr(np.zeros((5, 5), dtype=np.uint8))


def test_extract_answers_groups_words_and_handles_empty_data():
    processor = OCRProcessor()
    data = {
        "text": ["2.", "resposta", "livre"],
        "left": [10, 25, 4],
        "top": [10, 15, 50],
        "width": [10, 20, 12],
        "height": [5, 6, 8],
        "conf": [80, 100, 0],
    }

    answers = processor._extract_answers_by_layout(np.zeros((1, 1)), {"data": data})

    assert [answer["question_order"] for answer in answers] == [2, None]
    assert answers[0]["extracted_text"] == "resposta"
    assert answers[0]["ocr_confidence"] == 90
    assert answers[1]["ocr_confidence"] == 0
    assert processor._extract_answers_by_layout(np.zeros((1, 1)), {}) == []


def test_extract_question_regions_returns_text_confidence_and_saved_crop(monkeypatch):
    monkeypatch.setattr(
        "backend.app.integrations.ocr.processor.cv2.imread",
        lambda _path: np.zeros((20, 20, 3), dtype=np.uint8),
    )
    monkeypatch.setattr(
        "backend.app.integrations.ocr.processor.cv2.imwrite", lambda *_args: True
    )
    monkeypatch.setattr(pytesseract, "image_to_string", lambda *_args, **_kwargs: " answer ")
    monkeypatch.setattr(
        pytesseract,
        "image_to_data",
        lambda *_args, **_kwargs: {"conf": ["75", "-1"]},
    )

    results = OCRProcessor().extract_question_regions(
        "exam.png",
        [{"question_id": "q1", "x": 1, "y": 2, "width": 5, "height": 6}],
    )

    assert results == [
        {
            "question_id": "q1",
            "extracted_text": "answer",
            "ocr_confidence": 75,
            "extracted_image_path": "exam_qq1.png",
            "bounding_box": {"x": 1, "y": 2, "width": 5, "height": 6},
        }
    ]


def test_extract_question_regions_rejects_unreadable_image(monkeypatch):
    monkeypatch.setattr("backend.app.integrations.ocr.processor.cv2.imread", lambda _path: None)

    with pytest.raises(ValueError, match="Não foi possível carregar"):
        OCRProcessor().extract_question_regions("missing.png", [])


def test_paddle_ocr_processes_lines_and_returns_empty_for_no_results():
    processor = PaddleOCRProcessor()
    ocr = Mock()
    ocr.ocr.side_effect = [
        [[([[0, 0], [1, 0], [1, 1], [0, 1]], ("texto", 0.8765))]],
        [[]],
    ]
    processor._ocr = ocr

    assert processor.process("exam.png") == [
        {"text": "texto", "confidence": 87.65, "bbox": [[0, 0], [1, 0], [1, 1], [0, 1]]}
    ]
    assert processor.process("blank.png") == []


def test_paddle_ocr_reports_missing_dependency(monkeypatch):
    original_import = builtins.__import__

    def fail_paddle(name, *args, **kwargs):
        if name == "paddleocr":
            raise ImportError("not installed")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_paddle)

    with pytest.raises(RuntimeError, match="PaddleOCR não instalado"):
        PaddleOCRProcessor()._get_ocr()
