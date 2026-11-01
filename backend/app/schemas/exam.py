"""Schemas Pydantic para Provas, Questões, Gabaritos, Impressão, Submissões."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, model_validator


# ==================== Exam Schemas ====================

class ExamBase(BaseModel):
    """Campos base da prova."""
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    class_id: UUID
    subject_id: UUID
    academic_period_id: UUID
    total_score: Decimal = Field(default=Decimal("10.00"), gt=0)
    scheduled_date: Optional[date] = None
    duration_minutes: int = Field(default=120, ge=10, le=480)
    print_config: Dict[str, Any] = Field(default_factory=dict)


class ExamCreate(ExamBase):
    """Schema para criação de prova."""
    pass


class ExamQuestionDraft(BaseModel):
    """Questão e gabarito enviados junto com a prova."""
    type: str = Field(pattern="^(multiple_choice|essay|short_answer|calculation|multi_criteria)$")
    statement: str = Field(min_length=1)
    score: Decimal = Field(gt=0)
    config: Dict[str, Any] = Field(default_factory=dict)
    correct_answer: Optional[str] = None
    expected_answer: Optional[str] = None
    accepted_alternatives: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    required_concepts: List[str] = Field(default_factory=list)
    justification: Optional[str] = None

    @model_validator(mode="after")
    def validate_answer_key(self):
        if not any((
            self.correct_answer,
            self.expected_answer,
            self.accepted_alternatives,
            self.keywords,
            self.required_concepts,
        )):
            raise ValueError("Cada questão precisa ter um gabarito ou resposta esperada.")

        if self.type == "multiple_choice":
            alternatives = self.config.get("alternatives", [])
            if not isinstance(alternatives, list) or len(alternatives) < 2:
                raise ValueError("Questões objetivas precisam ter pelo menos duas alternativas.")
            valid_answers = {chr(65 + index) for index in range(len(alternatives))}
            if self.correct_answer not in valid_answers:
                raise ValueError("A resposta correta deve indicar uma das alternativas cadastradas.")
        return self


class ExamCreateWithQuestions(ExamCreate):
    """Prova completa: dados, questões pontuadas e gabaritos."""
    questions: List[ExamQuestionDraft] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_question_scores(self):
        question_total = sum((question.score for question in self.questions), Decimal("0"))
        if question_total != self.total_score:
            raise ValueError(
                f"A soma das questões ({question_total}) deve ser igual ao valor total ({self.total_score})."
            )
        return self


class ExamUpdate(BaseModel):
    """Schema para atualização de prova."""
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    total_score: Optional[Decimal] = Field(None, gt=0)
    scheduled_date: Optional[date] = None
    duration_minutes: Optional[int] = Field(None, ge=10, le=480)
    status: Optional[str] = None
    print_config: Optional[Dict[str, Any]] = None


class ExamResponse(ExamBase):
    """Schema de resposta da prova."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_by: UUID
    status: str
    version: int
    is_template: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None


class ExamWithRelations(ExamResponse):
    """Prova com relacionamentos."""
    class_: "ClassResponse"
    subject: "SubjectResponse"
    questions_count: int = 0


# ==================== Exam Version Schemas ====================

class ExamVersionBase(BaseModel):
    """Campos base da versão de prova."""
    exam_id: UUID
    version_number: int
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    total_score: Decimal
    questions_snapshot: List[Dict[str, Any]]
    answer_key_snapshot: Dict[str, Any]
    rubrics_snapshot: Dict[str, Any]


class ExamVersionCreate(ExamVersionBase):
    """Schema para criação de versão."""
    published_by: UUID


class ExamVersionResponse(ExamVersionBase):
    """Schema de resposta da versão."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    published_by: UUID
    published_at: datetime
    is_active: bool


# ==================== Question Schemas ====================

class QuestionBase(BaseModel):
    """Campos base da questão."""
    exam_id: UUID
    question_order: int = Field(..., ge=1)
    type: str = Field(..., pattern="^(multiple_choice|essay|short_answer|calculation|multi_criteria)$")
    statement: str = Field(..., min_length=1)
    score: Decimal = Field(..., gt=0)
    config: Dict[str, Any] = Field(default_factory=dict)


class QuestionCreate(QuestionBase):
    """Schema para criação de questão."""
    pass


class QuestionUpdate(BaseModel):
    """Schema para atualização de questão."""
    question_order: Optional[int] = Field(None, ge=1)
    type: Optional[str] = None
    statement: Optional[str] = Field(None, min_length=1)
    score: Optional[Decimal] = Field(None, gt=0)
    config: Optional[Dict[str, Any]] = None


class QuestionResponse(QuestionBase):
    """Schema de resposta da questão."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class QuestionWithAnswerKey(QuestionResponse):
    """Questão com gabarito e rubrica."""
    answer_key: Optional["AnswerKeyResponse"] = None
    grading_rubric: Optional["GradingRubricResponse"] = None


# ==================== Answer Key Schemas ====================

class AnswerKeyBase(BaseModel):
    """Campos base do gabarito."""
    question_id: UUID
    correct_answer: Optional[str] = None
    expected_answer: Optional[str] = None
    accepted_alternatives: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    required_concepts: List[str] = Field(default_factory=list)
    justification: Optional[str] = None
    partial_scoring: Dict[str, Any] = Field(default_factory=dict)


class AnswerKeyCreate(AnswerKeyBase):
    """Schema para criação de gabarito."""
    pass


