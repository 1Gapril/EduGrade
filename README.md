# 🎓 EduGrade — Sistema de Gestão e Desempenho Acadêmico com IA

> **Plataforma completa para gestão acadêmica, aplicação de provas e correção automatizada com Inteligência Artificial**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://sqlalchemy.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.5+-red.svg)](https://pydantic.dev)
[![Licença](https://img.shields.io/badge/Licença-MIT-yellow.svg)](LICENSE)

---

## 📖 Visão Geral

O **EduGrade** é uma plataforma full-stack para instituições de ensino que combina:

- **Gestão Acadêmica Completa**: Cursos, disciplinas, turmas, matrículas, períodos letivos
- **Banco de Provas**: Criação, versionamento, gabaritos, rubricas, impressão com QR Codes
- **Correção por IA**: Processamento assíncrono de provas digitalizadas com OCR + LLM
- **Processamento em Lote (ADENDO OFICIAL)**: Digitalização em lote com identificação automática de alunos (RA/matrícula), agrupamento inteligente de páginas e correção com revisão obrigatória do professor

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        EduGrade                                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Frontend      │    Backend      │     Integrações             │
│   (HTML/JS)     │   (FastAPI)     │                             │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ • Aluno         │ • Auth/JWT      │ • Gerador de PDF (ReportLab)│
│ • Professor     │ • RBAC          │ • Gerador de QR Code        │
│ • Admin         │ • API REST      │ • OCR (Tesseract/PaddleOCR) │
│ • Correção Lote │ • Tarefas Async │ • Provedores de IA (Ollama, │
│                 │ • WebSockets    │   OpenAI, Anthropic, Mock)  │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌─────────────┐       ┌─────────────┐
            │ PostgreSQL  │       │   Redis     │
            │  (Dados)    │       │  (Cache/    │
            │             │       │   Filas)    │
            └─────────────┘       └─────────────┘
```

---

## ✨ Funcionalidades Principais

### 👥 Gestão de Usuários
- **Alunos**: RA, matrícula, curso, turma, foto
- **Professores**: Matrícula funcional, disciplinas, turmas
- **Administradores**: Gestão completa do sistema
- **Autenticação**: Tokens JWT de acesso e atualização, 2FA opcional

### 📚 Gestão Acadêmica
- Cursos, disciplinas, pré-requisitos
- Turmas com horários, salas, professores
- Períodos letivos (planejado, ativo, fechado, arquivado)
- Matrículas com validação de regras acadêmicas
- Avaliações, notas, frequência

### 📝 Banco de Provas
- **Provas**: Múltiplas versões, status (rascunho, em edição, publicada, arquivada)
- **Questões**: Múltipla escolha, dissertativa, resposta curta, cálculo, multi-critério
- **Gabaritos**: Resposta correta, alternativas aceitas, palavras-chave, conceitos obrigatórios
- **Rubricas**: Critérios de pontuação parcial
- **Impressão**: Geração de PDF com QR Code único por cópia/aluno
- **Controle**: Registro de impressões, rastreabilidade completa

### 🤖 Correção por IA
- **Provedores**: Simulado (testes), Ollama (local), OpenAI, Anthropic
- **Processamento**: Assíncrono com filas, progresso em tempo real
- **OCR**: Tesseract/PaddleOCR para extração de texto e imagens
- **Correção**: Por questão, com pontuação, confiança e justificativa
- **Revisão Obrigatória**: Professor aprova, modifica ou rejeita sugestões da IA
- **Auditoria**: Registro completo de todas as ações

### 📦 Processamento em Lote (ADENDO OFICIAL) ⭐
- **Envio**: Múltiplos arquivos (PDF multipágina, imagens)
- **Pré-processamento**: Rotação, correção de perspectiva, binarização
- **Identificação**: OCR + IA para extrair RA, matrícula, nome, código da prova/turma/cópia
- **Correspondência**: Busca automática no cadastro de alunos
- **Conflitos**: Detecção de RA não encontrado ou com múltiplas correspondências
- **Revisão Manual**: Interface para o professor corrigir identificações incorretas
- **Agrupamento**: Páginas agrupadas automaticamente por aluno/prova
- **Criação de Envios**: Gera `ExamSubmission` a partir dos grupos identificados
- **Correção em Massa**: IA processa todas as submissões do lote
- **Progresso**: Acompanhamento em tempo real (envio → páginas → identificação → agrupamento → correção)
- **Auditoria**: Registro imutável de todas as operações

---

## 🚀 Início Rápido (Windows CMD)

```cmd
:: 1. Clone e acesse a pasta
git clone <url-do-repositorio>
cd EduGrade

:: 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate

:: 3. Instale as dependências
pip install -r requirements.txt

:: 4. Configure as variáveis de ambiente
copy .env.example .env
:: Abra o .env e altere a SECRET_KEY

:: 5. Inicie o servidor (sempre a partir da raiz do projeto)
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

> 💡 **Linux/macOS:** substitua `venv\Scripts\activate` por `source venv/bin/activate`

Acesse: **http://localhost:8000** → redireciona para o login automaticamente

**Usuários de demonstração criados automaticamente:**

| Perfil | Usuário | Senha |
|---|---|---|
| Administrador | `admin` | `admin123` |
| Professor | `professor` | `prof123` |
| Aluno | `aluno` | `aluno123` |

---

## 📁 Estrutura do Projeto

```
EduGrade/
├── 📁 backend/                 # API FastAPI
│   ├── 📁 app/
│   │   ├── 📁 api/routes/      # Endpoints REST
│   │   ├── 📁 core/            # Config, BD, Segurança, Exceções, Seed
│   │   ├── 📁 models/          # Modelos SQLAlchemy 2.0
│   │   ├── 📁 schemas/         # Schemas Pydantic v2
│   │   ├── 📁 repositories/    # Padrão Repository
│   │   ├── 📁 services/        # Lógica de Negócio
│   │   ├── 📁 integrations/    # PDF, QR, OCR, IA
│   │   └── main.py             # Ponto de Entrada
│   ├── 📁 migrations/          # Alembic
│   ├── 📁 tests/               # Pytest
│   └── alembic.ini
├── 📁 frontend/                # HTML/CSS/JS (painéis do sistema)
├── 📁 scripts/                 # Scripts utilitários (seed, etc.)
├── 📁 storage/                 # Arquivos enviados (provas, PDFs)
├── 📁 logs/                    # Logs da aplicação
├── 📄 SETUP.md                 # Guia detalhado de instalação
├── 📄 requirements.txt         # Dependências Python
└── 📄 README.md                # Este arquivo
```

---

## 🔧 Tecnologias Utilizadas

| Camada | Tecnologia | Versão |
|--------|------------|--------|
| **Framework API** | FastAPI | 0.109+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Validação** | Pydantic | 2.5+ |
| **Autenticação** | python-jose + passlib | 3.3+ / 1.7+ |
| **Banco de Dados** | PostgreSQL / SQLite | 15+ / 3.35+ |
| **Migrações** | Alembic | 1.13+ |
| **PDF** | ReportLab | 4.0+ |
| **QR Code** | qrcode + PIL | 7.4+ / 10+ |
| **OCR** | Tesseract / PaddleOCR | 5.3+ / 2.7+ |
| **IA** | Ollama / OpenAI / Anthropic | Recente |
| **Testes** | Pytest + pytest-asyncio | 7.4+ / 0.23+ |

---

## 📋 Requisitos do Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **Python** | 3.12 | 3.12 |
| **RAM** | 4 GB | 16 GB+ (para IA local) |
| **Disco** | 5 GB | 50 GB+ (SSD) |
| **CPU** | 2 núcleos | 8+ núcleos (para processamento em lote) |
| **GPU** | Opcional | NVIDIA 8GB+ VRAM (Ollama) |

### Dependências Externas
- **Tesseract OCR** + pacote de idioma português (`tesseract-ocr-por`)
- **Poppler** (`pdfinfo`, `pdftoppm` — para conversão de PDF em imagem)
- **Ollama** (opcional — para uso de IA localmente)

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [SETUP.md](SETUP.md) | Guia completo de instalação e configuração |
| [COMO_RODAR.md](COMO_RODAR.md) | Passo a passo para rodar no CMD |
| [INSTALAR_OCR_WINDOWS.md](INSTALAR_OCR_WINDOWS.md) | Instalação do Tesseract e idioma português para OCR no Windows |
| [docs/CONFIGURACOES_CENTRAL.md](docs/CONFIGURACOES_CENTRAL.md) | Central administrativa de provedores e configurações |
| [docs/INTEGRACAO_FCC.md](docs/INTEGRACAO_FCC.md) | Integração verificada com a API administrativa FCC |
| [docs/INTEGRACAO_NVIDIA_NIM.md](docs/INTEGRACAO_NVIDIA_NIM.md) | Cadastro e validação da NVIDIA NIM |
| [docs/SEGURANCA_CREDENCIAIS.md](docs/SEGURANCA_CREDENCIAIS.md) | Bootstrap e proteção de chaves de API |
| [docs/QA/TESTES_CONFIGURACOES.md](docs/QA/TESTES_CONFIGURACOES.md) | Evidências e limites dos testes da central |
| [API Docs](http://localhost:8000/docs) | Swagger UI (após iniciar o servidor) |
| [ReDoc](http://localhost:8000/redoc) | Documentação alternativa ReDoc |

---

## 🧪 Executando Testes

```cmd
:: A partir da raiz do projeto
pytest

:: Com relatório de cobertura
pytest --cov=backend/app --cov-report=html --cov-report=term-missing

:: Testes específicos
pytest tests\test_batch_grading.py -v
pytest tests\test_ai_correction.py -v
```

---

## 🔄 Pipeline de CI/CD

O fluxo do GitHub Actions (`.github/workflows/ci.yml`) executa:

1. **Verificação de Código**: ruff (lint), mypy (tipos)
2. **Testes**: pytest com cobertura ≥ 80%
3. **Build**: Imagem Docker multi-estágio
4. **Segurança**: bandit, safety check
5. **Deploy**: Homologação → Produção (aprovação manual)

---

## 🌐 Principais Endpoints da API

| Módulo | Prefixo | Descrição |
|--------|---------|-----------|
| **Autenticação** | `/api/v1/auth` | Login, cadastro, renovação de token, redefinição de senha |
| **Usuários** | `/api/v1/users` | CRUD de usuários e perfis |
| **Acadêmico** | `/api/v1/academic` | Cursos, disciplinas, turmas, matrículas |
| **Provas** | `/api/v1/exams` | Provas, questões, gabaritos, impressão |
| **Correção IA** | `/api/v1/ai-correction` | Correção automatizada e revisão |
| **Processamento em Lote** | `/api/v1/batch-grading` | **ADENDO: Processamento em lote** |
| **Auditoria** | `/api/v1/audit` | Registros de sistema e correção |

---

## 📦 API de Processamento em Lote (ADENDO)

```bash
# 1. Criar lote
POST /api/v1/batch-grading/
{ "exam_id": "...", "version_id": "..." }

# 2. Enviar arquivos (multipart)
POST /api/v1/batch-grading/{batch_id}/files

# 3. Executar o pipeline
POST /api/v1/batch-grading/{batch_id}/process-pages   # OCR + pré-processamento
POST /api/v1/batch-grading/{batch_id}/identify         # Identificação dos alunos
POST /api/v1/batch-grading/{batch_id}/group            # Agrupamento de páginas
POST /api/v1/batch-grading/{batch_id}/create-submissions
POST /api/v1/batch-grading/{batch_id}/grade            # Correção por IA

# 4. Revisão manual
GET  /api/v1/batch-grading/{batch_id}/pending-identifications
PUT  /api/v1/batch-grading/identifications/{id}/manual
{ "student_id": "..." }

# 5. Progresso e Auditoria
GET /api/v1/batch-grading/{batch_id}/progress
GET /api/v1/batch-grading/{batch_id}/audit
```

---

## 🐳 Docker

```dockerfile
# Dockerfile (multi-estágio)
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build e execução
docker build -t edugrade .
docker run -d -p 8000:8000 --env-file .env -v ./storage:/app/storage -v ./logs:/app/logs edugrade
```

---

## 🤝 Como Contribuir

1. Faça um fork do projeto
2. Crie sua branch: `git checkout -b feature/nova-funcionalidade`
3. Faça o commit: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Envie para o GitHub: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Padrão de Commits
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `refactor:` refatoração de código
- `test:` adição ou correção de testes
- `chore:` tarefas de manutenção

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** — veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **FastAPI** — Framework web moderno e de alta performance
- **SQLAlchemy** — ORM poderoso e flexível para Python
- **Pydantic** — Validação de dados robusta e tipada
- **Tesseract OCR** — Motor OCR de código aberto
- **Ollama** — IA generativa local e acessível
- **ReportLab** — Geração profissional de PDFs em Python

---

## 📞 Contato

**Desenvolvedor**: Fernando
- GitHub: [@fernando](https://github.com/fernando)

**Projeto**: [Repositório EduGrade](https://github.com/usuario/edugrade)

---

<div align="center">

**Feito com ❤️ para a educação brasileira**

*EduGrade — Transformando a correção de provas com Inteligência Artificial*

</div>
