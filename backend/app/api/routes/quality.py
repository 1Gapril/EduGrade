"""Administrative test and coverage quality endpoints."""

import hashlib
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID
from xml.etree import ElementTree

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models.operation_job import OperationKind, OperationStatus
from backend.app.models.quality_run import QualityRun
from backend.app.models.user import User, UserRole
from backend.app.schemas.operation_job import OperationJobCreatedResponse
from backend.app.services.operation_job_service import OperationJobService
from backend.app.services.operation_runner import run_quality_job

router = APIRouter(prefix="/quality", tags=["Qualidade"])
PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORT_TOKEN_PURPOSE = "coverage_report"
REPORT_TOKEN_TTL_SECONDS = 900


def _reports_dir() -> Path:
    configured = Path(settings.reports_dir)
    return configured if configured.is_absolute() else PROJECT_ROOT / configured


COVERAGE_XML = _reports_dir() / "coverage.xml"
COVERAGE_HTML = _reports_dir() / "coverage"
JUNIT_XML = _reports_dir() / "junit.xml"


@router.post(
    "/run",
    response_model=OperationJobCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_quality_run(
    background: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Executa a suíte de testes com cobertura em segundo plano."""
    from backend.app.models.operation_job import OperationJob

    active = (
        db.query(OperationJob.id)
        .filter(
            OperationJob.kind == OperationKind.QUALITY_RUN,
            OperationJob.status.in_([OperationStatus.PENDING, OperationStatus.RUNNING]),
        )
        .first()
    )
    if active is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma execução de testes em andamento.",
        )

    jobs = OperationJobService(db)
    job = jobs.create(
        kind=OperationKind.QUALITY_RUN,
        title="Execução dos testes com cobertura",
        user_id=current_user.id,
        payload={"reports_dir": str(_reports_dir())},
        step_key="queued",
        step_label="Aguardando início",
    )
    background.add_task(run_quality_job, job.id)
    return OperationJobCreatedResponse(job_id=job.id, status=job.status.value)


@router.get("/summary")
def get_quality_summary(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return real coverage data when a coverage XML report exists."""
    if not COVERAGE_XML.is_file():
        return {
            "available": False,
            "message": "Relatório de cobertura indisponível. Execute a suíte de testes.",
            "history": _quality_history(db),
        }

    try:
        root = ElementTree.parse(COVERAGE_XML).getroot()
        line_rate = float(root.attrib["line-rate"])
        lines_valid = int(root.attrib["lines-valid"])
        lines_covered = int(root.attrib["lines-covered"])
        generated_at = datetime.fromtimestamp(COVERAGE_XML.stat().st_mtime, tz=UTC)
    except (ElementTree.ParseError, KeyError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O relatório de cobertura existente está inválido.",
        ) from error

    html_report_available = (COVERAGE_HTML / "index.html").is_file()
    tests = _read_test_counts()
    summary = {
        "available": True,
        "coverage_percent": round(line_rate * 100, 2),
        "lines_valid": lines_valid,
        "lines_covered": lines_covered,
        "generated_at": generated_at.isoformat(),
        "html_report_available": html_report_available,
        "tests": tests,
    }
    _record_quality_run(
        db,
        generated_at=generated_at,
        coverage_percent=summary["coverage_percent"],
        lines_valid=lines_valid,
        lines_covered=lines_covered,
        tests=tests,
        html_report_available=html_report_available,
    )
    summary["history"] = _quality_history(db)
    return summary


def _read_test_counts() -> dict[str, int] | None:
    if not JUNIT_XML.is_file():
        return None
    try:
        tests_root = ElementTree.parse(JUNIT_XML).getroot()
        test_suites = tests_root.findall(".//testsuite")

        def count(attribute: str) -> int:
            if attribute in tests_root.attrib:
                return int(tests_root.attrib[attribute])
            return sum(int(suite.attrib.get(attribute, 0)) for suite in test_suites)

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


def _record_quality_run(
    db: Session,
    *,
    generated_at: datetime,
    coverage_percent: float,
    lines_valid: int,
    lines_covered: int,
    tests: dict[str, int] | None,
    html_report_available: bool,
) -> None:
    fingerprint = hashlib.sha256()
    fingerprint.update(str(COVERAGE_XML.stat().st_mtime_ns).encode())
    fingerprint.update(COVERAGE_XML.read_bytes())
    if JUNIT_XML.is_file():
        fingerprint.update(JUNIT_XML.read_bytes())
    run_key = fingerprint.hexdigest()
    if db.query(QualityRun.id).filter(QualityRun.run_key == run_key).first():
        return

    db.add(
        QualityRun(
            run_key=run_key,
            generated_at=generated_at,
            coverage_percent=coverage_percent,
            lines_valid=lines_valid,
            lines_covered=lines_covered,
            tests_total=tests["total"] if tests else None,
            tests_passed=tests["passed"] if tests else None,
            tests_failed=tests["failed"] if tests else None,
            tests_skipped=tests["skipped"] if tests else None,
            html_report_available=html_report_available,
            created_at=datetime.now(UTC),
        )
    )
    db.flush()


def _quality_history(db: Session) -> list[dict]:
    runs = (
        db.query(QualityRun)
        .order_by(QualityRun.generated_at.desc(), QualityRun.id.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "coverage_percent": run.coverage_percent,
            "lines_valid": run.lines_valid,
            "lines_covered": run.lines_covered,
            "generated_at": run.generated_at.isoformat(),
            "html_report_available": run.html_report_available,
            "tests": (
                {
                    "total": run.tests_total,
                    "passed": run.tests_passed,
                    "failed": run.tests_failed,
                    "skipped": run.tests_skipped,
                }
                if run.tests_total is not None
                else None
            ),
        }
        for run in runs
    ]


@router.get("/report/{asset_path:path}")
def get_coverage_report(
    asset_path: str,
    current_user: User = Depends(require_admin),
):
    """Serve files belonging to the generated HTML coverage report."""
    report_root = COVERAGE_HTML.resolve()
    requested_file = (report_root / asset_path).resolve()
    if report_root not in requested_file.parents or not requested_file.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado")
    return FileResponse(requested_file)
