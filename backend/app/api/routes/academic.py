"""Rotas do Módulo Acadêmico."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import (
    get_current_active_user,
    require_admin,
    require_teacher_or_admin,
)
from backend.app.models.academic import (
    ACADEMIC_ASSIGNMENT_PERMISSIONS,
    AcademicAssignment,
    AcademicPeriod,
    Assessment,
    Attendance,
    Course,
    Enrollment,
    EnrollmentStatus,
    Grade,
    Subject,
    TeacherSubject,
)
from backend.app.models.academic import (
    Class as AcademicClass,
)
from backend.app.models.audit import AuditActionType, AuditLog
from backend.app.models.user import Teacher, User, UserRole
from backend.app.schemas.academic import (
    AcademicAssignmentCreate,
    AcademicAssignmentResponse,
    AcademicAssignmentUpdate,
    AcademicPeriodCreate,
    AcademicPeriodResponse,
    AcademicRuleCreate,
    AcademicRuleResponse,
    AssessmentCreate,
    AssessmentResponse,
    AttendanceCreate,
    AttendanceResponse,
    BulkAttendanceCreate,
    BulkEnrollmentCreate,
    BulkGradeCreate,
    ClassCreate,
    ClassResponse,
    ClassUpdate,
    ClassWithRelations,
    CourseCreate,
    CourseResponse,
    CourseUpdate,
    CourseWithRelations,
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentUpdate,
    EnrollmentWithRelations,
    GradeCreate,
    GradeResponse,
    GradeUpdate,
    GradeWithRelations,
    MyAttendanceSummary,
    MyScheduleItem,
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
    TeacherSubjectCreate,
    TeacherSubjectResponse,
)
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.services.academic_service import (
    AcademicPeriodService,
    AcademicRuleService,
    AssessmentService,
    AttendanceService,
    ClassService,
    CourseService,
    EnrollmentService,
    GradeService,
    SubjectService,
    TeacherSubjectService,
)

router = APIRouter(prefix="/academic", tags=["Acadêmico"])


def _assignment_for_class(
    db: Session,
    teacher_id: UUID,
    class_record: AcademicClass,
) -> AcademicAssignment | None:
    return db.query(AcademicAssignment).filter(
        AcademicAssignment.teacher_id == teacher_id,
        AcademicAssignment.class_id == class_record.id,
        AcademicAssignment.subject_id == class_record.subject_id,
        AcademicAssignment.academic_period_id == class_record.academic_period_id,
        AcademicAssignment.is_active.is_(True),
    ).first()


def _has_assignment_history(db: Session, teacher_id: UUID, class_id: UUID) -> bool:
    return db.query(AcademicAssignment.id).filter(
        AcademicAssignment.teacher_id == teacher_id,
        AcademicAssignment.class_id == class_id,
    ).first() is not None


def require_class_permission(
    db: Session,
    current_user: User,
    class_id: UUID,
    permission: str,
) -> AcademicClass:
    class_record = db.get(AcademicClass, class_id)
    if class_record is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    if current_user.role == UserRole.ADMIN:
        return class_record
    teacher = current_user.teacher_profile
    if current_user.role != UserRole.TEACHER or teacher is None:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")

    assignment = _assignment_for_class(db, teacher.id, class_record)
    if assignment is not None:
        if assignment.permissions.get(permission) is True:
            return class_record
        raise HTTPException(status_code=403, detail="Atribuição sem permissão para esta operação")

    if _has_assignment_history(db, teacher.id, class_id):
        raise HTTPException(status_code=403, detail="Atribuição acadêmica inativa ou incompatível")

    if (
        class_record.teacher_id == teacher.id
        and _teacher_has_class_assignment(db, teacher.id, class_record)
    ):
        return class_record
    raise HTTPException(status_code=403, detail="Turma não autorizada")


def _validate_grade_score(score: Decimal, max_score: Decimal) -> None:
    if score > max_score:
        raise HTTPException(status_code=422, detail="A nota não pode exceder a pontuação máxima da avaliação")


def _teacher_has_class_assignment(db: Session, teacher_id: UUID, class_record: AcademicClass) -> bool:
    assignment = db.query(TeacherSubject.id).filter(
        TeacherSubject.teacher_id == teacher_id,
        TeacherSubject.subject_id == class_record.subject_id,
        or_(
            TeacherSubject.academic_period_id.is_(None),
            TeacherSubject.academic_period_id == class_record.academic_period_id,
        ),
    ).first()
    return assignment is not None


def _assert_class_access(db: Session, current_user: User, class_record: AcademicClass) -> None:
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher_profile
        if teacher is not None:
            if _assignment_for_class(db, teacher.id, class_record) is not None:
                return
            if _has_assignment_history(db, teacher.id, class_record.id):
                raise HTTPException(status_code=403, detail="Atribuição acadêmica inativa")
            if class_record.teacher_id == teacher.id and _teacher_has_class_assignment(
                db, teacher.id, class_record
            ):
                return
    elif current_user.role == UserRole.STUDENT:
        student = current_user.student_profile
        if student is not None and db.query(Enrollment.id).filter(
            Enrollment.student_id == student.id,
            Enrollment.class_id == class_record.id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
        ).first():
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Turma não autorizada")


# ==================== Courses ====================

@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.create(course_data, current_user.id)


@router.get("/courses", response_model=PaginatedResponse[CourseWithRelations])
def list_courses(
    active_only: bool = True,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    courses = service.list(active_only=active_only)
    total = len(courses)
    return PaginatedResponse(
        items=courses, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/courses/{course_id}", response_model=CourseWithRelations)
def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.get(course_id)


@router.patch("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.update(course_id, course_data, current_user.id)


# ==================== Subjects ====================

@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: SubjectCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = SubjectService(db)
    return service.create(subject_data, current_user.id)


@router.get("/subjects", response_model=PaginatedResponse[SubjectResponse])
def list_subjects(
    course_id: UUID | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(Subject)
    if course_id:
        query = query.filter(Subject.course_id == course_id)
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher_profile
        if teacher is None:
            query = query.filter(False)
        else:
            legacy_assignment = select(TeacherSubject.id).where(
                TeacherSubject.teacher_id == teacher.id,
                TeacherSubject.subject_id == Subject.id,
            ).exists()
            scoped_assignment = select(AcademicAssignment.id).where(
                AcademicAssignment.teacher_id == teacher.id,
                AcademicAssignment.subject_id == Subject.id,
                AcademicAssignment.is_active.is_(True),
            ).exists()
            assignment_history = select(AcademicAssignment.id).where(
                AcademicAssignment.teacher_id == teacher.id,
                AcademicAssignment.subject_id == Subject.id,
            ).exists()
            query = query.filter(
                or_(
                    scoped_assignment,
                    and_(legacy_assignment, ~assignment_history),
                )
            )
    elif current_user.role == UserRole.STUDENT:
        student = current_user.student_profile
        if student is None:
            query = query.filter(False)
        else:
            query = (
                query.join(AcademicClass, AcademicClass.subject_id == Subject.id)
                .join(Enrollment, Enrollment.class_id == AcademicClass.id)
                .filter(
                    Enrollment.student_id == student.id,
                    Enrollment.status == EnrollmentStatus.ACTIVE,
                    Enrollment.academic_period_id == AcademicClass.academic_period_id,
                    AcademicClass.is_active.is_(True),
                    Subject.is_active.is_(True),
                )
                .distinct()
            )
    total = query.distinct().count()
    subjects = query.distinct().offset(params.offset).limit(params.limit).all()
    return PaginatedResponse(
        items=subjects, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher_profile
        if teacher is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Disciplina não autorizada")
        has_scoped_assignment = db.query(AcademicAssignment.id).filter(
            AcademicAssignment.teacher_id == teacher.id,
            AcademicAssignment.subject_id == subject_id,
            AcademicAssignment.is_active.is_(True),
        ).first()
        has_assignment_history = db.query(AcademicAssignment.id).filter(
            AcademicAssignment.teacher_id == teacher.id,
            AcademicAssignment.subject_id == subject_id,
        ).first()
        has_legacy_assignment = db.query(TeacherSubject.id).filter(
            TeacherSubject.teacher_id == teacher.id,
            TeacherSubject.subject_id == subject_id,
        ).first()
        if not has_scoped_assignment and (has_assignment_history or not has_legacy_assignment):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Disciplina não autorizada")
    elif current_user.role == UserRole.STUDENT:
        student = current_user.student_profile
        if student is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil de aluno não encontrado")
        has_active_enrollment = (
            db.query(Enrollment.id)
            .join(AcademicClass, Enrollment.class_id == AcademicClass.id)
            .join(Subject, Subject.id == AcademicClass.subject_id)
            .filter(
                Enrollment.student_id == student.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
                Enrollment.academic_period_id == AcademicClass.academic_period_id,
                AcademicClass.subject_id == subject_id,
                AcademicClass.is_active.is_(True),
                Subject.is_active.is_(True),
            )
            .first()
        )
        if not has_active_enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    service = SubjectService(db)
    return service.get(subject_id)


@router.patch("/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: UUID,
    subject_data: SubjectUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = SubjectService(db)
    return service.update(subject_id, subject_data, current_user.id)


# ==================== Classes ====================

@router.post("/classes", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    subject = db.get(Subject, class_data.subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Matéria não encontrada")
    if subject.course_id != class_data.course_id:
        raise HTTPException(status_code=422, detail="A matéria não pertence ao curso selecionado")
    if db.get(AcademicPeriod, class_data.academic_period_id) is None:
        raise HTTPException(status_code=404, detail="Período letivo não encontrado")
    service = ClassService(db)
    return service.create(class_data, current_user.id)


@router.get("/classes", response_model=PaginatedResponse[ClassWithRelations])
def list_classes(
    teacher_id: UUID | None = None,
    course_id: UUID | None = None,
    subject_id: UUID | None = None,
    academic_period_id: UUID | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(AcademicClass)
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher_profile
        if teacher is None:
            query = query.filter(False)
        else:
            assigned_class = select(AcademicAssignment.id).where(
                AcademicAssignment.teacher_id == teacher.id,
                AcademicAssignment.class_id == AcademicClass.id,
                AcademicAssignment.subject_id == AcademicClass.subject_id,
                AcademicAssignment.academic_period_id == AcademicClass.academic_period_id,
                AcademicAssignment.is_active.is_(True),
            ).exists()
            assignment_history = select(AcademicAssignment.id).where(
                AcademicAssignment.teacher_id == teacher.id,
                AcademicAssignment.class_id == AcademicClass.id,
            ).exists()
            legacy_assignment = select(TeacherSubject.id).where(
                TeacherSubject.teacher_id == teacher.id,
                TeacherSubject.subject_id == AcademicClass.subject_id,
                or_(
                    TeacherSubject.academic_period_id.is_(None),
                    TeacherSubject.academic_period_id == AcademicClass.academic_period_id,
                ),
            ).exists()
            query = query.filter(
                or_(
                    assigned_class,
                    and_(
                        ~assignment_history,
                        AcademicClass.teacher_id == teacher.id,
                        legacy_assignment,
                    ),
                )
            )
    elif current_user.role == UserRole.STUDENT:
        student = current_user.student_profile
        if student is None:
            query = query.filter(False)
        else:
            query = query.join(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
    elif teacher_id:
        query = query.filter(AcademicClass.teacher_id == teacher_id)
    if course_id:
        query = query.filter(AcademicClass.course_id == course_id)
    if subject_id:
        query = query.filter(AcademicClass.subject_id == subject_id)
    if academic_period_id:
        query = query.filter(AcademicClass.academic_period_id == academic_period_id)
    total = query.distinct().count()
    classes = query.distinct().offset(params.offset).limit(params.limit).all()
    return PaginatedResponse(
        items=classes, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/classes/my", response_model=PaginatedResponse[ClassWithRelations])
def list_my_classes(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Lista turmas do professor autenticado."""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Apenas professores podem acessar esta rota")
    if not current_user.teacher_profile:
        raise HTTPException(status_code=403, detail="Perfil de professor não encontrado")
    return list_classes(params=params, current_user=current_user, db=db)


