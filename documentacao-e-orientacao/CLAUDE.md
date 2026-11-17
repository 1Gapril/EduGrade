# EduGrade - Regras de Arquitetura e Desenvolvimento

## 🏗️ Arquitetura Estrita: Separação Backend / Frontend

### Backend (`backend/`) - **EXCLUSIVO** para:
- ✅ Toda regra de negócio
- ✅ Autenticação e autorização
- ✅ Banco de dados (models, migrations, repositories)
- ✅ OCR e processamento de imagens
- ✅ Chamadas de IA / LLMs
- ✅ Serviços de domínio
- ✅ API routes (FastAPI)
- ✅ Schemas de validação (Pydantic)
- ✅ Jobs em background (Celery, etc.)

### Frontend (`frontend/`) - **APENAS** para:
- ✅ HTML, CSS, JS Vanilla (interface do usuário)
- ✅ Chamadas `fetch()` para a API do backend
- ✅ Renderização de dados recebidos da API
- ✅ Validação de formulários no lado do cliente (UX apenas)
- ❌ **NUNCA** lógica de negócio
- ❌ **NUNCA** chaves de API, secrets, tokens
- ❌ **NUNCA** conexão direta com banco de dados
- ❌ **NUNCA** processamento de OCR/IA

---

## 🧪 Testes Obrigatórios

**SEMPRE** rodar `pytest` após alterar:
- Qualquer rota da API (`backend/app/api/`)
- Qualquer serviço (`backend/app/services/`)
- Qualquer modelo (`backend/app/models/`)
- Qualquer repository (`backend/app/repositories/`)

```bash
cd backend && pytest -v
```

---

## 🌿 Git Workflow

Antes de commits ou refatorações grandes:

1. **Criar branch nova** com padrão:
   - `feat/<descricao>` - nova funcionalidade
   - `fix/<descricao>` - correção de bug
   - `refactor/<descricao>` - refatoração
   - `docs/<descricao>` - documentação

2. **Listar arquivos modificados** antes do commit:
   ```bash
   git status
   git diff --name-only
   ```

3. **Exemplo para separação backend/frontend:**
   ```bash
   git checkout -b feat/separacao-back-front
   ```

---

## 📁 Estrutura do Projeto

```
EduGrade/
├── backend/                 # FastAPI - TODA lógica de negócio
│   ├── app/
│   │   ├── api/            # Rotas da API
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Data access
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── integrations/   # OCR, IA, external APIs
│   ├── tests/              # Testes do backend
│   └── alembic/            # Migrations
├── frontend/               # Vanilla JS - APENAS interface
│   ├── admin/              # Páginas admin
│   ├── aluno/              # Páginas aluno
│   ├── professor/          # Páginas professor
│   ├── css/                # Estilos
│   ├── js/                 # JavaScript (apenas fetch para API)
│   └── *.html              # Páginas
├── tests/                  # Testes de integração/E2E
├── .claude/skills/         # Skills de desenvolvimento
└── CLAUDE.md              # Este arquivo
```

---

## 🚫 Regras de Ouro

| ❌ NUNCA FAZER | ✅ SEMPRE FAZER |
|---|---|
| Colocar lógica de negócio no frontend | Manter backend como source of truth |
| Hardcodear URLs da API no frontend | Usar variável de ambiente `API_BASE_URL` |
| Commitar secrets/chaves no git | Usar `.env` (nunca commitado) |
| Pular testes após mudar backend | Rodar `pytest` antes de commit |
| Fazer push direto na `develop`/`main` | Usar branches + PR |

---

## 🔧 Comandos Úteis

```bash
# Backend - rodar servidor
cd backend && uvicorn app.main:app --reload

# Backend - rodar testes
cd backend && pytest -v --cov=app

# Backend - criar migration
cd backend && alembic revision --autogenerate -m "descricao"

# Backend - aplicar migrations
cd backend && alembic upgrade head

# Frontend - servir estático (dev)
cd frontend && python -m http.server 8080
```

---

## 📋 Checklist de Auditoria (Backend/Frontend)

Antes de qualquer PR, verificar:

- [ ] Nenhum `import` de `backend.*` no frontend
- [ ] Nenhum `fetch()` para banco de dados direto
- [ ] Nenhuma chave secreta no frontend
- [ ] Todas as rotas da API têm testes
- [ ] `pytest` passa 100%
- [ ] Branch nomeada corretamente
- [ ] Arquivos modificados listados no PR