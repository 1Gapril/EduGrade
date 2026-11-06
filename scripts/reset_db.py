"""Recria o banco do EduGrade com apenas os dados necessarios para operar.

O script faz backup do banco SQLite antes de limpar, recria todas as tabelas e
executa o seed com duas contas para cada perfil (administrador, professor e
aluno).

Uso:
    python scripts/reset_db.py            # pede confirmacao
    python scripts/reset_db.py --yes      # sem confirmacao
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.engine import make_url  # noqa: E402

from backend.app.core.config import settings  # noqa: E402
from backend.app.core.database import Base, SessionLocal, engine, init_db  # noqa: E402
from backend.app.core.seed import SEED_ACCOUNTS, seed_database  # noqa: E402


def _resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path


def _sqlite_database_path() -> Path | None:
    url = make_url(settings.database_url)
    if url.get_backend_name() != "sqlite" or not url.database:
        return None
    return _resolve_path(url.database)


def backup_database() -> Path | None:
    """Copia o banco SQLite atual para a pasta de backups."""
    database_path = _sqlite_database_path()
    if database_path is None or not database_path.is_file():
        return None

    backup_dir = _resolve_path(settings.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    suffix = time.strftime("%Y%m%d-%H%M%S")
    target = backup_dir / f"edugrade-antes-da-limpeza-{suffix}.db"
    shutil.copy2(database_path, target)
    return target


def reset_database() -> bool:
    """Remove todos os dados e recria a estrutura minima."""
    database_path = _sqlite_database_path()
    if database_path is not None:
        engine.dispose()
        for candidate in (database_path, Path(f"{database_path}-wal"), Path(f"{database_path}-shm")):
            candidate.unlink(missing_ok=True)
    else:  # pragma: no cover - depende do banco configurado
        Base.metadata.drop_all(bind=engine)

    init_db()
    db = SessionLocal()
    try:
        return seed_database(db)
    finally:
        db.close()


def print_accounts() -> None:
    print("\nContas criadas:")
    for account in SEED_ACCOUNTS:
        print(
            f" - {account['role']:7s} usuário: {account['username']:12s} "
            f"senha: {account['password']:9s} e-mail: {account['email']}"
        )
    print("\nAs mesmas credenciais estão documentadas em CREDENCIAIS.md.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yes", action="store_true", help="Não pede confirmação")
    args = parser.parse_args()

    database_path = _sqlite_database_path()
    print(f"Banco configurado: {database_path or settings.database_url}")

    if not args.yes:
        answer = input(
            "Isso apaga TODOS os dados academicos existentes. Deseja continuar? [s/N] "
        ).strip().lower()
        if answer not in {"s", "sim", "y", "yes"}:
            print("Operação cancelada.")
            return 1

    backup = backup_database()
    if backup is not None:
        print(f"Backup criado em: {backup}")
    else:
        print("Nenhum backup foi necessário (banco inexistente).")

    created = reset_database()
    if not created:
        print("O banco já possuía os dados iniciais; nada foi alterado.")
        return 0

    print("Banco limpo e recriado com a estrutura minima do EduGrade.")
    print_accounts()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
