"""Importação em massa de alunos e notas via CSV.

Cada linha é validada e processada individualmente; linhas inválidas ou
duplicadas não interrompem a importação e são devolvidas no resumo final.
"""

import csv
import io
import logging
import re
import unicodedata
from decimal import Decimal
from typing import Callable
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.models.academic import (
    Assessment,
    Class,
    Enrollment,
    EnrollmentStatus,
    Grade,
)
from backend.app.models.user import Student, User, UserRole

logger = logging.getLogger("edugrade.imports")

MAX_ROWS = 2000
MAX_ERRORS = 200
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,100}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

STUDENT_HEADERS = {"nome", "email", "usuario", "senha", "ra", "matricula"}
GRADE_HEADERS = {"ra", "avaliacao", "nota"}

#: Nomes alternativos aceitos para as colunas do CSV.
HEADER_ALIASES = {
    "e_mail": "email",
    "email_do_aluno": "email",
    "nome_completo": "nome",
    "login": "usuario",
    "user": "usuario",
    "password": "senha",
    "registro": "matricula",
    "matricula_institucional": "matricula",
    "nome_da_avaliacao": "avaliacao",
    "avaliacao_nome": "avaliacao",
    "nota_final": "nota",
}


class ImportFormatError(ValueError):
    """CSV inválido (vazio, sem cabeçalho ou acima do limite)."""


def normalize_key(value: str) -> str:
    """Remove acentos e normaliza o nome da coluna."""
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def parse_csv_table(content: bytes) -> tuple[list[str], list[dict[str, str]]]:
    """Lê o CSV aceitando ``;`` ou ``,`` e cabeçalho na primeira linha."""
    if not content or not content.strip():
        raise ImportFormatError("O arquivo enviado está vazio.")

    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover - latin-1 decodifica qualquer byte
        raise ImportFormatError("Não foi possível decodificar o arquivo. Salve o CSV em UTF-8.")

    sample = text[:4096]
    delimiter = ";" if sample.count(";") >= sample.count(",") else ","
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    if not rows:
        raise ImportFormatError("O arquivo não possui linhas de dados.")
    if len(rows) - 1 > MAX_ROWS:
        raise ImportFormatError(f"O arquivo pode ter no máximo {MAX_ROWS} linhas de dados.")

    headers = [HEADER_ALIASES.get(normalize_key(cell), normalize_key(cell)) for cell in rows[0]]
    if not any(headers):
        raise ImportFormatError("A primeira linha deve conter os nomes das colunas.")
    if len(set(headers)) != len(headers):
        raise ImportFormatError("O cabeçalho possui colunas repetidas.")

    records: list[dict[str, str]] = []
    for raw_row in rows[1:]:
        record = {
            header: (raw_row[index].strip() if index < len(raw_row) else "")
            for index, header in enumerate(headers)
            if header
        }
        records.append(record)
    return headers, records


