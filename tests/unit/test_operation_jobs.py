"""Testes das operações de longa duração, importações e uploads com progresso."""

from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.app.services.operation_runner as operation_runner
from backend.app.core.database import Base, get_db
from backend.app.core.security import get_current_active_user
from backend.app.core.seed import seed_database
from backend.app.main import app
from backend.app.models.academic import Grade
from backend.app.models.operation_job import OperationJob, OperationKind, OperationStatus
from backend.app.models.user import Student, User
from backend.app.services.import_service import ImportFormatError, normalize_key, parse_csv_table
from backend.app.services.operation_job_service import OperationJobService


def _make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
def seeded_api():
    engine, session_factory = _make_session()
    db = session_factory()
    seed_database(db)
    users = {user.username: user for user in db.query(User).all()}
    actor = [users["professor"]]

    def override_db():
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def override_user():
        return actor[0]

    previous = app.dependency_overrides.copy()
    previous_session_local = operation_runner.SessionLocal
    operation_runner.SessionLocal = session_factory
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_active_user] = override_user
    client = TestClient(app, raise_server_exceptions=False)
    yield {
        "client": client,
        "db": db,
        "factory": session_factory,
        "users": users,
        "actor": actor,
    }
    client.close()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)
    operation_runner.SessionLocal = previous_session_local
    db.close()
    engine.dispose()


def _teacher_context(client):
    profile = client.get("/api/v1/academic/my-profile").json()
    assignment = profile["teacher"]["assignments"][0]
    return assignment


# ==================== Serviço de operações ====================

def test_job_service_progress_is_real_or_indeterminate(seeded_api):
    db = seeded_api["db"]
    service = OperationJobService(db)
    job = service.create(
        kind=OperationKind.AI_CORRECTION,
        title="Correção de teste",
        user_id=seeded_api["users"]["professor"].id,
        total=4,
    )
    assert service.serialize(job)["progress"] is None  # ainda não começou

    service.start(job.id, step_key="ocr", step_label="Lendo respostas")
    assert service.serialize(job)["progress"] is None  # etapa sem medida confiável

    service.set_progress(job.id, processed=2, total=4)
    assert service.serialize(job)["progress"] == 50.0

    service.set_progress(job.id, processed=4, total=4)
    assert service.serialize(job)["progress"] == 100.0

    # Recarrega do banco (SQLite devolve datetime sem timezone) e garante o cálculo.
    db.expire_all()
    reloaded = service.get(job.id)
    assert service.serialize(reloaded)["elapsed_seconds"] >= 0.0


def test_job_cancel_is_cooperative(seeded_api):
    db = seeded_api["db"]
    service = OperationJobService(db)
    job = service.create(
        kind=OperationKind.GRADE_IMPORT,
        title="Importação",
        user_id=seeded_api["users"]["professor"].id,
        total=10,
    )
    service.start(job.id)
    service.cancel(job.id)

    from backend.app.services.operation_job_service import OperationCancelled

    with pytest.raises(OperationCancelled):
        service.set_progress(job.id, processed=1)
    assert service.get(job.id).status == OperationStatus.CANCELLED


def test_job_access_is_scoped_to_owner_or_admin(seeded_api):
    db = seeded_api["db"]
    service = OperationJobService(db)
    job = service.create(
        kind=OperationKind.STUDENT_IMPORT,
        title="Importação privada",
        user_id=seeded_api["users"]["professor2"].id,
    )
    with pytest.raises(Exception):
        service.get_for_user(job.id, seeded_api["users"]["professor"])
    admin = seeded_api["users"]["admin"]
    assert service.get_for_user(job.id, admin).id == job.id


# ==================== CSV ====================

def test_parse_csv_accepts_semicolon_and_normalizes_headers():
    headers, rows = parse_csv_table(
        "Nome;E-mail;Usuário;RA\nAna;ana@escola.edu.br;ana;RA1\n".encode()
    )
    assert headers == ["nome", "email", "usuario", "ra"]
    assert rows[0]["ra"] == "RA1"


def test_parse_csv_rejects_empty_or_headerless_files():
    with pytest.raises(ImportFormatError):
        parse_csv_table(b"")
    with pytest.raises(ImportFormatError):
        parse_csv_table(";;\n".encode())


def test_normalize_key_removes_accents_and_symbols():
    assert normalize_key("Matrícula Institucional") == "matricula_institucional"


# ==================== Importação de alunos e notas ====================

