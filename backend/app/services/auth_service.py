"""Service de Autenticação e Autorização."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.exceptions import AuthenticationError, ValidationError
from backend.app.core.security import (
    TokenPayload,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from backend.app.models.user import User, UserRole
from backend.app.repositories.user_repository import (
    StudentRepository,
    TeacherRepository,
    UserRepository,
)
from backend.app.schemas.user import LoginRequest, TokenResponse, UserResponse


class AuthService:
    """Serviço de autenticação."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate(self, login_data: LoginRequest) -> TokenResponse:
        """Autentica usuário e retorna tokens."""
        user = self.user_repo.get_by_email_or_username(login_data.username)
        if not user:
            raise AuthenticationError("Credenciais inválidas")

        if not user.is_active:
            raise AuthenticationError("Usuário inativo")

        if not verify_password(login_data.password, user.hashed_password):
            # Log failed attempt
            from backend.app.repositories.ai_correction_repository import AuditLogRepository
            audit_repo = AuditLogRepository(self.db)
            audit_repo.log(
                action="login_failed",
                description=f"Tentativa de login falhada para {login_data.username}",
                user_id=user.id,
                success=False,
                error_message="Senha incorreta",
            )
            raise AuthenticationError("Credenciais inválidas")

        # Update last login
        user.last_login = datetime.now(UTC)
        self.db.flush()

        # Log successful login
        from backend.app.repositories.ai_correction_repository import AuditLogRepository
        audit_repo = AuditLogRepository(self.db)
        audit_repo.log(
            action="login",
            description=f"Login bem-sucedido para {user.email}",
            user_id=user.id,
            success=True,
        )

        return self._create_token_response(user)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Renova access token usando refresh token."""
        try:
            payload = decode_token(refresh_token)
            if payload.type != "refresh":
                raise AuthenticationError("Token inválido")
        except Exception as error:
            raise AuthenticationError("Refresh token inválido ou expirado") from error

        user = self.user_repo.get(UUID(payload.user_id))
        if not user or not user.is_active:
            raise AuthenticationError("Usuário não encontrado ou inativo")

        return self._create_token_response(user)

    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Altera senha do usuário."""
        user = self.user_repo.get(user_id)
        if not user:
            raise ValidationError("Usuário não encontrado")

        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError("Senha atual incorreta")

        user.hashed_password = get_password_hash(new_password)
        self.db.flush()

        # Log password change
        from backend.app.repositories.ai_correction_repository import AuditLogRepository
        audit_repo = AuditLogRepository(self.db)
        audit_repo.log(
            action="password_change",
            description=f"Senha alterada para usuário {user.email}",
            user_id=user.id,
            success=True,
        )

        return True

    def validate_token(self, token: str) -> TokenPayload:
        """Valida e decodifica token."""
        return decode_token(token)

    def _create_token_response(self, user: User) -> TokenResponse:
        """Cria resposta com tokens."""
        access_token = create_access_token(
            subject=user.email,
            role=user.role.value,
            user_id=user.id,
        )
        refresh_token = create_refresh_token(
            subject=user.email,
            role=user.role.value,
            user_id=user.id,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=UserResponse.model_validate(user),
        )


class PermissionService:
    """Serviço de verificação de permissões."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.teacher_repo = TeacherRepository(db)
        self.student_repo = StudentRepository(db)

    def can_access_class(self, user: User, class_id: UUID) -> bool:
        """Verifica se usuário pode acessar turma."""
        if user.role == UserRole.ADMIN:
            return True

        if user.role == UserRole.TEACHER:
            teacher = self.teacher_repo.get_by_user_id(user.id)
            if teacher:
                from backend.app.repositories.academic_repository import ClassRepository
                class_repo = ClassRepository(self.db)
                class_obj = class_repo.get(class_id)
                return class_obj and class_obj.teacher_id == teacher.id

        if user.role == UserRole.STUDENT:
            student = self.student_repo.get_by_user_id(user.id)
            if student:
                from backend.app.repositories.academic_repository import EnrollmentRepository
                enrollment_repo = EnrollmentRepository(self.db)
                enrollment = enrollment_repo.get_by_student_class(student.id, class_id)
                return enrollment is not None and enrollment.status.value == "active"

        return False

    def can_manage_exam(self, user: User, exam_id: UUID) -> bool:
        """Verifica se usuário pode gerenciar prova."""
        if user.role == UserRole.ADMIN:
            return True

        if user.role == UserRole.TEACHER:
            teacher = self.teacher_repo.get_by_user_id(user.id)
            if teacher:
                from backend.app.repositories.exam_repository import ExamRepository
                exam_repo = ExamRepository(self.db)
                exam = exam_repo.get(exam_id)
                if exam:
                    from backend.app.repositories.academic_repository import ClassRepository
                    class_repo = ClassRepository(self.db)
                    class_obj = class_repo.get(exam.class_id)
                    return class_obj and class_obj.teacher_id == teacher.id

        return False

    def can_grade_submission(self, user: User, submission_id: UUID) -> bool:
        """Verifica se usuário pode corrigir submissão."""
        if user.role == UserRole.ADMIN:
            return True

        if user.role == UserRole.TEACHER:
            teacher = self.teacher_repo.get_by_user_id(user.id)
            if teacher:
                from backend.app.repositories.exam_repository import (
                    ExamRepository,
                    ExamSubmissionRepository,
                )
                submission_repo = ExamSubmissionRepository(self.db)
                submission = submission_repo.get(submission_id)
                if submission:
                    exam_repo = ExamRepository(self.db)
                    exam = exam_repo.get(submission.version_id)  # Note: version_id is ExamVersion
                    # Need to get exam from version
                    from backend.app.repositories.exam_repository import ExamVersionRepository
                    version_repo = ExamVersionRepository(self.db)
                    version = version_repo.get(submission.version_id)
                    if version:
                        exam = exam_repo.get(version.exam_id)
                        if exam:
                            from backend.app.repositories.academic_repository import ClassRepository
                            class_repo = ClassRepository(self.db)
                            class_obj = class_repo.get(exam.class_id)
                            return class_obj and class_obj.teacher_id == teacher.id

        return False
