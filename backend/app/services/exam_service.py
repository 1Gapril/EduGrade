"""Service de Provas, Questões, Impressão e Submissões."""

import logging
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from backend.app.integrations.pdf.generator import PDFGenerator
from backend.app.integrations.qr.generator import QRCodeGenerator
from backend.app.models.academic import Class, Enrollment, EnrollmentStatus
from backend.app.models.exam import (
    AnswerKey,
    Exam,
    ExamCopy,
    ExamPrintLog,
    ExamQuestion,
    ExamStatus,
    ExamSubmission,
    ExamVersion,
    ExtractedAnswer,
    GradingRubric,
    QuestionType,
    SubmissionPage,
    SubmissionStatus,
)
from backend.app.models.user import Student, User, UserRole
from backend.app.repositories.ai_correction_repository import AuditActionType, AuditLogRepository
from backend.app.repositories.exam_repository import (
    AnswerKeyRepository,
    ExamCopyRepository,
    ExamPrintLogRepository,
    ExamQuestionRepository,
    ExamRepository,
    ExamSubmissionRepository,
    ExamVersionRepository,
    ExtractedAnswerRepository,
    GradingRubricRepository,
    SubmissionPageRepository,
)
from backend.app.schemas.exam import (
    AnswerKeyCreate,
    AnswerKeyUpdate,
    ExamCreate,
    ExamPrintLogCreate,
    ExamUpdate,
    ExamUpdateWithQuestions,
    GradingRubricCreate,
    GradingRubricUpdate,
    QuestionCreate,
    QuestionUpdate,
    SubmissionCreate,
    SubmissionPageCreate,
)

