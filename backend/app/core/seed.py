"""Seed do banco de dados do EduGrade.

Cria apenas a estrutura academica minima necessaria para o sistema operar e
duas contas de acesso para cada perfil (administrador, professor e aluno).

As credenciais ficam centralizadas em ``SEED_ACCOUNTS`` e sao documentadas em
``CREDENCIAIS.md`` na raiz do projeto.
"""

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.models.academic import (
    ACADEMIC_ASSIGNMENT_PERMISSIONS,
    AcademicAssignment,
    AcademicPeriod,
    AcademicPeriodStatus,
    Class,
    Course,
    Enrollment,
    EnrollmentStatus,
    Subject,
    TeacherSubject,
)
from backend.app.models.user import Administrator, Student, Teacher, User, UserRole

logger = logging.getLogger("edugrade.seed")

#: Senha padrao de cada perfil nas contas de demonstracao.
SEED_PASSWORDS = {
    "admin": "admin123",
    "teacher": "prof123",
    "student": "aluno123",
}

#: Contas administrativas criadas pelo seed.
SEED_ADMINS = [
    {
        "username": "admin",
        "email": "admin@edugrade.local",
        "full_name": "Administrador do Sistema",
        "employee_id": "ADM001",
        "department": "Tecnologia e Gestão Acadêmica",
    },
    {
        "username": "admin2",
        "email": "admin2@edugrade.local",
        "full_name": "Coordenação Acadêmica",
        "employee_id": "ADM002",
        "department": "Secretaria Acadêmica",
    },
]

#: Disciplinas minimas usadas na demonstracao.
SEED_SUBJECTS = [
    {
        "code": "IA101",
        "name": "Inteligência Artificial Aplicada",
        "description": "Fundamentos de IA, Machine Learning, Visão Computacional e LLMs",
        "workload_hours": 80,
        "credits": 4,
    },
    {
        "code": "ES201",
        "name": "Engenharia de Software",
        "description": "Processo, requisitos, arquitetura e qualidade de software",
        "workload_hours": 80,
        "credits": 4,
    },
]

#: Professores, suas disciplinas autorizadas e a turma que lecionam.
SEED_TEACHERS = [
    {
        "username": "professor",
        "email": "professor@edugrade.local",
        "full_name": "Prof. Carlos Silva",
        "employee_id": "PROF001",
        "department": "Departamento de Computação",
        "subject_code": "IA101",
        "class_name": "Turma A — Inteligência Artificial Aplicada",
        "class_code": "ES-IA-20261-A",
        "schedule": "Seg/Qua 19:00-20:40",
        "classroom": "Lab 04",
    },
    {
        "username": "professor2",
        "email": "professor2@edugrade.local",
        "full_name": "Profa. Ana Souza",
        "employee_id": "PROF002",
        "department": "Departamento de Engenharia de Software",
        "subject_code": "ES201",
        "class_name": "Turma A — Engenharia de Software",
        "class_code": "ES-ES-20261-A",
        "schedule": "Ter/Qui 19:00-20:40",
        "classroom": "Sala 12",
    },
]

#: Alunos matriculados em todas as turmas criadas pelo seed.
SEED_STUDENTS = [
    {
        "username": "aluno",
        "email": "aluno@edugrade.local",
        "full_name": "Lucas Santos",
        "ra": "RA123456",
        "registration_number": "2026001",
    },
    {
        "username": "aluno2",
        "email": "aluno2@edugrade.local",
        "full_name": "Marina Oliveira",
        "ra": "RA123457",
        "registration_number": "2026002",
    },
]

#: Senhas e logins consolidados (usado pelo script de seed e pela documentacao).
SEED_ACCOUNTS = [
    {
        "role": "admin",
        "username": account["username"],
        "email": account["email"],
        "full_name": account["full_name"],
        "password": SEED_PASSWORDS["admin"],
    }
    for account in SEED_ADMINS
] + [
    {
        "role": "teacher",
        "username": account["username"],
        "email": account["email"],
        "full_name": account["full_name"],
        "password": SEED_PASSWORDS["teacher"],
    }
    for account in SEED_TEACHERS
] + [
    {
        "role": "student",
        "username": account["username"],
        "email": account["email"],
        "full_name": account["full_name"],
        "password": SEED_PASSWORDS["student"],
    }
    for account in SEED_STUDENTS
]


