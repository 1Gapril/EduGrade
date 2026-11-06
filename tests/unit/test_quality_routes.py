from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.api.routes import quality
from backend.app.models.quality_run import QualityRun


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    QualityRun.__table__.create(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_quality_summary_returns_unavailable_without_coverage(monkeypatch, tmp_path, db):
    monkeypatch.setattr(quality, "COVERAGE_XML", tmp_path / "missing.xml")

    summary = quality.get_quality_summary(SimpleNamespace(), db)

    assert summary == {
        "available": False,
        "message": "Relatório de cobertura indisponível. Execute a suíte de testes.",
        "history": [],
    }


def test_quality_summary_reads_and_persists_coverage_report(monkeypatch, tmp_path, db):
    xml_path = tmp_path / "coverage.xml"
    xml_path.write_text(
        '<coverage line-rate="0.75" lines-valid="20" lines-covered="15"/>',
        encoding="utf-8",
    )
    report_dir = tmp_path / "coverage"
    report_dir.mkdir()
    (report_dir / "index.html").write_text("<html></html>", encoding="utf-8")
    junit_path = tmp_path / "junit.xml"
    junit_path.write_text(
        '<testsuites><testsuite tests="10" failures="2" errors="1" skipped="1"/></testsuites>',
        encoding="utf-8",
    )
    monkeypatch.setattr(quality, "COVERAGE_XML", xml_path)
    monkeypatch.setattr(quality, "COVERAGE_HTML", report_dir)
    monkeypatch.setattr(quality, "JUNIT_XML", junit_path)

    summary = quality.get_quality_summary(SimpleNamespace(), db)

    assert summary["available"]
    assert summary["coverage_percent"] == 75
    assert summary["lines_valid"] == 20
    assert summary["lines_covered"] == 15
    assert summary["html_report_available"]
    assert summary["tests"] == {
        "total": 10,
        "passed": 6,
        "failed": 3,
        "skipped": 1,
    }
    assert summary["generated_at"]
    assert len(summary["history"]) == 1
    assert summary["history"][0]["coverage_percent"] == 75

    repeated_summary = quality.get_quality_summary(SimpleNamespace(), db)
    assert len(repeated_summary["history"]) == 1
    assert db.query(QualityRun).count() == 1


def test_quality_summary_returns_persisted_history_without_current_report(
    monkeypatch,
    tmp_path,
    db,
):
    generated_at = datetime.now(UTC)
    db.add(
        QualityRun(
            run_key="stored-run",
            generated_at=generated_at,
            coverage_percent=80,
            lines_valid=100,
            lines_covered=80,
            tests_total=4,
            tests_passed=4,
            tests_failed=0,
            tests_skipped=0,
            html_report_available=False,
            created_at=generated_at,
        )
    )
    db.commit()
    monkeypatch.setattr(quality, "COVERAGE_XML", tmp_path / "missing.xml")

    summary = quality.get_quality_summary(SimpleNamespace(), db)

    assert not summary["available"]
    assert len(summary["history"]) == 1
    assert summary["history"][0]["coverage_percent"] == 80
    assert summary["history"][0]["tests"]["passed"] == 4


def test_quality_summary_reports_corrupt_coverage(monkeypatch, tmp_path, db):
    xml_path = tmp_path / "coverage.xml"
    xml_path.write_text("<coverage", encoding="utf-8")
    monkeypatch.setattr(quality, "COVERAGE_XML", xml_path)

    with pytest.raises(HTTPException) as error:
        quality.get_quality_summary(SimpleNamespace(), db)

    assert error.value.status_code == 503


def test_quality_report_rejects_path_traversal(monkeypatch, tmp_path):
    report_dir = tmp_path / "coverage"
    report_dir.mkdir()
    monkeypatch.setattr(quality, "COVERAGE_HTML", report_dir)

    with pytest.raises(HTTPException) as error:
        quality.get_coverage_report("../secret.txt", SimpleNamespace())

    assert error.value.status_code == 404


def test_quality_report_serves_generated_file(monkeypatch, tmp_path):
    report_dir = tmp_path / "coverage"
    report_dir.mkdir()
    report_file = report_dir / "index.html"
    report_file.write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(quality, "COVERAGE_HTML", report_dir)

    response = quality.get_coverage_report("index.html", SimpleNamespace())

    assert isinstance(response, quality.FileResponse)
    assert Path(response.path) == report_file