class BulkImportService:
    """Importa alunos e notas garantindo isolamento por linha."""

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------------- utilidades
    @staticmethod
    def _ensure_headers(headers: list[str], required: set[str], label: str) -> None:
        missing = sorted(required - set(headers))
        if missing:
            raise ImportFormatError(
                f"O CSV de {label} precisa das colunas: {', '.join(sorted(required))}. "
                f"Faltando: {', '.join(missing)}."
            )

    @classmethod
    def validate_student_csv(cls, headers: list[str]) -> None:
        """Valida o cabeçalho antes de iniciar a importação."""
        cls._ensure_headers(headers, STUDENT_HEADERS, "alunos")

    @classmethod
    def validate_grade_csv(cls, headers: list[str]) -> None:
        """Valida o cabeçalho antes de iniciar a importação."""
        cls._ensure_headers(headers, GRADE_HEADERS, "notas")

    @staticmethod
    def _limit_errors(errors: list[dict]) -> list[dict]:
        return errors[:MAX_ERRORS]

    # ------------------------------------------------------------------ alunos
    def import_students(
        self,
        *,
        class_record: Class,
        headers: list[str],
        rows: list[dict[str, str]],
        check_cancel: Callable[[int, int, dict], None] | None = None,
    ) -> dict:
        """Cria conta + perfil de aluno + matrícula na turma informada."""
        self._ensure_headers(headers, STUDENT_HEADERS, "alunos")

        imported = 0
        skipped = 0
        duplicated = 0
        failed = 0
        errors: list[dict] = []

        for index, row in enumerate(rows, start=2):
            if check_cancel is not None:
                check_cancel(
                    index - 1,
                    len(rows),
                    {
                        "imported": imported,
                        "duplicated": duplicated,
                        "skipped": skipped,
                        "failed": failed,
                    },
                )
            try:
                self._import_student_row(row, class_record, index)
            except _RowError as error:
                if error.kind == "duplicated":
                    duplicated += 1
                elif error.kind == "skipped":
                    skipped += 1
                else:
                    failed += 1
                errors.append({"row": index, "message": str(error), "kind": error.kind})
                self.db.rollback()
                continue
            except Exception as error:  # pragma: no cover - proteção contra falhas inesperadas
                failed += 1
                errors.append({"row": index, "message": str(error), "kind": "error"})
                logger.exception("Falha ao importar aluno na linha %s", index)
                self.db.rollback()
                continue
            imported += 1

        return {
            "imported": imported,
            "skipped": skipped,
            "duplicated": duplicated,
            "failed": failed,
            "errors": self._limit_errors(errors),
        }

    def _import_student_row(self, row: dict[str, str], class_record: Class, index: int) -> None:
        name = row.get("nome", "").strip()
        email = row.get("email", "").strip().lower()
        username = row.get("usuario", "").strip()
        password = row.get("senha", "")
        ra = row.get("ra", "").strip()
        registration = row.get("matricula", "").strip()

        if len(name) < 2:
            raise _RowError("Nome do aluno é obrigatório (mínimo 2 caracteres).")
        if not EMAIL_PATTERN.match(email):
            raise _RowError(f"E-mail inválido: '{email or '(vazio)'}'.")
        if not USERNAME_PATTERN.match(username):
            raise _RowError("Usuário deve ter 3-100 caracteres (letras, números, ponto, hífen).")
        if len(password) < 8:
            raise _RowError("Senha inicial deve ter pelo menos 8 caracteres.")
        if not ra:
            raise _RowError("RA é obrigatório.")
        if not registration:
            raise _RowError("Matrícula institucional é obrigatória.")

        existing = self.db.query(User).filter(
            or_(
                User.username == username,
                User.email == email,
            )
        ).first()
        if existing is not None:
            raise _RowError(
                f"Usuário ou e-mail já cadastrado (usuário '{existing.username}').",
                kind="duplicated",
            )

        existing_student = self.db.query(Student).filter(
            or_(Student.ra == ra, Student.registration_number == registration)
        ).first()
        if existing_student is not None:
            raise _RowError(
                f"RA ou matrícula já cadastrados (RA '{existing_student.ra}').",
                kind="duplicated",
            )

        with self.db.begin_nested():
            user = User(
                email=email,
                username=username,
                hashed_password=get_password_hash(password),
                full_name=name,
                role=UserRole.STUDENT,
                is_active=True,
                is_superuser=False,
            )
            self.db.add(user)
            self.db.flush()

            student = Student(
                user_id=user.id,
                ra=ra,
                registration_number=registration,
                course_id=class_record.course_id,
                class_id=class_record.id,
                status="active",
            )
            self.db.add(student)
            self.db.flush()

            enrollment = self.db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.class_id == class_record.id,
            ).first()
            if enrollment is None:
                self.db.add(
                    Enrollment(
                        student_id=student.id,
                        class_id=class_record.id,
                        academic_period_id=class_record.academic_period_id,
                        status=EnrollmentStatus.ACTIVE,
                    )
                )
                self.db.flush()
        self.db.commit()

    # ------------------------------------------------------------------- notas
    def import_grades(
        self,
        *,
        class_record: Class,
        headers: list[str],
        rows: list[dict[str, str]],
        check_cancel: Callable[[int, int, dict], None] | None = None,
        graded_by: UUID | None = None,
    ) -> dict:
        """Cria ou atualiza notas (rascunho) para a turma informada."""
        self._ensure_headers(headers, GRADE_HEADERS, "notas")

        imported = 0
        skipped = 0
        duplicated = 0
        failed = 0
        errors: list[dict] = []

        assessments = {
            assessment.title.strip().lower(): assessment
            for assessment in self.db.query(Assessment)
            .filter(Assessment.class_id == class_record.id)
            .all()
        }

        for index, row in enumerate(rows, start=2):
            if check_cancel is not None:
                check_cancel(
                    index - 1,
                    len(rows),
                    {
                        "imported": imported,
                        "duplicated": duplicated,
                        "skipped": skipped,
                        "failed": failed,
                    },
                )
            try:
                outcome = self._import_grade_row(
                    row, class_record, assessments, graded_by
                )
            except _RowError as error:
                if error.kind == "duplicated":
                    duplicated += 1
                elif error.kind == "skipped":
                    skipped += 1
                else:
                    failed += 1
                errors.append({"row": index, "message": str(error), "kind": error.kind})
                self.db.rollback()
                continue
            except Exception as error:  # pragma: no cover
                failed += 1
                errors.append({"row": index, "message": str(error), "kind": "error"})
                logger.exception("Falha ao importar nota na linha %s", index)
                self.db.rollback()
                continue
            if outcome == "updated":
                duplicated += 1
            imported += 1

        return {
            "imported": imported,
            "skipped": skipped,
            "duplicated": duplicated,
            "failed": failed,
            "errors": self._limit_errors(errors),
        }

    def _import_grade_row(
        self,
        row: dict[str, str],
        class_record: Class,
        assessments: dict[str, Assessment],
        graded_by: UUID | None,
    ) -> str:
        ra = row.get("ra", "").strip()
        assessment_title = row.get("avaliacao", "").strip()
        raw_score = row.get("nota", "").strip().replace(",", ".")

        if not ra:
            raise _RowError("RA é obrigatório.")
        if not assessment_title:
            raise _RowError("Nome da avaliação é obrigatório.")
        try:
            score = float(raw_score)
        except ValueError:
            raise _RowError(f"Nota inválida: '{raw_score or '(vazia)'}'.") from None

        assessment = assessments.get(assessment_title.lower())
        if assessment is None:
            available = ", ".join(sorted(item.title for item in assessments.values())) or "nenhuma"
            raise _RowError(
                f"Avaliação '{assessment_title}' não encontrada nesta turma. Disponíveis: {available}."
            )

        student = self.db.query(Student).filter(Student.ra == ra).first()
        if student is None:
            raise _RowError(f"Nenhum aluno encontrado com RA '{ra}'.")

        enrollment = self.db.query(Enrollment).filter(
            Enrollment.student_id == student.id,
            Enrollment.class_id == class_record.id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
        ).first()
        if enrollment is None:
            raise _RowError(f"Aluno com RA '{ra}' não está matriculado nesta turma.")

        score_value = score
        if score_value < 0:
            raise _RowError("A nota não pode ser negativa.")
        if score_value > float(assessment.max_score):
            raise _RowError(
                f"A nota {score:g} excede o máximo da avaliação ({assessment.max_score})."
            )

        outcome = "created"
        with self.db.begin_nested():
            grade = self.db.query(Grade).filter(
                Grade.enrollment_id == enrollment.id,
                Grade.assessment_id == assessment.id,
            ).first()
            if grade is None:
                self.db.add(
                    Grade(
                        enrollment_id=enrollment.id,
                        assessment_id=assessment.id,
                        score=Decimal(str(score_value)),
                        graded_by=graded_by,
                    )
                )
            elif grade.is_official:
                raise _RowError(
                    "Nota já publicada para este aluno nesta avaliação.",
                    kind="skipped",
                )
            else:
                grade.score = Decimal(str(score_value))
                grade.graded_by = graded_by
                outcome = "updated"
            self.db.flush()
        self.db.commit()
        return outcome


class _RowError(Exception):
    """Erro de uma linha de importação."""

    def __init__(self, message: str, kind: str = "error"):
        super().__init__(message)
        self.kind = kind