logger = logging.getLogger("edugrade.exams")


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

    def _assert_can_manage(self, exam: Exam, user_id: UUID) -> None:
        """Garante que o usuário pode gerenciar a prova.

        Administradores podem gerenciar qualquer prova. Professores só podem
        gerenciar provas de turmas que lecionam.
        """
        user = self.db.get(User, user_id)
        if user is None:
            raise AuthorizationError("Usuário não encontrado")
        if user.role == UserRole.ADMIN:
            return
        if user.role != UserRole.TEACHER:
            raise AuthorizationError("Permissão insuficiente para esta operação")
        teacher_id = user.teacher_profile.id if user.teacher_profile else None
        class_obj = self.db.get(Class, exam.class_id)
        if not class_obj or teacher_id is None or class_obj.teacher_id != teacher_id:
            raise AuthorizationError("Você não leciona esta turma")

    def _assert_can_manage_class(self, class_id: UUID, user_id: UUID) -> None:
        """Garante que o usuário pode usar a turma informada."""
        user = self.db.get(User, user_id)
        if user is None:
            raise AuthorizationError("Usuário não encontrado")
        if user.role == UserRole.ADMIN:
            return
        if user.role != UserRole.TEACHER:
            raise AuthorizationError("Permissão insuficiente para esta operação")
        teacher_id = user.teacher_profile.id if user.teacher_profile else None
        class_obj = self.db.get(Class, class_id)
        if not class_obj:
            raise NotFoundError("Turma não encontrada")
        if teacher_id is None or class_obj.teacher_id != teacher_id:
            raise AuthorizationError("Você não leciona esta turma")

    def update(self, exam_id: UUID, exam_data: ExamUpdate, updated_by: UUID) -> Exam:
        exam = self.get(exam_id)
        self._assert_can_manage(exam, updated_by)
        if exam.status not in [ExamStatus.DRAFT, ExamStatus.IN_EDIT]:
            raise ValidationError("Só é possível editar provas em rascunho ou edição")
        for k, v in exam_data.model_dump(exclude_unset=True).items():
            setattr(exam, k, v)
        exam.updated_at = datetime.now(UTC)
        self.db.flush()
        return exam

    def update_with_questions(
        self, exam_id: UUID, exam_data: ExamUpdateWithQuestions, updated_by: UUID
    ) -> Exam:
        exam = self.get(exam_id)
        self._assert_can_manage(exam, updated_by)
        self._assert_can_manage_class(exam_data.class_id, updated_by)
        if exam.status not in [ExamStatus.DRAFT, ExamStatus.IN_EDIT]:
            raise ValidationError("Somente provas em rascunho podem ser editadas.")

        existing_questions = self.question_repo.get_by_exam(exam_id)
        existing_by_id = {question.id: question for question in existing_questions}
        submitted_ids = [question.id for question in exam_data.questions if question.id]
        if len(submitted_ids) != len(set(submitted_ids)):
            raise ValidationError("Uma questão foi enviada mais de uma vez.")
        if any(question_id not in existing_by_id for question_id in submitted_ids):
            raise ValidationError("Uma das questões não pertence a esta prova.")

        exam_fields = exam_data.model_dump(exclude={"questions"})
        for field, value in exam_fields.items():
            setattr(exam, field, value)
        exam.updated_at = datetime.now(UTC)

        # Move orders out of the way before assigning new positions to avoid
        # conflicts with the unique (exam_id, question_order) constraint.
        order_offset = len(existing_questions) + len(exam_data.questions) + 1
        for question in existing_questions:
            question.question_order += order_offset
        self.db.flush()

        for order, question_data in enumerate(exam_data.questions, start=1):
            question = existing_by_id.get(question_data.id) if question_data.id else None
            if question is None:
                question = ExamQuestion(exam_id=exam.id)
                self.db.add(question)

            question.question_order = order
            question.type = QuestionType(question_data.type)
            question.statement = question_data.statement
            question.score = question_data.score
            question.config = question_data.config
            self.db.flush()

            answer_key = question.answer_key
            if answer_key is None:
                answer_key = AnswerKey(question_id=question.id)
                self.db.add(answer_key)
            answer_key.correct_answer = question_data.correct_answer
            answer_key.expected_answer = question_data.expected_answer
            answer_key.accepted_alternatives = question_data.accepted_alternatives
            answer_key.keywords = question_data.keywords
            answer_key.required_concepts = question_data.required_concepts
            answer_key.justification = question_data.justification

        for question in existing_questions:
            if question.id not in submitted_ids:
                self.db.delete(question)

        self.audit_repo.log(
            AuditActionType.UPDATE,
            f"Prova atualizada: {exam.title}",
            updated_by,
            "Exam",
            exam.id,
        )
        self.db.flush()
        return exam

    def cancel(self, exam_id: UUID, cancelled_by: UUID) -> Exam:
        exam = self.get(exam_id)
        self._assert_can_manage(exam, cancelled_by)
        if exam.status == ExamStatus.CANCELLED:
            return exam

        exam.status = ExamStatus.CANCELLED
        exam.updated_at = datetime.now(UTC)
        for version in exam.versions:
            version.is_active = False
        self.audit_repo.log(
            AuditActionType.DELETE,
            f"Prova cancelada: {exam.title}",
            cancelled_by,
            "Exam",
            exam.id,
            new_values={"status": ExamStatus.CANCELLED.value},
        )
        self.db.flush()
        return exam

    def restore(self, exam_id: UUID, restored_by: UUID) -> Exam:
        """Reativa uma prova cancelada, devolvendo-a como rascunho."""
        exam = self.get(exam_id)
        self._assert_can_manage(exam, restored_by)
        if exam.status != ExamStatus.CANCELLED:
            return exam

        exam.status = ExamStatus.DRAFT
        exam.updated_at = datetime.now(UTC)
        self.audit_repo.log(
            AuditActionType.UPDATE,
            f"Prova reativada: {exam.title}",
            restored_by,
            "Exam",
            exam.id,
            new_values={"status": ExamStatus.DRAFT.value},
        )
        self.db.flush()
        return exam

    def validate_scores(self, exam_id: UUID) -> tuple[Decimal, Decimal, bool]:
        return self.repo.validate_total_score(exam_id)

    def publish(self, exam_id: UUID, published_by: UUID) -> ExamVersion:
        """Publica a prova criando versão imutável."""
        exam = self.get(exam_id)
        self._assert_can_manage(exam, published_by)
        total_q, total_questions, valid = self.validate_scores(exam_id)
        if not valid:
            raise ValidationError(f"Soma das questões ({total_questions}) difere do total configurado ({total_q})")

        questions = self.question_repo.get_by_exam(exam_id)
        if not questions:
            raise ValidationError("Prova deve ter pelo menos uma questão")

        # Verifica se todas têm gabarito
        for q in questions:
            question_with_ak = self.question_repo.get_with_answer_key(q.id)
            if not question_with_ak or not question_with_ak.answer_key:
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
        exam.published_at = datetime.now(UTC)
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
        question.updated_at = datetime.now(UTC)
        self.db.flush()
        return question

    def reorder(self, exam_id: UUID, question_orders: list[dict]) -> list[ExamQuestion]:
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
        ak.updated_at = datetime.now(UTC)
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
        rubric.updated_at = datetime.now(UTC)
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

    def generate_copies(self, version_id: UUID, count: int, student_ids: list[UUID] | None = None,
                       generated_by: UUID = None) -> list[ExamCopy]:
        """Gera cópias para impressão."""
        version = self.version_repo.get(version_id)
        if not version:
            raise NotFoundError("Versão não encontrada")

        copies = []
        first_copy_number = len(self.repo.get_by_version(version_id)) + 1
        for i in range(count):
            copy_id = f"{version.exam_id}-v{version.version_number}-{first_copy_number+i:04d}"
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
            output_dir=settings.pdf_dir,
        )

        copy.pdf_path = pdf_path
        copy.printed_at = datetime.now(UTC)
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
            output_dir=settings.pdf_dir,
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

    def add_pages(self, submission_id: UUID, pages: list[SubmissionPageCreate]) -> list[SubmissionPage]:
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
        """Processa OCR das páginas, com fallback para a camada de texto do PDF."""
        from backend.app.integrations.ocr.processor import OCRProcessor
        from backend.app.integrations.ocr.text_layer import extract_answers_from_pdf

        submission = self.repo.get_with_pages(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        questions = ExamQuestionRepository(self.db).get_by_exam(submission.version.exam_id)
        questions_by_order = {question.question_order: question for question in questions}

        ocr = OCRProcessor()
        try:
            for page in submission.pages:
                page.extracted_answers.clear()
                result = ocr.process_page(page.original_image_path)
                page.processed_image_path = result.get("processed_path")
                page.rotation_angle = result.get("rotation", 0)
                page.perspective_corrected = result.get("perspective_corrected", False)
                page.ocr_confidence = result.get("confidence")

                for extracted in result.get("extracted_answers", []):
                    question_order = extracted.get("question_order")
                    question = questions_by_order.get(question_order)
                    if not question:
                        continue
                    page.extracted_answers.append(
                        ExtractedAnswer(
                            page_id=page.id,
                            question_id=question.id,
                            question_order=question_order,
                            extracted_text=extracted.get("extracted_text"),
                            extracted_image_path=extracted.get("image_path"),
                            ocr_confidence=extracted.get("ocr_confidence"),
                            bounding_box=extracted.get("bounding_box", {}),
                        )
                    )
        except Exception as ocr_error:
            # Sem Tesseract (ou com imagem ilegível), tenta o texto embutido no PDF.
            answers = self._answers_from_pdf_text_layer(submission, questions_by_order)
            if not answers:
                raise
            logger.info(
                "OCR indisponível para a submissão %s (%s); respostas lidas do texto do PDF.",
                submission_id,
                ocr_error,
            )

        submission.status = SubmissionStatus.PROCESSED
        submission.processed_at = datetime.now(UTC)
        submission.processed_files = [
            p.processed_image_path or p.original_image_path for p in submission.pages
        ]
        self.db.flush()

        return submission

    def _answers_from_pdf_text_layer(
        self,
        submission: ExamSubmission,
        questions_by_order: dict[int, ExamQuestion],
    ) -> list[ExtractedAnswer]:
        """Cria respostas a partir do texto do PDF original (sem OCR)."""
        from backend.app.integrations.ocr.text_layer import extract_answers_from_pdf

        if not submission.pages:
            return []

        first_page = submission.pages[0]
        first_page.extracted_answers.clear()
        created: list[ExtractedAnswer] = []
        for original_file in submission.original_files or []:
            for extracted in extract_answers_from_pdf(original_file):
                question = questions_by_order.get(extracted["question_order"])
                if question is None:
                    continue
                answer = ExtractedAnswer(
                    page_id=first_page.id,
                    question_id=question.id,
                    question_order=extracted["question_order"],
                    extracted_text=extracted["extracted_text"],
                    ocr_confidence=extracted["ocr_confidence"],
                    bounding_box={"source": "pdf_text_layer"},
                )
                first_page.extracted_answers.append(answer)
                created.append(answer)
        return created

    def identify_student(
        self,
        submission_id: UUID,
        student_id: UUID,
        confidence: Decimal,
        manual: bool = False,
        identified_by: UUID | None = None,
    ) -> ExamSubmission:
        """Identifica aluno da submissão (via QR Code ou manual)."""
        submission = self.repo.get(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        version = self.db.get(ExamVersion, submission.version_id)
        if version is None:
            raise NotFoundError("Versão da prova não encontrada")
        exam = self.db.get(Exam, version.exam_id)
        if exam is None:
            raise NotFoundError("Prova não encontrada")
        student = self.db.get(Student, student_id)
        if student is None:
            raise NotFoundError("Aluno não encontrado")
        enrollment = self.db.query(Enrollment.id).filter(
            Enrollment.student_id == student.id,
            Enrollment.class_id == exam.class_id,
            Enrollment.academic_period_id == exam.academic_period_id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
        ).first()
        if enrollment is None:
            raise ValidationError("O aluno não possui matrícula ativa na turma da prova")

        if submission.copy_id and not manual:
            copy = self.db.get(ExamCopy, submission.copy_id)
            if copy is not None and copy.student_id is not None and copy.student_id != student.id:
                raise ValidationError("O aluno identificado não corresponde à cópia personalizada")

        old_student_id = str(submission.student_id) if submission.student_id else None
        submission.identified_student_id = student_id
        submission.identification_confidence = confidence
        submission.manual_identification = manual
        submission.student_id = student_id
        self.db.flush()
        self.audit_repo.log(
            AuditActionType.UPDATE,
            "Aluno identificado na submissão",
            identified_by,
            "ExamSubmission",
            submission.id,
            old_values={"student_id": old_student_id},
            new_values={
                "student_id": str(student.id),
                "ra": student.ra,
                "registration_number": student.registration_number,
                "manual": manual,
            },
        )

        return submission

    def request_ai_correction(self, submission_id: UUID, question_ids: list[UUID] | None = None) -> ExamSubmission:
        """Solicita correção por IA."""
        submission = self.repo.get(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        submission.status = SubmissionStatus.AWAITING_CORRECTION
        self.db.flush()

        self.audit_repo.log(AuditActionType.AI_CORRECTION_REQUEST, "Correção IA solicitada", None,
                          "ExamSubmission", submission.id)
        return submission
