"""Service de Provas, Questões, Impressão e Submissões."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models.exam import (
    Exam, ExamStatus, ExamVersion, ExamQuestion, QuestionType,
    AnswerKey, GradingRubric, ExamCopy, ExamPrintLog, PrintStatus,
    ExamSubmission, SubmissionStatus, SubmissionPage, ExtractedAnswer
)
from backend.app.repositories.exam_repository import (
    ExamRepository, ExamVersionRepository, ExamQuestionRepository,
    AnswerKeyRepository, GradingRubricRepository, ExamCopyRepository,
    ExamPrintLogRepository, ExamSubmissionRepository,
    SubmissionPageRepository, ExtractedAnswerRepository
)
from backend.app.schemas.exam import (
    ExamCreate, ExamUpdate,
    QuestionCreate, QuestionUpdate,
    AnswerKeyCreate, AnswerKeyUpdate,
    GradingRubricCreate, GradingRubricUpdate,
    ExamCopyCreate, ExamPrintLogCreate,
    SubmissionCreate, SubmissionUpdate,
    SubmissionPageCreate, ExtractedAnswerCreate,
)
from backend.app.core.exceptions import ValidationError, NotFoundError, ConflictError
from backend.app.repositories.ai_correction_repository import AuditLogRepository, AuditActionType
from backend.app.integrations.pdf.generator import PDFGenerator
from backend.app.integrations.qr.generator import QRCodeGenerator


class ExamService:
    """Serviço de provas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ExamRepository(db)
        self.question_repo = ExamQuestionRepository(db)
        self.version_repo = ExamVersionRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.pdf_gen = PDFGenerator()
        self.qr_gen = QRCodeGenerator()

    def create(self, exam_data: ExamCreate, created_by: UUID) -> Exam:
        exam = Exam(**exam_data.model_dump(), created_by=created_by)
        self.db.add(exam)
        self.db.flush()
        self.audit_repo.log(AuditActionType.EXAM_CREATE, f"Prova criada: {exam.title}", created_by,
                          "Exam", exam.id, new_values=exam_data.model_dump())
        return exam

    def get(self, exam_id: UUID) -> Exam:
        exam = self.repo.get_with_questions(exam_id)
        if not exam:
            raise NotFoundError("Prova não encontrada")
        return exam

    def update(self, exam_id: UUID, exam_data: ExamUpdate, updated_by: UUID) -> Exam:
        exam = self.get(exam_id)
        if exam.status not in [ExamStatus.DRAFT, ExamStatus.IN_EDIT]:
            raise ValidationError("Só é possível editar provas em rascunho ou edição")
        for k, v in exam_data.model_dump(exclude_unset=True).items():
            setattr(exam, k, v)
        exam.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return exam

    def validate_scores(self, exam_id: UUID) -> tuple[Decimal, Decimal, bool]:
        return self.repo.validate_total_score(exam_id)

    def publish(self, exam_id: UUID, published_by: UUID) -> ExamVersion:
        """Publica a prova criando versão imutável."""
        exam = self.get(exam_id)
        total_q, total_questions, valid = self.validate_scores(exam_id)
        if not valid:
            raise ValidationError(f"Soma das questões ({total_questions}) difere do total configurado ({total_q})")

        questions = self.question_repo.get_by_exam(exam_id)
        if not questions:
            raise ValidationError("Prova deve ter pelo menos uma questão")

        # Verifica se todas têm gabarito
        for q in questions:
            if not self.question_repo.get_with_answer_key(q.id):
                raise ValidationError(f"Questão {q.question_order} não possui gabarito")

        # Cria snapshot
        questions_snapshot = []
        answer_key_snapshot = {}
        rubrics_snapshot = {}

        for q in questions:
            q_data = {
                "id": str(q.id),
                "order": q.question_order,
                "type": q.type.value,
                "statement": q.statement,
                "score": str(q.score),
                "config": q.config,
            }
            questions_snapshot.append(q_data)

            ak = q.answer_key
            if ak:
                answer_key_snapshot[str(q.id)] = {
                    "correct_answer": ak.correct_answer,
                    "expected_answer": ak.expected_answer,
                    "accepted_alternatives": ak.accepted_alternatives,
                    "keywords": ak.keywords,
                    "required_concepts": ak.required_concepts,
                    "justification": ak.justification,
                    "partial_scoring": ak.partial_scoring,
                }

            gr = q.grading_rubric
            if gr:
                rubrics_snapshot[str(q.id)] = {
                    "criteria": gr.criteria,
                    "max_score": str(gr.max_score),
                }

        version_num = exam.version + 1
        version = ExamVersion(
            exam_id=exam.id,
            version_number=version_num,
            title=exam.title,
            description=exam.description,
            instructions=exam.instructions,
            total_score=exam.total_score,
            questions_snapshot=questions_snapshot,
            answer_key_snapshot=answer_key_snapshot,
            rubrics_snapshot=rubrics_snapshot,
            published_by=published_by,
        )
        self.db.add(version)
        exam.version = version_num
        exam.status = ExamStatus.PUBLISHED
        exam.published_at = datetime.now(timezone.utc)
        self.db.flush()

        self.audit_repo.log(AuditActionType.EXAM_PUBLISH, f"Prova publicada v{version_num}: {exam.title}", published_by,
                          "ExamVersion", version.id)
        return version


