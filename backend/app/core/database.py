"""Configuração do banco de dados EduGrade."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.core.config import settings


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""
    pass


# Engine com configurações específicas para SQLite
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    pool_pre_ping=True,
    echo=settings.debug,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Habilitar foreign keys no SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Habilita foreign keys no SQLite."""
    if "sqlite" in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """Dependency para obter sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager para sessão do banco (uso fora de requests)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Inicializa o banco de dados criando todas as tabelas."""
    # Import models to register them
    from backend.app.models import (  # noqa: F401
        academic,
        access_request,
        admin_settings,
        ai_correction,
        audit,
        exam,
        grading_batch,
        quality_run,
        user,
    )

    Base.metadata.create_all(bind=engine)
    _ensure_exam_submission_batch_column(engine)


def _ensure_exam_submission_batch_column(bind: Engine) -> None:
    """Atualiza bancos existentes com a associação opcional a lotes de correção."""
    from backend.app.models.exam import ExamSubmission

    table = ExamSubmission.__table__
    column = table.c.batch_id
    with bind.begin() as connection:
        inspector = inspect(connection)
        if not inspector.has_table(table.name):
            return

        column_names = {item["name"] for item in inspector.get_columns(table.name)}
        if column.name not in column_names:
            foreign_key = next(iter(column.foreign_keys))
            preparer = connection.dialect.identifier_preparer
            table_name = preparer.quote(table.name)
            column_name = preparer.quote(column.name)
            referenced_table = preparer.quote(foreign_key.column.table.name)
            referenced_column = preparer.quote(foreign_key.column.name)
            column_type = column.type.compile(dialect=connection.dialect)
            on_delete = f" ON DELETE {foreign_key.ondelete}" if foreign_key.ondelete else ""
            connection.exec_driver_sql(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} "
                f"REFERENCES {referenced_table} ({referenced_column}){on_delete}"
            )

        index_name = f"ix_{table.name}_{column.name}"
        index = next(
            (candidate for candidate in table.indexes if candidate.name == index_name),
            None,
        )
        if index is not None:
            index.create(bind=connection, checkfirst=True)


def drop_db() -> None:
    """Remove todas as tabelas (apenas para testes)."""
    Base.metadata.drop_all(bind=engine)
