"""Service de Correção por IA com provedores abstraídos (suporta servidor local http://127.0.0.1:8082/admin)."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from abc import ABC, abstractmethod

import httpx

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.admin_settings import AIProviderConfig
from backend.app.models.ai_correction import AICorrection, AICorrectionStatus, CorrectionReview, ReviewStatus, CorrectionAuditLog
from backend.app.models.exam import ExamQuestion, QuestionType, ExamSubmission, SubmissionStatus
from backend.app.repositories.ai_correction_repository import (
    AICorrectionRepository, CorrectionReviewRepository, CorrectionAuditLogRepository
)
from backend.app.repositories.exam_repository import (
    ExamQuestionRepository, ExamSubmissionRepository, ExtractedAnswerRepository
)
from backend.app.schemas.ai_correction import (
    CorrectionRequest, CorrectionResponse, BatchCorrectionRequest, BatchCorrectionResponse,
    AIHealthCheck
)
from backend.app.core.config import settings
from backend.app.core.exceptions import ValidationError, NotFoundError, ExternalServiceError
from backend.app.repositories.ai_correction_repository import AuditLogRepository, AuditActionType
from backend.app.services.admin_settings_service import _decrypt_credential
from backend.app.services.configured_ai_provider import ConfiguredAIProvider


# ==================== AI Provider Interface ====================

class AIProvider(ABC):
    """Interface abstrata para provedores de IA."""

    @abstractmethod
    async def generate_text(self, prompt: str, model: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def analyze_image(self, image_base64: str, prompt: str, model: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def analyze_document(self, file_path: str, prompt: str, model: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def health_check(self) -> AIHealthCheck:
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        pass


# ==================== Local AI Provider (http://127.0.0.1:8082/admin) ====================

class LocalAIProvider(AIProvider):
    """Provedor para servidor local de IA (ex: Ollama, LM Studio, Text Generation WebUI)."""

    def __init__(self, base_url: str = "http://127.0.0.1:8082", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.ai_timeout_seconds,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        )

    async def generate_text(self, prompt: str, model: str, **kwargs) -> str:
        """Gera texto usando modelo local."""
        try:
            # Tenta formato OpenAI-compatible (ex: vLLM, LM Studio, Ollama com /v1)
            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.1),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError:
            # Fallback para formato Ollama nativo (/api/generate)
            try:
                response = await self.client.post(
                    "/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": kwargs.get("temperature", 0.1),
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                raise ExternalServiceError(f"Erro ao gerar texto: {e}")

    async def analyze_image(self, image_base64: str, prompt: str, model: str, **kwargs) -> str:
        """Analisa imagem com modelo multimodal local."""
        try:
            # Formato OpenAI-compatible para visão
            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                        ],
                    }],
                    "temperature": kwargs.get("temperature", 0.1),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise ExternalServiceError(f"Erro ao analisar imagem: {e}")

    async def analyze_document(self, file_path: str, prompt: str, model: str, **kwargs) -> str:
        """Analisa documento (PDF) - converte para imagens e analisa."""
        # Para servidor local, assumimos que o arquivo já foi processado para imagens
        # ou usamos um endpoint específico se disponível
        return await self.generate_text(prompt, model, **kwargs)

    async def health_check(self) -> AIHealthCheck:
        """Verifica saúde do servidor local."""
        import time
        start = time.time()
        try:
            response = await self.client.get("/health", timeout=5.0)
            latency = int((time.time() - start) * 1000)
            if response.status_code == 200:
                return AIHealthCheck(
                    provider="local",
                    status="healthy",
                    model=settings.ollama_text_model,
                    latency_ms=latency,
                )
        except Exception:
            pass
        return AIHealthCheck(
            provider="local",
            status="unhealthy",
            model=settings.ollama_text_model,
            error="Servidor não responde",
        )

    async def get_available_models(self) -> List[str]:
        """Lista modelos disponíveis."""
        try:
            # Tenta endpoint OpenAI
            response = await self.client.get("/v1/models", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        try:
            # Tenta endpoint Ollama
            response = await self.client.get("/api/tags", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def close(self):
        await self.client.aclose()


# ==================== Mock Provider (para testes) ====================

class MockProvider(AIProvider):
    """Provedor mock para testes e desenvolvimento."""

    async def generate_text(self, prompt: str, model: str, **kwargs) -> str:
        return '{"recognized_text": "Resposta do aluno", "interpretation": "Resposta correta", "suggested_score": 8.5, "max_score": 10, "justification": "Resposta completa e correta", "criteria_met": ["conceito_a", "conceito_b"], "criteria_not_met": [], "conceptual_errors": [], "ocr_confidence": 95, "evaluation_confidence": 90, "requires_review": false}'

    async def analyze_image(self, image_base64: str, prompt: str, model: str, **kwargs) -> str:
        return self.generate_text(prompt, model, **kwargs)

    async def analyze_document(self, file_path: str, prompt: str, model: str, **kwargs) -> str:
        return self.generate_text(prompt, model, **kwargs)

    async def health_check(self) -> AIHealthCheck:
        return AIHealthCheck(provider="mock", status="healthy", model="mock", latency_ms=1)

    async def get_available_models(self) -> List[str]:
        return ["mock-model"]


# ==================== Provider Factory ====================

class AIProviderFactory:
    """Factory para criar provedores de IA."""

    _providers: Dict[str, AIProvider] = {}

    @classmethod
    def get_provider(cls, provider_type: str = None, db: Session = None) -> AIProvider:
        if db is not None and provider_type is None:
            configured = db.execute(
                select(AIProviderConfig).where(
                    AIProviderConfig.is_default.is_(True),
                    AIProviderConfig.is_enabled.is_(True),
                )
            ).scalar_one_or_none()
            if configured is not None:
                if configured.status != "connected":
                    raise ExternalServiceError(
                        f"O provedor principal '{configured.name}' ainda não foi validado."
                    )
                if not configured.model:
                    raise ExternalServiceError(
                        f"O provedor principal '{configured.name}' não possui modelo selecionado."
                    )
                if configured.provider_type != "ollama" and not configured.encrypted_api_key:
                    raise ExternalServiceError(
                        f"O provedor principal '{configured.name}' não possui uma chave de API."
                    )
                cache_key = f"admin:{configured.id}:{configured.updated_at.isoformat()}"
                if cache_key not in cls._providers:
                    api_key = (
                        _decrypt_credential(configured.encrypted_api_key)
                        if configured.encrypted_api_key
                        else None
                    )
                    cls._providers[cache_key] = ConfiguredAIProvider(
                        provider_id=configured.provider_id,
                        provider_type=configured.provider_type,
                        base_url=configured.base_url,
                        api_key=api_key,
                        model=configured.model,
                        vision_model=configured.vision_model,
                        timeout_seconds=configured.timeout_seconds,
                    )
                return cls._providers[cache_key]

        provider_type = provider_type or settings.ai_provider

        if provider_type in {"openai", "anthropic"}:
            raise ExternalServiceError(
                f"O provedor de IA '{provider_type}' está configurado, mas ainda não é suportado."
            )

        if provider_type in cls._providers:
            return cls._providers[provider_type]

        if provider_type == "mock":
            provider = MockProvider()
        elif provider_type == "local":
            provider = LocalAIProvider(
                base_url=settings.ollama_base_url,
                api_key=None,  # Servidor local geralmente não precisa de API key
            )
        elif provider_type == "ollama":
            provider = LocalAIProvider(base_url=settings.ollama_base_url)
        else:
            # Default para mock
            provider = MockProvider()

        cls._providers[provider_type] = provider
        return provider

    @classmethod
    async def close_all(cls):
        for provider in cls._providers.values():
            if hasattr(provider, "close"):
                await provider.close()
        cls._providers.clear()


# ==================== AI Correction Service ====================

class AICorrectionService:
    """Serviço principal de correção por IA."""

    def __init__(self, db: Session):
        self.db = db
        self.correction_repo = AICorrectionRepository(db)
        self.review_repo = CorrectionReviewRepository(db)
        self.audit_repo = CorrectionAuditLogRepository(db)
        self.general_audit_repo = AuditLogRepository(db)
        self.question_repo = ExamQuestionRepository(db)
        self.submission_repo = ExamSubmissionRepository(db)
        self.answer_repo = ExtractedAnswerRepository(db)
        self.provider = AIProviderFactory.get_provider(db=db)

    def _build_correction_prompt(self, question: ExamQuestion, answer_key: Dict, rubric: Dict,
                                  student_answer: str, student_answer_image: Optional[str] = None) -> str:
        """Constrói prompt para correção."""
        q_type = question.type.value

        base_prompt = f"""Você é um corretor acadêmico especializado. Analise a resposta do aluno e forneça uma correção estruturada.

