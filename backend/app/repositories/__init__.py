"""Repositories package initialization."""

from backend.app.repositories.academic_repository import (
    AcademicPeriodRepository,
    AcademicRuleRepository,
    AssessmentRepository,
    AttendanceRepository,
    ClassRepository,
    CourseRepository,
    EnrollmentRepository,
    GradeRepository,
    SubjectRepository,
    TeacherSubjectRepository,
)
from backend.app.repositories.ai_correction_repository import (
    AICorrectionRepository,
    AuditLogRepository,
    CorrectionAuditLogRepository,
    CorrectionReviewRepository,
    SystemLogRepository,
)
from backend.app.repositories.base import BaseRepository
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
from backend.app.repositories.user_repository import (
    AdministratorRepository,
    StudentRepository,
    TeacherRepository,
    UserRepository,
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
