"""Rotas de Usuários, Alunos, Professores e Administradores."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_active_user, require_admin, require_teacher_or_admin
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    StudentCreate, StudentUpdate, StudentResponse, StudentWithUserResponse,
    TeacherCreate, TeacherUpdate, TeacherResponse, TeacherWithUserResponse,
    AdministratorCreate, AdministratorUpdate, AdministratorResponse,
)
from backend.app.services.user_service import UserService, StudentService, TeacherService, AdministratorService
from backend.app.schemas.common import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/users", tags=["Usuários"])


# ==================== Users ====================

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Cria novo usuário (apenas admin)."""
    service = UserService(db)
    user = service.create_user(user_data, current_user.id)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise
    return user


@router.get("", response_model=PaginatedResponse[UserListResponse])
def list_users(
    role: Optional[UserRole] = None,
    active_only: bool = True,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Lista usuários (apenas admin)."""
    service = UserService(db)
    users = service.list_users(role=role, active_only=active_only, skip=params.offset, limit=params.limit)
    total = len(users)  # Simplificado
    return PaginatedResponse(
        items=users, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/search", response_model=List[UserResponse])
def search_users(
    q: str = Query(..., min_length=2),
    role: Optional[UserRole] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca usuários."""
    service = UserService(db)
    return service.search_users(q, role)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca usuário por ID."""
    service = UserService(db)
    return service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Atualiza usuário."""
    service = UserService(db)
    user = service.update_user(user_id, user_data, current_user.id)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Desativa usuário (soft delete)."""
    service = UserService(db)
    service.delete_user(user_id, current_user.id)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"message": "Usuário desativado"}


# ==================== Students ====================

student_router = APIRouter(prefix="/students", tags=["Alunos"])


@student_router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Cria perfil de aluno."""
    service = StudentService(db)
    return service.create_student(student_data, current_user.id)


@student_router.get("", response_model=PaginatedResponse[StudentWithUserResponse])
def list_students(
    course_id: Optional[UUID] = None,
    class_id: Optional[UUID] = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Lista alunos."""
    service = StudentService(db)
    if course_id:
        students = service.student_repo.get_by_course(course_id)
    elif class_id:
        students = service.student_repo.get_by_class(class_id)
    else:
        students = service.student_repo.get_all(skip=params.offset, limit=params.limit)
    total = len(students)
    return PaginatedResponse(
        items=students, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@student_router.get("/me", response_model=StudentWithUserResponse)
def get_my_student_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retorna perfil do aluno logado."""
    service = StudentService(db)
    student = service.get_student_by_user(current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Perfil de aluno não encontrado")
    return student


@student_router.get("/{student_id}", response_model=StudentWithUserResponse)
def get_student(
    student_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Busca aluno por ID."""
    service = StudentService(db)
    return service.get_student(student_id)


@student_router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: UUID,
    student_data: StudentUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Atualiza aluno."""
    service = StudentService(db)
    return service.update_student(student_id, student_data, current_user.id)


# ==================== Teachers ====================

teacher_router = APIRouter(prefix="/teachers", tags=["Professores"])


@teacher_router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    teacher_data: TeacherCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Cria perfil de professor."""
    service = TeacherService(db)
    return service.create_teacher(teacher_data, current_user.id)


@teacher_router.get("", response_model=PaginatedResponse[TeacherWithUserResponse])
def list_teachers(
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Lista professores."""
    service = TeacherService(db)
    teachers = service.teacher_repo.get_all(skip=params.offset, limit=params.limit)
    total = len(teachers)
    return PaginatedResponse(
        items=teachers, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@teacher_router.get("/me", response_model=TeacherWithUserResponse)
def get_my_teacher_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retorna perfil do professor logado."""
    service = TeacherService(db)
    teacher = service.get_teacher_by_user(current_user.id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Perfil de professor não encontrado")
    return teacher


@teacher_router.get("/{teacher_id}", response_model=TeacherWithUserResponse)
def get_teacher(
    teacher_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca professor por ID."""
    service = TeacherService(db)
    return service.get_teacher(teacher_id)


@teacher_router.patch("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: UUID,
    teacher_data: TeacherUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Atualiza professor."""
    service = TeacherService(db)
    return service.update_teacher(teacher_id, teacher_data, current_user.id)


# ==================== Administrators ====================

admin_router = APIRouter(prefix="/administrators", tags=["Administradores"])


@admin_router.post("", response_model=AdministratorResponse, status_code=status.HTTP_201_CREATED)
def create_administrator(
    admin_data: AdministratorCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Cria perfil de administrador."""
    service = AdministratorService(db)
    return service.create_administrator(admin_data, current_user.id)


@admin_router.get("/me", response_model=AdministratorResponse)
def get_my_admin_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retorna perfil do administrador logado."""
    service = AdministratorService(db)
    admin = service.get_administrator_by_user(current_user.id)
    if not admin:
        raise HTTPException(status_code=404, detail="Perfil de administrador não encontrado")
    return admin


# Include sub-routers
router.include_router(student_router)
router.include_router(teacher_router)
router.include_router(admin_router)