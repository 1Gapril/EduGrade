# Roteiro de Apresentação - A3
## EduGrade — Sistema de Gestão e Desempenho Acadêmico com IA

### 1. Capa
* **Projeto:** EduGrade
* **Função DevOps/Documentação:** Gabriel Ferreira — RA 325140970
* **Integrantes do Grupo:**
  * Gabriel Ferreira — RA 325140970 — (GitHub, Versionamento, Documentação, DevOps e Apresentação)
  * Fernando Almeida — RA 326132695 — (Desenvolvimento Backend, Frontend e Testes)
  * Lucas Henrique — RA 325131396 — (QA, Testes, Validação Funcional e Documentação Técnica)
  * Caio Duraes — RA 325132875 — (IA/OCR, Modelos de Linguagem, Correção Assistida e Integrações)

### 2. Problema
* Dificuldade na gestão de desempenho acadêmico, aplicação e correção de provas em larga escala de forma ágil e justa.

### 3. Objetivo
* Desenvolver uma plataforma integrada que automatize processos de avaliação e forneça análise preditiva de desempenho de alunos utilizando Inteligência Artificial.

### 4. ODS 4 - Educação de Qualidade
* Como o EduGrade se alinha: Garantir o acesso à educação inclusiva, promovendo ferramentas tecnológicas que otimizam o tempo do docente e geram feedbacks personalizados para a evolução do aluno.

### 5. Público-alvo
* Instituições de ensino de grande porte, professores, coordenadores pedagógicos e estudantes de graduação/pós-graduação.

### 6. Arquitetura
* **Backend:** Python / FastAPI
* **Frontend:** HTML, CSS, JavaScript (Vanilla)
* **Integração:** Scripts de automação e processamento de dados.
* **Banco de Dados:** SQLite (desenvolvimento) / PostgreSQL (produção) com Alembic migrations
* **IA:** OCR (Tesseract/pymupdf) + LLMs (Ollama/FCC/Claude) para correção assistida

### 7. Banco de Dados
* **Desenvolvimento:** SQLite (`sqlite:///./edugrade.db`) — arquivo local, zero config.
* **Produção:** PostgreSQL — configurável via variável de ambiente `DATABASE_URL`.
* **Migrations:** Alembic — versionamento de schema, `alembic revision --autogenerate` + `alembic upgrade head`.
* **Modelo ER:** Principais entidades — Users, Students, Courses, Classes, Exams, Submissions, GradingBatches, AIProviderConfigs, AuditLogs.

### 8. Funcionalidades do Aluno
* Visualização de dashboard acadêmico integrado.
* Consulta de notas e relatórios de desempenho gerados pela IA (predição de dificuldades).

### 9. Funcionalidades do Professor
* Cadastro e gestão de turmas, cursos e períodos letivos.
* Criação padronizada de avaliações (objetivas e discursivas).
* Visualização de métricas consolidadas de desempenho da turma.

### 10. Criação e Impressão das Provas
* Módulo de geração de exames em formato padronizado (PDF) com suporte a exportação e impressão.
* Gabarito estruturado para correção automática de questões objetivas.

### 11. Correção Assistida por IA
* **OCR:** Leitura de imagens/documentos digitalizados (Tesseract + pymupdf) — extração de texto e respostas manuscritas.
* **LLM:** Modelos de linguagem (Ollama local / FCC / Claude) para interpretação e atribuição preliminar de notas a questões discursivas.
* **Fluxo:** Upload → OCR → IA sugere nota → Professor revisa/confirma → Nota final registrada.

### 12. Segurança
* Proteção de rotas com JWT (HS256/Argon2) + refresh tokens.
* Chaves de ambiente criptografadas (`.env` + `credential_encryption_key`).
* Controle de acesso baseado em funções (RBAC): Admin, Professor, Aluno.
* Auditoria de ações sensíveis (logs imutáveis).

### 13. Testes
* **37 testes unitários** em `tests/unit/` cobrindo:
  * Regras de negócio acadêmicas (turmas, matrículas, períodos)
  * Autorização e acesso a arquivos privados
  * Factory de provedores de IA (mock, Ollama, FCC)
  * Compatibilidade de schema de banco (migrations)
  * Importação de PDF/OCR e mapeamento de questões
* Ferramentas: `pytest`, `pytest-asyncio`, `pytest-mock`, `faker`.

### 14. Cobertura
* **Meta:** ≥ 80% (configurado no `pyproject.toml` via `--cov-fail-under=80`).
* **CI atual:** 55% threshold realista (enquanto suite de testes expande).
* **Relatórios:** HTML em `reports/coverage/` + XML artifact no GitHub Actions.
* **Comando local:** `pytest --cov=backend/app --cov-report=html`

### 15. CI/CD
* **GitHub Actions** (`.github/workflows/ci.yml`) — executa a cada push/PR em `main` e `develop`:
  1. **Lint** — `ruff check backend/app tests` (falha em erros E/F/W)
  2. **Test** — `pytest` + coverage ≥ 55% + upload artifact
  3. **Build** — Verifica imports (`import app`) e sintaxe
  4. **Notify** — Agrega status; falha se qualquer job falhar
* **Branches protegidas:** `main` via PR + reviews; `develop` integração contínua.

### 16. Resultados
* Otimização significativa no tempo de correção de avaliações (manual → assistida por IA).
* Relatórios precisos sobre pontos de dificuldade da turma por disciplina/assunto.
* Feedback personalizado por aluno com predição de desempenho futuro.
* Pipeline automatizado garantindo qualidade a cada integração.

### 17. Conclusão
* O EduGrade moderniza a gestão educacional unindo automação DevOps e IA para focar no que mais importa: o aprendizado real do estudante.
* Próximos passos: expandir cobertura de testes, suportar mais provedores de IA, deploy em nuvem (Docker/K8s).

---

### 📋 Entregas por Integrante (para slide final)

| Integrante | Entregas Principais |
|------------|---------------------|
| **Gabriel Ferreira** | Repositório organizado (GitFlow), README completo, Branches + Commits padronizados, Pipeline CI/CD, Roteiro A3, Slides, Vídeo pitch |
| **Fernando Almeida** | Backend (FastAPI, SQLAlchemy, Alembic), Frontend (HTML/CSS/JS), Testes unitários, API endpoints, Autenticação/Autorização |
| **Lucas Henrique** | QA e Validação Funcional, Testes de integração, Documentação técnica (SETUP, CHECKLIST, REGRAS), Checklist de entrega |
| **Caio Duraes** | IA/OCR (Tesseract, pymupdf), Modelos de linguagem (Ollama, FCC), Correção assistida, Integrações externas, Processamento de PDF |