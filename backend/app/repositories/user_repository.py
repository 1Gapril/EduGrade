"""Repository de Usuários."""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from backend.app.models.user import User, UserRole, Student, Teacher, Administrator
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository para usuários."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Busca por email."""
        return self.get_by_field("email", email)

    def get_by_username(self, username: str) -> Optional[User]:
        """Busca por username."""
        return self.get_by_field("username", username)

    def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Busca por email ou username."""
        stmt = select(User).where(
            or_(User.email == identifier, User.username == identifier)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_role(self, role: UserRole, active_only: bool = True) -> List[User]:
        """Busca usuários por role."""
        filters = {"role": role}
        if active_only:
            filters["is_active"] = True
        return self.get_all(filters=filters)

    def search(self, query: str, role: Optional[UserRole] = None) -> List[User]:
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
            stmt = stmt.where(User.is_active == True)
        return list(self.db.execute(stmt).scalars().all())


class StudentRepository(BaseRepository[Student]):
    """Repository para alunos."""

    def __init__(self, db: Session):
        super().__init__(Student, db)

    def get_by_ra(self, ra: str) -> Optional[Student]:
        """Busca por RA."""
        return self.get_by_field("ra", ra)

    def get_by_user_id(self, user_id: UUID) -> Optional[Student]:
        """Busca por user_id."""
        return self.get_by_field("user_id", user_id)

    def get_by_class(self, class_id: UUID) -> List[Student]:
        """Busca alunos de uma turma."""
        return self.get_all(filters={"class_id": class_id})

    def get_by_course(self, course_id: UUID) -> List[Student]:
        """Busca alunos de um curso."""
        return self.get_all(filters={"course_id": course_id})


class TeacherRepository(BaseRepository[Teacher]):
    """Repository para professores."""

    def __init__(self, db: Session):
        super().__init__(Teacher, db)

    def get_by_employee_id(self, employee_id: str) -> Optional[Teacher]:
        """Busca por ID do funcionário."""
        return self.get_by_field("employee_id", employee_id)

    def get_by_user_id(self, user_id: UUID) -> Optional[Teacher]:
        """Busca por user_id."""
        return self.get_by_field("user_id", user_id)

    def get_by_subject(self, subject_id: UUID, academic_period_id: Optional[UUID] = None) -> List[Teacher]:
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

    def get_by_employee_id(self, employee_id: str) -> Optional[Administrator]:
        """Busca por ID do funcionário."""
        return self.get_by_field("employee_id", employee_id)

    def get_by_user_id(self, user_id: UUID) -> Optional[Administrator]:
        """Busca por user_id."""
        return self.get_by_field("user_id", user_id)