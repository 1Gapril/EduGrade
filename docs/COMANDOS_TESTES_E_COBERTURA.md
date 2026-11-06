# Comandos de testes e cobertura — EduGrade

Guia único para executar testes unitários, gerar relatórios de cobertura (HTML,
XML e JUnit) e validar a meta de 80%.

> Todos os comandos devem ser executados na **raiz do projeto** (`EduGrade\`),
> com o ambiente virtual ativado.

---

## 1. Preparação (uma vez)

```cmd
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Linux/macOS:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Testes unitários (rápido, sem cobertura)

```cmd
pytest tests\unit -q --no-cov
```

Um arquivo específico:

```cmd
pytest tests\unit\test_operation_jobs.py -v
```

Um teste específico:

```cmd
pytest tests\unit\test_auth_service.py::test_login_success -vv
```

Parar no primeiro erro:

```cmd
pytest tests -q --no-cov -x
```

---

## 3. Suíte completa com cobertura (padrão do projeto)

O `pyproject.toml` já configura `--cov=backend/app`, relatório HTML em
`reports/coverage` e a meta de 80%:

```cmd
pytest
```

Saída esperada: todos os testes aprovados e a linha
`Required test coverage of 80% reached`, com o total de cobertura.

---

## 4. Relatórios completos (HTML + XML + JUnit)

```cmd
python -m pytest tests -q ^
  --cov=backend/app ^
  --cov-report=term-missing ^
  --cov-report=html:reports/coverage ^
  --cov-report=xml:reports/coverage.xml ^
  --junitxml=reports/junit.xml ^
  --cov-fail-under=80
```

Linux/macOS (mesma coisa, com `\`):

```bash
python -m pytest tests -q \
  --cov=backend/app \
  --cov-report=term-missing \
  --cov-report=html:reports/coverage \
  --cov-report=xml:reports/coverage.xml \
  --junitxml=reports/junit.xml \
  --cov-fail-under=80
```

Resultado:

| Arquivo | Para que serve |
|---|---|
| `reports/coverage/index.html` | relatório navegável por arquivo/linha |
| `reports/coverage.xml` | lido pelo painel `/admin/quality.html` |
| `reports/junit.xml` | contagem de testes aprovados/reprovados/ignorados |

Abrir o HTML no Windows:

```cmd
start reports\coverage\index.html
```

---

## 5. Cobertura por módulo

```cmd
:: Somente rotas
pytest --cov=backend/app/api --cov-report=term-missing --no-cov-on-fail

:: Somente serviços
pytest --cov=backend/app/services --cov-report=term-missing

:: Somente integrações (PDF, QR, OCR, armazenamento)
pytest --cov=backend/app/integrations --cov-report=term-missing

:: Um arquivo específico
pytest tests/unit/test_operation_jobs.py --cov=backend/app/services/operation_runner --cov-report=term-missing
```

---

## 6. Executar a cobertura pela interface (recomendado para a apresentação)

1. Entre como **administrador** (`admin` / `admin123`).
2. Abra **Painel administrativo → Qualidade** (`/admin/quality.html`).
3. Clique em **Executar testes agora**.
4. Acompanhe o progresso no painel global (etapas: preparação → execução →
   leitura dos relatórios).
5. Ao concluir, a página mostra cobertura, contagem de testes e o histórico.
6. Clique em **Abrir relatório HTML detalhado**.

Por baixo, a interface executa exatamente:

```
python -m pytest tests -q -o addopts= --cov=backend/app \
  --cov-report=xml:reports/coverage.xml \
  --cov-report=html:reports/coverage \
  --junitxml=reports/junit.xml --cov-fail-under=80
```

> A operação roda no servidor em segundo plano (limite de 30 minutos) e só pode
> ser iniciada por administradores. Não há execução simultânea duplicada.

---

## 7. Limpar caches antes de uma execução “limpa”

Windows (PowerShell):

```powershell
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Remove-Item .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item reports\coverage -Recurse -Force -ErrorAction SilentlyContinue
```

Linux/macOS:

```bash
find . -type d -name __pycache__ -exec rm -rf {} +
rm -rf .pytest_cache reports/coverage
```

> Não apague `edugrade.db` para “limpar” o sistema: use `python scripts\reset_db.py`,
> que faz backup antes de recriar os dados mínimos.

---

## 8. CI/CD (GitHub Actions)

O workflow `.github/workflows/ci.yml` executa em cada `push` e `pull request`:

```bash
python -m pytest tests/unit \
  --cov=backend.app \
  --cov-report=term-missing \
  --cov-report=xml:reports/coverage.xml \
  --junitxml=reports/junit.xml
```

e publica `reports/coverage.xml` + `reports/junit.xml` como artefatos
(`coverage-report`) por 7 dias.

---

## 9. Resultado atual (referência para o relatório)

| Métrica | Valor |
|---|---|
| Testes coletados | 262 |
| Aprovados | 262 |
| Reprovados | 0 |
| Cobertura global | 81,32% |
| Meta do projeto | 80% |
| Tempo aproximado | 4–5 minutos |

> Os números podem variar levemente conforme a máquina. Registre sempre o valor
> impresso na execução que você fez.

---

## 10. Problemas comuns

| Sintoma | Solução |
|---|---|
| `ModuleNotFoundError: No module named 'backend'` | rode na raiz do projeto; confirme `conftest.py` na raiz |
| `no such table` em testes | os testes usam banco em memória; verifique se não existe `DATABASE_URL` apontando para outro banco |
| Cobertura abaixo de 80% | o comando falha de propósito (`--cov-fail-under=80`); veja `--cov-report=term-missing` para os arquivos descobertos |
| `PermissionError` em `reports/` | a pasta precisa ser gravável; rode fora de diretórios sincronizados/OneDrive |
| Teste dependente de IA externa falhando | os testes unitários usam `MockProvider`; não exigem Ollama/FCC |
| Tesseract ausente | testes de OCR usam simulação; a aplicação cai para a camada de texto do PDF |
| Porta 8000 ocupada | `python -m uvicorn backend.app.main:app --port 8001` |

---

## 11. Comandos úteis de qualidade

```cmd
:: Lint
ruff check backend\app

:: Formatação
black backend\app

:: Tipagem
mypy backend\app
```

> Se `ruff`/`black`/`mypy` não estiverem instalados: `pip install ruff black mypy`.