class QuestionService:
    """Serviço de questões."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ExamQuestionRepository(db)
        self.answer_key_repo = AnswerKeyRepository(db)
        self.rubric_repo = GradingRubricRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, question_data: QuestionCreate) -> ExamQuestion:
        # Verifica ordem única
        existing = self.repo.get_by_exam(question_data.exam_id)
        if any(q.question_order == question_data.question_order for q in existing):
            raise ConflictError(f"Ordem {question_data.question_order} já existe")
        question = ExamQuestion(**question_data.model_dump())
        self.db.add(question)
        self.db.flush()
        return question

    def get(self, question_id: UUID) -> ExamQuestion:
        question = self.repo.get_with_answer_key(question_id)
        if not question:
            raise NotFoundError("Questão não encontrada")
        return question

    def update(self, question_id: UUID, question_data: QuestionUpdate) -> ExamQuestion:
        question = self.get(question_id)
        exam = question.exam
        if exam.status not in [ExamStatus.DRAFT, ExamStatus.IN_EDIT]:
            raise ValidationError("Não pode editar questão de prova publicada")
        for k, v in question_data.model_dump(exclude_unset=True).items():
            setattr(question, k, v)
        question.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return question

    def reorder(self, exam_id: UUID, question_orders: List[dict]) -> List[ExamQuestion]:
        """Reordena questões: [{id, order}, ...]"""
        questions = self.repo.get_by_exam(exam_id)
        qmap = {q.id: q for q in questions}
        for item in question_orders:
            q = qmap.get(UUID(item["id"]))
            if q:
                q.question_order = item["order"]
        self.db.flush()
        return self.repo.get_by_exam(exam_id)


class AnswerKeyService:
    """Serviço de gabaritos."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AnswerKeyRepository(db)
        self.question_repo = ExamQuestionRepository(db)

    def create(self, answer_key_data: AnswerKeyCreate) -> AnswerKey:
        question = self.question_repo.get(answer_key_data.question_id)
        if not question:
            raise NotFoundError("Questão não encontrada")
        if self.repo.get_by_question(answer_key_data.question_id):
            raise ConflictError("Gabarito já existe para esta questão")
        ak = AnswerKey(**answer_key_data.model_dump())
        self.db.add(ak)
        self.db.flush()
        return ak

    def update(self, question_id: UUID, data: AnswerKeyUpdate) -> AnswerKey:
        ak = self.repo.get_by_question(question_id)
        if not ak:
            raise NotFoundError("Gabarito não encontrado")
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(ak, k, v)
        ak.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return ak