@router.get("/classes/{class_id}", response_model=ClassWithRelations)
def get_class(
    class_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = ClassService(db)
    class_record = service.get(class_id)
    _assert_class_access(db, current_user, class_record)
    return class_record


@router.patch("/classes/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: UUID,
    class_data: ClassUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = ClassService(db)
    return service.update(class_id, class_data, current_user.id)


# ==================== Academic Periods ====================

@router.post("/periods", response_model=AcademicPeriodResponse, status_code=status.HTTP_201_CREATED)
def create_period(
    period_data: AcademicPeriodCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AcademicPeriodService(db)
    return service.create(period_data, current_user.id)


@router.get("/periods", response_model=PaginatedResponse[AcademicPeriodResponse])
def list_periods(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AcademicPeriodService(db)
    periods = service.repo.get_all(skip=params.offset, limit=params.limit)
    total = len(periods)
    return PaginatedResponse(
        items=periods, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/periods/current", response_model=AcademicPeriodResponse)
def get_current_period(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AcademicPeriodService(db)
    period = service.get_current()
    if not period:
        raise HTTPException(status_code=404, detail="Nenhum período atual definido")
    return period


@router.post("/periods/{period_id}/set-current", response_model=AcademicPeriodResponse)
def set_current_period(
    period_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AcademicPeriodService(db)
    return service.set_current(period_id, current_user.id)


# ==================== Consultas do usuário autenticado ====================

def _serialize_period(period: AcademicPeriod | None) -> dict | None:
    if period is None:
        return None
    return {
        "id": str(period.id),
        "name": period.name,
        "code": period.code,
        "start_date": period.start_date.isoformat(),
        "end_date": period.end_date.isoformat(),
        "status": period.status,
        "is_current": period.is_current,
    }


@router.get("/my-profile")
def get_my_academic_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Perfil acadêmico do usuário autenticado.

    Alunos recebem curso, turma e matrículas; professores recebem as
    disciplinas e turmas autorizadas; administradores recebem o setor.
    """
    current_period = db.query(AcademicPeriod).filter(
        AcademicPeriod.is_current.is_(True)
    ).first()
    payload: dict = {
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
        },
        "role": current_user.role,
        "current_period": _serialize_period(current_period),
        "student": None,
        "teacher": None,
        "administrator": None,
    }

    student = current_user.student_profile
    if student is not None:
        course = db.get(Course, student.course_id) if student.course_id else None
        class_record = db.get(AcademicClass, student.class_id) if student.class_id else None
        enrollments = (
            db.query(Enrollment)
            .filter(
                Enrollment.student_id == student.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            .all()
        )
        payload["student"] = {
            "id": str(student.id),
            "ra": student.ra,
            "registration_number": student.registration_number,
            "status": student.status,
            "course": (
                {"id": str(course.id), "code": course.code, "name": course.name}
                if course is not None
                else None
            ),
            "class": (
                {
                    "id": str(class_record.id),
                    "code": class_record.code,
                    "name": class_record.name,
                    "schedule": class_record.schedule,
                    "classroom": class_record.classroom,
                }
                if class_record is not None
                else None
            ),
            "enrollments": [
                {
                    "id": str(enrollment.id),
                    "class_id": str(enrollment.class_id),
                    "status": enrollment.status,
                    "final_grade": (
                        str(enrollment.final_grade)
                        if enrollment.final_grade is not None
                        else None
                    ),
                    "attendance_percentage": (
                        str(enrollment.attendance_percentage)
                        if enrollment.attendance_percentage is not None
                        else None
                    ),
                }
                for enrollment in enrollments
            ],
        }

    teacher = current_user.teacher_profile
    if teacher is not None:
        assignments = db.query(AcademicAssignment).filter(
            AcademicAssignment.teacher_id == teacher.id,
            AcademicAssignment.is_active.is_(True),
        ).all()
        payload["teacher"] = {
            "id": str(teacher.id),
            "employee_id": teacher.employee_id,
            "department": teacher.department,
            "status": teacher.status,
            "assignments": [
                {
                    "id": str(assignment.id),
                    "subject_id": str(assignment.subject_id),
                    "subject_name": assignment.subject.name if assignment.subject else None,
                    "class_id": str(assignment.class_id),
                    "class_name": assignment.class_.name if assignment.class_ else None,
                    "academic_period_id": str(assignment.academic_period_id),
                }
                for assignment in assignments
            ],
        }

    administrator = current_user.admin_profile
    if administrator is not None:
        payload["administrator"] = {
            "id": str(administrator.id),
            "employee_id": administrator.employee_id,
            "department": administrator.department,
            "permissions": administrator.permissions,
        }

    return payload


@router.get("/schedule/my", response_model=list[MyScheduleItem])
def get_my_schedule(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Grade horária das turmas em que o usuário autenticado está envolvido."""
    if current_user.role == UserRole.STUDENT:
        student = current_user.student_profile
        if student is None:
            raise HTTPException(status_code=404, detail="Perfil de aluno não encontrado")
        classes = (
            db.query(AcademicClass)
            .join(Enrollment, Enrollment.class_id == AcademicClass.id)
            .filter(
                Enrollment.student_id == student.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            .all()
        )
    elif current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher_profile
        if teacher is None:
            raise HTTPException(status_code=404, detail="Perfil de professor não encontrado")
        classes = (
            db.query(AcademicClass)
            .filter(AcademicClass.teacher_id == teacher.id, AcademicClass.is_active.is_(True))
            .all()
        )
    else:
        classes = db.query(AcademicClass).filter(AcademicClass.is_active.is_(True)).all()

    return [
        MyScheduleItem(
            class_id=class_record.id,
            class_code=class_record.code,
            class_name=class_record.name,
            subject_name=class_record.subject.name if class_record.subject else "",
            course_name=class_record.course.name if class_record.course else "",
            teacher_name=(
                class_record.teacher.user.full_name if class_record.teacher else None
            ),
            schedule=class_record.schedule,
            classroom=class_record.classroom,
            semester=class_record.semester,
            year=class_record.year,
            period_name=(
                class_record.academic_period.name
                if class_record.academic_period is not None
                else None
            ),
        )
        for class_record in classes
    ]


# ==================== Enrollments ====================

@router.post("/enrollments", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_data: EnrollmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    class_record = db.get(AcademicClass, enrollment_data.class_id)
    if class_record is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    if class_record.academic_period_id != enrollment_data.academic_period_id:
        raise HTTPException(status_code=422, detail="O período da matrícula deve corresponder ao período da turma")
    service = EnrollmentService(db)
    return service.create(enrollment_data, current_user.id)


@router.post("/enrollments/bulk", response_model=list[EnrollmentResponse])
def bulk_create_enrollments(
    data: BulkEnrollmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    class_record = db.get(AcademicClass, data.class_id)
    if class_record is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    if class_record.academic_period_id != data.academic_period_id:
        raise HTTPException(status_code=422, detail="O período da matrícula deve corresponder ao período da turma")
    service = EnrollmentService(db)
    return service.bulk_create(data.class_id, data.student_ids, data.academic_period_id, current_user.id)


@router.get("/enrollments", response_model=PaginatedResponse[EnrollmentWithRelations])
def list_enrollments(
    student_id: UUID | None = None,
    class_id: UUID | None = None,
    academic_period_id: UUID | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher_profile
        if teacher is None:
            raise HTTPException(status_code=403, detail="Perfil de professor não encontrado")
        allowed_classes = {
            assignment.class_id
            for assignment in db.query(AcademicAssignment).filter(
                AcademicAssignment.teacher_id == teacher.id,
                AcademicAssignment.is_active.is_(True),
                AcademicAssignment.permissions["view_students"].as_boolean().is_(True),
            ).all()
        }
        legacy_classes = db.query(AcademicClass).join(
            TeacherSubject,
            (TeacherSubject.teacher_id == teacher.id)
            & (TeacherSubject.subject_id == AcademicClass.subject_id)
            & or_(
                TeacherSubject.academic_period_id.is_(None),
                TeacherSubject.academic_period_id == AcademicClass.academic_period_id,
            ),
        ).filter(AcademicClass.teacher_id == teacher.id).all()
        for legacy_class in legacy_classes:
            if not _has_assignment_history(db, teacher.id, legacy_class.id):
                allowed_classes.add(legacy_class.id)
        if class_id is not None and class_id not in allowed_classes:
            raise HTTPException(status_code=403, detail="Sem permissão para visualizar alunos desta turma")
        if student_id is not None:
            query = db.query(Enrollment).filter(
                Enrollment.student_id == student_id,
                Enrollment.class_id.in_(allowed_classes or {UUID(int=0)}),
            )
            if academic_period_id is not None:
                query = query.filter(Enrollment.academic_period_id == academic_period_id)
            enrollments = query.offset(params.offset).limit(params.limit).all()
        else:
            query = db.query(Enrollment).filter(
                Enrollment.class_id.in_(allowed_classes or {UUID(int=0)})
            )
            if class_id is not None:
                query = query.filter(Enrollment.class_id == class_id)
            if academic_period_id is not None:
                query = query.filter(Enrollment.academic_period_id == academic_period_id)
            enrollments = query.offset(params.offset).limit(params.limit).all()
        total = len(enrollments)
        return PaginatedResponse(
            items=enrollments, total=total, page=params.page, page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
            has_next=params.page * params.page_size < total, has_prev=params.page > 1,
        )

    service = EnrollmentService(db)
    if student_id and academic_period_id:
        enrollments = service.get_by_student(student_id, academic_period_id)
    elif class_id:
        enrollments = service.repo.get_by_class(class_id)
    else:
        enrollments = service.repo.get_all(skip=params.offset, limit=params.limit)
    total = len(enrollments)
    return PaginatedResponse(
        items=enrollments, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.patch("/enrollments/{enrollment_id}", response_model=EnrollmentResponse)
def update_enrollment(
    enrollment_id: UUID,
    enrollment_data: EnrollmentUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = EnrollmentService(db)
    return service.update(enrollment_id, enrollment_data, current_user.id)


# ==================== Teacher Subjects ====================

@router.get("/teacher-subjects", response_model=PaginatedResponse[TeacherSubjectResponse])
def list_teacher_subjects(
    teacher_id: UUID | None = None,
    subject_id: UUID | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = TeacherSubjectService(db)
    if teacher_id:
        items = service.list_by_teacher(teacher_id)
    elif subject_id:
        items = service.list_by_subject(subject_id)
    else:
        items = service.repo.get_all(skip=params.offset, limit=params.limit)
    total = len(items)
    return PaginatedResponse(
        items=items, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.post("/teacher-subjects", response_model=TeacherSubjectResponse, status_code=status.HTTP_201_CREATED)
def assign_teacher_subject(
    data: TeacherSubjectCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = TeacherSubjectService(db)
    return service.create(data)


@router.patch("/teacher-subjects/{teacher_subject_id}", response_model=TeacherSubjectResponse)
def update_teacher_subject(
    teacher_subject_id: UUID,
    is_coordinator: bool | None = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = TeacherSubjectService(db)
    return service.update(teacher_subject_id, is_coordinator=is_coordinator)


@router.delete("/teacher-subjects/{teacher_subject_id}")
def remove_teacher_subject(
    teacher_subject_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = TeacherSubjectService(db)
    service.delete(teacher_subject_id)
    return {"message": "Associação removida com sucesso"}


# ==================== Context-scoped academic assignments ====================

@router.get("/assignments", response_model=list[AcademicAssignmentResponse])
def list_academic_assignments(
    teacher_id: UUID | None = None,
    subject_id: UUID | None = None,
    class_id: UUID | None = None,
    active_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(AcademicAssignment)
    if current_user.role == UserRole.TEACHER:
        if current_user.teacher_profile is None:
            raise HTTPException(status_code=403, detail="Perfil de professor não encontrado")
        query = query.filter(AcademicAssignment.teacher_id == current_user.teacher_profile.id)
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    elif teacher_id is not None:
        query = query.filter(AcademicAssignment.teacher_id == teacher_id)
    if subject_id is not None:
        query = query.filter(AcademicAssignment.subject_id == subject_id)
    if class_id is not None:
        query = query.filter(AcademicAssignment.class_id == class_id)
    if active_only:
        query = query.filter(AcademicAssignment.is_active.is_(True))
    return query.order_by(AcademicAssignment.created_at.desc()).all()


@router.post(
    "/assignments",
    response_model=AcademicAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_academic_assignment(
    data: AcademicAssignmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    teacher = db.get(Teacher, data.teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="Perfil de professor não encontrado")
    if teacher.status != "active" or not teacher.user.is_active:
        raise HTTPException(status_code=422, detail="O professor está inativo")

    subject = db.get(Subject, data.subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    class_record = db.get(AcademicClass, data.class_id)
    if class_record is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    if class_record.subject_id != data.subject_id:
        raise HTTPException(status_code=422, detail="A disciplina não pertence à turma selecionada")
    if class_record.academic_period_id != data.academic_period_id:
        raise HTTPException(status_code=422, detail="O período letivo não corresponde à turma")
    if db.get(AcademicPeriod, data.academic_period_id) is None:
        raise HTTPException(status_code=404, detail="Período letivo não encontrado")

    active_duplicate = db.query(AcademicAssignment.id).filter(
        AcademicAssignment.teacher_id == data.teacher_id,
        AcademicAssignment.subject_id == data.subject_id,
        AcademicAssignment.class_id == data.class_id,
        AcademicAssignment.academic_period_id == data.academic_period_id,
        AcademicAssignment.is_active.is_(True),
    ).first()
    if active_duplicate is not None:
        raise HTTPException(status_code=409, detail="Já existe uma atribuição ativa para este contexto")

    permissions = {key: data.permissions.get(key, False) for key in ACADEMIC_ASSIGNMENT_PERMISSIONS}
    assignment = AcademicAssignment(
        teacher_id=data.teacher_id,
        subject_id=data.subject_id,
        class_id=data.class_id,
        academic_period_id=data.academic_period_id,
        permissions=permissions,
        assigned_by=current_user.id,
    )
    db.add(assignment)
    db.flush()
    db.add(
        AuditLog(
            user_id=current_user.id,
            action=AuditActionType.PERMISSION_CHANGE,
            entity_type="AcademicAssignment",
            entity_id=assignment.id,
            description="Atribuição acadêmica criada com permissões contextuais",
            new_values={
                "teacher_id": str(data.teacher_id),
                "subject_id": str(data.subject_id),
                "class_id": str(data.class_id),
                "academic_period_id": str(data.academic_period_id),
                "permissions": permissions,
                "is_active": True,
            },
        )
    )
    try:
        db.commit()
        db.refresh(assignment)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma atribuição ativa para este contexto",
        ) from exc
    return assignment


@router.patch(
    "/assignments/{assignment_id}",
    response_model=AcademicAssignmentResponse,
)
def update_academic_assignment(
    assignment_id: UUID,
    data: AcademicAssignmentUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    assignment = db.get(AcademicAssignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Atribuição acadêmica não encontrada")

    old_values = {
        "permissions": assignment.permissions.copy(),
        "is_active": assignment.is_active,
    }
    updates = data.model_dump(exclude_unset=True)
    if "permissions" in updates and updates["permissions"] is not None:
        assignment.permissions = {
            key: updates["permissions"].get(key, False)
            for key in ACADEMIC_ASSIGNMENT_PERMISSIONS
        }
    if updates.get("is_active") is not None:
        assignment.is_active = updates["is_active"]
        assignment.deactivated_at = None if assignment.is_active else datetime.now(UTC)
    assignment.updated_at = datetime.now(UTC)
    db.flush()

    new_values = {
        "permissions": assignment.permissions,
        "is_active": assignment.is_active,
    }
    db.add(
        AuditLog(
            user_id=current_user.id,
            action=AuditActionType.PERMISSION_CHANGE,
            entity_type="AcademicAssignment",
            entity_id=assignment.id,
            description="Permissões ou situação da atribuição acadêmica alteradas",
            old_values=old_values,
            new_values=new_values,
        )
    )
    try:
        db.commit()
        db.refresh(assignment)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma atribuição ativa para este contexto",
        ) from exc
    return assignment


# ==================== Assessments ====================

@router.post("/assessments", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    class_record = require_class_permission(
        db,
        current_user,
        assessment_data.class_id,
        "create_assessments",
    )
    if (
        assessment_data.subject_id != class_record.subject_id
        or assessment_data.academic_period_id != class_record.academic_period_id
    ):
        raise HTTPException(
            status_code=422,
            detail="A avaliação deve corresponder à disciplina e período da turma",
        )
    service = AssessmentService(db)
    return service.create(assessment_data, current_user.id)


@router.get("/assessments", response_model=PaginatedResponse[AssessmentResponse])
def list_assessments(
    class_id: UUID | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(Assessment)
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher_profile
        if teacher is None:
            raise HTTPException(status_code=403, detail="Perfil de professor não encontrado")
        allowed_classes = {
            assignment.class_id
            for assignment in db.query(AcademicAssignment).filter(
                AcademicAssignment.teacher_id == teacher.id,
                AcademicAssignment.is_active.is_(True),
                AcademicAssignment.permissions["view_history"].as_boolean().is_(True),
            ).all()
        }
        legacy_classes = db.query(AcademicClass).join(
            TeacherSubject,
            (TeacherSubject.teacher_id == teacher.id)
            & (TeacherSubject.subject_id == AcademicClass.subject_id)
            & or_(
                TeacherSubject.academic_period_id.is_(None),
                TeacherSubject.academic_period_id == AcademicClass.academic_period_id,
            ),
        ).filter(AcademicClass.teacher_id == teacher.id).all()
        for legacy_class in legacy_classes:
            if not _has_assignment_history(db, teacher.id, legacy_class.id):
                allowed_classes.add(legacy_class.id)
        if class_id is not None and class_id not in allowed_classes:
            raise HTTPException(status_code=403, detail="Turma não autorizada")
        query = query.filter(Assessment.class_id.in_(allowed_classes or {UUID(int=0)}))
    elif current_user.role == UserRole.STUDENT:
        student = current_user.student_profile
        if student is None:
            raise HTTPException(status_code=403, detail="Perfil de aluno não encontrado")
        allowed_classes = {
            enrollment.class_id for enrollment in db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            ).all()
        }
        if class_id is not None and class_id not in allowed_classes:
            raise HTTPException(status_code=404, detail="Avaliações não encontradas")
        query = query.filter(
            Assessment.class_id.in_(allowed_classes or {UUID(int=0)}),
            Assessment.is_published.is_(True),
        )
    if class_id is not None:
        query = query.filter(Assessment.class_id == class_id)
    total = query.count()
    assessments = query.order_by(Assessment.created_at.desc()).offset(params.offset).limit(params.limit).all()
    return PaginatedResponse(
        items=assessments, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.post("/assessments/{assessment_id}/publish", response_model=AssessmentResponse)
def publish_assessment(
    assessment_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = AssessmentService(db)
    assessment = service.get(assessment_id)
    require_class_permission(db, current_user, assessment.class_id, "create_assessments")
    return service.publish(assessment_id, current_user.id)


@router.get("/grades/my", response_model=PaginatedResponse[GradeWithRelations])
def list_my_published_grades(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.STUDENT or current_user.student_profile is None:
        raise HTTPException(status_code=403, detail="Apenas alunos podem consultar suas próprias notas")
    query = db.query(Grade).join(Enrollment).filter(
        Enrollment.student_id == current_user.student_profile.id,
        Enrollment.status == EnrollmentStatus.ACTIVE,
        Grade.is_official.is_(True),
        Grade.published_at.is_not(None),
    )
    total = query.count()
    grades = query.order_by(Grade.published_at.desc()).offset(params.offset).limit(params.limit).all()
    return PaginatedResponse(
        items=grades, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/grades", response_model=PaginatedResponse[GradeWithRelations])
def list_grades(
    class_id: UUID | None = None,
    student_id: UUID | None = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Grade).join(Enrollment)
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher_profile
        if teacher is None:
            raise HTTPException(status_code=403, detail="Perfil de professor não encontrado")
        allowed_classes = {
            assignment.class_id
            for assignment in db.query(AcademicAssignment).filter(
                AcademicAssignment.teacher_id == teacher.id,
                AcademicAssignment.is_active.is_(True),
                AcademicAssignment.permissions["view_history"].as_boolean().is_(True),
            ).all()
        }
        legacy_classes = db.query(AcademicClass).join(
            TeacherSubject,
            (TeacherSubject.teacher_id == teacher.id)
            & (TeacherSubject.subject_id == AcademicClass.subject_id)
            & or_(
                TeacherSubject.academic_period_id.is_(None),
                TeacherSubject.academic_period_id == AcademicClass.academic_period_id,
            ),
        ).filter(AcademicClass.teacher_id == teacher.id).all()
        for legacy_class in legacy_classes:
            if not _has_assignment_history(db, teacher.id, legacy_class.id):
                allowed_classes.add(legacy_class.id)
        if class_id is not None and class_id not in allowed_classes:
            raise HTTPException(status_code=403, detail="Turma não autorizada")
        query = query.filter(Enrollment.class_id.in_(allowed_classes or {UUID(int=0)}))
    if class_id is not None:
        query = query.filter(Enrollment.class_id == class_id)
    if student_id is not None:
        query = query.filter(Enrollment.student_id == student_id)
    total = query.count()
    grades = query.order_by(Grade.created_at.desc()).offset(params.offset).limit(params.limit).all()
    return PaginatedResponse(
        items=grades, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


# ==================== Grades ====================

@router.post("/grades", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(
    grade_data: GradeCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    enrollment = db.get(Enrollment, grade_data.enrollment_id)
    assessment = db.get(Assessment, grade_data.assessment_id)
    if enrollment is None or assessment is None:
        raise HTTPException(status_code=404, detail="Matrícula ou avaliação não encontrada")
    if enrollment.class_id != assessment.class_id:
        raise HTTPException(
            status_code=422,
            detail="A matrícula e a avaliação pertencem a turmas diferentes",
        )
    _validate_grade_score(grade_data.score, assessment.max_score)
    require_class_permission(db, current_user, enrollment.class_id, "edit_grades")
    service = GradeService(db)
    return service.create(grade_data, current_user.id)


@router.post("/grades/bulk", response_model=list[GradeResponse])
def bulk_create_grades(
    data: BulkGradeCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = GradeService(db)
    grades = []
    for g in data.grades:
        enrollment = db.get(Enrollment, g.enrollment_id)
        assessment = db.get(Assessment, g.assessment_id)
        if enrollment is None or assessment is None:
            raise HTTPException(status_code=404, detail="Matrícula ou avaliação não encontrada")
        if enrollment.class_id != assessment.class_id:
            raise HTTPException(
                status_code=422,
                detail="A matrícula e a avaliação pertencem a turmas diferentes",
            )
        _validate_grade_score(g.score, assessment.max_score)
        require_class_permission(db, current_user, enrollment.class_id, "edit_grades")
        grade = service.create(g, current_user.id)
        grades.append(grade)
    return grades


@router.patch("/grades/{grade_id}", response_model=GradeResponse)
def update_grade(
    grade_id: UUID,
    grade_data: GradeUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    grade = db.get(Grade, grade_id)
    if grade is None:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    enrollment = db.get(Enrollment, grade.enrollment_id)
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    assessment = db.get(Assessment, grade.assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    if grade_data.score is not None:
        _validate_grade_score(grade_data.score, assessment.max_score)
    if grade_data.is_official is not None and grade_data.is_official != grade.is_official:
        raise HTTPException(
            status_code=422,
            detail="Use a operação de publicação para alterar a situação oficial da nota",
        )
    require_class_permission(db, current_user, enrollment.class_id, "edit_grades")
    service = GradeService(db)
    return service.update(grade_id, grade_data, current_user.id)


@router.post("/grades/{grade_id}/publish", response_model=GradeResponse)
def publish_grade(
    grade_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    grade = db.get(Grade, grade_id)
    if grade is None:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    enrollment = db.get(Enrollment, grade.enrollment_id)
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    require_class_permission(db, current_user, enrollment.class_id, "publish_grades")
    service = GradeService(db)
    return service.publish(grade_id, current_user.id)


# ==================== Attendance ====================

@router.post("/attendance", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    attendance_data: AttendanceCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = AttendanceService(db)
    return service.create(attendance_data, current_user.id)


@router.post("/attendance/bulk", response_model=list[AttendanceResponse])
def bulk_create_attendance(
    data: BulkAttendanceCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = AttendanceService(db)
    return service.bulk_create(data.class_id, data.class_date, data.attendances, current_user.id)


@router.get("/attendance/my", response_model=list[MyAttendanceSummary])
def list_my_attendance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Resumo de frequência das matrículas ativas do usuário autenticado."""
    student = current_user.student_profile
    if student is None:
        raise HTTPException(status_code=404, detail="Perfil de aluno não encontrado")

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.status == EnrollmentStatus.ACTIVE,
    ).all()

    summaries: list[MyAttendanceSummary] = []
    for enrollment in enrollments:
        records = db.query(Attendance).filter(
            Attendance.enrollment_id == enrollment.id
        ).order_by(Attendance.class_date).all()
        total = len(records)
        present = sum(1 for record in records if record.is_present)
        justified = sum(1 for record in records if record.justified)
        absent = total - present
        percentage = (
            (Decimal(present) / Decimal(total) * Decimal(100)).quantize(Decimal("0.01"))
            if total
            else Decimal("0.00")
        )
        class_record = enrollment.class_
        summaries.append(
            MyAttendanceSummary(
                enrollment_id=enrollment.id,
                class_id=enrollment.class_id,
                class_code=class_record.code if class_record else "",
                class_name=class_record.name if class_record else "",
                subject_name=(
                    class_record.subject.name
                    if class_record is not None and class_record.subject is not None
                    else ""
                ),
                total_classes=total,
                present_count=present,
                absent_count=absent,
                justified_count=justified,
                percentage=percentage,
                records=[
                    {
                        "date": record.class_date,
                        "is_present": record.is_present,
                        "justified": record.justified,
                        "justification": record.justification,
                    }
                    for record in records
                ],
            )
        )
    return summaries


@router.get("/attendance/percentage/{enrollment_id}", response_model=Decimal)
def get_attendance_percentage(
    enrollment_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AttendanceService(db)
    return service.calculate_percentage(enrollment_id)


# ==================== Academic Rules ====================

@router.post("/rules", response_model=AcademicRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_data: AcademicRuleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = AcademicRuleService(db)
    return service.create(rule_data)


@router.get("/rules", response_model=list[AcademicRuleResponse])
def list_rules(
    rule_type: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AcademicRuleService(db)
    if rule_type:
        return service.get_by_type(rule_type)
    return service.repo.get_all(filters={"is_active": True})
