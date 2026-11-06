"""Repository de Usuários."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.app.models.user import Administrator, Student, Teacher, User, UserRole
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository para usuários."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        """Busca por email."""
        return self.get_by_field("email", email)

    def get_by_username(self, username: str) -> User | None:
        """Busca por username."""
        return self.get_by_field("username", username)

    def get_by_email_or_username(self, identifier: str) -> User | None:
        """Busca por email ou username."""
        stmt = select(User).where(
            or_(User.email == identifier, User.username == identifier)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_role(self, role: UserRole, active_only: bool = True) -> list[User]:
        """Busca usuários por role."""
        filters = {"role": role}
        if active_only:
            filters["is_active"] = True
        return self.get_all(filters=filters)

    def search(self, query: str, role: UserRole | None = None) -> list[User]:
        """Busca textual por nome, email ou username."""
        stmt = select(User).where(
            or_(
                User.full_name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
                User.username.ilike(f"%{query}%"),
            )
        )
        if role:
            stmt = stmt.where(User.role == role)
        if query:
            stmt = stmt.where(User.is_active.is_(True))
        return list(self.db.execute(stmt).scalars().all())


class StudentRepository(BaseRepository[Student]):
    """Repository para alunos."""

    def __init__(self, db: Session):
        super().__init__(Student, db)

    def get_by_ra(self, ra: str) -> Student | None:
        """Busca por RA."""
        return self.get_by_field("ra", ra)

    def get_by_registration_number(self, registration_number: str) -> Student | None:
        """Busca pela matrícula institucional."""
        return self.get_by_field("registration_number", registration_number)

    def get_by_user_id(self, user_id: UUID) -> Student | None:
        """Busca por user_id."""
        return self.get_by_field("user_id", user_id)

    def get_by_class(self, class_id: UUID) -> list[Student]:
        """Busca alunos de uma turma."""
        return self.get_all(filters={"class_id": class_id})

    def get_by_course(self, course_id: UUID) -> list[Student]:
        """Busca alunos de um curso."""
        return self.get_all(filters={"course_id": course_id})


class TeacherRepository(BaseRepository[Teacher]):
    """Repository para professores."""

    def __init__(self, db: Session):
        super().__init__(Teacher, db)

    def get_by_employee_id(self, employee_id: str) -> Teacher | None:
        """Busca por ID do funcionário."""
        return self.get_by_field("employee_id", employee_id)

    def get_by_user_id(self, user_id: UUID) -> Teacher | None:
        """Busca por user_id."""
        return self.get_by_field("user_id", user_id)

    def get_by_subject(self, subject_id: UUID, academic_period_id: UUID | None = None) -> list[Teacher]:
        """Busca professores autorizados para uma disciplina."""
        from backend.app.models.academic import TeacherSubject

        stmt = select(Teacher).join(TeacherSubject).where(
            TeacherSubject.subject_id == subject_id
        )
        if academic_period_id:
            stmt = stmt.where(
                (TeacherSubject.academic_period_id == academic_period_id) |
                (TeacherSubject.academic_period_id.is_(None))
            )
        return list(self.db.execute(stmt).scalars().all())


class AdministratorRepository(BaseRepository[Administrator]):
    """Repository para administradores."""

    def __init__(self, db: Session):
        super().__init__(Administrator, db)

    def get_by_employee_id(self, employee_id: str) -> Administrator | None:
        """Busca por ID do funcionário."""
        return self.get_by_field("employee_id", employee_id)

    def get_by_user_id(self, user_id: UUID) -> Administrator | None:
        """Busca por user_id."""
        return self.get_by_field("user_id", user_id)
