"""Processador de OCR para digitalização de provas."""

from typing import Any

import cv2
import numpy as np
import pytesseract

from backend.app.core.config import settings
from backend.app.core.exceptions import ExternalServiceError


class OCRProcessor:
    """Processador de OCR para imagens de provas."""

    def __init__(
        self,
        tesseract_path: str | None = None,
        language: str = "por",
        dpi: int = 300,
    ):
        self.tesseract_path = tesseract_path or settings.tesseract_path
        self.language = language
        self.dpi = dpi
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

    def process_page(self, image_path: str) -> dict[str, Any]:
        """
        Processa uma página de prova.

        Returns:
            Dict com:
            - processed_path: caminho da imagem processada
            - rotation: ângulo de rotação aplicado
            - perspective_corrected: bool
            - confidence: confiança média do OCR
            - extracted_answers: lista de respostas extraídas
            - full_text: texto completo da página
        """
        # Carrega imagem
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Não foi possível carregar imagem: {image_path}")

        # 1. Correção de rotação
        rotation = self._detect_rotation(image)
        if rotation != 0:
            image = self._rotate_image(image, rotation)

        # 2. Correção de perspectiva
        perspective_corrected = False
        image, perspective_corrected = self._correct_perspective(image)

        # 3. Pré-processamento para OCR
        processed = self._preprocess_for_ocr(image)

        # 4. Salva imagem processada
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, processed)

        # 5. OCR completo
        ocr_data = self._run_ocr(processed)
        full_text = ocr_data.get('text', '')
        confidence = ocr_data.get('confidence', 0)

        # 6. Extrai respostas por região (simplificado - seria melhor com detecção de layout)
        extracted_answers = self._extract_answers_by_layout(processed, ocr_data)

        return {
            "processed_path": processed_path,
            "rotation": rotation,
            "perspective_corrected": perspective_corrected,
            "confidence": confidence,
            "extracted_answers": extracted_answers,
            "full_text": full_text,
            "ocr_data": ocr_data,
        }

    def _detect_rotation(self, image: np.ndarray) -> float:
        """Detecta rotação da imagem usando OSD do Tesseract."""
        try:
            osd = pytesseract.image_to_osd(image, config='--psm 0')
            for line in osd.split('\n'):
                if 'Rotate:' in line:
                    return float(line.split(':')[1].strip())
        except Exception:
            pass
        return 0.0

    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotaciona imagem."""
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def _correct_perspective(self, image: np.ndarray) -> tuple:
        """Corrige perspectiva (detecta cantos do papel)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 200)

        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) == 4:
                # Encontrou retângulo (papel)
                pts = approx.reshape(4, 2)
                rect = self._order_points(pts)
                (tl, tr, br, bl) = rect

                width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
                width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
                max_width = max(int(width_a), int(width_b))

                height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
                height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
                max_height = max(int(height_a), int(height_b))

                dst = np.array([
                    [0, 0],
                    [max_width - 1, 0],
                    [max_width - 1, max_height - 1],
                    [0, max_height - 1]
                ], dtype="float32")

                M = cv2.getPerspectiveTransform(rect, dst)
                warped = cv2.warpPerspective(image, M, (max_width, max_height))
                return warped, True

        return image, False

    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """Ordena pontos: top-left, top-right, bottom-right, bottom-left."""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa imagem para melhorar OCR."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Binarização adaptativa
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Remoção de ruído
        denoised = cv2.medianBlur(binary, 3)

        # Morfologia para conectar caracteres
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)

        return morph

    def _run_ocr(self, image: np.ndarray) -> dict[str, Any]:
        """Executa OCR na imagem."""
        try:
            # Dados detalhados
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                output_type=pytesseract.Output.DICT,
                config=f'--psm 6 --dpi {self.dpi}'
            )

            # Texto completo
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=f'--psm 6 --dpi {self.dpi}'
            )

            # Confiança média (apenas palavras com conf > 0)
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return {
                'text': text.strip(),
                'confidence': round(avg_confidence, 2),
                'data': data,
                'word_count': len([w for w in data['text'] if w.strip()]),
            }
        except pytesseract.TesseractNotFoundError as e:
            raise ExternalServiceError(
                "Tesseract não encontrado. Instale o mecanismo OCR e configure TESSERACT_PATH.",
                detail=str(e),
            ) from e
        except pytesseract.TesseractError as e:
            error = str(e)
            if "traineddata" in error or "load language" in error:
                message = (
                    f"Modelo de idioma '{self.language}' do Tesseract não encontrado. "
                    "Instale o arquivo traineddata correspondente e configure TESSDATA_PREFIX."
                )
            else:
                message = "Tesseract não conseguiu processar a imagem."
            raise ExternalServiceError(message, detail=error) from e

    def _extract_answers_by_layout(
        self,
        image: np.ndarray,
        ocr_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Extrai respostas baseado no layout da prova.
        Versão simplificada - em produção usar detecção de questões por coordenadas.
        """
        data = ocr_data.get('data', {})
        if not data:
            return []

        # Agrupa texto por linhas (baseado em coordenadas y)
        lines = {}
        for i in range(len(data.get('text', []))):
            if data['text'][i].strip():
                y = data['top'][i]
                # Agrupa linhas próximas (tolerância 10px)
                line_key = (y // 10) * 10
                if line_key not in lines:
                    lines[line_key] = []
                lines[line_key].append({
                    'text': data['text'][i],
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'conf': data['conf'][i],
                })

        # Converte para lista de respostas extraídas
        extracted = []
        for _, words in sorted(lines.items()):
            line_text = ' '.join(w['text'] for w in words)
            avg_conf = sum(w['conf'] for w in words if w['conf'] > 0) / max(1, len([w for w in words if w['conf'] > 0]))

            # Tenta identificar número da questão
            import re
            q_match = re.match(r'^(\d+)[\.\)]\s*(.+)', line_text)
            if q_match:
                question_num = int(q_match.group(1))
                answer_text = q_match.group(2)
            else:
                question_num = None
                answer_text = line_text

            # Bounding box aproximado
            lefts = [w['left'] for w in words]
            tops = [w['top'] for w in words]
            rights = [w['left'] + w['width'] for w in words]
            bottoms = [w['top'] + w['height'] for w in words]

            extracted.append({
                "question_order": question_num,
                "question_id": None,  # Será preenchido depois via matching
                "extracted_text": answer_text,
                "ocr_confidence": round(avg_conf, 2),
                "bounding_box": {
                    "x": min(lefts),
                    "y": min(tops),
                    "width": max(rights) - min(lefts),
                    "height": max(bottoms) - min(tops),
                },
            })

        return extracted

    def extract_question_regions(
        self,
        image_path: str,
        question_areas: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Extrai regiões específicas de questões.

        question_areas: Lista de dicts com {question_id, x, y, width, height, page}
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Não foi possível carregar: {image_path}")

        results = []
        for area in question_areas:
            x, y, w, h = area['x'], area['y'], area['width'], area['height']
            roi = image[y:y+h, x:x+w]

            # OCR na região
            text = pytesseract.image_to_string(
                roi, lang=self.language, config=f'--psm 6 --dpi {self.dpi}'
            )
            data = pytesseract.image_to_data(
                roi, lang=self.language, output_type=pytesseract.Output.DICT,
                config=f'--psm 6 --dpi {self.dpi}'
            )

            confs = [int(c) for c in data['conf'] if int(c) > 0]
            avg_conf = sum(confs) / len(confs) if confs else 0

            # Salva recorte
            crop_path = image_path.replace('.', f'_q{area["question_id"]}.')
            cv2.imwrite(crop_path, roi)

            results.append({
                "question_id": area['question_id'],
                "extracted_text": text.strip(),
                "ocr_confidence": round(avg_conf, 2),
                "extracted_image_path": crop_path,
                "bounding_box": {"x": x, "y": y, "width": w, "height": h},
            })

        return results


class PaddleOCRProcessor:
    """Wrapper para PaddleOCR (melhor para manuscrito)."""

    def __init__(self, lang: str = "pt", use_gpu: bool = False):
        self.lang = lang
        self.use_gpu = use_gpu
        self._ocr = None

    def _get_ocr(self):
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang, use_gpu=self.use_gpu)
            except ImportError as error:
                raise RuntimeError(
                    "PaddleOCR não instalado. Instale com: pip install paddleocr"
                ) from error
        return self._ocr

    def process(self, image_path: str) -> list[dict[str, Any]]:
        """Processa imagem com PaddleOCR."""
        ocr = self._get_ocr()
        result = ocr.ocr(image_path, cls=True)

        extracted = []
        if result and result[0]:
            for line in result[0]:
                bbox, (text, confidence) = line
                extracted.append({
                    "text": text,
                    "confidence": round(confidence * 100, 2),
                    "bbox": bbox,
                })
        return extracted
