"""Alembic environment configuration."""

from logging.config import fileConfig
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy import Numeric, Uuid, engine_from_config, pool
from alembic import context

# Importa configurações e modelos
from backend.app.core.config import settings
from backend.app.core.database import Base
from backend.app.models import (  # noqa: F401
    user, academic, exam, ai_correction, audit, grading_batch
)

# Configuração do Alembic
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configuração de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata alvo para autogenerate
target_metadata = Base.metadata


def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    if (
        context.dialect.name == "sqlite"
        and isinstance(inspected_type, Numeric)
        and isinstance(metadata_type, Uuid)
    ):
        return False
    return None


def run_migrations_offline() -> None:
    """Executa migrações em modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_server_default=True,
        compare_type=compare_type,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações em modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=compare_type,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()