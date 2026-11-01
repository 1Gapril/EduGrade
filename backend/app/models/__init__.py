"""Models package initialization."""

# User models
from backend.app.models.user import (
    User,
    UserRole,
    Student,
    Teacher,
    Administrator,
)
from backend.app.models.access_request import AccessRequest, AccessRequestStatus
from backend.app.models.material import StudyMaterial
from backend.app.models.admin_settings import AIProviderConfig, AdminSetting

# Academic models
from backend.app.models.academic import (
    Course,
    Subject,
    Class,
    AcademicPeriod,
    AcademicPeriodStatus,
    Enrollment,
    EnrollmentStatus,
    TeacherSubject,
    Assessment,
    AssessmentType,
    Grade,
    Attendance,
    AcademicRule,
)

# Exam models
from backend.app.models.exam import (
    Exam,
    ExamStatus,
    ExamVersion,
    ExamQuestion,
    QuestionType,
    AnswerKey,
    GradingRubric,
    ExamCopy,
    ExamPrintLog,
    PrintStatus,
    ExamSubmission,
    SubmissionStatus,
    SubmissionPage,
    ExtractedAnswer,
)

# AI Correction models
from backend.app.models.ai_correction import (
    AICorrection,
    AICorrectionStatus,
    CorrectionReview,
    ReviewStatus,
    CorrectionAuditLog,
)

# Audit models
from backend.app.models.audit import (
    AuditLog,
    AuditActionType,
    SystemLog,
)

# Grading Batch models (ADENDO OFICIAL)
from backend.app.models.grading_batch import (
    GradingBatch,
    BatchStatus,
    GradingBatchFile,
    FileStatus,
    ExamSubmissionPage,
    StudentIdentificationResult,
    IdentificationStatus,
    ExamPageGroup,
    PageGroupStatus,
    GradingAuditLog,
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
    # Academic
    "Course",
    "Subject",
    "Class",
    "AcademicPeriod",
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