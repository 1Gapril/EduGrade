import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.core import database


def _session_factory():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE records (value TEXT NOT NULL)"))
    return engine, sessionmaker(bind=engine, autocommit=False, autoflush=False)


def test_get_db_commits_and_closes_after_success(monkeypatch):
    engine, local_session = _session_factory()
    monkeypatch.setattr(database, "SessionLocal", local_session)

    dependency = database.get_db()
    session = next(dependency)
    session.execute(text("INSERT INTO records (value) VALUES ('saved')"))
    with pytest.raises(StopIteration):
        next(dependency)

    with local_session() as verification_session:
        assert verification_session.execute(text("SELECT value FROM records")).scalar_one() == "saved"
    engine.dispose()


def test_get_db_rolls_back_and_closes_after_error(monkeypatch):
    engine, local_session = _session_factory()
    monkeypatch.setattr(database, "SessionLocal", local_session)

    dependency = database.get_db()
    session = next(dependency)
    session.execute(text("INSERT INTO records (value) VALUES ('rolled back')"))
    with pytest.raises(RuntimeError, match="request failed"):
        dependency.throw(RuntimeError("request failed"))

    with local_session() as verification_session:
        assert verification_session.execute(text("SELECT COUNT(*) FROM records")).scalar_one() == 0
    engine.dispose()
