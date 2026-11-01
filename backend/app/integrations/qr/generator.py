"""Gerador de QR Code para identificação de provas."""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from io import BytesIO
from typing import Dict, Any, Optional
import base64
from PIL import Image


class QRCodeGenerator:
    """Gerador de QR Codes para provas."""

    def __init__(
        self,
        version: int = 1,
        error_correction: int = qrcode.constants.ERROR_CORRECT_M,
        box_size: int = 10,
        border: int = 4,
    ):
        self.version = version
        self.error_correction = error_correction
        self.box_size = box_size
        self.border = border

    def generate(
        self,
        data: Dict[str, Any],
        output_path: Optional[str] = None,
        styled: bool = False,
    ) -> bytes:
        """
        Gera QR Code.

        Args:
            data: Dados para codificar (dict será convertido para string)
            output_path: Caminho para salvar arquivo (opcional)
            styled: Usar estilo arredondado

        Returns:
            Bytes da imagem PNG
        """
        import json
        qr_data = json.dumps(data, ensure_ascii=False)

        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        if styled:
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(26, 26, 46)),
            )
        else:
            img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        png_bytes = buffer.getvalue()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(png_bytes)

        return png_bytes

    def generate_base64(self, data: Dict[str, Any], styled: bool = False) -> str:
        """Gera QR Code e retorna base64."""
        png_bytes = self.generate(data, styled=styled)
        return base64.b64encode(png_bytes).decode('utf-8')

    def generate_data_uri(self, data: Dict[str, Any], styled: bool = False) -> str:
        """Gera QR Code como data URI para HTML."""
        b64 = self.generate_base64(data, styled=styled)
        return f"data:image/png;base64,{b64}"

    def generate_batch(
        self,
        items: list[Dict[str, Any]],
        output_dir: str,
        prefix: str = "qr_",
    ) -> list[str]:
        """Gera múltiplos QR Codes em lote."""
        from pathlib import Path
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        paths = []
        for i, data in enumerate(items):
            filename = f"{prefix}{i+1:04d}.png"
            filepath = Path(output_dir) / filename
            self.generate(data, output_path=str(filepath))
            paths.append(str(filepath))
        return paths

    @staticmethod
    def parse_qr_data(qr_string: str) -> Dict[str, Any]:
        """Parseia dados do QR Code."""
        import json
        try:
            return json.loads(qr_string)
        except json.JSONDecodeError:
            # Tenta parsear como string simples
            return {"raw": qr_string}

    @staticmethod
    def build_exam_qr_data(
        exam_id: str,
        version_id: str,
        copy_identifier: str,
        student_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Constrói dados padrão para QR Code de prova."""
        data = {
            "exam_id": exam_id,
            "version_id": version_id,
            "copy_identifier": copy_identifier,
            "type": "exam_copy",
        }
        if student_id:
            data["student_id"] = student_id
        return data