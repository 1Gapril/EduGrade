"""Schemas Pydantic para Usuário e Autenticação."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

# ==================== Base Schemas ====================

class UserBase(BaseModel):
    """Campos base do usuário."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    """Schema para criação de usuário."""
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(..., pattern="^(student|teacher|admin)$")


class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = Field(None, min_length=2, max_length=255)
    is_active: bool | None = None
    role: str | None = Field(None, pattern="^(student|teacher|admin)$")


class UserUpdatePassword(BaseModel):
    """Schema para alteração de senha."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema de resposta do usuário."""
    model_config = ConfigDict(from_attributes=True)

    # Override to plain str — email validation only applies on create/update,
    # not when reading back existing records from the database.
    email: str
    id: UUID
    role: str
    is_active: bool
    is_superuser: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Schema para listagem de usuários."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


# ==================== Student Schemas ====================

class StudentBase(BaseModel):
    """Campos base do aluno."""
    ra: str = Field(..., min_length=1, max_length=50)
    registration_number: str | None = Field(None, min_length=1, max_length=50)


class StudentCreate(StudentBase):
    """Schema para criação de aluno."""
    registration_number: str = Field(..., min_length=1, max_length=50)
    user_id: UUID
    course_id: UUID | None = None
    class_id: UUID | None = None


class StudentUpdate(BaseModel):
    """Schema para atualização de aluno."""
    ra: str | None = Field(None, min_length=1, max_length=50)
    registration_number: str | None = Field(None, min_length=1, max_length=50)
    course_id: UUID | None = None
    class_id: UUID | None = None
    status: str | None = None


class StudentResponse(StudentBase):
    """Schema de resposta do aluno."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    course_id: UUID | None = None
    class_id: UUID | None = None
    enrollment_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime


class StudentWithUserResponse(StudentResponse):
    """Aluno com dados do usuário."""
    user: UserResponse


# ==================== Teacher Schemas ====================

class TeacherBase(BaseModel):
    """Campos base do professor."""
    employee_id: str = Field(..., min_length=1, max_length=50)
    department: str | None = Field(None, max_length=100)


class TeacherCreate(TeacherBase):
    """Schema para criação de professor."""
    user_id: UUID


class TeacherUpdate(BaseModel):
    """Schema para atualização de professor."""
    employee_id: str | None = Field(None, min_length=1, max_length=50)
    department: str | None = Field(None, max_length=100)
    status: str | None = None


class TeacherResponse(TeacherBase):
    """Schema de resposta do professor."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    hire_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime


class TeacherWithUserResponse(TeacherResponse):
    """Professor com dados do usuário."""
    user: UserResponse


class UserProvisionCreate(BaseModel):
    """Cria uma conta e seu perfil acadêmico na mesma transação."""

    user: UserCreate
    student_ra: str | None = Field(None, min_length=1, max_length=50)
    student_registration_number: str | None = Field(None, min_length=1, max_length=50)
    student_course_id: UUID | None = None
    student_class_id: UUID | None = None
    teacher_employee_id: str | None = Field(None, min_length=1, max_length=50)
    teacher_department: str | None = Field(None, max_length=100)

    @model_validator(mode="after")
    def validate_profile(self):
        if self.user.role == "student":
            if not self.student_ra:
                raise ValueError("RA obrigatório para criar perfil de aluno")
            if not self.student_registration_number:
                raise ValueError("Matrícula institucional obrigatória para criar perfil de aluno")
            if self.teacher_employee_id is not None:
                raise ValueError("Dados funcionais não se aplicam a um aluno")
            if self.teacher_department is not None:
                raise ValueError("Dados funcionais não se aplicam a um aluno")
        elif self.user.role == "teacher":
            if not self.teacher_employee_id:
                raise ValueError("Identificação funcional obrigatória para criar perfil de professor")
            if (
                self.student_ra is not None
                or self.student_registration_number is not None
                or self.student_class_id is not None
                or self.student_course_id is not None
            ):
                raise ValueError("Dados de matrícula não se aplicam a um professor")
        else:
            raise ValueError("Use a operação de usuário padrão para criar administradores")
        return self


class UserProvisionResponse(BaseModel):
    """Conta e perfil criados conjuntamente."""

    user: UserResponse
    student: StudentResponse | None = None
    teacher: TeacherResponse | None = None


class AcademicUserProfileUpdate(BaseModel):
    """Atualiza a conta e seu perfil acadêmico na mesma transação."""

    user: UserUpdate
    student: StudentUpdate | None = None
    teacher: TeacherUpdate | None = None


# ==================== Administrator Schemas ====================

class AdministratorBase(BaseModel):
    """Campos base do administrador."""
    employee_id: str = Field(..., min_length=1, max_length=50)
    department: str | None = Field(None, max_length=100)
    permissions: str = "full"


class AdministratorCreate(AdministratorBase):
    """Schema para criação de administrador."""
    user_id: UUID


class AdministratorUpdate(BaseModel):
    """Schema para atualização de administrador."""
    employee_id: str | None = Field(None, min_length=1, max_length=50)
    department: str | None = Field(None, max_length=100)
    permissions: str | None = None


class AdministratorResponse(AdministratorBase):
    """Schema de resposta do administrador."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


# ==================== Auth Schemas ====================

class LoginRequest(BaseModel):
    """Requisição de login."""
    username: str = Field(..., description="Email ou username")
    password: str


class TokenResponse(BaseModel):
    """Resposta com tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Requisição de refresh token."""
    refresh_token: str


class TokenPayload(BaseModel):
    """Payload decodificado do token."""
    sub: str
    role: str
    user_id: UUID
    type: str
    exp: int
    iat: int


# ==================== Profile Schemas ====================

class ProfileResponse(BaseModel):
    """Perfil completo do usuário logado."""
    user: UserResponse
    student: StudentResponse | None = None
    teacher: TeacherResponse | None = None
    administrator: AdministratorResponse | None = None
