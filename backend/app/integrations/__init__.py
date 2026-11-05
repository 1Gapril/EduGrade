"""Integrations package initialization."""

from backend.app.integrations.ocr.processor import OCRProcessor, PaddleOCRProcessor
from backend.app.integrations.pdf.generator import PDFGenerator
from backend.app.integrations.qr.generator import QRCodeGenerator

__all__ = [
    "PDFGenerator",
    "QRCodeGenerator",
    "OCRProcessor",
    "PaddleOCRProcessor",
]
