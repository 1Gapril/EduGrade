"""Rotas de Provas, Questões, Impressão e Submissões."""

from decimal import Decimal
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi import status as http_status
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.api.routes.academic import require_class_permission
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import (
    get_current_active_user,
    require_teacher_or_admin,
)
from backend.app.models.academic import (
    AcademicAssignment,
    Class,
    Enrollment,
    EnrollmentStatus,
    TeacherSubject,
)
from backend.app.models.exam import (
    Exam,
    ExamCopy,
    ExamQuestion,
    ExamStatus,
    ExamSubmission,
    ExamVersion,
)
from backend.app.models.user import User, UserRole
from backend.app.models.operation_job import OperationKind
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.operation_job import (
    OperationJobCreatedResponse,
    SubmissionFromUploadsRequest,
    SubmissionUploadResponse,
)
from backend.app.schemas.exam import (
    AnswerKeyCreate,
    AnswerKeyResponse,
    AnswerKeyUpdate,
    ExamCreate,
    ExamCreateWithQuestions,
    ExamPDFImportResponse,
    ExamPrintLogCreate,
    ExamPrintLogResponse,
    ExamResponse,
    ExamScoreValidation,
    ExamUpdate,
    ExamUpdateWithQuestions,
    ExamWithRelations,
    GradingRubricCreate,
    GradingRubricResponse,
    GradingRubricUpdate,
    QRCodeGenerateRequest,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    QuestionWithAnswerKey,
    SubmissionCreate,
    SubmissionPageCreate,
    SubmissionResponse,
    SubmissionStudentResponse,
)
from backend.app.services.exam_import_service import ExamPDFImportService
from backend.app.services.exam_service import (
    AnswerKeyService,
    ExamCopyService,
    ExamService,
    GradingRubricService,
    QuestionService,
    SubmissionService,
)
from backend.app.services.operation_job_service import OperationJobService
from backend.app.services.operation_runner import (
    run_ai_correction_job,
    run_exam_pdf_import_job,
)

router = APIRouter(prefix="/exams", tags=["Provas"])
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _private_pdf_response(file_path: str) -> FileResponse:
    pdf_directory = (PROJECT_ROOT / settings.pdf_dir).resolve() if not Path(
        settings.pdf_dir
    ).is_absolute() else Path(settings.pdf_dir).resolve()
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


# Statuses que o aluno pode visualizar. Rascunhos, provas em edição e
# provas canceladas ficam restritos a professores e administradores.
STUDENT_VISIBLE_EXAM_STATUSES = {
    ExamStatus.PUBLISHED,
    ExamStatus.PRINTED,
    ExamStatus.IN_APPLICATION,
    ExamStatus.AWAITING_CORRECTION,
    ExamStatus.IN_CORRECTION,
    ExamStatus.AWAITING_REVIEW,
    ExamStatus.FINALIZED,
}


def _parse_exam_status(status: str) -> ExamStatus:
    try:
        return ExamStatus(status)
    except ValueError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Status de prova inválido: {status}",
        ) from exc


def _teacher_id_or_none(current_user: User) -> UUID | None:
    """Retorna o id do perfil de professor, se o usuário for professor."""
    if current_user.role != UserRole.TEACHER:
        return None
    if not current_user.teacher_profile:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Perfil de professor não encontrado",
        )
    return current_user.teacher_profile.id


def _teacher_class_ids(db: Session, current_user: User, permission: str) -> set[UUID]:
    teacher_id = _teacher_id_or_none(current_user)
    if teacher_id is None:
        return set()
    allowed = {
        assignment.class_id
        for assignment in db.query(AcademicAssignment).filter(
            AcademicAssignment.teacher_id == teacher_id,
            AcademicAssignment.is_active.is_(True),
            AcademicAssignment.permissions[permission].as_boolean().is_(True),
        ).all()
    }
    legacy_classes = db.query(Class).join(
        TeacherSubject,
        (TeacherSubject.teacher_id == teacher_id)
        & (TeacherSubject.subject_id == Class.subject_id)
        & or_(
            TeacherSubject.academic_period_id.is_(None),
            TeacherSubject.academic_period_id == Class.academic_period_id,
        ),
    ).filter(Class.teacher_id == teacher_id).all()
    for class_record in legacy_classes:
        has_history = db.query(AcademicAssignment.id).filter(
            AcademicAssignment.teacher_id == teacher_id,
            AcademicAssignment.class_id == class_record.id,
        ).first()
        if has_history is None:
            allowed.add(class_record.id)
    return allowed