class GradingRubricService:
    """Serviço de rubricas."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = GradingRubricRepository(db)
        self.question_repo = ExamQuestionRepository(db)

    def create(self, rubric_data: GradingRubricCreate) -> GradingRubric:
        question = self.question_repo.get(rubric_data.question_id)
        if not question:
            raise NotFoundError("Questão não encontrada")
        if self.repo.get_by_question(rubric_data.question_id):
            raise ConflictError("Rubrica já existe para esta questão")
        rubric = GradingRubric(**rubric_data.model_dump())
        self.db.add(rubric)
        self.db.flush()
        return rubric

    def update(self, question_id: UUID, data: GradingRubricUpdate) -> GradingRubric:
        rubric = self.repo.get_by_question(question_id)
        if not rubric:
            raise NotFoundError("Rubrica não encontrada")
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(rubric, k, v)
        rubric.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return rubric


class ExamCopyService:
    """Serviço de cópias de prova (impressão)."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ExamCopyRepository(db)
        self.version_repo = ExamVersionRepository(db)
        self.exam_repo = ExamRepository(db)
        self.print_repo = ExamPrintLogRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.pdf_gen = PDFGenerator()
        self.qr_gen = QRCodeGenerator()

    def generate_copies(self, version_id: UUID, count: int, student_ids: Optional[List[UUID]] = None,
                       generated_by: UUID = None) -> List[ExamCopy]:
        """Gera cópias para impressão."""
        version = self.version_repo.get(version_id)
        if not version:
            raise NotFoundError("Versão não encontrada")

        copies = []
        for i in range(count):
            copy_id = f"{version.exam_id}-v{version.version_number}-{i+1:04d}"
            student_id = student_ids[i] if student_ids and i < len(student_ids) else None

            qr_data = {
                "exam_id": str(version.exam_id),
                "version_id": str(version.id),
                "copy_identifier": copy_id,
                "student_id": str(student_id) if student_id else None,
            }

            copy = ExamCopy(
                version_id=version_id,
                copy_identifier=copy_id,
                qr_code_data=str(qr_data),
                student_id=student_id,
                is_personalized=student_id is not None,
            )
            self.db.add(copy)
            copies.append(copy)

        self.db.flush()
        return copies

    def generate_pdf_student(self, copy_id: UUID, generated_by: UUID) -> str:
        """Gera PDF da prova do aluno."""
        copy = self.repo.get(copy_id)
        if not copy:
            raise NotFoundError("Cópia não encontrada")

        version = self.version_repo.get(copy.version_id)
        exam = self.exam_repo.get(version.exam_id)

        pdf_path = self.pdf_gen.generate_student_exam(
            exam=exam,
            version=version,
            copy=copy,
            output_dir="./storage/exams/pdfs",
        )

        copy.pdf_path = pdf_path
        copy.printed_at = datetime.now(timezone.utc)
        copy.printed_by = generated_by
        self.db.flush()

        return pdf_path

    def generate_pdf_teacher(self, version_id: UUID, generated_by: UUID) -> str:
        """Gera PDF do gabarito do professor."""
        version = self.version_repo.get(version_id)
        if not version:
            raise NotFoundError("Versão não encontrada")

        exam = self.exam_repo.get(version.exam_id)

        pdf_path = self.pdf_gen.generate_teacher_answer_key(
            exam=exam,
            version=version,
            output_dir="./storage/exams/pdfs",
        )

        return pdf_path

    def log_print(self, log_data: ExamPrintLogCreate) -> ExamPrintLog:
        log = ExamPrintLog(**log_data.model_dump())
        self.db.add(log)
        self.db.flush()
        self.audit_repo.log(AuditActionType.EXAM_PRINT, f"Impressão: {log.copy_count} cópias", log_data.printed_by,
                          "ExamPrintLog", log.id)
        return log


