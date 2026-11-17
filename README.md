# EduGrade — Sistema de Gestão e Desempenho Acadêmico com IA

Plataforma completa para gestão acadêmica, aplicação de provas e correção
automatizada com Inteligência Artificial.

---

## 📦 Repositórios Separados (Monorepo Dividido)

> **Este repositório original agora serve apenas como referência histórica.**  
> O projeto foi dividido em dois repositórios independentes para deploy separado:

| Repositório | Descrição | Tech Stack |
|-------------|-----------|------------|
| **[EduGrade-backend](https://github.com/vivoeasy100/EduGrade-backend)** | API REST, Lógica de Negócio, OCR, IA, Banco de Dados | FastAPI, SQLAlchemy, PostgreSQL/SQLite, Tesseract, OpenAI |
| **[EduGrade-frontend](https://github.com/vivoeasy100/EduGrade-frontend)** | Interface do Usuário (HTML, CSS, JS Vanilla) | ES Modules, Fetch API, Feather Icons |

---

## 🎯 Objetivo

Otimizar o tempo do corpo docente na criação, aplicação e correção de
avaliações, além de fornecer relatórios analíticos precisos sobre os pontos
de dificuldade e evolução dos estudantes por meio de IA.

---

## 🛠️ Tecnologias Utilizadas

### Backend (Repo: EduGrade-backend)
* **Python 3.11+** com **FastAPI** — Framework web assíncrono
* **SQLAlchemy 2.0** — ORM assíncrono
* **Alembic** — Migrations de banco de dados
* **Pydantic v2** — Validação de dados
* **Tesseract OCR** — Reconhecimento óptico de caracteres
* **OpenAI API** — Correção automática com IA
* **pytest** — Testes automatizados (cobertura ≥ 80%)

### Frontend (Repo: EduGrade-frontend)
* **HTML5 + CSS3 + JavaScript Vanilla (ES Modules)** — Sem frameworks
* **Fetch API** — Comunicação com Backend
* **Feather Icons** — Ícones via CDN
* **Variáveis de ambiente** — `API_BASE_URL` configurável

---

## 🚀 Funcionalidades Principais

* **Portal do Aluno:** Dashboard acadêmico, consulta de notas, materiais, provas
* **Portal do Professor:** Gerenciamento de turmas, criação de avaliações, lançamento de notas, revisão de correções IA
* **Painel Admin:** Usuários, cursos/disciplinas/turmas/períodos, atribuições, configurações de IA/OCR, auditoria
* **Correção Assistida:** OCR de imagens/documentos + IA para questões discursivas e objetivas
* **Importação de Provas:** PDF/Imagem → OCR → Estruturação automática
* **Jobs Assíncronos:** Processamento em background (Celery-ready)

---

## 📂 Estrutura Atual (Histórica)

```text
EduGrade/                          ← Monorepo original (apenas referência)
├── .github/workflows/             # CI/CD antigo (monorepo)
├── backend/ → [MOVIDO]            # Agora em: github.com/vivoeasy100/EduGrade-backend
├── frontend/ → [MOVIDO]           # Agora em: github.com/vivoeasy100/EduGrade-frontend
├── documentacao-e-orientacao/     # 📚 TODA DOCUMENTAÇÃO (.md, .pptx, imagens)
│   ├── QA/                        # Relatórios QA (admin, aluno, professor, IA, etc.)
│   ├── auditoria/                 # Relatórios de auditoria técnica
│   └── evidencias/                # Capturas de tela (QA)
├── scripts/                       # Scripts auxiliares
├── tests/                         # Testes de integração/E2E
├── .env.example                   # Template de variáveis (monorepo)
├── requirements.txt               # Dependências Python (monorepo)
├── pyproject.toml                 # Configuração do projeto
└── README.md                      # Este arquivo
```

---

## ⚡ Início Rápido (Novos Repositórios)

### 1. Backend
```bash
git clone https://github.com/vivoeasy100/EduGrade-backend.git
cd EduGrade-backend

# Configurar
cp .env.example .env
# Edite .env com: DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, CORS_ORIGINS, etc.

# Instalar e rodar
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
# API em http://localhost:8000/docs
```

### 2. Frontend
```bash
git clone https://github.com/vivoeasy100/EduGrade-frontend.git
cd EduGrade-frontend

# Configurar
cp .env.example .env
# Edite .env: API_BASE_URL=http://localhost:8000/api/v1

# Rodar (arquivos estáticos)
python -m http.server 8080
# App em http://localhost:8080
```

---

## 🔐 Contas de Demonstração

Após rodar o backend com `alembic upgrade head` (roda o seed):

| Perfil | Usuário | Senha |
|--------|---------|-------|
| Administrador | `admin` / `admin2` | `admin123` |
| Professor | `professor` / `professor2` | `prof123` |
| Aluno | `aluno` / `aluno2` | `aluno123` |

Lista completa em `CREDENCIAIS.md` (neste repo) ou no README de cada repo.

---

## 🧪 Testes

### Backend
```bash
cd EduGrade-backend
pytest --cov=app --cov-fail-under=80 -v
# Cobertura atual: 80.07% (265 testes passando)
```

### Frontend
```bash
cd EduGrade-frontend
# CI valida: HTML, JS syntax, imports de config.js
```

---

## 📚 Documentação Adicional (Neste Repo)

> **Toda documentação foi movida para a pasta [`documentacao-e-orientacao/`](documentacao-e-orientacao/)**

| Documento | Descrição |
|-----------|-----------|
| [SETUP.md](documentacao-e-orientacao/SETUP.md) | Guia completo de instalação e configuração |
| [CREDENCIAIS.md](documentacao-e-orientacao/CREDENCIAIS.md) | Usuários e senhas das contas de demonstração |
| [PROGRESSO_GLOBAL.md](documentacao-e-orientacao/PROGRESSO_GLOBAL.md) | Barra global de progresso: uploads, importações e IA |
| [COMANDOS_TESTES_E_COBERTURA.md](documentacao-e-orientacao/COMANDOS_TESTES_E_COBERTURA.md) | Comandos de testes unitários e cobertura |
| [ROTEIRO_APRESENTACAO_COMPLETO.md](documentacao-e-orientacao/ROTEIRO_APRESENTACAO_COMPLETO.md) | Roteiro de apresentação (tecnologias, telas, Git, testes) |
| [como_rodar.md](documentacao-e-orientacao/como_rodar.md) | Passo a passo para rodar no CMD |
| [INSTALAR_OCR_WINDOWS.md](documentacao-e-orientacao/INSTALAR_OCR_WINDOWS.md) | Configuração do OCR no Windows |
| [ROTEIRO_APRESENTACAO_A3.md](documentacao-e-orientacao/ROTEIRO_APRESENTACAO_A3.md) | Roteiro estruturado da apresentação acadêmica |
| [CLAUDE.md](documentacao-e-orientacao/CLAUDE.md) | Regras de arquitetura backend/frontend para IA |
| [RELATORIO_NOTURNO.md](documentacao-e-orientacao/RELATORIO_NOTURNO.md) | Relatório de auditoria e cobertura de testes |
| [GUIA OPERACIONAL](documentacao-e-orientacao/GUIA_OPERACIONAL.md) | Guia operacional completo |
| [REGRAS_DE_NEGOCIO.md](documentacao-e-orientacao/REGRAS_DE_NEGOCIO.md) | Regras de negócio do sistema |
| [REQUISITOS_FUNCIONAIS.md](documentacao-e-orientacao/REQUISITOS_FUNCIONAIS.md) | Requisitos funcionais detalhados |
| [DOCUMENTO_ENTREGA_A3.md](documentacao-e-orientacao/DOCUMENTO_ENTREGA_A3.md) | Documento de entrega formato A3 |
| [INTEGRACAO_FCC.md](documentacao-e-orientacao/INTEGRACAO_FCC.md) | Integração com FCC (Claude Code) |
| [INTEGRACAO_NVIDIA_NIM.md](documentacao-e-orientacao/INTEGRACAO_NVIDIA_NIM.md) | Integração com NVIDIA NIM |
| [CONFIGURACOES_CENTRAL.md](documentacao-e-orientacao/CONFIGURACOES_CENTRAL.md) | Configurações centrais do sistema |
| [SEGURANCA_CREDENCIAIS.md](documentacao-e-orientacao/SEGURANCA_CREDENCIAIS.md) | Segurança de credenciais |
| [REGISTRO_PROBLEMAS.md](documentacao-e-orientacao/REGISTRO_PROBLEMAS.md) | Registro de problemas conhecidos |
| [CHECKLIST_VALIDACAO_FUNCIONAL.md](documentacao-e-orientacao/CHECKLIST_VALIDACAO_FUNCIONAL.md) | Checklist de validação funcional |
| [guia_completo.md](documentacao-e-orientacao/guia_completo.md) | Guia completo do projeto |
| [prompt.md](documentacao-e-orientacao/prompt.md) | Prompts utilizados |
| [auditoria2.md](documentacao-e-orientacao/auditoria2.md) | Auditoria adicional |
| **Pasta QA/** | Relatórios de QA por perfil (admin, aluno, professor, IA, segurança, etc.) |
| **Pasta auditoria/** | Relatórios de auditoria técnica |

---

## 👥 Integrantes da Equipe

- **Gabriel Ferreira** — RA 325140970 — GitHub, Versionamento, Documentação, DevOps, Apresentação
- **Fernando Almeida** — RA 326132695 — Desenvolvimento Backend, Frontend, Testes
- **Lucas Henrique** — RA 325131396 — QA, Testes, Validação Funcional, Documentação Técnica
- **Caio Durães** — RA 325132875 — IA/OCR, Modelos de Linguagem, Correção Assistida, Integrações

---

## 🔗 Links Úteis

- **Backend Repo:** https://github.com/vivoeasy100/EduGrade-backend
- **Frontend Repo:** https://github.com/vivoeasy100/EduGrade-frontend
- **Backend Docs (Swagger):** `http://localhost:8000/docs` (local)
- **Frontend App:** `http://localhost:8080` (local)

---

## ⚠️ Nota Importante

**Este repositório não será mais atualizado ativamente.**  
Todas as novas features, correções e releases devem ser feitas nos repositórios separados:

- **Backend:** `git push origin main` em `vivoeasy100/EduGrade-backend`
- **Frontend:** `git push origin main` em `vivoeasy100/EduGrade-frontend`

O CI/CD, issues, PRs e deployments agora acontecem independentemente em cada repo.