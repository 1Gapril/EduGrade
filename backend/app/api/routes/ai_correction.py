"""Rotas de Correção por IA e Revisão."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.routes.exams import _assert_submission_access
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import get_current_active_user, require_teacher_or_admin
from backend.app.models.ai_correction import AICorrection, CorrectionReview
from backend.app.models.exam import ExamSubmission
from backend.app.models.user import User, UserRole
from backend.app.schemas.ai_correction import (
    AICorrectionResponse,
    AIHealthCheck,
    AIModelsList,
    BatchCorrectionRequest,
    BatchCorrectionResponse,
    CorrectionRequest,
    CorrectionResponse,
    CorrectionReviewResponse,
    CorrectionReviewUpdate,
)
from backend.app.services.ai_correction_service import AICorrectionService

router = APIRouter(prefix="/ai", tags=["Correção por IA"])


def _assert_correction_access(
    db: Session,
    current_user: User,
    correction_id: UUID,
    permission: str,
) -> AICorrection:
    correction = db.get(AICorrection, correction_id)
    if correction is None:
        raise HTTPException(status_code=404, detail="Correção não encontrada")
    submission = db.get(ExamSubmission, correction.submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission, permission)
    return correction


# ==================== AI Provider ====================

@router.get("/health", response_model=AIHealthCheck)
async def ai_health_check(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Verifica saúde do provedor de IA."""
    from backend.app.services.ai_correction_service import AIProviderFactory
    provider = AIProviderFactory.get_provider(db=db)
    return await provider.health_check()


@router.get("/models", response_model=AIModelsList)
async def list_ai_models(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Lista modelos disponíveis no provedor de IA."""
    from backend.app.services.ai_correction_service import AIProviderFactory
    provider = AIProviderFactory.get_provider(db=db)
    models = await provider.get_available_models()
    from backend.app.core.config import settings
    return AIModelsList(
        provider=getattr(provider, "provider_id", settings.ai_provider),
        models=models,
    )


# ==================== Corrections ====================

@router.post("/correct", response_model=CorrectionResponse)
async def correct_single(
    request: CorrectionRequest,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Corrige uma única resposta (para teste)."""
    from backend.app.services.ai_correction_service import AIProviderFactory

    provider = AIProviderFactory.get_provider(db=db)
    import json
    import time

    prompt = (
        f"{request.question_statement}\n\n"
        f"Gabarito: {json.dumps(request.answer_key, ensure_ascii=False)}\n"
        f"Rubrica: {json.dumps(request.rubric or {}, ensure_ascii=False)}\n"
        f"Pontuação máxima: {request.max_score}\n"
        f"Resposta do aluno: {request.student_answer}"
    )
    started_at = time.time()
    response_text = await provider.generate_text(
        prompt,
        getattr(provider, "model", settings.ollama_text_model),
    )
    processing_time_ms = int((time.time() - started_at) * 1000)

    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError:
        import re

        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match is None:
            raise HTTPException(
                status_code=502,
                detail="O provedor de IA retornou uma resposta que não é JSON.",
            )
        payload = json.loads(match.group())

    payload.setdefault("raw_response", {"response": response_text})
    payload.setdefault("processing_time_ms", processing_time_ms)
    payload.setdefault("max_score", request.max_score)
    return CorrectionResponse(**payload)


@router.post("/batch-correct", response_model=BatchCorrectionResponse)
async def batch_correct(
    request: BatchCorrectionRequest,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Correção em lote de uma submissão."""
    submission = db.get(ExamSubmission, request.submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission, "grade_questions")
    service = AICorrectionService(db)
    try:
        result = await service.batch_correct(request)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.get("/submissions/{submission_id}/corrections", response_model=list[AICorrectionResponse])
def list_corrections(
    submission_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Lista correções de uma submissão."""
    submission = db.get(ExamSubmission, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission, "review_corrections")
    service = AICorrectionService(db)
    return service.correction_repo.get_by_submission(submission_id)


@router.get("/corrections/{correction_id}", response_model=AICorrectionResponse)
def get_correction(
    correction_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Busca correção específica."""
    service = AICorrectionService(db)
    _assert_correction_access(db, current_user, correction_id, "review_corrections")
    correction = service.correction_repo.get_with_review(correction_id)
    if not correction:
        raise HTTPException(status_code=404, detail="Correção não encontrada")
    return correction


# ==================== Reviews ====================

@router.post("/corrections/{correction_id}/review", response_model=CorrectionReviewResponse)
def start_review(
    correction_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Inicia revisão de uma correção."""
    _assert_correction_access(db, current_user, correction_id, "review_corrections")
    service = AICorrectionService(db)
    return service.create_review(correction_id, current_user.id)


@router.patch("/reviews/{review_id}", response_model=CorrectionReviewResponse)
def update_review(
    review_id: UUID,
    review_data: CorrectionReviewUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Atualiza revisão com decisão do professor."""
    review = db.get(CorrectionReview, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Revisão não encontrada")
    _assert_correction_access(db, current_user, review.ai_correction_id, "review_corrections")
    service = AICorrectionService(db)
    return service.update_review(
        review_id=review_id,
        final_score=review_data.final_score,
        corrected_text=review_data.corrected_text,
        reviewer_justification=review_data.reviewer_justification,
        reviewer_notes=review_data.reviewer_notes,
        criteria_overrides=review_data.criteria_overrides,
        reviewer_id=current_user.id,
    )


@router.get("/reviews/pending", response_model=list[CorrectionReviewResponse])
def list_pending_reviews(
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Lista revisões pendentes do professor."""
    service = AICorrectionService(db)
    reviews = service.review_repo.get_pending()
    if current_user.role == UserRole.ADMIN:
        return reviews
    accessible = []
    for review in reviews:
        submission = db.get(ExamSubmission, review.ai_correction.submission_id)
        if submission is None:
            continue
        try:
            _assert_submission_access(db, current_user, submission, "review_corrections")
        except HTTPException as exc:
            if exc.status_code != 403:
                raise
            continue
        accessible.append(review)
    return accessible


# ==================== Publish Grades ====================

@router.post("/submissions/{submission_id}/publish-grades", response_model=dict)
def publish_grades(
    submission_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Publica notas após revisão completa."""
    submission_record = db.get(ExamSubmission, submission_id)
    if submission_record is None:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    _assert_submission_access(db, current_user, submission_record, "publish_grades")
    service = AICorrectionService(db)
    submission = service.publish_grades(submission_id, current_user.id)
    return {"message": "Notas publicadas com sucesso", "submission_id": str(submission.id)}