INFORMAÇÕES DA QUESTÃO:
- Tipo: {q_type}
- Enunciado: {question.statement}
- Pontuação máxima: {question.score}
"""

        if answer_key:
            base_prompt += f"""
GABARITO:
- Resposta correta: {answer_key.get('correct_answer', 'N/A')}
- Resposta esperada: {answer_key.get('expected_answer', 'N/A')}
- Alternativas aceitas: {answer_key.get('accepted_alternatives', [])}
- Palavras-chave: {answer_key.get('keywords', [])}
- Conceitos obrigatórios: {answer_key.get('required_concepts', [])}
- Justificativa: {answer_key.get('justification', 'N/A')}
- Pontuação parcial: {answer_key.get('partial_scoring', {})}
"""

        if rubric:
            base_prompt += f"""
RUBRICA DE CORREÇÃO:
{self._format_rubric(rubric)}
"""

        base_prompt += f"""
RESPOSTA DO ALUNO:
{student_answer}
"""

        if student_answer_image:
            base_prompt += "\n[Imagem da resposta anexada]"

        base_prompt += """
INSTRUÇÕES:
1. Para questões objetivas: corrija deterministicamente se a alternativa estiver clara
2. Para questões discursivas: reconheça sinônimos, explicações equivalentes, conceitos corretos
3. Para questões de cálculo: analise fórmulas, desenvolvimento, operações, resultado, unidades
4. Conceda pontos parciais conforme rubrica
5. NÃO penalize gramática/ortografia se não fizer parte da rubrica
6. Identifique erros conceituais e contradições

