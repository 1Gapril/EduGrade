"""Rotas de Provas, Questões, Impressão e Submissões."""

from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_active_user, require_teacher_or_admin, require_admin
from backend.app.models.user import User, UserRole
from backend.app.models.exam import Exam, ExamStatus, ExamVersion
from backend.app.schemas.exam import (
    ExamCreate, ExamCreateWithQuestions, ExamPDFImportResponse, ExamUpdate, ExamResponse, ExamWithRelations,
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionWithAnswerKey,
    AnswerKeyCreate, AnswerKeyUpdate, AnswerKeyResponse,
    GradingRubricCreate, GradingRubricUpdate, GradingRubricResponse,
    ExamCopyCreate, ExamPrintLogCreate, ExamPrintLogResponse,
    SubmissionCreate, SubmissionUpdate, SubmissionResponse, SubmissionWithRelations,
    SubmissionStudentResponse, SubmissionPageCreate, ExtractedAnswerCreate,
    ExamScoreValidation, QRCodeGenerateRequest,
)
from backend.app.services.exam_service import (
    ExamService, QuestionService, AnswerKeyService, GradingRubricService,
    ExamCopyService, SubmissionService,
)
from backend.app.services.exam_import_service import ExamPDFImportService
from backend.app.core.config import settings
from backend.app.schemas.common import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/exams", tags=["Provas"])
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _private_pdf_response(file_path: str) -> FileResponse:
    pdf_directory = (PROJECT_ROOT / "storage" / "exams" / "pdfs").resolve()
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path = path.resolve()
    if path.parent != pdf_directory or not path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(path, media_type="application/pdf", filename=path.name)


def _question_response(question, include_answer_key: bool) -> dict:
    schema = QuestionWithAnswerKey if include_answer_key else QuestionResponse
    return schema.model_validate(question).model_dump(mode="json")


# ==================== Exams ====================

