"""Rotas do Módulo Acadêmico."""

from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_active_user, require_admin, require_teacher_or_admin
from backend.app.models.user import User, UserRole
from backend.app.schemas.academic import (
    CourseCreate, CourseUpdate, CourseResponse, CourseWithRelations,
    SubjectCreate, SubjectUpdate, SubjectResponse,
    ClassCreate, ClassUpdate, ClassResponse, ClassWithRelations,
    AcademicPeriodCreate, AcademicPeriodUpdate, AcademicPeriodResponse,
    EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse, EnrollmentWithRelations,
    TeacherSubjectCreate, TeacherSubjectResponse,
    AssessmentCreate, AssessmentUpdate, AssessmentResponse,
    GradeCreate, GradeUpdate, GradeResponse,
    AttendanceCreate, AttendanceUpdate, AttendanceResponse,
    AcademicRuleCreate, AcademicRuleUpdate, AcademicRuleResponse,
    BulkEnrollmentCreate, BulkGradeCreate, BulkAttendanceCreate,
)
from backend.app.services.academic_service import (
    CourseService, SubjectService, ClassService, AcademicPeriodService,
    EnrollmentService, AssessmentService, GradeService,
    AttendanceService, TeacherSubjectService, AcademicRuleService,
)
from backend.app.schemas.common import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/academic", tags=["Acadêmico"])


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
    course_id: Optional[UUID] = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = SubjectService(db)
    if course_id:
        subjects = service.get_by_course(course_id)
    else:
        subjects = service.repo.get_all(skip=params.offset, limit=params.limit)
    total = len(subjects)
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
    service = ClassService(db)
    return service.create(class_data, current_user.id)


@router.get("/classes", response_model=PaginatedResponse[ClassWithRelations])
def list_classes(
    teacher_id: Optional[UUID] = None,
    course_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    academic_period_id: Optional[UUID] = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = ClassService(db)
    if teacher_id:
        classes = service.get_by_teacher(teacher_id)
    else:
        classes = service.repo.get_all(skip=params.offset, limit=params.limit)
    total = len(classes)
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
    service = ClassService(db)
    classes = service.get_by_teacher(current_user.teacher_profile.id)
    total = len(classes)
    return PaginatedResponse(
        items=classes, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total, has_prev=params.page > 1,
    )


@router.get("/classes/{class_id}", response_model=ClassWithRelations)
def get_class(
    class_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = ClassService(db)
    return service.get(class_id)


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


# ==================== Enrollments ====================

@router.post("/enrollments", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_data: EnrollmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = EnrollmentService(db)
    return service.create(enrollment_data, current_user.id)


@router.post("/enrollments/bulk", response_model=List[EnrollmentResponse])
def bulk_create_enrollments(
    data: BulkEnrollmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = EnrollmentService(db)
    return service.bulk_create(data.class_id, data.student_ids, data.academic_period_id, current_user.id)


@router.get("/enrollments", response_model=PaginatedResponse[EnrollmentWithRelations])
def list_enrollments(
    student_id: Optional[UUID] = None,
    class_id: Optional[UUID] = None,
    academic_period_id: Optional[UUID] = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
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


# ==================== Teacher Subjects ====================

@router.post("/teacher-subjects", response_model=TeacherSubjectResponse, status_code=status.HTTP_201_CREATED)
def assign_teacher_subject(
    data: TeacherSubjectCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = TeacherSubjectService(db)
    return service.create(data)


# ==================== Assessments ====================

@router.post("/assessments", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = AssessmentService(db)
    return service.create(assessment_data, current_user.id)


@router.get("/assessments", response_model=PaginatedResponse[AssessmentResponse])
def list_assessments(
    class_id: Optional[UUID] = None,
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AssessmentService(db)
    if class_id:
        assessments = service.repo.get_by_class(class_id)
    else:
        assessments = service.repo.get_all(skip=params.offset, limit=params.limit)
    total = len(assessments)
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
    return service.publish(assessment_id, current_user.id)


# ==================== Grades ====================

@router.post("/grades", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(
    grade_data: GradeCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = GradeService(db)
    return service.create(grade_data, current_user.id)


@router.post("/grades/bulk", response_model=List[GradeResponse])
def bulk_create_grades(
    data: BulkGradeCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = GradeService(db)
    grades = []
    for g in data.grades:
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
    service = GradeService(db)
    return service.update(grade_id, grade_data, current_user.id)


@router.post("/grades/{grade_id}/publish", response_model=GradeResponse)
def publish_grade(
    grade_id: UUID,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
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


@router.post("/attendance/bulk", response_model=List[AttendanceResponse])
def bulk_create_attendance(
    data: BulkAttendanceCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    service = AttendanceService(db)
    return service.bulk_create(data.class_id, data.class_date, data.attendances, current_user.id)


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


@router.get("/rules", response_model=List[AcademicRuleResponse])
def list_rules(
    rule_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AcademicRuleService(db)
    if rule_type:
        return service.get_by_type(rule_type)
    return service.repo.get_all(filters={"is_active": True})