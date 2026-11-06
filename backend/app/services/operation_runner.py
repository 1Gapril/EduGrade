"""Execução em segundo plano das operações acompanhadas pelo ProgressManager.

Cada função abre a própria sessão do banco, atualiza ``operation_jobs`` nas
fronteiras de etapa e trata cancelamento cooperativamente. O frontend apenas
consulta o estado — o backend é a fonte oficial do progresso.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from uuid import UUID
from xml.etree import ElementTree

from backend.app.core.database import SessionLocal
from backend.app.models.academic import Class
from backend.app.models.exam import ExamSubmission, SubmissionStatus
from backend.app.models.operation_job import OperationKind
from backend.app.services.import_service import (
    BulkImportService,
    ImportFormatError,
    parse_csv_table,
)
from backend.app.services.operation_job_service import (
    OperationCancelled,
    OperationJobService,
)

logger = logging.getLogger("edugrade.jobs.runner")


def _open_job(job_id: UUID):
    db = SessionLocal()
    return db, OperationJobService(db)


# ==================== Importação de alunos / notas ====================

def run_import_job(
    job_id: UUID,
    *,
    kind: str,
    content: bytes,
    class_id: UUID,
    graded_by: UUID | None = None,
) -> None:
    """Executa a importação de alunos ou de notas em segundo plano."""
    db, jobs = _open_job(job_id)
    try:
        header_labels = "alunos" if kind == OperationKind.STUDENT_IMPORT.value else "notas"
        jobs.start(
            job_id,
            step_key="read",
            step_label=f"Lendo arquivo de {header_labels}",
        )
        headers, rows = parse_csv_table(content)
        class_record = db.get(Class, class_id)
        if class_record is None:
            jobs.fail(job_id, "Turma não encontrada.")
            return

        jobs.set_step(
            job_id,
            step_key="import",
            step_label=f"Importando {len(rows)} registro(s)",
            progress=0.0,
            total=len(rows),
        )

        def on_progress(processed: int, total: int, counters: dict) -> None:
            jobs.set_progress(
                job_id,
                processed=processed,
                total=total,
                succeeded=counters["imported"],
                failed=counters["failed"],
                skipped=counters["skipped"] + counters["duplicated"],
            )

        if kind == OperationKind.STUDENT_IMPORT.value:
            service = BulkImportService(db)
            summary = service.import_students(
                class_record=class_record,
                headers=headers,
                rows=rows,
                check_cancel=on_progress,
            )
        else:
            service = BulkImportService(db)
            summary = service.import_grades(
                class_record=class_record,
                headers=headers,
                rows=rows,
                check_cancel=on_progress,
                graded_by=graded_by,
            )

        jobs.set_step(
            job_id,
            step_key="finish",
            step_label="Preparando resumo",
            total=len(rows),
        )
        imported = summary["imported"]
        problems = summary["failed"] + summary["duplicated"] + summary["skipped"]
        message = (
            f"{imported} registro(s) importado(s); "
            f"{summary['duplicated']} duplicado(s), {summary['skipped']} ignorado(s) "
            f"e {summary['failed']} com erro."
        )
        jobs.finish(
            job_id,
            message=message,
            result={
                "total_rows": len(rows),
                **summary,
            },
            with_warnings=problems > 0,
        )
    except OperationCancelled:
        jobs.mark_cancelled(job_id, "Importação cancelada pelo usuário.")
    except ImportFormatError as error:
        jobs.fail(job_id, str(error))
    except Exception as error:  # pragma: no cover - falha inesperada
        logger.exception("Falha na importação %s", job_id)
        jobs.fail(job_id, f"Não foi possível concluir a importação: {error}")
    finally:
        db.close()


# ==================== Importação de prova a partir de PDF ====================

def run_exam_pdf_import_job(job_id: UUID, exam_pdf_path: str, answer_key_path: str | None) -> None:
    """Analisa o PDF da prova com a IA e devolve o rascunho no resultado."""
    import asyncio

    db, jobs = _open_job(job_id)
    try:
        jobs.start(job_id, step_key="read", step_label="Lendo PDF enviado")
        exam_bytes = Path(exam_pdf_path).read_bytes()
        answer_key_bytes = Path(answer_key_path).read_bytes() if answer_key_path else None

        jobs.set_step(job_id, step_key="extract", step_label="Extraindo texto das páginas")
        jobs.set_step(job_id, step_key="ai", step_label="Analisando a prova com a IA")
        jobs.set_step(job_id, step_key="validate", step_label="Conferindo questões e gabaritos")

        from backend.app.services.exam_import_service import ExamPDFImportService

        parsed = asyncio.run(ExamPDFImportService(db).analyze(exam_bytes, answer_key_bytes))
        payload = parsed.model_dump(mode="json")
        jobs.finish(
            job_id,
            message=(
                f"Prova analisada: {len(payload.get('questions', []))} questão(ões) encontradas. "
                "Confira os dados antes de salvar."
            ),
            result=parsed.model_dump(mode="json"),
            with_warnings=bool(payload.get("review_notes")),
        )
    except OperationCancelled:
        jobs.mark_cancelled(job_id, "Análise do PDF cancelada.")
    except Exception as error:
        logger.exception("Falha ao analisar PDF da prova")
        jobs.fail(job_id, f"Não foi possível analisar a prova: {error}")
    finally:
        db.close()


# ==================== Correção por IA ====================

def run_ai_correction_job(job_id: UUID, submission_id: UUID, user_id: UUID) -> None:
    """Executa OCR (quando necessário) e a correção das questões."""
    import asyncio

    db, jobs = _open_job(job_id)
    try:
        submission = db.get(ExamSubmission, submission_id)
        if submission is None:
            jobs.fail(job_id, "Submissão não encontrada.")
            return

        from backend.app.models.exam import ExamQuestion
        from backend.app.services.ai_correction_service import AICorrectionService
        from backend.app.services.exam_service import SubmissionService

        questions = (
            db.query(ExamQuestion)
            .filter(ExamQuestion.exam_id == submission.version.exam_id)
            .order_by(ExamQuestion.question_order)
            .all()
        )
        total_questions = len(questions)
        if total_questions == 0:
            jobs.fail(job_id, "A prova não possui questões para corrigir.")
            return

        jobs.start(job_id, step_key="prepare", step_label="Preparando páginas da prova")
        jobs.set_step(
            job_id,
            step_key="ocr",
            step_label="Lendo as respostas (OCR)",
            progress=None,
            total=total_questions,
        )
        try:
            submission = SubmissionService(db).process_ocr(submission_id)
            db.commit()
        except Exception as error:
            db.rollback()
            jobs.fail(
                job_id,
                "Não foi possível ler as respostas da prova. Instale o Tesseract OCR ou envie "
                f"um PDF com texto selecionável. Detalhe: {error}",
            )
            return

        db.refresh(submission)
        answers_found = sum(len(page.extracted_answers) for page in submission.pages)
        if answers_found == 0:
            jobs.fail(
                job_id,
                "Nenhuma resposta foi identificada na prova. Confira se as respostas estão "
                "numeradas (ex.: 'Questão 1 ... Resposta: B') e se a digitalização está legível.",
            )
            return
        jobs.add_warning(job_id, f"{answers_found} resposta(s) identificada(s) na prova.")

        jobs.set_step(
            job_id,
            step_key="identify",
            step_label="Identificando o aluno",
            progress=None,
        )

        service = AICorrectionService(db)
        corrected = 0
        failed = 0
        requires_review = 0
        skipped = 0

        for index, question in enumerate(questions, start=1):
            if jobs.is_cancelled(job_id):
                jobs.mark_cancelled(job_id, "Correção cancelada pelo usuário.")
                return
            jobs.set_step(
                job_id,
                step_key="correct",
                step_label=(
                    f"Corrigindo questão {index} de {total_questions}"
                    f" ({question.question_order}ª questão)"
                ),
                progress=round((index - 1) / total_questions * 100, 2),
                total=total_questions,
            )
            try:
                correction = asyncio.run(
                    service.correct_question(submission_id, question.id)
                )
                db.commit()
                corrected += 1
                if correction.requires_review:
                    requires_review += 1
            except Exception as error:
                db.rollback()
                failed += 1
                logger.warning(
                    "Falha ao corrigir questão %s da submissão %s: %s",
                    question.id,
                    submission_id,
                    error,
                )
            jobs.set_progress(
                job_id,
                processed=index,
                total=total_questions,
                succeeded=corrected,
                failed=failed,
                skipped=skipped,
            )

        if corrected == 0:
            jobs.fail(
                job_id,
                "Nenhuma resposta pôde ser corrigida. Verifique o OCR das provas enviadas.",
            )
            return

        submission = db.get(ExamSubmission, submission_id)
        if submission is not None and failed == 0:
            submission.status = SubmissionStatus.AWAITING_REVIEW
            db.commit()

        jobs.finish(
            job_id,
            message=(
                f"{corrected} questão(ões) corrigida(s) por IA; "
                f"{requires_review} aguardam revisão do professor"
                + (f" e {failed} falharam." if failed else ".")
            ),
            result={
                "submission_id": str(submission_id),
                "corrected": corrected,
                "failed": failed,
                "requires_review": requires_review,
                "questions_total": total_questions,
            },
            with_warnings=failed > 0 or requires_review > 0,
        )
    except OperationCancelled:
        jobs.mark_cancelled(job_id, "Correção cancelada pelo usuário.")
    except Exception as error:
        logger.exception("Falha na correção por IA da submissão %s", submission_id)
        jobs.fail(job_id, f"Não foi possível concluir a correção: {error}")
    finally:
        db.close()


# ==================== Execução dos testes com cobertura ====================

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _read_coverage_xml(xml_path: Path) -> dict | None:
    if not xml_path.is_file():
        return None
    try:
        root = ElementTree.parse(xml_path).getroot()
        return {
            "coverage_percent": round(float(root.attrib["line-rate"]) * 100, 2),
            "lines_valid": int(root.attrib["lines-valid"]),
            "lines_covered": int(root.attrib["lines-covered"]),
        }
    except (ElementTree.ParseError, KeyError, ValueError):
        return None


def _read_junit_xml(junit_path: Path) -> dict | None:
    if not junit_path.is_file():
        return None
    try:
        root = ElementTree.parse(junit_path).getroot()
        suites = root.findall(".//testsuite")

        def count(attribute: str) -> int:
            if attribute in root.attrib:
                return int(root.attrib[attribute])
            return sum(int(suite.attrib.get(attribute, 0)) for suite in suites)

        total = count("tests")
        failures = count("failures")
        errors = count("errors")
        skipped = count("skipped")
        return {
            "total": total,
            "passed": total - failures - errors - skipped,
            "failed": failures + errors,
            "skipped": skipped,
        }
    except (ElementTree.ParseError, ValueError):
        return None


def run_quality_job(job_id: UUID) -> None:
    """Executa ``pytest`` com cobertura em segundo plano e publica os relatórios."""
    import time

    db, jobs = _open_job(job_id)
    try:
        job = jobs.get(job_id)
        configured = (job.payload or {}).get("reports_dir")
        reports_dir = Path(configured) if configured else PROJECT_ROOT / "reports"
        if not reports_dir.is_absolute():
            reports_dir = PROJECT_ROOT / reports_dir

        jobs.start(job_id, step_key="prepare", step_label="Preparando execução dos testes")
        reports_dir.mkdir(parents=True, exist_ok=True)
        coverage_xml = reports_dir / "coverage.xml"
        coverage_html = reports_dir / "coverage"
        junit_xml = reports_dir / "junit.xml"
        for stale in (coverage_xml, junit_xml):
            stale.unlink(missing_ok=True)

        command = [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-q",
            "-p",
            "no:cacheprovider",
            "-o",
            "addopts=",
            "--cov=backend/app",
            f"--cov-report=xml:{coverage_xml}",
            f"--cov-report=html:{coverage_html}",
            f"--junitxml={junit_xml}",
            "--cov-fail-under=80",
        ]
        jobs.set_step(
            job_id,
            step_key="tests",
            step_label="Executando testes e medindo cobertura",
        )
        started = time.time()
        try:
            completed = subprocess.run(
                command,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=1800,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
        except subprocess.TimeoutExpired:
            jobs.fail(
                job_id,
                "A execução dos testes excedeu 30 minutos e foi interrompida.",
            )
            return
        except OSError as error:
            jobs.fail(job_id, f"Não foi possível iniciar o pytest: {error}")
            return

        jobs.set_step(job_id, step_key="report", step_label="Lendo relatórios gerados")
        coverage = _read_coverage_xml(coverage_xml)
        tests = _read_junit_xml(junit_xml)
        output = (completed.stdout or "") + (completed.stderr or "")
        output_tail = "\n".join(output.strip().splitlines()[-30:])

        parts = []
        if coverage:
            parts.append(
                f"Cobertura: {coverage['coverage_percent']}% "
                f"({coverage['lines_covered']}/{coverage['lines_valid']} linhas)"
            )
        if tests:
            parts.append(
                f"Testes: {tests['passed']}/{tests['total']} aprovados, "
                f"{tests['failed']} reprovados, {tests['skipped']} ignorados"
            )
        summary = ". ".join(parts) or "Execução concluída sem relatórios."
        result = {
            "return_code": completed.returncode,
            "coverage": coverage,
            "tests": tests,
            "reports_dir": str(reports_dir),
            "html_report": str(coverage_html / "index.html"),
            "output_tail": output_tail,
            "duration_seconds": round(time.time() - started, 1),
        }
        if completed.returncode == 0:
            jobs.finish(job_id, message=f"{summary}. Meta de 80% atingida.", result=result)
        else:
            jobs.fail(
                job_id,
                f"A execução terminou com código {completed.returncode}. {summary}.",
                result=result,
            )
    except Exception as error:  # pragma: no cover - falha inesperada
        logger.exception("Falha ao executar os testes de qualidade")
        jobs.fail(job_id, f"Não foi possível executar os testes: {error}")
    finally:
        db.close()

