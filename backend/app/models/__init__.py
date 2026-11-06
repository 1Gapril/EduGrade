"""Models package initialization."""

# User models
# Academic models
from backend.app.models.academic import (
    AcademicAssignment,
    AcademicPeriod,
    AcademicPeriodStatus,
    AcademicRule,
    Assessment,
    AssessmentType,
    Attendance,
    Class,
    Course,
    Enrollment,
    EnrollmentStatus,
    Grade,
    Subject,
    TeacherSubject,
)
from backend.app.models.access_request import AccessRequest, AccessRequestStatus
from backend.app.models.admin_settings import AdminSetting, AIProviderConfig

# AI Correction models
from backend.app.models.ai_correction import (
    AICorrection,
    AICorrectionStatus,
    CorrectionAuditLog,
    CorrectionReview,
    ReviewStatus,
)

# Audit models
from backend.app.models.audit import (
    AuditActionType,
    AuditLog,
    SystemLog,
)

# Exam models
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
    PrintStatus,
    QuestionType,
    SubmissionPage,
    SubmissionStatus,
)

# Grading Batch models (ADENDO OFICIAL)
from backend.app.models.grading_batch import (
    BatchStatus,
    ExamPageGroup,
    ExamSubmissionPage,
    FileStatus,
    GradingAuditLog,
    GradingBatch,
    GradingBatchFile,
    IdentificationStatus,
    PageGroupStatus,
    StudentIdentificationResult,
)
from backend.app.models.material import StudyMaterial
from backend.app.models.operation_job import (
    TERMINAL_STATUSES,
    OperationJob,
    OperationKind,
    OperationStatus,
)
from backend.app.models.quality_run import QualityRun
from backend.app.models.user import (
    Administrator,
    Student,
    Teacher,
    User,
    UserRole,
)

__all__ = [
    # User
    "User",
    "UserRole",
    "Student",
    "Teacher",
    "Administrator",
    "AccessRequest",
    "AccessRequestStatus",
    "StudyMaterial",
    "AIProviderConfig",
    "AdminSetting",
    "QualityRun",
    # Operações de longa duração
    "OperationJob",
    "OperationKind",
    "OperationStatus",
    "TERMINAL_STATUSES",
    # Academic
    "Course",
    "Subject",
    "Class",
    "AcademicPeriod",
    "AcademicAssignment",
    "AcademicPeriodStatus",
    "Enrollment",
    "EnrollmentStatus",
    "TeacherSubject",
    "Assessment",
    "AssessmentType",
    "Grade",
    "Attendance",
    "AcademicRule",
    # Exam
    "Exam",
    "ExamStatus",
    "ExamVersion",
    "ExamQuestion",
    "QuestionType",
    "AnswerKey",
    "GradingRubric",
    "ExamCopy",
    "ExamPrintLog",
    "PrintStatus",
    "ExamSubmission",
    "SubmissionStatus",
    "SubmissionPage",
    "ExtractedAnswer",
    # AI Correction
    "AICorrection",
    "AICorrectionStatus",
    "CorrectionReview",
    "ReviewStatus",
    "CorrectionAuditLog",
    # Audit
    "AuditLog",
    "AuditActionType",
    "SystemLog",
    # Grading Batch
    "GradingBatch",
    "BatchStatus",
    "GradingBatchFile",
    "FileStatus",
    "ExamSubmissionPage",
    "StudentIdentificationResult",
    "IdentificationStatus",
    "ExamPageGroup",
    "PageGroupStatus",
    "GradingAuditLog",
]
