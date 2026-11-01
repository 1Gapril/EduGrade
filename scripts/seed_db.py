"""Script utilitário para popular dados de demonstração no EduGrade."""

import sys
from pathlib import Path

# Adiciona raiz do projeto ao path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.database import SessionLocal, init_db
from backend.app.core.seed import seed_database


def main():
    print("Inicializando tabelas do banco de dados...")
    init_db()
    
    print("Verificando/populando dados iniciais...")
    db = SessionLocal()
    try:
        created = seed_database(db)
        if created:
            print("Sucesso! Usuários de demonstração criados:")
            print(" - Admin:     admin / admin123 (email: admin@edugrade.local)")
            print(" - Professor: professor / prof123 (email: professor@edugrade.local)")
            print(" - Aluno:     aluno / aluno123 (email: aluno@edugrade.local)")
        else:
            print("O banco de dados já continha dados. Nenhuma alteração feita.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

