"""Rotas de importação em massa (alunos e notas) com acompanhamento de progresso."""

from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from backend.app.api.routes.academic import require_class_permission
from backend.app.core.database import get_db
from backend.app.core.security import require_teacher_or_admin
from backend.app.models.operation_job import OperationKind
from backend.app.models.user import User
from backend.app.schemas.operation_job import OperationJobCreatedResponse
from backend.app.services.import_service import (
    BulkImportService,
    ImportFormatError,
    parse_csv_table,
)
from backend.app.services.operation_job_service import OperationJobService
from backend.app.services.operation_runner import run_import_job

router = APIRouter(prefix="/imports", tags=["Importações"])

MAX_IMPORT_BYTES = 5 * 1024 * 1024


async def _read_csv(upload: UploadFile) -> bytes:
    if upload is None or not upload.filename:
        raise HTTPException(status_code=422, detail="Envie um arquivo CSV.")
    suffix = upload.filename.lower().rsplit(".", 1)[-1]
    if suffix not in {"csv", "txt"}:
        raise HTTPException(status_code=422, detail="Envie um arquivo .csv com os dados.")
    try:
        content = await upload.read(MAX_IMPORT_BYTES + 1)
    finally:
        await upload.close()
    if len(content) > MAX_IMPORT_BYTES:
        raise HTTPException(status_code=413, detail="O CSV pode ter no máximo 5 MB.")
    return content


@router.post(
    "/students",
    response_model=OperationJobCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def import_students(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    class_id: UUID = Form(...),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Importa alunos (conta + perfil + matrícula) para a turma informada."""
    require_class_permission(db, current_user, class_id, "create_students")
    content = await _read_csv(file)
    try:
        headers, rows = parse_csv_table(content)
        BulkImportService.validate_student_csv(headers)
    except ImportFormatError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    jobs = OperationJobService(db)
    job = jobs.create(
        kind=OperationKind.STUDENT_IMPORT,
        title=f"Importação de alunos — {file.filename}",
        user_id=current_user.id,
        payload={"class_id": str(class_id), "filename": file.filename},
        total=len(rows),
        step_key="queued",
        step_label="Aguardando início",
    )
    background.add_task(
        run_import_job,
        job.id,
        kind=OperationKind.STUDENT_IMPORT.value,
        content=content,
        class_id=class_id,
        graded_by=current_user.id,
    )
    return OperationJobCreatedResponse(job_id=job.id, status=job.status.value)


@router.post(
    "/grades",
    response_model=OperationJobCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def import_grades(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    class_id: UUID = Form(...),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Importa notas (rascunho) de uma turma a partir de um CSV."""
    require_class_permission(db, current_user, class_id, "edit_grades")
    content = await _read_csv(file)
    try:
        headers, rows = parse_csv_table(content)
        BulkImportService.validate_grade_csv(headers)
    except ImportFormatError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    jobs = OperationJobService(db)
    job = jobs.create(
        kind=OperationKind.GRADE_IMPORT,
        title=f"Importação de notas — {file.filename}",
        user_id=current_user.id,
        payload={"class_id": str(class_id), "filename": file.filename},
        total=len(rows),
        step_key="queued",
        step_label="Aguardando início",
    )
    background.add_task(
        run_import_job,
        job.id,
        kind=OperationKind.GRADE_IMPORT.value,
        content=content,
        class_id=class_id,
        graded_by=current_user.id,
    )
    return OperationJobCreatedResponse(job_id=job.id, status=job.status.value)


@router.get("/templates/{kind}.csv", include_in_schema=False)
def download_template(kind: str):
    """Modelo de CSV para apoiar a importação."""
    from fastapi.responses import Response

    if kind == "students":
        content = (
            "nome;email;usuario;senha;ra;matricula\n"
            "Maria Souza;maria.souza@escola.edu.br;maria.souza;SenhaForte123;"
            "RA2026001;20261001\n"
        )
    elif kind == "grades":
        content = (
            "ra;avaliacao;nota\n"
            "RA123456;A1 — Validação;8,5\n"
        )
    else:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="modelo_{kind}.csv"'},
    )