def seed_database(db: Session) -> bool:
    """Verifica e popula os dados iniciais caso o banco esteja vazio.

    Retorna ``True`` quando os dados foram criados e ``False`` quando o banco
    ja possuia a conta administrativa principal.
    """
    if db.execute(select(User).where(User.username == "admin")).scalar_one_or_none():
        return False

    logger.info("Populando banco de dados com a estrutura academica inicial...")

    # 1. Periodo letivo
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

    # 3. Disciplinas
    subjects: dict[str, Subject] = {}
    for subject_data in SEED_SUBJECTS:
        subject = Subject(**subject_data, course_id=course.id, is_active=True)
        db.add(subject)
        db.flush()
        subjects[subject.code] = subject

    # 4. Administradores
    for index, admin_data in enumerate(SEED_ADMINS, start=1):
        admin_user = User(
            email=admin_data["email"],
            username=admin_data["username"],
            hashed_password=get_password_hash(SEED_PASSWORDS["admin"]),
            full_name=admin_data["full_name"],
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=index == 1,
        )
        db.add(admin_user)
        db.flush()
        db.add(
            Administrator(
                user_id=admin_user.id,
                employee_id=admin_data["employee_id"],
                department=admin_data["department"],
                permissions="full",
            )
        )

    # 5. Professores, disciplinas autorizadas e turmas
    classes: dict[str, Class] = {}
    for teacher_data in SEED_TEACHERS:
        subject = subjects[teacher_data["subject_code"]]

        teacher_user = User(
            email=teacher_data["email"],
            username=teacher_data["username"],
            hashed_password=get_password_hash(SEED_PASSWORDS["teacher"]),
            full_name=teacher_data["full_name"],
            role=UserRole.TEACHER,
            is_active=True,
            is_superuser=False,
        )
        db.add(teacher_user)
        db.flush()

        teacher_profile = Teacher(
            user_id=teacher_user.id,
            employee_id=teacher_data["employee_id"],
            department=teacher_data["department"],
        )
        db.add(teacher_profile)
        db.flush()

        db.add(
            TeacherSubject(
                teacher_id=teacher_profile.id,
                subject_id=subject.id,
                academic_period_id=period.id,
            )
        )

        class_obj = Class(
            name=teacher_data["class_name"],
            code=teacher_data["class_code"],
            course_id=course.id,
            subject_id=subject.id,
            academic_period_id=period.id,
            teacher_id=teacher_profile.id,
            semester=1,
            year=2026,
            schedule=teacher_data["schedule"],
            classroom=teacher_data["classroom"],
            max_students=40,
            is_active=True,
        )
        db.add(class_obj)
        db.flush()
        classes[class_obj.code] = class_obj

        db.add(
            AcademicAssignment(
                teacher_id=teacher_profile.id,
                subject_id=subject.id,
                class_id=class_obj.id,
                academic_period_id=period.id,
                permissions={permission: True for permission in ACADEMIC_ASSIGNMENT_PERMISSIONS},
                is_active=True,
            )
        )

    # 6. Alunos e matriculas em todas as turmas
    first_class = next(iter(classes.values()))
    for student_data in SEED_STUDENTS:
        student_user = User(
            email=student_data["email"],
            username=student_data["username"],
            hashed_password=get_password_hash(SEED_PASSWORDS["student"]),
            full_name=student_data["full_name"],
            role=UserRole.STUDENT,
            is_active=True,
            is_superuser=False,
        )
        db.add(student_user)
        db.flush()

        student_profile = Student(
            user_id=student_user.id,
            ra=student_data["ra"],
            registration_number=student_data["registration_number"],
            course_id=course.id,
            class_id=first_class.id,
        )
        db.add(student_profile)
        db.flush()

        for class_obj in classes.values():
            db.add(
                Enrollment(
                    student_id=student_profile.id,
                    class_id=class_obj.id,
                    academic_period_id=period.id,
                    status=EnrollmentStatus.ACTIVE,
                )
            )

    db.commit()
    logger.info("Banco de dados populado com sucesso!")
    return True
