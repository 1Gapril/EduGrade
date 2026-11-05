"""Service de Usuários."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.app.core.security import get_password_hash
from backend.app.models.user import Administrator, Student, Teacher, User, UserRole
from backend.app.repositories.ai_correction_repository import AuditActionType, AuditLogRepository
from backend.app.repositories.user_repository import (
    AdministratorRepository,
    StudentRepository,
    TeacherRepository,
    UserRepository,
)
from backend.app.schemas.user import (
    AdministratorCreate,
    AdministratorUpdate,
    StudentCreate,
    StudentUpdate,
    TeacherCreate,
    TeacherUpdate,
    UserCreate,
    UserUpdate,
)


class UserService:
    """Serviço de usuários."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create_user(self, user_data: UserCreate, created_by: UUID) -> User:
        """Cria novo usuário."""
        # Check duplicates
        if self.user_repo.get_by_email(user_data.email):
            raise ConflictError("Email já cadastrado")
        if self.user_repo.get_by_username(user_data.username):
            raise ConflictError("Username já cadastrado")

        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=UserRole(user_data.role),
        )
        self.db.add(user)
        self.db.flush()

        self.audit_repo.log(
            action=AuditActionType.CREATE,
            description=f"Usuário criado: {user.email}",
            user_id=created_by,
            entity_type="User",
            entity_id=user.id,
            new_values={"email": user.email, "role": user.role.value},
        )

        return user

    def get_user(self, user_id: UUID) -> User:
        """Busca usuário por ID."""
        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        return user

    def update_user(self, user_id: UUID, user_data: UserUpdate, updated_by: UUID) -> User:
        """Atualiza usuário."""
        user = self.get_user(user_id)

        old_values = {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "role": user.role.value,
        }

        # Check email/username conflicts
        if (
            user_data.email
            and user_data.email != user.email
            and self.user_repo.get_by_email(user_data.email)
        ):
            raise ConflictError("Email já cadastrado")
        if (
            user_data.username
            and user_data.username != user.username
            and self.user_repo.get_by_username(user_data.username)
        ):
            raise ConflictError("Username já cadastrado")

        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.now(UTC)
        self.db.flush()

        new_values = {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "role": user.role.value,
        }

        self.audit_repo.log(
            action=AuditActionType.UPDATE,
            description=f"Usuário atualizado: {user.email}",
            user_id=updated_by,
            entity_type="User",
            entity_id=user.id,
            old_values=old_values,
            new_values=new_values,
        )

        return user

    def delete_user(self, user_id: UUID, deleted_by: UUID) -> bool:
        """Deleta usuário (soft delete - desativa)."""
        user = self.get_user(user_id)
        user.is_active = False
        self.db.flush()

        self.audit_repo.log(
            action=AuditActionType.DELETE,
            description=f"Usuário desativado: {user.email}",
            user_id=deleted_by,
            entity_type="User",
            entity_id=user.id,
        )
        return True

    def list_users(
        self,
        role: UserRole | None = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Lista usuários."""
        return self.user_repo.get_all(
            skip=skip,
            limit=limit,
            filters={"role": role, "is_active": True} if active_only else {"role": role} if role else None,
        )

    def search_users(self, query: str, role: UserRole | None = None) -> list[User]:
        """Busca usuários."""
        return self.user_repo.search(query, role)


class StudentService:
    """Serviço de alunos."""

    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create_student(self, student_data: StudentCreate, created_by: UUID) -> Student:
        """Cria perfil de aluno."""
        user = self.user_repo.get(student_data.user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        if user.role != UserRole.STUDENT:
            raise ValidationError("Usuário não possui role de aluno")

        if self.student_repo.get_by_ra(student_data.ra):
            raise ConflictError("RA já cadastrado")
        registration_number = getattr(student_data, "registration_number", None)
        if registration_number and self.student_repo.get_by_registration_number(registration_number):
            raise ConflictError("Matrícula institucional já cadastrada")
        if self.student_repo.get_by_user_id(student_data.user_id):
            raise ConflictError("Usuário já possui perfil de aluno")

        student = Student(**student_data.model_dump())
        self.db.add(student)
        self.db.flush()

        self.audit_repo.log(
            action=AuditActionType.CREATE,
            description=f"Perfil de aluno criado: {student.ra}",
            user_id=created_by,
            entity_type="Student",
            entity_id=student.id,
        )

        return student

    def get_student(self, student_id: UUID) -> Student:
        """Busca aluno por ID."""
        student = self.student_repo.get(student_id)
        if not student:
            raise NotFoundError("Aluno não encontrado")
        return student

    def get_student_by_user(self, user_id: UUID) -> Student | None:
        """Busca aluno por user_id."""
        return self.student_repo.get_by_user_id(user_id)

    def update_student(self, student_id: UUID, student_data: StudentUpdate, updated_by: UUID) -> Student:
        """Atualiza aluno."""
        student = self.get_student(student_id)

        old_values = {
            "ra": student.ra,
            "registration_number": student.registration_number,
            "course_id": str(student.course_id) if student.course_id else None,
            "class_id": str(student.class_id) if student.class_id else None,
            "status": student.status,
        }

        update_data = student_data.model_dump(exclude_unset=True)
        ra = update_data.get("ra")
        if ra and ra != student.ra and self.student_repo.get_by_ra(ra):
            raise ConflictError("RA já cadastrado")
        registration_number = update_data.get("registration_number")
        if (
            registration_number
            and registration_number != student.registration_number
            and self.student_repo.get_by_registration_number(registration_number)
        ):
            raise ConflictError("Matrícula institucional já cadastrada")
        for key, value in update_data.items():
            if hasattr(student, key):
                setattr(student, key, value)

        student.updated_at = datetime.now(UTC)
        self.db.flush()

        self.audit_repo.log(
            action=AuditActionType.UPDATE,
            description=f"Aluno atualizado: {student.ra}",
            user_id=updated_by,
            entity_type="Student",
            entity_id=student.id,
            old_values=old_values,
            new_values=student_data.model_dump(exclude_unset=True),
        )

        return student


class TeacherService:
    """Serviço de professores."""

    def __init__(self, db: Session):
        self.db = db
        self.teacher_repo = TeacherRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create_teacher(self, teacher_data: TeacherCreate, created_by: UUID) -> Teacher:
        """Cria perfil de professor."""
        user = self.user_repo.get(teacher_data.user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        if user.role != UserRole.TEACHER:
            raise ValidationError("Usuário não possui role de professor")

        if self.teacher_repo.get_by_employee_id(teacher_data.employee_id):
            raise ConflictError("ID do funcionário já cadastrado")
        if self.teacher_repo.get_by_user_id(teacher_data.user_id):
            raise ConflictError("Usuário já possui perfil de professor")

        teacher = Teacher(**teacher_data.model_dump())
        self.db.add(teacher)
        self.db.flush()

        self.audit_repo.log(
            action=AuditActionType.CREATE,
            description=f"Perfil de professor criado: {teacher.employee_id}",
            user_id=created_by,
            entity_type="Teacher",
            entity_id=teacher.id,
        )

        return teacher

    def get_teacher(self, teacher_id: UUID) -> Teacher:
        """Busca professor por ID."""
        teacher = self.teacher_repo.get(teacher_id)
        if not teacher:
            raise NotFoundError("Professor não encontrado")
        return teacher

    def get_teacher_by_user(self, user_id: UUID) -> Teacher | None:
        """Busca professor por user_id."""
        return self.teacher_repo.get_by_user_id(user_id)

    def update_teacher(self, teacher_id: UUID, teacher_data: TeacherUpdate, updated_by: UUID) -> Teacher:
        """Atualiza professor."""
        teacher = self.get_teacher(teacher_id)

        old_values = {
            "employee_id": teacher.employee_id,
            "department": teacher.department,
            "status": teacher.status,
        }

        update_data = teacher_data.model_dump(exclude_unset=True)
        employee_id = update_data.get("employee_id")
        if (
            employee_id
            and employee_id != teacher.employee_id
            and self.teacher_repo.get_by_employee_id(employee_id)
        ):
            raise ConflictError("ID do funcionário já cadastrado")
        for key, value in update_data.items():
            if hasattr(teacher, key):
                setattr(teacher, key, value)

        teacher.updated_at = datetime.now(UTC)
        self.db.flush()

        self.audit_repo.log(
            action=AuditActionType.UPDATE,
            description=f"Professor atualizado: {teacher.employee_id}",
            user_id=updated_by,
            entity_type="Teacher",
            entity_id=teacher.id,
            old_values=old_values,
            new_values=teacher_data.model_dump(exclude_unset=True),
        )

        return teacher


class AdministratorService:
    """Serviço de administradores."""

    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdministratorRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create_administrator(self, admin_data: AdministratorCreate, created_by: UUID) -> Administrator:
        """Cria perfil de administrador."""
        user = self.user_repo.get(admin_data.user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        if user.role != UserRole.ADMIN:
            raise ValidationError("Usuário não possui role de administrador")

        if self.admin_repo.get_by_employee_id(admin_data.employee_id):
            raise ConflictError("ID do funcionário já cadastrado")
        if self.admin_repo.get_by_user_id(admin_data.user_id):
            raise ConflictError("Usuário já possui perfil de administrador")

        admin = Administrator(**admin_data.model_dump())
        self.db.add(admin)
        self.db.flush()

        self.audit_repo.log(
            action=AuditActionType.CREATE,
            description=f"Perfil de administrador criado: {admin.employee_id}",
            user_id=created_by,
            entity_type="Administrator",
            entity_id=admin.id,
        )

        return admin

    def get_administrator(self, admin_id: UUID) -> Administrator:
        """Busca administrador por ID."""
        admin = self.admin_repo.get(admin_id)
        if not admin:
            raise NotFoundError("Administrador não encontrado")
        return admin

    def get_administrator_by_user(self, user_id: UUID) -> Administrator | None:
        """Busca administrador por user_id."""
        return self.admin_repo.get_by_user_id(user_id)

    def update_administrator(self, admin_id: UUID, admin_data: AdministratorUpdate, updated_by: UUID) -> Administrator:
        """Atualiza administrador."""
        admin = self.get_administrator(admin_id)

        update_data = admin_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(admin, key):
                setattr(admin, key, value)

        admin.updated_at = datetime.now(UTC)
        self.db.flush()

        self.audit_repo.log(
            action=AuditActionType.UPDATE,
            description=f"Administrador atualizado: {admin.employee_id}",
            user_id=updated_by,
            entity_type="Administrator",
            entity_id=admin.id,
        )

        return admin
