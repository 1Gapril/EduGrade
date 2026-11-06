"""Repository de Provas e Questões."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

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
    SubmissionPage,
    SubmissionStatus,
)
from backend.app.repositories.base import BaseRepository


class ExamRepository(BaseRepository[Exam]):
    """Repository para provas."""

    def __init__(self, db: Session):
        super().__init__(Exam, db)

    def get_by_class(self, class_id: UUID) -> list[Exam]:
        """Busca provas de uma turma."""
        return self.get_all(filters={"class_id": class_id})

    def get_by_status(self, status: ExamStatus) -> list[Exam]:
        """Busca provas por status."""
        return self.get_all(filters={"status": status})

    def get_published(self, class_id: UUID) -> list[Exam]:
        """Busca provas publicadas de uma turma."""
        return self.get_all(filters={"class_id": class_id, "status": ExamStatus.PUBLISHED})

    def get_with_questions(self, exam_id: UUID) -> Exam | None:
        """Busca prova com questões carregadas."""
        stmt = select(Exam).options(
            joinedload(Exam.questions).joinedload(ExamQuestion.answer_key),
            joinedload(Exam.questions).joinedload(ExamQuestion.grading_rubric),
        ).where(Exam.id == exam_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def validate_total_score(self, exam_id: UUID) -> tuple[Decimal, Decimal, bool]:
        """Valida se soma das questões = total_score."""
        stmt = select(func.sum(ExamQuestion.score)).where(ExamQuestion.exam_id == exam_id)
        total_questions = self.db.execute(stmt).scalar_one_or_none() or Decimal("0")
        exam = self.get(exam_id)
        if not exam:
            return Decimal("0"), Decimal("0"), False
        is_valid = total_questions == exam.total_score
        return exam.total_score, total_questions, is_valid


class ExamVersionRepository(BaseRepository[ExamVersion]):
    """Repository para versões de provas."""

    def __init__(self, db: Session):
        super().__init__(ExamVersion, db)

    def get_by_exam(self, exam_id: UUID) -> list[ExamVersion]:
        """Busca versões de uma prova."""
        return self.get_all(filters={"exam_id": exam_id})

    def get_latest(self, exam_id: UUID) -> ExamVersion | None:
        """Busca versão mais recente."""
        stmt = select(ExamVersion).where(
            and_(ExamVersion.exam_id == exam_id, ExamVersion.is_active.is_(True))
        ).order_by(ExamVersion.version_number.desc()).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()


class ExamQuestionRepository(BaseRepository[ExamQuestion]):
    """Repository para questões."""

    def __init__(self, db: Session):
        super().__init__(ExamQuestion, db)

    def get_by_exam(self, exam_id: UUID) -> list[ExamQuestion]:
        """Busca questões de uma prova ordenadas."""
        stmt = select(ExamQuestion).where(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.question_order)
        return list(self.db.execute(stmt).scalars().all())

    def get_with_answer_key(self, question_id: UUID) -> ExamQuestion | None:
        """Busca questão com gabarito."""
        stmt = select(ExamQuestion).options(
            joinedload(ExamQuestion.answer_key),
            joinedload(ExamQuestion.grading_rubric),
        ).where(ExamQuestion.id == question_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()


class AnswerKeyRepository(BaseRepository[AnswerKey]):
    """Repository para gabaritos."""

    def __init__(self, db: Session):
        super().__init__(AnswerKey, db)

    def get_by_question(self, question_id: UUID) -> AnswerKey | None:
        """Busca gabarito da questão."""
        return self.get_by_field("question_id", question_id)


class GradingRubricRepository(BaseRepository[GradingRubric]):
    """Repository para rubricas."""

    def __init__(self, db: Session):
        super().__init__(GradingRubric, db)

    def get_by_question(self, question_id: UUID) -> GradingRubric | None:
        """Busca rubrica da questão."""
        return self.get_by_field("question_id", question_id)


class ExamCopyRepository(BaseRepository[ExamCopy]):
    """Repository para cópias de provas."""

    def __init__(self, db: Session):
        super().__init__(ExamCopy, db)

    def get_by_version(self, version_id: UUID) -> list[ExamCopy]:
        """Busca cópias de uma versão."""
        return self.get_all(filters={"version_id": version_id})

    def get_by_identifier(self, identifier: str) -> ExamCopy | None:
        """Busca por identificador único."""
        return self.get_by_field("copy_identifier", identifier)

    def get_by_student(self, student_id: UUID) -> list[ExamCopy]:
        """Busca cópias personalizadas de um aluno."""
        return self.get_all(filters={"student_id": student_id, "is_personalized": True})

    def get_unprinted(self, version_id: UUID) -> list[ExamCopy]:
        """Busca cópias não impressas."""
        stmt = select(ExamCopy).where(
            and_(ExamCopy.version_id == version_id, ExamCopy.printed_at.is_(None))
        )
        return list(self.db.execute(stmt).scalars().all())


class ExamPrintLogRepository(BaseRepository[ExamPrintLog]):
    """Repository para logs de impressão."""

    def __init__(self, db: Session):
        super().__init__(ExamPrintLog, db)

    def get_by_exam(self, exam_id: UUID) -> list[ExamPrintLog]:
        """Busca logs de impressão de uma prova."""
        return self.get_all(filters={"exam_id": exam_id})

    def get_by_version(self, version_id: UUID) -> list[ExamPrintLog]:
        """Busca logs de impressão de uma versão."""
        return self.get_all(filters={"version_id": version_id})


class ExamSubmissionRepository(BaseRepository[ExamSubmission]):
    """Repository para submissões."""

    def __init__(self, db: Session):
        super().__init__(ExamSubmission, db)

    def get_by_copy(self, copy_id: UUID) -> ExamSubmission | None:
        """Busca submissão por cópia."""
        return self.get_by_field("copy_id", copy_id)

    def get_by_version(self, version_id: UUID) -> list[ExamSubmission]:
        """Busca submissões de uma versão."""
        return self.get_all(filters={"version_id": version_id})

    def get_by_student(self, student_id: UUID) -> list[ExamSubmission]:
        """Busca submissões de um aluno."""
        return self.get_all(filters={"student_id": student_id})

    def get_pending_correction(self) -> list[ExamSubmission]:
        """Busca submissões aguardando correção."""
        return self.get_all(filters={"status": SubmissionStatus.AWAITING_CORRECTION})

    def get_with_pages(self, submission_id: UUID) -> ExamSubmission | None:
        """Busca submissão com páginas carregadas."""
        stmt = select(ExamSubmission).options(
            joinedload(ExamSubmission.pages).joinedload(SubmissionPage.extracted_answers),
        ).where(ExamSubmission.id == submission_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()


class SubmissionPageRepository(BaseRepository[SubmissionPage]):
    """Repository para páginas de submissão."""

    def __init__(self, db: Session):
        super().__init__(SubmissionPage, db)

    def get_by_submission(self, submission_id: UUID) -> list[SubmissionPage]:
        """Busca páginas de uma submissão."""
        stmt = select(SubmissionPage).where(
            SubmissionPage.submission_id == submission_id
        ).order_by(SubmissionPage.page_number)
        return list(self.db.execute(stmt).scalars().all())


class ExtractedAnswerRepository(BaseRepository[ExtractedAnswer]):
    """Repository para respostas extraídas."""

    def __init__(self, db: Session):
        super().__init__(ExtractedAnswer, db)

    def get_by_page(self, page_id: UUID) -> list[ExtractedAnswer]:
        """Busca respostas extraídas de uma página."""
        return self.get_all(filters={"page_id": page_id})

    def get_by_question(self, question_id: UUID) -> list[ExtractedAnswer]:
        """Busca respostas extraídas de uma questão."""
        return self.get_all(filters={"question_id": question_id})

    def get_by_submission_question(self, submission_id: UUID, question_id: UUID) -> ExtractedAnswer | None:
        """Busca resposta extraída de uma questão em uma submissão."""
        answers = self.get_all_by_submission_question(submission_id, question_id)
        return answers[0] if answers else None

    def get_all_by_submission_question(
        self,
        submission_id: UUID,
        question_id: UUID,
    ) -> list[ExtractedAnswer]:
        """Busca todas as páginas com resposta extraída para uma questão."""
        from backend.app.models.exam import SubmissionPage

        stmt = select(ExtractedAnswer).join(SubmissionPage).where(
            and_(
                SubmissionPage.submission_id == submission_id,
                ExtractedAnswer.question_id == question_id
            )
        ).order_by(SubmissionPage.page_number, ExtractedAnswer.created_at)
        return list(self.db.execute(stmt).scalars().all())