@router.post("/analyze-pdfs", response_model=ExamPDFImportResponse)
async def analyze_exam_pdfs(
    exam_file: UploadFile = File(...),
    answer_key_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Extrai questões e gabaritos de PDFs sem salvar ou publicar a prova."""

    async def read_pdf(upload: UploadFile | None, label: str) -> bytes | None:
        if upload is None:
            return None
        if Path((upload.filename or "").replace("\\", "/")).suffix.lower() != ".pdf":
            raise HTTPException(status_code=422, detail=f"Envie um arquivo PDF para {label}.")
        try:
            content = await upload.read(settings.max_upload_size_mb * 1024 * 1024 + 1)
        finally:
            await upload.close()
        if len(content) > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"O arquivo {label} excede o limite de {settings.max_upload_size_mb} MB.",
            )
        if b"%PDF-" not in content[:1024]:
            raise HTTPException(status_code=422, detail=f"O arquivo enviado para {label} não é um PDF válido.")
        return content

    exam_content = await read_pdf(exam_file, "a prova")
    answer_key_content = await read_pdf(answer_key_file, "o gabarito")
    return await ExamPDFImportService(db).analyze(exam_content, answer_key_content)


@router.post("/complete", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_complete_exam(
    exam_data: ExamCreateWithQuestions,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Cria prova, questões e gabaritos na mesma transação."""
    exam_service = ExamService(db)
    question_service = QuestionService(db)
    answer_key_service = AnswerKeyService(db)
    exam_fields = ExamCreate.model_validate(
        exam_data.model_dump(exclude={"questions"})
    )

    try:
        exam = exam_service.create(exam_fields, current_user.id)
        for order, question_data in enumerate(exam_data.questions, start=1):
            question = question_service.create(
                QuestionCreate(
                    exam_id=exam.id,
                    question_order=order,
                    type=question_data.type,
                    statement=question_data.statement,
                    score=question_data.score,
                    config=question_data.config,
                )
            )
            answer_key_service.create(
                AnswerKeyCreate(
                    question_id=question.id,
                    correct_answer=question_data.correct_answer,
                    expected_answer=question_data.expected_answer,
                    accepted_alternatives=question_data.accepted_alternatives,
                    keywords=question_data.keywords,
                    required_concepts=question_data.required_concepts,
                    justification=question_data.justification,
                )
            )

        db.commit()
        db.refresh(exam)
    except Exception:
        db.rollback()
        raise
    return exam


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(
    exam_data: ExamCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    exam = service.create(exam_data, current_user.id)
    try:
        db.commit()
        db.refresh(exam)
    except Exception:
        db.rollback()
        raise
    return exam


@router.get("", response_model=PaginatedResponse[ExamWithRelations])
def list_exams(
    class_id: Optional[UUID] = None,
    status: Optional[str] = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    if class_id:
        exams = service.repo.get_by_class(class_id)
    elif status:
        from backend.app.models.exam import ExamStatus
        exams = service.repo.get_by_status(ExamStatus(status))
    else:
        exams = service.repo.get_all(skip=params.offset, limit=params.limit)
    total = len(exams)
    return PaginatedResponse(
        items=exams, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/versions/active")
def list_active_exam_versions(
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Lista versões publicadas disponíveis para receber provas respondidas."""
    versions = (
        db.query(ExamVersion)
        .join(Exam, Exam.id == ExamVersion.exam_id)
        .filter(ExamVersion.is_active.is_(True), Exam.status == ExamStatus.PUBLISHED)
        .order_by(Exam.title, ExamVersion.version_number.desc())
        .all()
    )
    return [
        {
            "version_id": str(version.id),
            "exam_id": str(version.exam_id),
            "title": version.title,
            "version_number": version.version_number,
            "class_id": str(version.exam.class_id),
            "class_name": version.exam.class_.name,
            "subject_name": version.exam.subject.name,
        }
        for version in versions
    ]


@router.get("/{exam_id:uuid}", response_model=ExamWithRelations)
def get_exam(
    exam_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    return service.get(exam_id)


@router.patch("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: UUID,
    exam_data: ExamUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    exam = service.update(exam_id, exam_data, current_user.id)
    try:
        db.commit()
        db.refresh(exam)
    except Exception:
        db.rollback()
        raise
    return exam


@router.get("/{exam_id}/validate", response_model=ExamScoreValidation)
def validate_exam_scores(
    exam_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    total, questions_total, valid = service.validate_scores(exam_id)
    return ExamScoreValidation(
        total_configured=total,
        total_questions=questions_total,
        is_valid=valid,
        differences=[] if valid else [f"Soma das questões ({questions_total}) ≠ Total configurado ({total})"],
    )


@router.post("/{exam_id}/publish", response_model=dict)
def publish_exam(
    exam_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Publica prova criando versão imutável."""
    service = ExamService(db)
    try:
        version = service.publish(exam_id, current_user.id)
        db.commit()
        db.refresh(version)
    except Exception:
        db.rollback()
        raise
    return {"version_id": str(version.id), "version_number": version.version_number, "message": "Prova publicada com sucesso"}


# ==================== Questions ====================

@router.post("/{exam_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    exam_id: UUID,
    question_data: QuestionCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    question_data = question_data.model_copy(update={"exam_id": exam_id})
    service = QuestionService(db)
    question = service.create(question_data)
    try:
        db.commit()
        db.refresh(question)
    except Exception:
        db.rollback()
        raise
    return question


@router.get("/{exam_id}/questions", response_model=List[dict])
def list_questions(
    exam_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = QuestionService(db)
    include_answer_key = current_user.role in {UserRole.TEACHER, UserRole.ADMIN}
    return [
        _question_response(question, include_answer_key)
        for question in service.repo.get_by_exam(exam_id)
    ]


@router.get("/questions/{question_id}", response_model=dict)
def get_question(
    question_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = QuestionService(db)
    question = service.get(question_id)
    include_answer_key = current_user.role in {UserRole.TEACHER, UserRole.ADMIN}
    return _question_response(question, include_answer_key)


@router.patch("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: UUID,
    question_data: QuestionUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = QuestionService(db)
    return service.update(question_id, question_data)


@router.post("/{exam_id}/questions/reorder", response_model=List[QuestionResponse])
def reorder_questions(
    exam_id: UUID,
    question_orders: List[dict],
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = QuestionService(db)
    return service.reorder(exam_id, question_orders)


# ==================== Answer Keys ====================

@router.post("/questions/{question_id}/answer-key", response_model=AnswerKeyResponse, status_code=status.HTTP_201_CREATED)
def create_answer_key(
    question_id: UUID,
    answer_key_data: AnswerKeyCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    answer_key_data = answer_key_data.model_copy(update={"question_id": question_id})
    service = AnswerKeyService(db)
    answer_key = service.create(answer_key_data)
    try:
        db.commit()
        db.refresh(answer_key)
    except Exception:
        db.rollback()
        raise
    return answer_key


@router.patch("/questions/{question_id}/answer-key", response_model=AnswerKeyResponse)
def update_answer_key(
    question_id: UUID,
    answer_key_data: AnswerKeyUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = AnswerKeyService(db)
    answer_key = service.update(question_id, answer_key_data)
    try:
        db.commit()
        db.refresh(answer_key)
    except Exception:
        db.rollback()
        raise
    return answer_key


# ==================== Grading Rubrics ====================

@router.post("/questions/{question_id}/rubric", response_model=GradingRubricResponse, status_code=status.HTTP_201_CREATED)
def create_rubric(
    question_id: UUID,
    rubric_data: GradingRubricCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    rubric_data.question_id = question_id
    service = GradingRubricService(db)
    return service.create(rubric_data)


@router.patch("/questions/{question_id}/rubric", response_model=GradingRubricResponse)
def update_rubric(
    question_id: UUID,
    rubric_data: GradingRubricUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = GradingRubricService(db)
    return service.update(question_id, rubric_data)


# ==================== Copies & Printing ====================

@router.post("/versions/{version_id}/copies", response_model=List[dict])
def generate_copies(
    version_id: UUID,
    count: int = Query(..., ge=1, le=500),
    student_ids: Optional[List[UUID]] = None,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Gera cópias para impressão."""
    service = ExamCopyService(db)
    try:
        copies = service.generate_copies(version_id, count, student_ids, current_user.id)
        db.commit()
        for copy in copies:
            db.refresh(copy)
    except Exception:
        db.rollback()
        raise
    return [{"id": str(c.id), "copy_identifier": c.copy_identifier} for c in copies]


@router.post("/copies/{copy_id}/pdf-student")
def generate_student_pdf(
    copy_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Gera PDF da prova do aluno."""
    service = ExamCopyService(db)
    try:
        pdf_path = service.generate_pdf_student(copy_id, current_user.id)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return _private_pdf_response(pdf_path)

@router.post("/versions/{version_id}/pdf-teacher")
def generate_teacher_pdf(
    version_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Gera PDF do gabarito do professor."""
    service = ExamCopyService(db)
    pdf_path = service.generate_pdf_teacher(version_id, current_user.id)
    return _private_pdf_response(pdf_path)

@router.post("/print-log", response_model=ExamPrintLogResponse)
def log_print(
    log_data: ExamPrintLogCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Registra log de impressão."""
    service = ExamCopyService(db)
    return service.log_print(log_data)


# ==================== Submissions ====================

@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    copy_id: UUID = Form(...),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Cria submissão com upload de arquivos."""
    from backend.app.integrations.storage import FileStorage

    # Salva arquivos
    storage = FileStorage()
    file_paths = []
    for file in files:
        path = await storage.save(file, folder="exams")
        file_paths.append(path)

    submission_data = SubmissionCreate(
        copy_id=copy_id,
        version_id=UUID("00000000-0000-0000-0000-000000000000"),  # será preenchido pelo service
        original_files=file_paths,
    )
    service = SubmissionService(db)
    submission = service.create(submission_data, current_user.id)
    try:
        page_paths = [
            page_path
            for file_path in file_paths
            for page_path in storage.expand_pdf_pages(file_path)
        ]
        service.add_pages(
            submission.id,
            [
                SubmissionPageCreate(
                    submission_id=submission.id,
                    page_number=page_number,
                    original_image_path=page_path,
                )
                for page_number, page_path in enumerate(page_paths, start=1)
            ],
        )
        db.commit()
        db.refresh(submission)
    except Exception:
        db.rollback()
        raise
    return submission


@router.get("/submissions")
def list_submissions(
    version_id: Optional[UUID] = None,
    student_id: Optional[UUID] = None,
    status: Optional[str] = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = SubmissionService(db)
    if current_user.role == UserRole.STUDENT:
        student = current_user.student_profile
        if student is None:
            filters = {"student_id": UUID(int=0)}
        else:
            filters = {"student_id": student.id}
        if version_id:
            filters["version_id"] = version_id
        if status:
            from backend.app.models.exam import SubmissionStatus
            filters["status"] = SubmissionStatus(status)
        submissions = service.repo.get_all(
            skip=params.offset,
            limit=params.limit,
            filters=filters,
            order_by="submitted_at",
            order_desc=True,
        )
        total = service.repo.count(filters=filters)
        items = [
            SubmissionStudentResponse.model_validate(submission).model_dump(mode="json")
            for submission in submissions
        ]
    elif version_id:
        submissions = service.repo.get_by_version(version_id)
        total = len(submissions)
        items = submissions
    elif student_id:
        submissions = service.repo.get_by_student(student_id)
        total = len(submissions)
        items = submissions
    elif status:
        from backend.app.models.exam import SubmissionStatus
        submissions = service.repo.get_all(filters={"status": SubmissionStatus(status)})
        total = len(submissions)
        items = submissions
    else:
        submissions = service.repo.get_all(skip=params.offset, limit=params.limit)
        total = len(submissions)
        items = submissions
    return PaginatedResponse(
        items=items, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/submissions/{submission_id}")
def get_submission(
    submission_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = SubmissionService(db)
    submission = service.repo.get_with_pages(submission_id)
    if not submission or (
        current_user.role == UserRole.STUDENT
        and (
            current_user.student_profile is None
            or submission.student_id != current_user.student_profile.id
        )
    ):
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    if current_user.role == UserRole.STUDENT:
        return SubmissionStudentResponse.model_validate(submission).model_dump(mode="json")
    return submission


@router.post("/submissions/{submission_id}/pages", response_model=List[dict])
def add_submission_pages(
    submission_id: UUID,
    pages: List[SubmissionPageCreate],
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = SubmissionService(db)
    created = service.add_pages(submission_id, pages)
    return [{"id": str(p.id), "page_number": p.page_number} for p in created]


@router.post("/submissions/{submission_id}/process-ocr")
def process_ocr(
    submission_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Processa OCR das páginas da submissão."""
    service = SubmissionService(db)
    try:
        submission = service.process_ocr(submission_id)
        extracted_answers = sum(len(page.extracted_answers) for page in submission.pages)
        db.commit()
        db.refresh(submission)
    except Exception:
        db.rollback()
        raise
    return {
        "submission_id": str(submission.id),
        "status": submission.status.value,
        "answers_extracted": extracted_answers,
    }


@router.post("/submissions/{submission_id}/identify", response_model=SubmissionResponse)
def identify_student(
    submission_id: UUID,
    student_id: UUID,
    confidence: Decimal = Query(..., ge=0, le=100),
    manual: bool = False,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Identifica aluno da submissão."""
    service = SubmissionService(db)
    return service.identify_student(submission_id, student_id, confidence, manual)


@router.post("/submissions/{submission_id}/request-correction", response_model=SubmissionResponse)
def request_ai_correction(
    submission_id: UUID,
    question_ids: Optional[List[UUID]] = None,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Solicita correção por IA."""
    service = SubmissionService(db)
    return service.request_ai_correction(submission_id, question_ids)


# ==================== QR Code ====================

@router.post("/qr/generate", response_model=dict)
def generate_qr_codes(
    request: QRCodeGenerateRequest,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Gera QR Codes para cópias."""
    from backend.app.integrations.qr.generator import QRCodeGenerator
    qr_gen = QRCodeGenerator()

    items = []
    for copy_data in request.copies:
        qr_data = QRCodeGenerator.build_exam_qr_data(
            exam_id=str(copy_data.exam_id),
            version_id=str(copy_data.version_id),
            copy_identifier=copy_data.copy_identifier,
            student_id=str(copy_data.student_id) if copy_data.student_id else None,
        )
        items.append(qr_data)

    paths = qr_gen.generate_batch(items, output_dir="./storage/exams/qrcodes", prefix="qr_")
    return {"count": len(paths), "paths": paths}