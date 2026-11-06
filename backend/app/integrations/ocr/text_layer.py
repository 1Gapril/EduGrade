"""Extração de respostas da camada de texto de PDFs digitais.

Quando o PDF já contém texto (prova digitada ou digitalizada com OCR embutido),
não é necessário executar OCR nas imagens. Esta camada lê o documento original e
associa cada resposta à numeração da questão, mantendo a confiança da leitura.
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger("edugrade.ocr.text_layer")

QUESTION_RE = re.compile(r"Quest[ãa]o\s+(\d+)", re.IGNORECASE)
RESPONSE_RE = re.compile(r"Resposta\s*:\s*([^\r\n]+)", re.IGNORECASE)


def extract_answers_from_pdf(pdf_path: str | Path) -> list[dict]:
    """Lê respostas ``Resposta: X`` associadas a ``Questão N`` no texto do PDF.

    Retorna uma lista de dicionários com ``question_order``, ``extracted_text`` e
    ``ocr_confidence`` (100, pois o texto vem do próprio PDF).
    """
    path = Path(pdf_path)
    if path.suffix.lower() != ".pdf" or not path.is_file():
        return []

    try:
        import pymupdf
    except ImportError:  # pragma: no cover - dependência opcional
        logger.warning("PyMuPDF indisponível para ler a camada de texto do PDF.")
        return []

    try:
        with pymupdf.open(path) as document:
            text = "\n".join(page.get_text("text") for page in document)
    except Exception as error:  # pragma: no cover - PDF corrompido
        logger.warning("Não foi possível ler o PDF %s: %s", path, error)
        return []

    if "Resposta" not in text:
        return []

    matches = list(QUESTION_RE.finditer(text))
    answers: list[dict] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        segment = text[start:end]
        response = RESPONSE_RE.search(segment)
        if response is None:
            continue
        value = response.group(1).strip()
        if not value:
            continue
        answers.append(
            {
                "question_order": int(match.group(1)),
                "extracted_text": value,
                "ocr_confidence": 100.0,
            }
        )
    return answers
