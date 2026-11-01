"""Repositories package initialization."""

from backend.app.repositories.base import BaseRepository
from backend.app.repositories.user_repository import (
    UserRepository,
    StudentRepository,
    TeacherRepository,
    AdministratorRepository,
)
from backend.app.repositories.academic_repository import (
    CourseRepository,
    SubjectRepository,
    ClassRepository,
    AcademicPeriodRepository,
    EnrollmentRepository,
    TeacherSubjectRepository,
    AssessmentRepository,
    GradeRepository,
    AttendanceRepository,
    AcademicRuleRepository,
)
from backend.app.repositories.exam_repository import (
    ExamRepository,
    ExamVersionRepository,
    ExamQuestionRepository,
    AnswerKeyRepository,
    GradingRubricRepository,
    ExamCopyRepository,
    ExamPrintLogRepository,
    ExamSubmissionRepository,
    SubmissionPageRepository,
    ExtractedAnswerRepository,
)
from backend.app.repositories.ai_correction_repository import (
    AICorrectionRepository,
    CorrectionReviewRepository,
    CorrectionAuditLogRepository,
    AuditLogRepository,
    SystemLogRepository,
)

__all__ = [
    "BaseRepository",
    # User
    "UserRepository",
    "StudentRepository",
    "TeacherRepository",
    "AdministratorRepository",
    # Academic
    "CourseRepository",
    "SubjectRepository",
    "ClassRepository",
    "AcademicPeriodRepository",
    "EnrollmentRepository",
    "TeacherSubjectRepository",
    "AssessmentRepository",
    "GradeRepository",
    "AttendanceRepository",
    "AcademicRuleRepository",
    # Exam
    "ExamRepository",
    "ExamVersionRepository",
    "ExamQuestionRepository",
    "AnswerKeyRepository",
    "GradingRubricRepository",
    "ExamCopyRepository",
    "ExamPrintLogRepository",
    "ExamSubmissionRepository",
    "SubmissionPageRepository",
    "ExtractedAnswerRepository",
    # AI Correction
    "AICorrectionRepository",
    "CorrectionReviewRepository",
    "CorrectionAuditLogRepository",
    "AuditLogRepository",
    "SystemLogRepository",
]