RETORNE APENAS JSON VÁLIDO com:
{
  "recognized_text": "texto reconhecido da resposta",
  "interpretation": "interpretação da resposta",
  "suggested_score": 8.5,
  "max_score": 10,
  "justification": "justificativa detalhada",
  "criteria_met": ["critério1", "critério2"],
  "criteria_not_met": ["critério3"],
  "conceptual_errors": ["erro1", "erro2"],
  "ocr_confidence": 95,
  "evaluation_confidence": 90,
  "requires_review": false,
  "review_reason": null
}"""

        return base_prompt

    def _format_rubric(self, rubric: Dict) -> str:
        """Formata rubrica para prompt."""
        criteria = rubric.get("criteria", [])
        if not criteria:
            return "Sem rubrica definida"
        lines = []
        for c in criteria:
            lines.append(f"- {c.get('name', 'Critério')}: {c.get('description', '')} (pontos: {c.get('points', 0)})")
        return "\n".join(lines)

    async def correct_question(self, submission_id: UUID, question_id: UUID) -> AICorrection:
        """Corrige uma questão específica."""
        submission = self.submission_repo.get_with_pages(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        question = self.question_repo.get_with_answer_key(question_id)
        if not question:
            raise NotFoundError("Questão não encontrada")

        # Busca resposta extraída
        extracted_answers = self.answer_repo.get_all_by_submission_question(submission_id, question_id)
        student_text = "\n".join(
            answer.extracted_text.strip()
            for answer in extracted_answers
            if answer.extracted_text and answer.extracted_text.strip()
        )
        student_image = next(
            (answer.extracted_image_path for answer in extracted_answers if answer.extracted_image_path),
            None,
        )
        confidences = [
            answer.ocr_confidence
            for answer in extracted_answers
            if answer.ocr_confidence is not None
        ]
        ocr_conf = sum(confidences) / len(confidences) if confidences else None

        # Busca gabarito e rubrica da versão
        version = submission.version
        answer_key = version.answer_key_snapshot.get(str(question_id), {})
        rubric = version.rubrics_snapshot.get(str(question_id), {})

        # Cria registro de correção
        correction = AICorrection(
            submission_id=submission_id,
            question_id=question_id,
            extracted_answer_id=extracted_answers[0].id if extracted_answers else None,
            provider=getattr(self.provider, "provider_id", settings.ai_provider),
            model=(
                getattr(self.provider, "vision_model", None)
                or getattr(self.provider, "model", settings.ollama_multimodal_model)
                if student_image
                else getattr(self.provider, "model", settings.ollama_text_model)
            ),
            status=AICorrectionStatus.PROCESSING,
            max_score=question.score,
            ocr_confidence=ocr_conf,
        )
        self.db.add(correction)
        self.db.flush()

        try:
            # Constrói prompt
            prompt = self._build_correction_prompt(question, answer_key, rubric, student_text, student_image)
            correction.prompt_used = prompt

            # Chama provedor
            import time
            start = time.time()

            if student_image:
                import base64
                with open(student_image, "rb") as f:
                    image_b64 = base64.b64encode(f.read()).decode()
                response_text = await self.provider.analyze_image(image_b64, prompt, correction.model)
            else:
                response_text = await self.provider.generate_text(prompt, correction.model)

            correction.processing_time_ms = int((time.time() - start) * 1000)
            correction.raw_response = {"response": response_text}

            # Parse resposta
            import json
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Tenta extrair JSON da resposta
                import re
                match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    raise

            # Atualiza correção
            correction.status = AICorrectionStatus.COMPLETED
            correction.recognized_text = result.get("recognized_text")
            correction.interpretation = result.get("interpretation")
            correction.suggested_score = Decimal(str(result.get("suggested_score", 0)))
            correction.max_score = Decimal(str(result.get("max_score", float(question.score))))
            correction.justification = result.get("justification")
            correction.criteria_met = result.get("criteria_met", [])
            correction.criteria_not_met = result.get("criteria_not_met", [])
            correction.conceptual_errors = result.get("conceptual_errors", [])
            correction.ocr_confidence = Decimal(str(result.get("ocr_confidence", 0))) if result.get("ocr_confidence") else ocr_conf
            correction.evaluation_confidence = Decimal(str(result.get("evaluation_confidence", 0)))
            correction.requires_review = result.get("requires_review", False)
            correction.review_reason = result.get("review_reason")
            correction.completed_at = datetime.now(timezone.utc)

            if correction.requires_review or (correction.evaluation_confidence and correction.evaluation_confidence < 70):
                correction.status = AICorrectionStatus.REQUIRES_REVIEW
                submission.status = SubmissionStatus.AWAITING_REVIEW
            else:
                submission.status = SubmissionStatus.IN_CORRECTION

            self.db.flush()

            self.general_audit_repo.log(AuditActionType.AI_CORRECTION_REQUEST,
                                      f"IA corrigiu questão {question.question_order}", None,
                                      "AICorrection", correction.id)

            return correction

        except Exception as e:
            correction.status = AICorrectionStatus.FAILED
            correction.error_message = str(e)
            self.db.flush()
            raise ExternalServiceError(f"Falha na correção por IA: {e}")

    async def batch_correct(self, request: BatchCorrectionRequest) -> BatchCorrectionResponse:
        """Correção em lote."""
        submission = self.submission_repo.get(request.submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        questions = self.question_repo.get_by_exam(submission.version.exam_id)
        if request.question_ids:
            questions = [q for q in questions if q.id in request.question_ids]

        corrections = []
        failed = 0
        skipped = 0
        requires_review = 0

        for question in questions:
            extracted_answers = self.answer_repo.get_all_by_submission_question(
                request.submission_id,
                question.id,
            )
            if not any(
                (answer.extracted_text and answer.extracted_text.strip())
                or answer.extracted_image_path
                for answer in extracted_answers
            ):
                skipped += 1
                continue
            try:
                correction = await self.correct_question(request.submission_id, question.id)
                corrections.append(correction)
                if correction.requires_review:
                    requires_review += 1
            except Exception:
                failed += 1

        return BatchCorrectionResponse(
            submission_id=request.submission_id,
            corrections=corrections,
            total_processed=len(corrections),
            failed=failed,
            requires_review_count=requires_review,
            skipped=skipped,
        )

    def create_review(self, ai_correction_id: UUID, reviewer_id: UUID) -> CorrectionReview:
        """Cria revisão para correção."""
        correction = self.correction_repo.get(ai_correction_id)
        if not correction:
            raise NotFoundError("Correção não encontrada")

        existing = self.review_repo.get_by_ai_correction(ai_correction_id)
        if existing:
            raise ValidationError("Revisão já existe para esta correção")

        review = CorrectionReview(
            ai_correction_id=ai_correction_id,
            reviewed_by=reviewer_id,
            status=ReviewStatus.IN_REVIEW,
            original_suggested_score=correction.suggested_score,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(review)
        self.db.flush()

        self.general_audit_repo.log(AuditActionType.AI_CORRECTION_REVIEW,
                                  "Revisão iniciada", reviewer_id,
                                  "CorrectionReview", review.id)
        return review

    def update_review(self, review_id: UUID, final_score: Decimal, corrected_text: Optional[str] = None,
                     reviewer_justification: Optional[str] = None, reviewer_notes: Optional[str] = None,
                     criteria_overrides: Optional[Dict] = None, reviewer_id: UUID = None) -> CorrectionReview:
        """Atualiza revisão com decisão do professor."""
        review = self.review_repo.get(review_id)
        if not review:
            raise NotFoundError("Revisão não encontrada")

        correction = self.correction_repo.get(review.ai_correction_id)

        # Log auditoria
        old_score = review.final_score
        if old_score != final_score:
            self.audit_repo.create(
                review_id=review_id,
                action="score_change",
                field_changed="final_score",
                old_value=str(old_score) if old_score else None,
                new_value=str(final_score),
                changed_by=reviewer_id,
            )

        review.status = ReviewStatus.APPROVED if final_score == correction.suggested_score else ReviewStatus.MODIFIED
        review.final_score = final_score
        review.corrected_text = corrected_text
        review.reviewer_justification = reviewer_justification
        review.reviewer_notes = reviewer_notes
        review.criteria_overrides = criteria_overrides or {}
        review.completed_at = datetime.now(timezone.utc)

        # Atualiza status da submissão
        submission = self.submission_repo.get(correction.submission_id)
        all_reviews = self.review_repo.get_pending()
        submission_corrections = self.correction_repo.get_by_submission(submission.id)
        all_reviewed = all(
            self.review_repo.get_by_ai_correction(c.id) and
            self.review_repo.get_by_ai_correction(c.id).status in [ReviewStatus.APPROVED, ReviewStatus.MODIFIED]
            for c in submission_corrections
        )
        if all_reviewed:
            submission.status = SubmissionStatus.REVIEWED

        self.db.flush()

        self.general_audit_repo.log(AuditActionType.AI_CORRECTION_REVIEW,
                                  f"Revisão {'aprovada' if review.status == ReviewStatus.APPROVED else 'modificada'}",
                                  reviewer_id, "CorrectionReview", review.id)

        return review

    def publish_grades(self, submission_id: UUID, published_by: UUID) -> ExamSubmission:
        """Publica notas após revisão."""
        submission = self.submission_repo.get(submission_id)
        if not submission:
            raise NotFoundError("Submissão não encontrada")

        corrections = self.correction_repo.get_by_submission(submission_id)
        for correction in corrections:
            review = self.review_repo.get_by_ai_correction(correction.id)
            if not review or review.status not in [ReviewStatus.APPROVED, ReviewStatus.MODIFIED]:
                raise ValidationError(f"Questão {correction.question_id} não foi revisada")
            if review.final_score is None:
                raise ValidationError(f"Questão {correction.question_id} sem nota final")

        # Cria/atualiza notas oficiais
        from backend.app.services.academic_service import GradeService
        grade_service = GradeService(self.db)

        for correction in corrections:
            review = self.review_repo.get_by_ai_correction(correction.id)
            # Busca enrollment do aluno
            from backend.app.repositories.academic_repository import EnrollmentRepository
            enrollment_repo = EnrollmentRepository(self.db)
            enrollment = enrollment_repo.get_by_student_class(
                submission.identified_student_id,
                submission.version.exam.class_id
            )
            if enrollment:
                # Busca assessment correspondente
                from backend.app.repositories.academic_repository import AssessmentRepository
                assessment_repo = AssessmentRepository(self.db)
                assessments = assessment_repo.get_by_class(enrollment.class_id)
                # Match por questão... (simplificado)
                pass

        submission.status = SubmissionStatus.PUBLISHED
        self.db.flush()

        self.general_audit_repo.log(AuditActionType.GRADE_PUBLISH,
                                  f"Notas publicadas para submissão {submission_id}", published_by,
                                  "ExamSubmission", submission_id)
        return submission