class AnswerKeyUpdate(BaseModel):
    """Schema para atualização de gabarito."""
    correct_answer: Optional[str] = None
    expected_answer: Optional[str] = None
    accepted_alternatives: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    required_concepts: Optional[List[str]] = None
    justification: Optional[str] = None
    partial_scoring: Optional[Dict[str, Any]] = None


class AnswerKeyResponse(AnswerKeyBase):
    """Schema de resposta do gabarito."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# ==================== Grading Rubric Schemas ====================

class GradingRubricBase(BaseModel):
    """Campos base da rubrica."""
    question_id: UUID
    criteria: List[Dict[str, Any]] = Field(default_factory=list)
    max_score: Decimal = Field(..., gt=0)


class GradingRubricCreate(GradingRubricBase):
    """Schema para criação de rubrica."""
    pass


class GradingRubricUpdate(BaseModel):
    """Schema para atualização de rubrica."""
    criteria: Optional[List[Dict[str, Any]]] = None
    max_score: Optional[Decimal] = Field(None, gt=0)


class GradingRubricResponse(GradingRubricBase):
    """Schema de resposta da rubrica."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# ==================== Exam Copy Schemas ====================

class ExamCopyBase(BaseModel):
    """Campos base da cópia de prova."""
    version_id: UUID
    copy_identifier: str
    qr_code_data: str
    student_id: Optional[UUID] = None
    is_personalized: bool = False


class ExamCopyCreate(ExamCopyBase):
    """Schema para criação de cópia."""
    pass


class ExamCopyResponse(ExamCopyBase):
    """Schema de resposta da cópia."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pdf_path: Optional[str] = None
    printed_at: Optional[datetime] = None
    printed_by: Optional[UUID] = None
    created_at: datetime


# ==================== Print Log Schemas ====================

class ExamPrintLogBase(BaseModel):
    """Campos base do log de impressão."""
    exam_id: UUID
    version_id: UUID
    printed_by: UUID
    copy_count: int = Field(..., ge=1)
    copy_identifiers: List[str]


class ExamPrintLogCreate(ExamPrintLogBase):
    """Schema para criação de log."""
    pass


class ExamPrintLogResponse(ExamPrintLogBase):
    """Schema de resposta do log."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    pdf_path: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


# ==================== Submission Schemas ====================

class SubmissionBase(BaseModel):
    """Campos base da submissão."""
    copy_id: UUID
    version_id: UUID
    student_id: Optional[UUID] = None
    original_files: List[str]


class SubmissionCreate(SubmissionBase):
    """Schema para criação de submissão."""
    pass


class SubmissionUpdate(BaseModel):
    """Schema para atualização de submissão."""
    status: Optional[str] = None
    processed_files: Optional[List[str]] = None
    identified_student_id: Optional[UUID] = None
    identification_confidence: Optional[Decimal] = None
    manual_identification: Optional[bool] = None


class SubmissionResponse(SubmissionBase):
    """Schema de resposta da submissão."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    processed_files: List[str]
    identified_student_id: Optional[UUID] = None
    identification_confidence: Optional[Decimal] = None
    manual_identification: bool
    submitted_at: datetime
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SubmissionWithRelations(SubmissionResponse):
    """Submissão com relacionamentos."""
    copy: ExamCopyResponse
    pages: List["SubmissionPageResponse"] = []
    ai_corrections: List["AICorrectionResponse"] = []


class SubmissionStudentResponse(BaseModel):
    """Visão limitada da própria submissão para estudantes."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    submitted_at: datetime
    processed_at: Optional[datetime] = None


# ==================== Submission Page Schemas ====================

class SubmissionPageBase(BaseModel):
    """Campos base da página de submissão."""
    submission_id: UUID
    page_number: int
    original_image_path: str


class SubmissionPageCreate(SubmissionPageBase):
    """Schema para criação de página."""
    pass


class SubmissionPageResponse(SubmissionPageBase):
    """Schema de resposta da página."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    processed_image_path: Optional[str] = None
    rotation_angle: float
    perspective_corrected: bool
    ocr_confidence: Optional[Decimal] = None
    created_at: datetime


# ==================== Extracted Answer Schemas ====================

class ExtractedAnswerBase(BaseModel):
    """Campos base da resposta extraída."""
    page_id: UUID
    question_id: UUID
    question_order: int
    extracted_text: Optional[str] = None
    extracted_image_path: Optional[str] = None
    ocr_confidence: Optional[Decimal] = None
    bounding_box: Dict[str, Any] = Field(default_factory=dict)


class ExtractedAnswerCreate(ExtractedAnswerBase):
    """Schema para criação de resposta extraída."""
    pass


class ExtractedAnswerResponse(ExtractedAnswerBase):
    """Schema de resposta da resposta extraída."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


# ==================== QR Code Schemas ====================

class QRCodeData(BaseModel):
    """Dados codificados no QR Code."""
    exam_id: UUID
    version_id: UUID
    copy_identifier: str
    student_id: Optional[UUID] = None


class QRCodeGenerateRequest(BaseModel):
    """Requisição para geração de QR Code."""
    exam_id: UUID
    version_id: UUID
    copies: List[QRCodeData]


# ==================== Validation Schemas ====================

class ExamScoreValidation(BaseModel):
    """Validação de pontuação da prova."""
    total_configured: Decimal
    total_questions: Decimal
    is_valid: bool
    differences: List[str] = Field(default_factory=list)


class QuestionScoreValidation(BaseModel):
    """Validação de pontuação da questão."""
    question_id: UUID
    question_score: Decimal
    max_possible: Decimal
    is_valid: bool