def _assert_exam_access(
    db: Session,
    current_user: User,
    exam_id: UUID,
    permission: str = "edit_assessments",
) -> Exam:
    """Garante que o usuário autenticado pode acessar/manter a prova."""
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Prova não encontrada")

    if current_user.role == UserRole.TEACHER:
        require_class_permission(db, current_user, exam.class_id, permission)
    elif current_user.role == UserRole.STUDENT:
        if (
            exam.class_id not in _student_class_ids(db, current_user)
            or exam.status not in STUDENT_VISIBLE_EXAM_STATUSES
        ):
            raise HTTPException(status_code=404, detail="Prova não encontrada")
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    return exam


def _assert_submission_access(
    db: Session,
    current_user: User,
    submission: ExamSubmission,
    permission: str,
) -> Exam:
    version = db.get(ExamVersion, submission.version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Versão da prova não encontrada")
    return _assert_exam_access(db, current_user, version.exam_id, permission)


def _assert_version_access(
    db: Session,
    current_user: User,
    version_id: UUID,
    permission: str,
) -> ExamVersion:
    version = db.get(ExamVersion, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Versão da prova não encontrada")
    _assert_exam_access(db, current_user, version.exam_id, permission)
    return version


def _assert_question_access(
    db: Session,
    current_user: User,
    question_id: UUID,
    permission: str = "edit_assessments",
) -> Exam:
    question = db.get(ExamQuestion, question_id)
    if not question:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Questão não encontrada",
        )
    return _assert_exam_access(db, current_user, question.exam_id, permission)


def _student_class_ids(db: Session, current_user: User) -> set[UUID]:
    if not current_user.student_profile:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Perfil de aluno não encontrado",
        )
    class_ids = set()
    if current_user.student_profile.class_id:
        class_ids.add(current_user.student_profile.class_id)
    enrollments = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == current_user.student_profile.id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
        )
        .all()
    )
    class_ids.update(enrollment.class_id for enrollment in enrollments)
    return class_ids


# ==================== Exams ====================