def test_student_import_creates_accounts_and_reports_problems(seeded_api):
    client = seeded_api["client"]
    assignment = _teacher_context(client)
    class_id = assignment["class_id"]

    csv_content = (
        "nome;email;usuario;senha;ra;matricula\n"
        "Aluno Importado;aluno.importado@escola.edu.br;aluno.importado;SenhaForte123;RA9001;20269001\n"
        "Aluno Duplicado;aluno@edugrade.local;outro.usuario;SenhaForte123;RA9002;20269002\n"
        "Sem Senha;sem.senha@escola.edu.br;sem.senha;;RA9003;20269003\n"
    ).encode()

    response = client.post(
        "/api/v1/imports/students",
        data={"class_id": class_id},
        files={"file": ("alunos.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 202, response.text
    job_id = response.json()["job_id"]

    job = client.get(f"/api/v1/jobs/{job_id}")
    assert job.status_code == 200
    body = job.json()
    assert body["kind"] == "student_import"
    assert body["status"] in {"succeeded", "succeeded_with_warnings"}
    assert body["result"]["imported"] == 1
    assert body["result"]["duplicated"] == 1
    assert body["result"]["failed"] == 1
    assert len(body["result"]["errors"]) == 2

    db = seeded_api["db"]
    created = db.query(User).filter(User.username == "aluno.importado").one()
    assert created.role.value == "student"
    student = db.query(Student).filter(Student.user_id == created.id).one()
    assert student.ra == "RA9001"


def test_grade_import_updates_drafts_and_rejects_out_of_range(seeded_api):
    client = seeded_api["client"]
    assignment = _teacher_context(client)
    class_id = assignment["class_id"]
    subject_id = assignment["subject_id"]
    period_id = assignment["academic_period_id"]

    assessment = client.post(
        "/api/v1/academic/assessments",
        json={
            "title": "Prova de importação",
            "type": "a1",
            "weight": "1.00",
            "max_score": "10.00",
            "class_id": class_id,
            "subject_id": subject_id,
            "academic_period_id": period_id,
            "scheduled_date": "2026-04-10",
        },
    )
    assert assessment.status_code == 201, assessment.text

    csv_content = (
        "ra;avaliacao;nota\n"
        "RA123456;Prova de importação;9,5\n"
        "RA123456;Avaliação inexistente;7\n"
        "RA999999;Prova de importação;8\n"
        "RA123456;Prova de importação;11\n"
        "RA123456;Prova de importação;7\n"
    ).encode()

    response = client.post(
        "/api/v1/imports/grades",
        data={"class_id": class_id},
        files={"file": ("notas.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 202, response.text

    job = client.get(f"/api/v1/jobs/{response.json()['job_id']}").json()
    assert job["result"]["imported"] == 2, job["result"]  # primeira nota + atualização
    assert job["result"]["failed"] == 3  # avaliação inexistente, RA e nota acima do máximo
    assert job["result"]["duplicated"] == 1  # nota atualizada

    db = seeded_api["db"]
    grade = (
        db.query(Grade)
        .filter(Grade.assessment_id == UUID(assessment.json()["id"]))
        .one()
    )
    assert float(grade.score) == 7.0  # a última linha válida sobrescreve


def test_import_rejects_wrong_headers(seeded_api):
    client = seeded_api["client"]
    assignment = _teacher_context(client)
    response = client.post(
        "/api/v1/imports/students",
        data={"class_id": assignment["class_id"]},
        files={"file": ("alunos.csv", b"nome;ra\nAna;RA1\n", "text/csv")},
    )
    assert response.status_code == 422
    assert "colunas" in response.json()["detail"].lower()


# ==================== Rotas de jobs ====================

def test_jobs_list_only_shows_own_operations(seeded_api):
    client = seeded_api["client"]
    db = seeded_api["db"]
    teacher = seeded_api["users"]["professor"]
    other = seeded_api["users"]["professor2"]

    service = OperationJobService(db)
    mine = service.create(
        kind=OperationKind.EXAM_PDF_IMPORT, title="Minha", user_id=teacher.id
    )
    service.create(kind=OperationKind.EXAM_PDF_IMPORT, title="De outro", user_id=other.id)
    service.finish(mine.id, message="ok")

    response = client.get("/api/v1/jobs?limit=10")
    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["items"]]
    assert "Minha" in titles
    assert "De outro" not in titles

    seeded_api["actor"][0] = teacher
    other_job = db.query(OperationJob).filter(OperationJob.title == "De outro").one()
    assert client.get(f"/api/v1/jobs/{other_job.id}").status_code == 404


def test_cancel_endpoint_marks_operation_cancelled(seeded_api):
    client = seeded_api["client"]
    db = seeded_api["db"]
    service = OperationJobService(db)
    job = service.create(
        kind=OperationKind.GRADE_IMPORT,
        title="Cancelável",
        user_id=seeded_api["users"]["professor"].id,
        total=3,
    )
    service.start(job.id)

    response = client.post(f"/api/v1/jobs/{job.id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


# ==================== Upload por arquivo + correção em segundo plano ====================

def _published_exam_with_copy(client, assignment):
    exam = client.post(
        "/api/v1/exams/complete",
        json={
            "title": "Prova com upload",
            "class_id": assignment["class_id"],
            "subject_id": assignment["subject_id"],
            "academic_period_id": assignment["academic_period_id"],
            "total_score": "10.00",
            "duration_minutes": 60,
            "questions": [
                {
                    "type": "essay",
                    "statement": "Explique generalização.",
                    "score": "10.00",
                    "expected_answer": "Capacidade de aplicar o aprendizado a dados novos.",
                }
            ],
        },
    )
    assert exam.status_code == 201, exam.text
    publish = client.post(f"/api/v1/exams/{exam.json()['id']}/publish")
    assert publish.status_code == 200, publish.text
    versions = client.get("/api/v1/exams/versions/active").json()
    version = versions[0]
    copies = client.post(f"/api/v1/exams/versions/{version['version_id']}/copies?count=1")
    assert copies.status_code == 200, copies.text
    return exam.json(), version, copies.json()[0]


def test_upload_files_and_follow_ai_correction_job(seeded_api, monkeypatch):
    import pymupdf

    from backend.app.integrations.ocr.processor import OCRProcessor
    from backend.app.services.ai_correction_service import AIProviderFactory, MockProvider

    monkeypatch.setattr(
        AIProviderFactory,
        "get_provider",
        classmethod(lambda cls, provider_type=None, db=None: MockProvider()),
    )

    def _tesseract_missing(self, image_path):
        raise RuntimeError("Tesseract não encontrado")

    monkeypatch.setattr(OCRProcessor, "process_page", _tesseract_missing)

    client = seeded_api["client"]
    assignment = _teacher_context(client)
    _exam, version, copy = _published_exam_with_copy(client, assignment)

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((50, 70), "Questão 1", fontsize=12)
    page.insert_text((50, 90), "Explique generalização.", fontsize=11)
    page.insert_text((50, 110), "Resposta: capacidade de aplicar a dados novos", fontsize=11)
    pdf_bytes = document.tobytes()
    document.close()

    upload = client.post(
        "/api/v1/exams/uploads",
        data={"copy_id": copy["id"]},
        files={"file": ("pagina1.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 200, upload.text
    uploaded = upload.json()
    assert uploaded["size_bytes"] > 0

    submission = client.post(
        "/api/v1/exams/submissions/from-uploads",
        json={"copy_id": copy["id"], "uploads": [uploaded]},
    )
    assert submission.status_code == 201, submission.text

    started = client.post(
        f"/api/v1/exams/submissions/{submission.json()['id']}/correction-jobs"
    )
    assert started.status_code == 202, started.text

    job = client.get(f"/api/v1/jobs/{started.json()['job_id']}").json()
    assert job["kind"] == "ai_correction"
    assert job["status"] == "succeeded", job
    assert job["result"]["corrected"] == 1
    assert job["total"] == 1
    assert job["progress"] == 100.0
    # Sem Tesseract, as respostas são lidas da camada de texto do PDF.
    assert any("resposta" in warning.lower() for warning in job["warnings"])


def test_extract_answers_from_pdf_text_layer(tmp_path):
    import pymupdf

    from backend.app.integrations.ocr.text_layer import extract_answers_from_pdf

    path = tmp_path / "prova.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((50, 70), "Questão 1", fontsize=12)
    page.insert_text((50, 90), "Resposta: B", fontsize=11)
    page.insert_text((50, 120), "Questão 2", fontsize=12)
    page.insert_text((50, 140), "Resposta: c", fontsize=11)
    page.insert_text((50, 170), "Questão 3", fontsize=12)
    document.save(path)
    document.close()

    answers = extract_answers_from_pdf(path)
    assert [answer["question_order"] for answer in answers] == [1, 2]
    assert answers[0]["extracted_text"] == "B"
    assert answers[1]["extracted_text"] == "c"
    assert answers[0]["ocr_confidence"] == 100.0


def test_cancelled_exam_can_be_restored_and_published(seeded_api):
    client = seeded_api["client"]
    assignment = _teacher_context(client)
    exam = client.post(
        "/api/v1/exams/complete",
        json={
            "title": "Prova para reativar",
            "class_id": assignment["class_id"],
            "subject_id": assignment["subject_id"],
            "academic_period_id": assignment["academic_period_id"],
            "total_score": "10.00",
            "duration_minutes": 60,
            "questions": [
                {
                    "type": "essay",
                    "statement": "Pergunta qualquer.",
                    "score": "10.00",
                    "expected_answer": "Resposta esperada.",
                }
            ],
        },
    )
    exam_id = exam.json()["id"]

    cancelled = client.delete(f"/api/v1/exams/{exam_id}")
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "cancelled"

    restore = client.post(f"/api/v1/exams/{exam_id}/restore")
    assert restore.status_code == 200, restore.text
    assert restore.json()["status"] == "draft"

    publish = client.post(f"/api/v1/exams/{exam_id}/publish")
    assert publish.status_code == 200, publish.text


# ==================== Painel de qualidade ====================

def test_quality_run_requires_admin_and_blocks_duplicates(seeded_api, monkeypatch):
    import backend.app.api.routes.quality as quality_routes

    monkeypatch.setattr(quality_routes, "run_quality_job", lambda job_id: None)
    client = seeded_api["client"]

    seeded_api["actor"][0] = seeded_api["users"]["aluno"]
    assert client.post("/api/v1/quality/run").status_code == 403

    seeded_api["actor"][0] = seeded_api["users"]["admin"]
    started = client.post("/api/v1/quality/run")
    assert started.status_code == 202, started.text
    job = client.get(f"/api/v1/jobs/{started.json()['job_id']}").json()
    assert job["kind"] == "quality_run"

    duplicate = client.post("/api/v1/quality/run")
    assert duplicate.status_code == 409


def test_quality_report_parsers(tmp_path):
    from backend.app.services.operation_runner import _read_coverage_xml, _read_junit_xml

    coverage = tmp_path / "coverage.xml"
    coverage.write_text(
        '<coverage line-rate="0.8132" lines-valid="100" lines-covered="82"></coverage>',
        encoding="utf-8",
    )
    parsed = _read_coverage_xml(coverage)
    assert parsed == {
        "coverage_percent": 81.32,
        "lines_valid": 100,
        "lines_covered": 82,
    }

    junit = tmp_path / "junit.xml"
    junit.write_text(
        '<testsuites tests="10" failures="1" errors="1" skipped="2">'
        '<testsuite tests="10" failures="1" errors="1" skipped="2"></testsuite>'
        "</testsuites>",
        encoding="utf-8",
    )
    tests = _read_junit_xml(junit)
    assert tests == {"total": 10, "passed": 6, "failed": 2, "skipped": 2}

    assert _read_coverage_xml(tmp_path / "ausente.xml") is None
    assert _read_junit_xml(tmp_path / "ausente.xml") is None


def test_quality_job_marks_success_and_reports_numbers(seeded_api, monkeypatch, tmp_path):
    """Executa o runner com um pytest simulado para validar o caminho de sucesso."""
    import subprocess

    import backend.app.services.operation_runner as runner

    reports = tmp_path / "reports"
    reports.mkdir()

    class FakeCompleted:
        returncode = 0
        stdout = "262 passed"
        stderr = ""

    def fake_run(*args, **kwargs):
        # O runner apaga relatórios antigos e executa pytest; simulamos a saída.
        (reports / "coverage.xml").write_text(
            '<coverage line-rate="0.81" lines-valid="1000" lines-covered="810"></coverage>',
            encoding="utf-8",
        )
        (reports / "junit.xml").write_text(
            '<testsuites tests="262" failures="0" errors="0" skipped="0"></testsuites>',
            encoding="utf-8",
        )
        return FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)

    db = seeded_api["db"]
    service = OperationJobService(db)
    job = service.create(
        kind=OperationKind.QUALITY_RUN,
        title="Execução simulada",
        user_id=seeded_api["users"]["admin"].id,
        payload={"reports_dir": str(reports)},
    )
    runner.run_quality_job(job.id)

    db.expire_all()
    finished = service.get(job.id)
    assert finished.status == OperationStatus.SUCCEEDED
    assert finished.result["coverage"]["coverage_percent"] == 81.0
    assert finished.result["tests"]["passed"] == 262
    assert "81.0%" in finished.message
