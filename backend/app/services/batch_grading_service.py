"""Service de Processamento em Lote (Batch Grading) - ADENDO OFICIAL."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models.grading_batch import (
    GradingBatch, BatchStatus, GradingBatchFile, FileStatus,
    ExamSubmissionPage, StudentIdentificationResult, IdentificationStatus,
    ExamPageGroup, PageGroupStatus, GradingAuditLog,
)
from backend.app.models.exam import ExamSubmission, SubmissionStatus, ExtractedAnswer
from backend.app.models.user import Student
from backend.app.repositories.exam_repository import (
    ExamRepository, ExamVersionRepository, ExamSubmissionRepository,
    ExamQuestionRepository, ExtractedAnswerRepository,
)
from backend.app.repositories.user_repository import StudentRepository
from backend.app.repositories.ai_correction_repository import AICorrectionRepository
from backend.app.services.ai_correction_service import AICorrectionService
from backend.app.integrations.ocr.processor import OCRProcessor
from backend.app.core.exceptions import ValidationError, NotFoundError, ExternalServiceError
from backend.app.core.config import settings


class BatchGradingService:
    """Serviço principal para processamento em lote de provas."""

    def __init__(self, db: Session):
        self.db = db
        self.batch_repo = GradingBatch
        self.file_repo = GradingBatchFile
        self.page_repo = ExamSubmissionPage
        self.id_repo = StudentIdentificationResult
        self.group_repo = ExamPageGroup
        self.submission_repo = ExamSubmissionRepository(db)
        self.student_repo = StudentRepository(db)
        self.exam_repo = ExamRepository(db)
        self.version_repo = ExamVersionRepository(db)
        self.question_repo = ExamQuestionRepository(db)
        self.answer_repo = ExtractedAnswerRepository(db)
        self.ai_correction_repo = AICorrectionRepository(db)
        self.ai_service = AICorrectionService(db)
        self.ocr = OCRProcessor()
        self._batch: Optional[GradingBatch] = None

    # ==================== Batch Management ====================

    def create_batch(self, exam_id: UUID, version_id: UUID, uploaded_by: UUID) -> GradingBatch:
        """Cria novo lote de processamento."""
        exam = self.exam_repo.get(exam_id)
        if not exam:
            raise NotFoundError("Prova não encontrada")

        version = self.version_repo.get(version_id)
        if not version:
            raise NotFoundError("Versão não encontrada")

        batch = GradingBatch(
            exam_id=exam_id,
            version_id=version_id,
            uploaded_by=uploaded_by,
            status=BatchStatus.UPLOADING,
        )
        self.db.add(batch)
        self.db.flush()
        return batch

    def add_files(self, batch_id: UUID, files: List[Dict[str, Any]]) -> List[GradingBatchFile]:
        """Adiciona arquivos ao lote."""
        batch = self.get_batch(batch_id)
        if batch.status != BatchStatus.UPLOADING:
            raise ValidationError("Lote não está em estado de upload")

        batch_files = []
        for file_data in files:
            bf = GradingBatchFile(
                batch_id=batch_id,
                original_filename=file_data["filename"],
                stored_path=file_data["path"],
                content_type=file_data["content_type"],
                file_size=file_data["size"],
                file_type=file_data["type"],  # image, pdf
                page_count=file_data.get("page_count", 1),
            )
            self.db.add(bf)
            batch_files.append(bf)

        batch.total_files = len(batch_files)
        batch.updated_at = datetime.now(timezone.utc)
        self.db.flush()

        self._log_audit(batch_id, "files_added", "GradingBatch", batch_id,
                       description=f"{len(batch_files)} arquivos adicionados ao lote",
                       new_values={"total_files": batch.total_files})
        return batch_files

    def start_processing(self, batch_id: UUID) -> GradingBatch:
        """Inicia processamento assíncrono do lote."""
        batch = self.get_batch(batch_id)
        batch.status = BatchStatus.PROCESSING
        batch.processing_started_at = datetime.now(timezone.utc)
        self.db.flush()

        self._log_audit(batch_id, "processing_started", "GradingBatch", batch_id,
                       description="Processamento do lote iniciado")

        return batch

    def get_batch(self, batch_id: UUID) -> GradingBatch:
        """Busca lote por ID."""
        batch = self.db.get(GradingBatch, batch_id)
        if not batch:
            raise NotFoundError("Lote não encontrado")
        return batch

    def get_batch_with_details(self, batch_id: UUID) -> Dict[str, Any]:
        """Retorna detalhes completos do lote para o painel."""
        batch = self.get_batch(batch_id)

        # Conta status dos arquivos
        from sqlalchemy import select, func
        file_stats = self.db.execute(
            select(GradingBatchFile.status, func.count(GradingBatchFile.id))
            .where(GradingBatchFile.batch_id == batch_id)
            .group_by(GradingBatchFile.status)
        ).all()

        file_status_map = {s.value: c for s, c in file_stats}

        # Conta submissões
        submission_stats = self.db.execute(
            select(ExamSubmission.status, func.count(ExamSubmission.id))
            .where(ExamSubmission.batch_id == batch_id)
            .group_by(ExamSubmission.status)
        ).all()

        submission_status_map = {s.value: c for s, c in submission_stats}

        # Identificações pendentes
        pending_ids = self.db.execute(
            select(func.count(StudentIdentificationResult.id))
            .where(
                StudentIdentificationResult.submission_id.in_(
                    select(ExamSubmission.id).where(ExamSubmission.batch_id == batch_id)
                ),
                StudentIdentificationResult.status.in_([
                    IdentificationStatus.PENDING, IdentificationStatus.AMBIGUOUS,
                    IdentificationStatus.CONFLICT, IdentificationStatus.NOT_FOUND
                ])
            )
        ).scalar_one()

        return {
            "batch": batch,
            "file_stats": file_status_map,
            "submission_stats": submission_status_map,
            "pending_identifications": pending_ids,
            "progress": self._calculate_progress(batch),
        }

    def _calculate_progress(self, batch: GradingBatch) -> Dict[str, Any]:
        """Calcula progresso do processamento."""
        if batch.total_files == 0:
            return {"percentage": 0, "stage": "uploading"}

        stages = {
            "uploading": 10,
            "processing_pages": 30,
            "identifying": 50,
            "grouping": 70,
            "grading": 90,
            "completed": 100,
        }

        current_stage = stages.get(batch.status.value, 0)
        return {
            "percentage": current_stage,
            "stage": batch.status.value,
            "files_processed": f"{batch.processed_files}/{batch.total_files}",
            "pages_processed": batch.total_pages,
            "students_identified": batch.identified_students,
            "submissions_grouped": batch.grouped_submissions,
            "submissions_graded": batch.graded_submissions,
        }

    # ==================== Page Processing ====================

    def process_batch_files(self, batch_id: UUID) -> GradingBatch:
        """Processa todos os arquivos do lote (páginas, OCR, etc.)."""
        batch = self.get_batch(batch_id)
        batch.status = BatchStatus.PROCESSING_PAGES

        files = self.db.query(GradingBatchFile).filter(
            GradingBatchFile.batch_id == batch_id,
            GradingBatchFile.status == FileStatus.PENDING
        ).all()

        total_pages = 0
        for file in files:
            try:
                file.status = FileStatus.PROCESSING
                self.db.flush()

                pages = self._process_file(file)
                file.processed_pages = len(pages)
                file.status = FileStatus.PROCESSED
                file.processed_at = datetime.now(timezone.utc)
                total_pages += len(pages)

                batch.processed_files += 1
                batch.total_pages = total_pages
                self.db.flush()

            except Exception as e:
                file.status = FileStatus.FAILED
                file.error_message = str(e)
                batch.failed_files += 1
                self._log_audit(batch_id, "file_failed", "GradingBatchFile", file.id,
                               description=f"Falha ao processar arquivo: {file.original_filename}",
                               success=False, error_message=str(e))
                self.db.flush()

        batch.status = BatchStatus.IDENTIFYING
        self.db.flush()
        return batch

    def _process_file(self, file: GradingBatchFile) -> List[ExamSubmissionPage]:
        """Processa um arquivo (imagem ou PDF) e extrai páginas."""
        pages = []

        if file.file_type == "pdf":
            pages = self._process_pdf(file)
        else:
            pages = self._process_image(file)

        return pages

    def _process_pdf(self, file: GradingBatchFile) -> List[ExamSubmissionPage]:
        """Processa PDF multipágina."""
        import fitz  # PyMuPDF
        doc = fitz.open(file.stored_path)
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=300)
            img_path = file.stored_path.replace('.pdf', f'_page{page_num+1}.png')
            pix.save(img_path)

            # OCR
            ocr_result = self.ocr.process_page(img_path)

            page_obj = ExamSubmissionPage(
                batch_file_id=file.id,
                page_number=page_num + 1,
                original_image_path=img_path,
                processed_image_path=ocr_result.get("processed_path"),
                rotation_angle=ocr_result.get("rotation", 0),
                perspective_corrected=ocr_result.get("perspective_corrected", False),
                ocr_confidence=ocr_result.get("confidence"),
                full_text=ocr_result.get("full_text"),
                ocr_data=ocr_result,
            )
            self.db.add(page_obj)
            pages.append(page_obj)

        doc.close()
        self.db.flush()
        return pages

    def _process_image(self, file: GradingBatchFile) -> List[ExamSubmissionPage]:
        """Processa imagem única."""
        ocr_result = self.ocr.process_page(file.stored_path)

        page_obj = ExamSubmissionPage(
            batch_file_id=file.id,
            page_number=1,
            original_image_path=file.stored_path,
            processed_image_path=ocr_result.get("processed_path"),
            rotation_angle=ocr_result.get("rotation", 0),
            perspective_corrected=ocr_result.get("perspective_corrected", False),
            ocr_confidence=ocr_result.get("confidence"),
            full_text=ocr_result.get("full_text"),
            ocr_data=ocr_result,
        )
        self.db.add(page_obj)
        self.db.flush()
        return [page_obj]

    # ==================== Student Identification ====================

    def identify_students(self, batch_id: UUID) -> GradingBatch:
        """Identifica alunos em todas as páginas usando IA/OCR."""
        batch = self.get_batch(batch_id)
        batch.status = BatchStatus.IDENTIFYING

        pages = self.db.query(ExamSubmissionPage).join(GradingBatchFile).filter(
            GradingBatchFile.batch_id == batch_id,
            ExamSubmissionPage.submission_id.is_(None)
        ).all()

        identified_count = 0
        for page in pages:
            try:
                result = self._identify_page(page)
                if result and result.status == IdentificationStatus.IDENTIFIED:
                    identified_count += 1
            except Exception as e:
                self._log_audit(batch_id, "identification_failed", "ExamSubmissionPage", page.id,
                               success=False, error_message=str(e))

        batch.identified_students = identified_count
        batch.status = BatchStatus.GROUPING
        self.db.flush()
        return batch

    def _identify_page(self, page: ExamSubmissionPage) -> StudentIdentificationResult:
        """Identifica aluno em uma página usando OCR + IA."""
        # Extrai texto da página
        full_text = page.full_text or ""
        ocr_data = page.ocr_data

        # Busca RA e matrícula no texto
        import re
        ra_pattern = r'\b(RA|ra|Ra)\s*[:\-]?\s*(\d{8,12})\b'
        mat_pattern = r'\b(Matr[ií]cula|matr[ií]cula)\s*[:\-]?\s*(\d{8,12})\b'

        ra_match = re.search(ra_pattern, full_text, re.IGNORECASE)
        mat_match = re.search(mat_pattern, full_text, re.IGNORECASE)

        identified_ra = ra_match.group(2) if ra_match else None
        identified_matricula = mat_match.group(2) if mat_match else None

        # Consulta banco de dados
        matched_student = None
        match_type = "none"
        status = IdentificationStatus.PENDING
        conflict = {}

        if identified_ra and identified_matricula:
            student_ra = self.student_repo.get_by_ra(identified_ra)
            student_mat = self.student_repo.get_by_field("matricula", identified_matricula) if hasattr(self.student_repo, 'get_by_field') else None
            # Simplificado - buscar por campo customizado
            if student_ra:
                matched_student = student_ra
                match_type = "ra_only"
                status = IdentificationStatus.IDENTIFIED
            # TODO: implementar busca por matricula
        elif identified_ra:
            student_ra = self.student_repo.get_by_ra(identified_ra)
            if student_ra:
                matched_student = student_ra
                match_type = "ra_only"
                status = IdentificationStatus.IDENTIFIED
            else:
                status = IdentificationStatus.NOT_FOUND
                conflict["ra_not_found"] = identified_ra
        elif identified_matricula:
            # TODO: buscar por matricula
            status = IdentificationStatus.NOT_FOUND
            conflict["matricula_not_found"] = identified_matricula
        else:
            status = IdentificationStatus.PENDING
            conflict["no_identifiers"] = True

        # Cria registro de identificação
        result = StudentIdentificationResult(
            page_id=page.id,
            identified_ra=identified_ra,
            identified_matricula=identified_matricula,
            matched_student_id=matched_student.id if matched_student else None,
            ra_confidence=Decimal("95") if identified_ra else None,
            matricula_confidence=Decimal("90") if identified_matricula else None,
            match_type=match_type,
            status=status,
            conflict_details=conflict,
            ai_provider=settings.ai_provider,
            ai_model=settings.ollama_text_model,
            raw_response={"ocr_text": full_text[:500]},
        )
        self.db.add(result)
        self.db.flush()
        return result

    # ==================== Page Grouping ====================

    def group_pages(self, batch_id: UUID) -> GradingBatch:
        """Agrupa páginas por aluno/prova."""
        batch = self.get_batch(batch_id)
        batch.status = BatchStatus.GROUPING

        # Busca identificações bem-sucedidas
        identifications = self.db.query(StudentIdentificationResult).join(ExamSubmissionPage).join(GradingBatchFile).filter(
            GradingBatchFile.batch_id == batch_id,
            StudentIdentificationResult.status == IdentificationStatus.IDENTIFIED,
            StudentIdentificationResult.matched_student_id.isnot(None)
        ).all()

        # Agrupa por aluno
        from collections import defaultdict
        student_pages = defaultdict(list)
        for ident in identifications:
            student_pages[ident.matched_student_id].append(ident.page_id)

        grouped_count = 0
        for student_id, page_ids in student_pages.items():
            group = ExamPageGroup(
                batch_id=batch_id,
                student_id=student_id,
                exam_id=batch.exam_id,
                version_id=batch.version_id,
                page_ids=[str(pid) for pid in page_ids],
                status=PageGroupStatus.GROUPED,
                confidence=Decimal("90"),
            )
            self.db.add(group)
            grouped_count += 1

        batch.grouped_submissions = grouped_count
        batch.status = BatchStatus.GRADING
        self.db.flush()
        return batch

    # ==================== Create Submissions ====================

    def create_submissions_from_groups(self, batch_id: UUID) -> List[ExamSubmission]:
        """Cria submissões a partir dos grupos de páginas."""
        batch = self.get_batch(batch_id)

        groups = self.db.query(ExamPageGroup).filter(
            ExamPageGroup.batch_id == batch_id,
            ExamPageGroup.status == PageGroupStatus.GROUPED
        ).all()

        submissions = []
        for group in groups:
            # Cria submissão
            submission = ExamSubmission(
                batch_id=batch_id,
                version_id=group.version_id,
                student_id=group.student_id,
                identified_student_id=group.student_id,
                status=SubmissionStatus.AWAITING_CORRECTION,
                original_files=[],  # Será preenchido com paths das páginas
            )
            self.db.add(submission)
            self.db.flush()

            # Associa páginas
            for page_id_str in group.page_ids:
                page = self.db.get(ExamSubmissionPage, UUID(page_id_str))
                if page:
                    page.submission_id = submission.id
                    submission.original_files.append(page.original_image_path)

            # Atualiza grupo
            group.created_submission_id = submission.id
            submissions.append(submission)

        self.db.flush()
        return submissions

    # ==================== AI Grading ====================

    async def grade_all_submissions(self, batch_id: UUID) -> GradingBatch:
        """Executa correção por IA em todas as submissões."""
        batch = self.get_batch(batch_id)
        batch.status = BatchStatus.GRADING

        submissions = self.db.query(ExamSubmission).filter(
            ExamSubmission.batch_id == batch_id
        ).all()

        graded = 0
        pending_review = 0

        for submission in submissions:
            try:
                result = await self.ai_service.batch_correct(
                    type('obj', (object,), {
                        'submission_id': submission.id,
                        'question_ids': None
                    })()
                )
                graded += result.total_processed
                pending_review += result.requires_review_count
            except Exception as e:
                self._log_audit(batch_id, "grading_failed", "ExamSubmission", submission.id,
                               success=False, error_message=str(e))

        batch.graded_submissions = graded
        batch.pending_review = pending_review

        if pending_review > 0:
            batch.status = BatchStatus.PARTIAL
        else:
            batch.status = BatchStatus.COMPLETED
            batch.processing_completed_at = datetime.now(timezone.utc)

        self.db.flush()
        return batch

    # ==================== Manual Operations ====================

    def manual_identify(self, identification_id: UUID, student_id: UUID, teacher_id: UUID) -> StudentIdentificationResult:
        """Identificação manual pelo professor."""
        ident = self.db.get(StudentIdentificationResult, identification_id)
        if not ident:
            raise NotFoundError("Identificação não encontrada")

        student = self.student_repo.get(student_id)
        if not student:
            raise NotFoundError("Aluno não encontrado")

        ident.matched_student_id = student_id
        ident.status = IdentificationStatus.MANUAL
        ident.manual_override = True
        ident.overridden_by = teacher_id
        ident.overridden_at = datetime.now(timezone.utc)
        self.db.flush()

        self._log_audit(ident.submission_id, "manual_identification", "StudentIdentificationResult", identification_id,
                       old_values={"status": "pending"}, new_values={"student_id": str(student_id), "manual": True})
        return ident

    def get_pending_identifications(self, batch_id: UUID) -> List[StudentIdentificationResult]:
        """Busca identificações pendentes de revisão."""
        return self.db.query(StudentIdentificationResult).join(ExamSubmissionPage).join(GradingBatchFile).filter(
            GradingBatchFile.batch_id == batch_id,
            StudentIdentificationResult.status.in_([
                IdentificationStatus.PENDING,
                IdentificationStatus.AMBIGUOUS,
                IdentificationStatus.CONFLICT,
                IdentificationStatus.NOT_FOUND
            ])
        ).all()

    # ==================== Audit ====================

    def _log_audit(self, batch_id: UUID, action: str, entity_type: str, entity_id: UUID,
                   description: str, old_values: Dict = None, new_values: Dict = None,
                   performed_by: UUID = None, success: bool = True, error_message: str = None):
        """Registra log de auditoria."""
        log = GradingAuditLog(
            batch_id=batch_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            performed_by=performed_by,
            success=success,
            error_message=error_message,
        )
        self.db.add(log)
        self.db.flush()