from sqlalchemy import create_engine, inspect

from backend.app.core.database import _ensure_exam_submission_batch_column


def test_legacy_exam_submissions_table_gets_optional_batch_column():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "CREATE TABLE grading_batches (id UUID PRIMARY KEY)"
            )
            connection.exec_driver_sql(
                "CREATE TABLE exam_submissions (id UUID PRIMARY KEY)"
            )
            connection.exec_driver_sql(
                "INSERT INTO exam_submissions (id) VALUES ('existing-submission')"
            )

        _ensure_exam_submission_batch_column(engine)
        _ensure_exam_submission_batch_column(engine)

        inspector = inspect(engine)
        columns = {column["name"] for column in inspector.get_columns("exam_submissions")}
        indexes = {
            index["name"] for index in inspector.get_indexes("exam_submissions")
        }
        with engine.connect() as connection:
            submission = connection.exec_driver_sql(
                "SELECT batch_id FROM exam_submissions WHERE id = 'existing-submission'"
            ).one()
            foreign_keys = connection.exec_driver_sql(
                "PRAGMA foreign_key_list(exam_submissions)"
            ).all()

        assert "batch_id" in columns
        assert "ix_exam_submissions_batch_id" in indexes
        assert submission.batch_id is None
        assert any(row[2] == "grading_batches" for row in foreign_keys)
    finally:
        engine.dispose()
