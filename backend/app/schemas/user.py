"""Schemas Pydantic para Usuário e Autenticação."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, ConfigDict


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
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    is_active: Optional[bool] = None
    role: Optional[str] = Field(None, pattern="^(student|teacher|admin)$")


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
    last_login: Optional[datetime] = None
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


class StudentCreate(StudentBase):
    """Schema para criação de aluno."""
    user_id: UUID
    course_id: Optional[UUID] = None
    class_id: Optional[UUID] = None


class StudentUpdate(BaseModel):
    """Schema para atualização de aluno."""
    ra: Optional[str] = Field(None, min_length=1, max_length=50)
    course_id: Optional[UUID] = None
    class_id: Optional[UUID] = None
    status: Optional[str] = None


class StudentResponse(StudentBase):
    """Schema de resposta do aluno."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    course_id: Optional[UUID] = None
    class_id: Optional[UUID] = None
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
    department: Optional[str] = Field(None, max_length=100)


class TeacherCreate(TeacherBase):
    """Schema para criação de professor."""
    user_id: UUID


class TeacherUpdate(BaseModel):
    """Schema para atualização de professor."""
    employee_id: Optional[str] = Field(None, min_length=1, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None


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


# ==================== Administrator Schemas ====================

class AdministratorBase(BaseModel):
    """Campos base do administrador."""
    employee_id: str = Field(..., min_length=1, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    permissions: str = "full"


class AdministratorCreate(AdministratorBase):
    """Schema para criação de administrador."""
    user_id: UUID


class AdministratorUpdate(BaseModel):
    """Schema para atualização de administrador."""
    employee_id: Optional[str] = Field(None, min_length=1, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    permissions: Optional[str] = None


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
    student: Optional[StudentResponse] = None
    teacher: Optional[TeacherResponse] = None
    administrator: Optional[AdministratorResponse] = None