@router.post("/analyze-pdfs", response_model=ExamPDFImportResponse)
async def analyze_exam_pdfs(
    exam_file: UploadFile = File(...),
    answer_key_file: UploadFile | None = File(None),
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


@router.post(
    "/import/pdf",
    response_model=OperationJobCreatedResponse,
    status_code=http_status.HTTP_202_ACCEPTED,
)
async def import_exam_pdf_job(
    background_tasks: BackgroundTasks,
    exam_file: UploadFile = File(...),
    answer_key_file: UploadFile | None = File(None),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Analisa o PDF em segundo plano e acompanha as etapas pela barra global."""
    from backend.app.integrations.storage import FileStorage

    async def validate_pdf(upload: UploadFile | None, label: str) -> None:
        if upload is None:
            return
        suffix = Path((upload.filename or "").replace("\\", "/")).suffix.lower()
        if suffix != ".pdf":
            raise HTTPException(status_code=422, detail=f"Envie um arquivo PDF para {label}.")
        head = await upload.read(1024)
        await upload.seek(0)
        if b"%PDF-" not in head:
            raise HTTPException(
                status_code=422,
                detail=f"O arquivo enviado para {label} não é um PDF válido.",
            )

    await validate_pdf(answer_key_file, "o gabarito")
    await validate_pdf(exam_file, "a prova")

    storage = FileStorage()
    exam_path = await storage.save(exam_file, folder="temp")
    answer_key_path = (
        await storage.save(answer_key_file, folder="temp") if answer_key_file is not None else None
    )

    jobs = OperationJobService(db)
    job = jobs.create(
        kind=OperationKind.EXAM_PDF_IMPORT,
        title=f"Importação de prova — {exam_file.filename}",
        user_id=current_user.id,
        payload={
            "exam_filename": exam_file.filename,
            "answer_key_filename": answer_key_file.filename if answer_key_file else None,
        },
        step_key="queued",
        step_label="Aguardando início",
    )
    background_tasks.add_task(run_exam_pdf_import_job, job.id, exam_path, answer_key_path)
    return OperationJobCreatedResponse(job_id=job.id, status=job.status.value)


@router.post("/complete", response_model=ExamResponse, status_code=http_status.HTTP_201_CREATED)
def create_complete_exam(
    exam_data: ExamCreateWithQuestions,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Cria prova, questões e gabaritos na mesma transação."""
    # Validar se professor leciona a turma
    class_record = require_class_permission(
        db, current_user, exam_data.class_id, "create_assessments"
    )
    if (
        exam_data.subject_id != class_record.subject_id
        or exam_data.academic_period_id != class_record.academic_period_id
    ):
        raise HTTPException(status_code=422, detail="A prova não corresponde à disciplina e período da turma")

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


@router.post("", response_model=ExamResponse, status_code=http_status.HTTP_201_CREATED)
def create_exam(
    exam_data: ExamCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.TEACHER:
        require_class_permission(db, current_user, exam_data.class_id, "create_assessments")

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
    class_id: UUID | None = None,
    status: str | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = ExamService(db)
    parsed_status = _parse_exam_status(status) if status else None

    # Se for professor (não admin), filtrar apenas provas das turmas que leciona
    if current_user.role == UserRole.TEACHER:
        teacher_id = _teacher_id_or_none(current_user)
        # Buscar IDs das turmas do professor
        teacher_class_ids = {
            assignment.class_id
            for assignment in db.query(AcademicAssignment).filter(
                AcademicAssignment.teacher_id == teacher_id,
                AcademicAssignment.is_active.is_(True),
                AcademicAssignment.permissions["view_history"].as_boolean().is_(True),
            ).all()
        }
        legacy_classes = db.query(Class).join(
            TeacherSubject,
            (TeacherSubject.teacher_id == teacher_id)
            & (TeacherSubject.subject_id == Class.subject_id)
            & or_(
                TeacherSubject.academic_period_id.is_(None),
                TeacherSubject.academic_period_id == Class.academic_period_id,
            ),
        ).filter(Class.teacher_id == teacher_id).all()
        for legacy_class in legacy_classes:
            has_new_assignment_history = db.query(AcademicAssignment.id).filter(
                AcademicAssignment.teacher_id == teacher_id,
                AcademicAssignment.class_id == legacy_class.id,
            ).first()
            if has_new_assignment_history is None:
                teacher_class_ids.add(legacy_class.id)
        if class_id:
            # Se foi passado class_id, verificar se o professor leciona essa turma
            if class_id not in teacher_class_ids:
                raise HTTPException(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    detail="Você não leciona esta turma"
                )
            exams = service.repo.get_by_class(class_id)
        elif parsed_status:
            exams = service.repo.get_by_status(parsed_status)
            # Filtrar por turmas do professor
            exams = [e for e in exams if e.class_id in teacher_class_ids]
        else:
            # Buscar provas apenas das turmas do professor
            exams = []
            for class_id_ in teacher_class_ids:
                exams.extend(service.repo.get_by_class(class_id_))
        # Ordenar por data de criação (mais recentes primeiro) e paginar
        exams.sort(key=lambda e: e.created_at, reverse=True)
        total = len(exams)
        exams = exams[params.offset:params.offset + params.limit]
        return PaginatedResponse(
            items=exams, total=total, page=params.page, page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
            has_next=params.page * params.page_size < total, has_prev=params.page > 1,
        )

    # Aluno vê apenas provas das turmas em que está matriculado
    if current_user.role == UserRole.STUDENT:
        student_class_ids = _student_class_ids(db, current_user)
        if not student_class_ids:
            return PaginatedResponse(
                items=[], total=0, page=params.page, page_size=params.page_size,
                total_pages=0, has_next=False, has_prev=params.page > 1,
            )
        if class_id and class_id not in student_class_ids:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Você não está matriculado nesta turma",
            )
        query = db.query(Exam).filter(
            Exam.class_id.in_(student_class_ids),
            Exam.status.in_(STUDENT_VISIBLE_EXAM_STATUSES),
        )
        if parsed_status:
            query = query.filter(Exam.status == parsed_status)
        total = query.count()
        exams = query.order_by(Exam.created_at.desc()).offset(params.offset).limit(params.limit).all()
        return PaginatedResponse(
            items=exams, total=total, page=params.page, page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
            has_next=params.page * params.page_size < total, has_prev=params.page > 1,
        )

    # Admin vê todas as provas (com paginação consistente)
    query = db.query(Exam)
    if class_id:
        query = query.filter(Exam.class_id == class_id)
    if parsed_status:
        query = query.filter(Exam.status == parsed_status)
    total = query.count()
    exams = (
        query.order_by(Exam.created_at.desc())
        .offset(params.offset)
        .limit(params.limit)
        .all()
    )
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
    query = (
        db.query(ExamVersion)
        .join(Exam, Exam.id == ExamVersion.exam_id)
        .filter(ExamVersion.is_active.is_(True), Exam.status == ExamStatus.PUBLISHED)
    )

    # Se for professor, filtrar apenas versões de provas das turmas que leciona
    if current_user.role == UserRole.TEACHER:
        allowed_classes = _teacher_class_ids(db, current_user, "receive_submissions")
        query = query.filter(Exam.class_id.in_(allowed_classes or {UUID(int=0)}))

    versions = query.order_by(Exam.title, ExamVersion.version_number.desc()).all()
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
    exam = service.get(exam_id)
    if current_user.role == UserRole.STUDENT:
        student_class_ids = _student_class_ids(db, current_user)
        if exam.class_id not in student_class_ids or exam.status not in STUDENT_VISIBLE_EXAM_STATUSES:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Prova não encontrada",
            )
    elif current_user.role == UserRole.TEACHER:
        _assert_exam_access(db, current_user, exam_id, "view_history")
    return exam


@router.patch("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: UUID,
    exam_data: ExamUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    _assert_exam_access(db, current_user, exam_id)
    service = ExamService(db)
    exam = service.update(exam_id, exam_data, current_user.id)
    try:
        db.commit()
        db.refresh(exam)
    except Exception:
        db.rollback()
        raise
    return exam


@router.patch("/{exam_id}/complete", response_model=ExamResponse)
def update_complete_exam(
    exam_id: UUID,
    exam_data: ExamUpdateWithQuestions,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Atualiza dados, questões e gabaritos de uma prova em rascunho."""
    _assert_exam_access(db, current_user, exam_id)
    if current_user.role == UserRole.TEACHER:
        # A prova não pode ser transferida para uma turma de outro professor.
        require_class_permission(db, current_user, exam_data.class_id, "edit_assessments")
    service = ExamService(db)
    try:
        exam = service.update_with_questions(exam_id, exam_data, current_user.id)
        db.commit()
        db.refresh(exam)
    except Exception:
        db.rollback()
        raise
    return exam


@router.delete("/{exam_id}", response_model=ExamResponse)
def cancel_exam(
    exam_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Cancela uma prova preservando versões, cópias e histórico."""
    _assert_exam_access(db, current_user, exam_id, "edit_assessments")
    service = ExamService(db)
    try:
        exam = service.cancel(exam_id, current_user.id)
        db.commit()
        db.refresh(exam)
    except Exception:
        db.rollback()
        raise
    return exam


@router.post("/{exam_id}/restore", response_model=ExamResponse)
def restore_exam(
    exam_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Reativa uma prova cancelada como rascunho (permite publicar de novo)."""
    _assert_exam_access(db, current_user, exam_id, "edit_assessments")
    service = ExamService(db)
    try:
        exam = service.restore(exam_id, current_user.id)
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
    _assert_exam_access(db, current_user, exam_id, "view_history")
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
    _assert_exam_access(db, current_user, exam_id, "create_assessments")
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

@router.post("/{exam_id}/questions", response_model=QuestionResponse, status_code=http_status.HTTP_201_CREATED)
def create_question(
    exam_id: UUID,
    question_data: QuestionCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    question_data = question_data.model_copy(update={"exam_id": exam_id})
    _assert_exam_access(db, current_user, exam_id, "create_assessments")
    service = QuestionService(db)
    question = service.create(question_data)
    try:
        db.commit()
        db.refresh(question)
    except Exception:
        db.rollback()
        raise
    return question


@router.get("/{exam_id}/questions", response_model=list[dict])
def list_questions(
    exam_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    exam = _assert_exam_access(db, current_user, exam_id, "view_history")
    service = QuestionService(db)
    include_answer_key = current_user.role == UserRole.ADMIN
    if current_user.role == UserRole.TEACHER:
        assignment = db.query(AcademicAssignment).filter(
            AcademicAssignment.teacher_id == current_user.teacher_profile.id,
            AcademicAssignment.class_id == exam.class_id,
            AcademicAssignment.subject_id == exam.subject_id,
            AcademicAssignment.academic_period_id == exam.academic_period_id,
            AcademicAssignment.is_active.is_(True),
        ).first()
        include_answer_key = (
            assignment.permissions.get("manage_answer_keys") is True
            if assignment is not None
            else not db.query(AcademicAssignment.id).filter(
                AcademicAssignment.teacher_id == current_user.teacher_profile.id,
                AcademicAssignment.class_id == exam.class_id,
            ).first()
            and exam.class_.teacher_id == current_user.teacher_profile.id
        )
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
    exam = _assert_exam_access(db, current_user, question.exam_id, "view_history")
    include_answer_key = current_user.role == UserRole.ADMIN
    if current_user.role == UserRole.TEACHER:
        assignment = db.query(AcademicAssignment).filter(
            AcademicAssignment.teacher_id == current_user.teacher_profile.id,
            AcademicAssignment.class_id == exam.class_id,
            AcademicAssignment.subject_id == exam.subject_id,
            AcademicAssignment.academic_period_id == exam.academic_period_id,
            AcademicAssignment.is_active.is_(True),
        ).first()
        include_answer_key = (
            assignment.permissions.get("manage_answer_keys") is True
            if assignment is not None
            else not db.query(AcademicAssignment.id).filter(
                AcademicAssignment.teacher_id == current_user.teacher_profile.id,
                AcademicAssignment.class_id == exam.class_id,
            ).first()
            and exam.class_.teacher_id == current_user.teacher_profile.id
        )
    return _question_response(question, include_answer_key)


@router.patch("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: UUID,
    question_data: QuestionUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = QuestionService(db)
    _assert_question_access(db, current_user, question_id, "edit_assessments")
    return service.update(question_id, question_data)


@router.post("/{exam_id}/questions/reorder", response_model=list[QuestionResponse])
def reorder_questions(
    exam_id: UUID,
    question_orders: list[dict],
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = QuestionService(db)
    _assert_exam_access(db, current_user, exam_id, "edit_assessments")
    return service.reorder(exam_id, question_orders)


# ==================== Answer Keys ====================

@router.post("/questions/{question_id}/answer-key", response_model=AnswerKeyResponse, status_code=http_status.HTTP_201_CREATED)
def create_answer_key(
    question_id: UUID,
    answer_key_data: AnswerKeyCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    answer_key_data = answer_key_data.model_copy(update={"question_id": question_id})
    _assert_question_access(db, current_user, question_id, "manage_answer_keys")
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
    _assert_question_access(db, current_user, question_id, "manage_answer_keys")
    answer_key = service.update(question_id, answer_key_data)
    try:
        db.commit()
        db.refresh(answer_key)
    except Exception:
        db.rollback()
        raise
    return answer_key


# ==================== Grading Rubrics ====================

@router.post("/questions/{question_id}/rubric", response_model=GradingRubricResponse, status_code=http_status.HTTP_201_CREATED)
def create_rubric(
    question_id: UUID,
    rubric_data: GradingRubricCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    rubric_data.question_id = question_id
    _assert_question_access(db, current_user, question_id, "manage_answer_keys")
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
    _assert_question_access(db, current_user, question_id, "manage_answer_keys")
    return service.update(question_id, rubric_data)


# ==================== Copies & Printing ====================

@router.post("/versions/{version_id}/copies", response_model=list[dict])
def generate_copies(
    version_id: UUID,
    count: int = Query(..., ge=1, le=500),
    student_ids: list[UUID] | None = Query(None),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Gera cópias para impressão."""
    _assert_version_access(db, current_user, version_id, "create_assessments")
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
    copy = db.get(ExamCopy, copy_id)
    if copy is None:
        raise HTTPException(status_code=404, detail="Cópia de prova não encontrada")
    _assert_exam_access(db, current_user, copy.version.exam_id, "create_assessments")
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
    _assert_version_access(db, current_user, version_id, "manage_answer_keys")
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
    _assert_exam_access(db, current_user, log_data.exam_id, "create_assessments")
    version = _assert_version_access(db, current_user, log_data.version_id, "create_assessments")
    if version.exam_id != log_data.exam_id:
        raise HTTPException(status_code=422, detail="A versão não corresponde à prova informada")
    service = ExamCopyService(db)
    return service.log_print(log_data)


# ==================== Submissions ====================

@router.post("/submissions", response_model=SubmissionResponse, status_code=http_status.HTTP_201_CREATED)
async def create_submission(
    copy_id: UUID = Form(...),
    files: list[UploadFile] = File(...),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Cria submissão com upload de arquivos."""
    from backend.app.integrations.storage import FileStorage

    copy = db.get(ExamCopy, copy_id)
    if copy is None:
        raise HTTPException(status_code=404, detail="Cópia de prova não encontrada")
    _assert_exam_access(db, current_user, copy.version.exam_id, "upload_submissions")

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
    version_id: UUID | None = None,
    student_id: UUID | None = None,
    status: str | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = SubmissionService(db)
    if current_user.role == UserRole.STUDENT:
        student = current_user.student_profile
        filters = (
            {"student_id": UUID(int=0)}
            if student is None
            else {"student_id": student.id}
        )
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
    elif current_user.role == UserRole.TEACHER:
        allowed_classes = _teacher_class_ids(db, current_user, "receive_submissions")
        query = db.query(ExamSubmission).join(
            ExamVersion, ExamSubmission.version_id == ExamVersion.id
        ).join(Exam, ExamVersion.exam_id == Exam.id).filter(
            Exam.class_id.in_(allowed_classes or {UUID(int=0)})
        )
        if version_id:
            query = query.filter(ExamSubmission.version_id == version_id)
        if student_id:
            query = query.filter(ExamSubmission.student_id == student_id)
        if status:
            from backend.app.models.exam import SubmissionStatus
            query = query.filter(ExamSubmission.status == SubmissionStatus(status))
        total = query.count()
        items = [
            SubmissionResponse.model_validate(submission).model_dump(mode="json")
            for submission in query.order_by(ExamSubmission.submitted_at.desc())
            .offset(params.offset)
            .limit(params.limit)
            .all()
        ]
        submissions = items
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
    if items and not isinstance(items[0], dict):
        items = [
            SubmissionResponse.model_validate(submission).model_dump(mode="json")
            for submission in items
        ]
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
    if current_user.role == UserRole.TEACHER:
        _assert_submission_access(db, current_user, submission, "receive_submissions")
    return SubmissionResponse.model_validate(submission).model_dump(mode="json")


@router.post("/submissions/{submission_id}/pages", response_model=list[dict])
def add_submission_pages(
    submission_id: UUID,
    pages: list[SubmissionPageCreate],
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = SubmissionService(db)
    submission = service.repo.get(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission, "upload_submissions")
    created = service.add_pages(submission_id, pages)
    return [{"id": str(p.id), "page_number": p.page_number} for p in created]


# ==================== Uploads individuais (progresso real por arquivo) ====================

def _upload_storage_root() -> Path:
    """Diretório autorizado para arquivos enviados individualmente."""
    configured = Path(settings.upload_dir)
    if not configured.is_absolute():
        configured = PROJECT_ROOT / configured
    return configured.resolve()


def _validated_upload_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path = path.resolve()
    root = _upload_storage_root()
    if root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo enviado não encontrado")
    return path


@router.post("/uploads", response_model=SubmissionUploadResponse)
async def upload_submission_file(
    copy_id: UUID = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Recebe um arquivo por vez, permitindo progresso real no navegador.

    Os arquivos ficam em ``storage/exams`` e só passam a compor a submissão
    quando o professor envia a lista completa em ``/exams/submissions/from-uploads``.
    """
    from backend.app.integrations.storage import FileStorage

    copy = db.get(ExamCopy, copy_id)
    if copy is None:
        raise HTTPException(status_code=404, detail="Cópia de prova não encontrada")
    _assert_exam_access(db, current_user, copy.version.exam_id, "upload_submissions")

    storage = FileStorage()
    saved_path = await storage.save(file, folder="exams")
    path = _validated_upload_path(saved_path)
    return SubmissionUploadResponse(
        path=str(path),
        filename=file.filename or path.name,
        size_bytes=path.stat().st_size,
    )


@router.post(
    "/submissions/from-uploads",
    response_model=SubmissionResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_submission_from_uploads(
    data: SubmissionFromUploadsRequest,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Cria a submissão a partir dos arquivos já recebidos por ``/exams/uploads``."""
    from backend.app.integrations.storage import FileStorage

    copy = db.get(ExamCopy, data.copy_id)
    if copy is None:
        raise HTTPException(status_code=404, detail="Cópia de prova não encontrada")
    _assert_exam_access(db, current_user, copy.version.exam_id, "upload_submissions")

    paths: list[str] = []
    seen: set[str] = set()
    for upload in data.uploads:
        path = _validated_upload_path(upload.path)
        if str(path) in seen:
            raise HTTPException(status_code=422, detail="Arquivo repetido na submissão")
        seen.add(str(path))
        paths.append(str(path))

    submission_data = SubmissionCreate(
        copy_id=data.copy_id,
        version_id=copy.version_id,
        student_id=data.student_id,
        original_files=paths,
    )
    service = SubmissionService(db)
    try:
        submission = service.create(submission_data, current_user.id)
        storage = FileStorage()
        page_paths = [
            page_path for file_path in paths for page_path in storage.expand_pdf_pages(file_path)
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


@router.post(
    "/submissions/{submission_id}/correction-jobs",
    response_model=OperationJobCreatedResponse,
    status_code=http_status.HTTP_202_ACCEPTED,
)
def start_correction_job(
    submission_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Inicia OCR + correção por IA em segundo plano, com progresso por etapa."""
    submission = db.get(ExamSubmission, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission, "grade_questions")

    questions_total = (
        db.query(ExamQuestion).filter(ExamQuestion.exam_id == submission.version.exam_id).count()
    )
    jobs = OperationJobService(db)
    job = jobs.create(
        kind=OperationKind.AI_CORRECTION,
        title=f"Correção por IA — {submission.copy.copy_identifier}",
        user_id=current_user.id,
        payload={
            "submission_id": str(submission_id),
            "exam_id": str(submission.version.exam_id),
        },
        total=questions_total,
        step_key="queued",
        step_label="Aguardando início",
    )
    background_tasks.add_task(
        run_ai_correction_job,
        job.id,
        submission_id,
        current_user.id,
    )
    return OperationJobCreatedResponse(job_id=job.id, status=job.status.value)


@router.post("/submissions/{submission_id}/process-ocr")
def process_ocr(
    submission_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Processa OCR das páginas da submissão."""
    service = SubmissionService(db)
    submission = service.repo.get(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission, "run_ocr")
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
    submission = service.repo.get(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission, "receive_submissions")
    return service.identify_student(
        submission_id,
        student_id,
        confidence,
        manual,
        identified_by=current_user.id,
    )


@router.post("/submissions/{submission_id}/request-correction", response_model=SubmissionResponse)
def request_ai_correction(
    submission_id: UUID,
    question_ids: list[UUID] | None = None,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Solicita correção por IA."""
    service = SubmissionService(db)
    submission = service.repo.get(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission, "grade_questions")
    return service.request_ai_correction(submission_id, question_ids)


# ==================== QR Code ====================

@router.post("/qr/generate", response_model=dict)
def generate_qr_codes(
    request: QRCodeGenerateRequest,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Gera QR Codes para cópias."""
    _assert_exam_access(db, current_user, request.exam_id, "create_assessments")
    version = _assert_version_access(db, current_user, request.version_id, "create_assessments")
    if version.exam_id != request.exam_id or any(
        copy.exam_id != request.exam_id or copy.version_id != request.version_id
        for copy in request.copies
    ):
        raise HTTPException(status_code=422, detail="Os códigos QR devem corresponder à prova e versão autorizadas")
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

    paths = qr_gen.generate_batch(items, output_dir=settings.qr_dir, prefix="qr_")
    return {"count": len(paths), "paths": paths}
