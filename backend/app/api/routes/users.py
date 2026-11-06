"""Rotas de Usuários, Alunos, Professores e Administradores."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import (
    get_current_active_user,
    require_admin,
    require_teacher_or_admin,
)
from backend.app.models.academic import (
    AcademicAssignment,
    Enrollment,
    EnrollmentStatus,
    TeacherSubject,
)
from backend.app.models.academic import (
    Class as AcademicClass,
)
from backend.app.models.user import Student, User, UserRole
from backend.app.schemas.academic import EnrollmentCreate
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.user import (
    AcademicUserProfileUpdate,
    AdministratorCreate,
    AdministratorResponse,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    StudentWithUserResponse,
    TeacherCreate,
    TeacherResponse,
    TeacherUpdate,
    TeacherWithUserResponse,
    UserCreate,
    UserListResponse,
    UserProvisionCreate,
    UserProvisionResponse,
    UserResponse,
    UserUpdate,
)
from backend.app.services.academic_service import EnrollmentService
from backend.app.services.user_service import (
    AdministratorService,
    StudentService,
    TeacherService,
    UserService,
)

router = APIRouter(prefix="/users", tags=["Usuários"])


def _teacher_class_ids(
    db: Session,
    current_user: User,
    permission: str,
    include_legacy: bool = False,
) -> set[UUID]:
    teacher = current_user.teacher_profile
    if teacher is None:
        raise HTTPException(status_code=403, detail="Perfil de professor não encontrado")
    class_ids = {
        assignment.class_id
        for assignment in db.query(AcademicAssignment).filter(
            AcademicAssignment.teacher_id == teacher.id,
            AcademicAssignment.is_active.is_(True),
            AcademicAssignment.permissions[permission].as_boolean().is_(True),
        ).all()
    }
    if include_legacy:
        legacy_classes = db.query(AcademicClass).join(
            TeacherSubject,
            (TeacherSubject.teacher_id == teacher.id)
            & (TeacherSubject.subject_id == AcademicClass.subject_id)
            & or_(
                TeacherSubject.academic_period_id.is_(None),
                TeacherSubject.academic_period_id == AcademicClass.academic_period_id,
            ),
        ).filter(AcademicClass.teacher_id == teacher.id).all()
        for class_record in legacy_classes:
            has_assignment_history = db.query(AcademicAssignment.id).filter(
                AcademicAssignment.teacher_id == teacher.id,
                AcademicAssignment.class_id == class_record.id,
            ).first()
            if has_assignment_history is None:
                class_ids.add(class_record.id)
    return class_ids


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


@router.post(
    "/provision",
    response_model=UserProvisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def provision_academic_user(
    data: UserProvisionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.TEACHER:
        if data.user.role != "student" or data.student_class_id is None:
            raise HTTPException(
                status_code=403,
                detail="Professor só pode cadastrar aluno no contexto de uma turma autorizada",
            )
        if data.student_class_id not in _teacher_class_ids(db, current_user, "create_students"):
            raise HTTPException(status_code=403, detail="Atribuição sem permissão para cadastrar alunos")
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")

    user = UserService(db).create_user(data.user, current_user.id)
    if user.role == UserRole.STUDENT:
        class_record = None
        if data.student_class_id is not None:
            class_record = db.get(AcademicClass, data.student_class_id)
            if class_record is None:
                raise HTTPException(status_code=404, detail="Turma não encontrada")
            if (
                data.student_course_id is not None
                and data.student_course_id != class_record.course_id
            ):
                raise HTTPException(
                    status_code=422,
                    detail="O curso selecionado não corresponde à turma",
                )
        student = StudentService(db).create_student(
            StudentCreate(
                user_id=user.id,
                ra=data.student_ra,
                registration_number=data.student_registration_number,
                course_id=data.student_course_id or (class_record.course_id if class_record else None),
                class_id=data.student_class_id,
            ),
            current_user.id,
        )
        if class_record is not None:
            EnrollmentService(db).create(
                EnrollmentCreate(
                    student_id=student.id,
                    class_id=class_record.id,
                    academic_period_id=class_record.academic_period_id,
                ),
                current_user.id,
            )
        return UserProvisionResponse(user=user, student=student)

    teacher = TeacherService(db).create_teacher(
        TeacherCreate(
            user_id=user.id,
            employee_id=data.teacher_employee_id,
            department=data.teacher_department,
        ),
        current_user.id,
    )
    return UserProvisionResponse(user=user, teacher=teacher)


@router.get("", response_model=PaginatedResponse[UserListResponse])
def list_users(
    role: UserRole | None = None,
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


@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = Query(..., min_length=2),
    role: UserRole | None = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Busca usuários."""
    service = UserService(db)
    return service.search_users(q, role)


