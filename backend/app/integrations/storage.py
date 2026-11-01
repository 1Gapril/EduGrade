"""Armazenamento local de provas enviadas."""

from pathlib import Path
from uuid import uuid4

import fitz
from fastapi import HTTPException, UploadFile

from backend.app.core.config import settings


class FileStorage:
    """Salva uploads em diretórios controlados e expande PDFs em páginas OCR."""

    _folders = {
        "exams": settings.upload_dir,
        "processed": settings.processed_dir,
        "temp": settings.temp_dir,
    }

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[3]

    def _folder_path(self, folder: str) -> Path:
        configured_folder = self._folders.get(folder)
        if configured_folder is None:
            raise HTTPException(status_code=400, detail="Pasta de upload inválida.")
        path = Path(configured_folder)
        if not path.is_absolute():
            path = self.project_root / path
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def save(self, file: UploadFile, folder: str = "exams") -> str:
        extension = Path((file.filename or "").replace("\\", "/")).suffix.lower()
        allowed_extensions = {item.lower() for item in settings.allowed_extensions}
        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não permitido. Use: {', '.join(sorted(allowed_extensions))}.",
            )

        destination = self._folder_path(folder) / f"{uuid4().hex}{extension}"
        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        size = 0
        try:
            with destination.open("wb") as saved_file:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > max_bytes:
                        raise HTTPException(
                            status_code=413,
                            detail=f"O arquivo excede o limite de {settings.max_upload_size_mb} MB.",
                        )
                    saved_file.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        finally:
            await file.close()

        return str(destination)

    def expand_pdf_pages(self, file_path: str) -> list[str]:
        path = Path(file_path)
        if path.suffix.lower() != ".pdf":
            return [str(path)]

        output_dir = self._folder_path("processed") / uuid4().hex
        output_dir.mkdir(parents=True, exist_ok=True)
        page_paths = []
        try:
            with fitz.open(path) as document:
                if document.page_count == 0:
                    raise HTTPException(status_code=400, detail="O PDF enviado não contém páginas.")
                if document.page_count > 100:
                    raise HTTPException(status_code=400, detail="O PDF pode ter no máximo 100 páginas.")
                for page_number, page in enumerate(document, start=1):
                    image_path = output_dir / f"page_{page_number:03d}.png"
                    page.get_pixmap(dpi=180, alpha=False).save(image_path)
                    page_paths.append(str(image_path))
        except HTTPException:
            raise
        except (fitz.FileDataError, RuntimeError) as exc:
            raise HTTPException(status_code=400, detail="Não foi possível ler o PDF enviado.") from exc
        return page_paths
