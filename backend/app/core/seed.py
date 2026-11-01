"""Seed inicial do banco de dados com dados de demonstração."""

from datetime import datetime, date, timezone
from uuid import uuid4
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole, Student, Teacher, Administrator
from backend.app.models.academic import (
    Course, Subject, Class, AcademicPeriod, AcademicPeriodStatus,
    Enrollment, EnrollmentStatus
)

logger = logging.getLogger("edugrade.seed")


def seed_database(db: Session) -> bool:
    """Verifica e popula dados iniciais caso o banco esteja vazio."""
    # Verifica se já existe um admin
    admin_exists = db.execute(
        select(User).where(User.username == "admin")
    ).scalar_one_or_none()

    if admin_exists:
        return False

    logger.info("Populando banco de dados com dados iniciais de demonstração...")

    # 1. Período Letivo
    period = AcademicPeriod(
        name="2026.1",
        code="20261",
        start_date=date(2026, 2, 1),
        end_date=date(2026, 6, 30),
        status=AcademicPeriodStatus.ACTIVE,
        is_current=True,
    )
    db.add(period)
    db.flush()

    # 2. Curso
    course = Course(
        name="Engenharia de Software",
        code="ES01",
        description="Bacharelado em Engenharia de Software com foco em IA e Cloud",
        duration_semesters=8,
        is_active=True,
    )
    db.add(course)
    db.flush()

    # 3. Disciplina
    subject = Subject(
        name="Inteligência Artificial Aplicada",
        code="IA101",
        description="Fundamentos de IA, Machine Learning, Visão Computacional e LLMs",
        workload_hours=80,
        credits=4,
        course_id=course.id,
        is_active=True,
    )
    db.add(subject)
    db.flush()

    # 4. Usuários
    # Admin
    admin_user = User(
        email="admin@edugrade.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="Administrador do Sistema",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True,
    )
    db.add(admin_user)
    db.flush()

    admin_profile = Administrator(
        user_id=admin_user.id,
        employee_id="ADM001",
        department="Tecnologia e Gestão Acadêmica",
        permissions="full",
    )
    db.add(admin_profile)

    # Professor
    teacher_user = User(
        email="professor@edugrade.com",
        username="professor",
        hashed_password=get_password_hash("prof123"),
        full_name="Prof. Carlos Silva",
        role=UserRole.TEACHER,
        is_active=True,
        is_superuser=False,
    )
    db.add(teacher_user)
    db.flush()

    teacher_profile = Teacher(
        user_id=teacher_user.id,
        employee_id="PROF001",
        department="Departamento de Computação",
    )
    db.add(teacher_profile)

    # Aluno
    student_user = User(
        email="aluno@edugrade.com",
        username="aluno",
        hashed_password=get_password_hash("aluno123"),
        full_name="Lucas Santos",
        role=UserRole.STUDENT,
        is_active=True,
        is_superuser=False,
    )
    db.add(student_user)
    db.flush()

    student_profile = Student(
        user_id=student_user.id,
        ra="RA123456",
        course_id=course.id,
    )
    db.add(student_profile)
    db.flush()

    # 5. Turma
    class_obj = Class(
        name="Turma A - IA",
        code="ES-IA-20261-A",
        course_id=course.id,
        subject_id=subject.id,
        academic_period_id=period.id,
        teacher_id=teacher_profile.id,
        semester=1,
        year=2026,
        schedule="Seg/Qua 19:00-20:40",
        classroom="Lab 04",
        max_students=40,
        is_active=True,
    )
    db.add(class_obj)
    db.flush()

    student_profile.class_id = class_obj.id

    # 6. Matrícula
    enrollment = Enrollment(
        student_id=student_profile.id,
        class_id=class_obj.id,
        academic_period_id=period.id,
        status=EnrollmentStatus.ACTIVE,
    )
    db.add(enrollment)

    db.commit()
    logger.info("Banco de dados populado com sucesso!")
    return True