# Rotas específicas precisam ser declaradas antes de /{user_id}; caso contrário
# o FastAPI tenta interpretar "students"/"teachers" como UUID.
@router.get("/students", response_model=PaginatedResponse[StudentWithUserResponse])
def list_users_students(
    course_id: UUID | None = None,
    class_id: UUID | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Lista alunos com os dados de usuário (alias de /students)."""
    return list_students(
        course_id=course_id,
        class_id=class_id,
        params=params,
        current_user=current_user,
        db=db,
    )


@router.get("/teachers", response_model=PaginatedResponse[TeacherWithUserResponse])
def list_users_teachers(
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Lista professores com os dados de usuário (alias de /teachers)."""
    return list_teachers(params=params, current_user=current_user, db=db)


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


@router.patch("/{user_id}/academic-profile", response_model=UserProvisionResponse)
def update_academic_user_profile(
    user_id: UUID,
    data: AcademicUserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if current_user.role == UserRole.TEACHER:
        if user.role != UserRole.STUDENT or data.student is None:
            raise HTTPException(
                status_code=403,
                detail="Professor só pode editar dados de alunos vinculados a turmas autorizadas",
            )
        if data.user.is_active is not None or data.student.class_id is not None or data.student.course_id is not None:
            raise HTTPException(
                status_code=403,
                detail="Professor não pode alterar o acesso, curso ou turma do aluno",
            )
        student = StudentService(db).get_student_by_user(user_id)
        if student is None:
            raise HTTPException(status_code=404, detail="Perfil de aluno não encontrado")
        allowed_classes = _teacher_class_ids(db, current_user, "edit_students")
        active_classes = {
            enrollment.class_id for enrollment in db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            ).all()
        }
        if not active_classes.intersection(allowed_classes):
            raise HTTPException(status_code=403, detail="Sem permissão para editar este aluno")
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")

    if data.user.role is not None and data.user.role != user.role.value:
        raise HTTPException(status_code=422, detail="A edição acadêmica não pode alterar o perfil da conta")

    updated_user = user_service.update_user(user_id, data.user, current_user.id)
    if user.role == UserRole.STUDENT:
        if data.teacher is not None:
            raise HTTPException(status_code=422, detail="Informe somente os dados acadêmicos do aluno")
        student_service = StudentService(db)
        student = student_service.get_student_by_user(user_id)
        if student is None:
            if data.student is None:
                return UserProvisionResponse(user=updated_user)
            raise HTTPException(status_code=404, detail="Perfil de aluno não encontrado")
        if data.student is None:
            raise HTTPException(status_code=422, detail="Informe os dados acadêmicos do aluno")
        updated_student = student_service.update_student(student.id, data.student, current_user.id)
        return UserProvisionResponse(user=updated_user, student=updated_student)

    if user.role == UserRole.TEACHER:
        if data.student is not None:
            raise HTTPException(status_code=422, detail="Informe somente os dados acadêmicos do professor")
        teacher_service = TeacherService(db)
        teacher = teacher_service.get_teacher_by_user(user_id)
        if teacher is None:
            if data.teacher is None:
                return UserProvisionResponse(user=updated_user)
            raise HTTPException(status_code=404, detail="Perfil de professor não encontrado")
        if data.teacher is None:
            raise HTTPException(status_code=422, detail="Informe os dados acadêmicos do professor")
        updated_teacher = teacher_service.update_teacher(teacher.id, data.teacher, current_user.id)
        return UserProvisionResponse(user=updated_user, teacher=updated_teacher)

    if data.student is not None or data.teacher is not None:
        raise HTTPException(status_code=422, detail="Administrador não possui perfil acadêmico de aluno ou professor")
    return UserProvisionResponse(user=updated_user)


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
    course_id: UUID | None = None,
    class_id: UUID | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Lista alunos."""
    service = StudentService(db)
    if current_user.role == UserRole.TEACHER:
        allowed_classes = _teacher_class_ids(
            db,
            current_user,
            "view_students",
            include_legacy=True,
        )
        if class_id is not None and class_id not in allowed_classes:
            raise HTTPException(status_code=403, detail="Sem permissão para visualizar alunos desta turma")
        query = db.query(Student).join(Enrollment).filter(
            Enrollment.class_id.in_(allowed_classes or {UUID(int=0)}),
            Enrollment.status == EnrollmentStatus.ACTIVE,
        )
        if class_id is not None:
            query = query.filter(Enrollment.class_id == class_id)
        if course_id is not None:
            query = query.filter(Student.course_id == course_id)
        total = query.distinct().count()
        students = query.distinct().offset(params.offset).limit(params.limit).all()
        return PaginatedResponse(
            items=students, total=total, page=params.page, page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
            has_next=params.page * params.page_size < total, has_prev=params.page > 1,
        )
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
    student = service.get_student(student_id)
    if current_user.role == UserRole.TEACHER:
        allowed_classes = _teacher_class_ids(
            db,
            current_user,
            "view_students",
            include_legacy=True,
        )
        active_classes = {
            enrollment.class_id for enrollment in db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            ).all()
        }
        if not active_classes.intersection(allowed_classes):
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return student


@student_router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: UUID,
    student_data: StudentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Atualiza aluno."""
    if current_user.role == UserRole.TEACHER:
        if student_data.class_id is not None or student_data.course_id is not None:
            raise HTTPException(
                status_code=403,
                detail="Alterações de matrícula e curso devem ser feitas pelo administrador",
            )
        student = db.get(Student, student_id)
        if student is None:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        allowed_classes = _teacher_class_ids(db, current_user, "edit_students")
        active_classes = {
            enrollment.class_id for enrollment in db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            ).all()
        }
        if not active_classes.intersection(allowed_classes):
            raise HTTPException(status_code=403, detail="Sem permissão para editar este aluno")
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
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


# Rotas de perfis acadêmicos também ficam disponíveis em /students e /teachers.
router.include_router(student_router)
router.include_router(teacher_router)
router.include_router(admin_router)

# Sub-routers expostos na raiz da API (/api/v1/students, /api/v1/teachers).
students_router = student_router
teachers_router = teacher_router
administrators_router = admin_router