class SubmissionService:
    """Serviço de submissões (provas digitalizadas)."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ExamSubmissionRepository(db)
        self.copy_repo = ExamCopyRepository(db)
        self.version_repo = ExamVersionRepository(db)
        self.page_repo = SubmissionPageRepository(db)
        self.answer_repo = ExtractedAnswerRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create(self, submission_data: SubmissionCreate, uploaded_by: UUID) -> ExamSubmission:
        # Verifica se cópia existe
        copy = self.copy_repo.get(submission_data.copy_id)
        if not copy:
            raise NotFoundError("Cópia não encontrada")

        existing = self.repo.get_by_copy(submission_data.copy_id)
        if existing:
            raise ConflictError("Submissão já existe para esta cópia")

        submission = ExamSubmission(
            **{
                **submission_data.model_dump(),
                "version_id": copy.version_id,
                "student_id": submission_data.student_id or copy.student_id,
            },
        )
        self.db.add(submission)
        self.db.flush()

        self.audit_repo.log(AuditActionType.EXAM_UPLOAD, f"Prova enviada: {copy.copy_identifier}", uploaded_by,
                          "ExamSubmission", submission.id)
        return submission

    def add_pages(self, submission_id: UUID, pages: List[SubmissionPageCreate]) -> List[SubmissionPage]:
        """Adiciona páginas à submissão."""
        submission = self.repo.get(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        created_pages = []
        for page_data in pages:
            page_values = page_data.model_dump()
            page_values["submission_id"] = submission_id
            page = SubmissionPage(**page_values)
            self.db.add(page)
            created_pages.append(page)

        self.db.flush()
        return created_pages

    def process_ocr(self, submission_id: UUID) -> ExamSubmission:
        """Processa OCR das páginas (integração com serviço de OCR)."""
        from backend.app.integrations.ocr.processor import OCRProcessor

        submission = self.repo.get_with_pages(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        ocr = OCRProcessor()
        questions = ExamQuestionRepository(self.db).get_by_exam(submission.version.exam_id)
        questions_by_order = {question.question_order: question for question in questions}

        for page in submission.pages:
            page.extracted_answers.clear()
            # Processa imagem
            result = ocr.process_page(page.original_image_path)
            page.processed_image_path = result.get("processed_path")
            page.rotation_angle = result.get("rotation", 0)
            page.perspective_corrected = result.get("perspective_corrected", False)
            page.ocr_confidence = result.get("confidence")

            # Extrai respostas por questão
            for extracted in result.get("extracted_answers", []):
                question_order = extracted.get("question_order")
                question = questions_by_order.get(question_order)
                if not question:
                    continue
                answer = ExtractedAnswer(
                    page_id=page.id,
                    question_id=question.id,
                    question_order=question_order,
                    extracted_text=extracted.get("extracted_text"),
                    extracted_image_path=extracted.get("image_path"),
                    ocr_confidence=extracted.get("ocr_confidence"),
                    bounding_box=extracted.get("bounding_box", {}),
                )
                page.extracted_answers.append(answer)

        submission.status = SubmissionStatus.PROCESSED
        submission.processed_at = datetime.now(timezone.utc)
        submission.processed_files = [p.processed_image_path for p in submission.pages if p.processed_image_path]
        self.db.flush()

        return submission

    def identify_student(self, submission_id: UUID, student_id: UUID, confidence: Decimal,
                        manual: bool = False) -> ExamSubmission:
        """Identifica aluno da submissão (via QR Code ou manual)."""
        submission = self.repo.get(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        submission.identified_student_id = student_id
        submission.identification_confidence = confidence
        submission.manual_identification = manual
        submission.student_id = student_id
        self.db.flush()

        return submission

    def request_ai_correction(self, submission_id: UUID, question_ids: Optional[List[UUID]] = None) -> ExamSubmission:
        """Solicita correção por IA."""
        submission = self.repo.get(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        submission.status = SubmissionStatus.AWAITING_CORRECTION
        self.db.flush()

        self.audit_repo.log(AuditActionType.AI_CORRECTION_REQUEST, "Correção IA solicitada", None,
                          "ExamSubmission", submission.id)
        return submission