"""Script utilitário para popular os dados iniciais do EduGrade."""

import sys
from pathlib import Path

# Adiciona raiz do projeto ao path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.database import SessionLocal, init_db
from backend.app.core.seed import SEED_ACCOUNTS, seed_database


def main():
    print("Inicializando tabelas do banco de dados...")
    init_db()

    print("Verificando/populando dados iniciais...")
    db = SessionLocal()
    try:
        created = seed_database(db)
        if created:
            print("Sucesso! Contas de acesso criadas:")
            for account in SEED_ACCOUNTS:
                print(
                    f" - {account['role']:7s} usuário: {account['username']:12s} "
                    f"senha: {account['password']:9s} e-mail: {account['email']}"
                )
            print("\nConsulte CREDENCIAIS.md para a lista completa.")
        else:
            print("O banco de dados já continha os dados iniciais. Nenhuma alteração feita.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
