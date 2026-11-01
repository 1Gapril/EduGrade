# EduGrade — Guia de Configuração e Execução

> Para o guia rápido de como rodar no CMD, veja também [como_rodar.md](como_rodar.md).

---

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10/11, Linux (Ubuntu 20.04+) ou macOS 12+

### Dependências do Sistema

#### Windows
```cmd
:: Instalar Python 3.12+
:: Baixe em: https://www.python.org/downloads/
:: Marque a opção "Add Python to PATH" durante a instalação

:: Instalar Tesseract OCR (opcional — necessário para correção por OCR)
:: Baixe em: https://github.com/UB-Mannheim/tesseract/wiki
:: Adicione ao PATH: C:\Program Files\Tesseract-OCR

:: Instalar Poppler (opcional — necessário para processar PDFs)
:: Baixe em: https://github.com/oschwartz10612/poppler-windows/releases/
:: Adicione ao PATH: C:\poppler\Library\bin
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev \
    tesseract-ocr tesseract-ocr-por \
    poppler-utils \
    libgl1-mesa-glx libglib2.0-0 \
    build-essential libpq-dev
```

#### macOS
```bash
brew install python@3.12 tesseract tesseract-lang poppler
```

---

## 🚀 Configuração do Projeto

### 1. Clone o Repositório
```cmd
git clone <url-do-repositorio>
cd EduGrade
```

### 2. Crie e Ative o Ambiente Virtual

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

Você verá `(venv)` no início do prompt quando o ambiente estiver ativo.

### 3. Atualize o pip e Instale as Dependências
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente

**Windows (CMD):**
```cmd
copy .env.example .env
```

**Linux/macOS:**
```bash
cp .env.example .env
```

Edite o arquivo `.env` e altere ao menos:
- `SECRET_KEY` — gere uma chave segura:
  ```cmd
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- `DATABASE_URL` — se quiser usar PostgreSQL em vez de SQLite
- `AI_PROVIDER` — `mock` (padrão), `ollama`, `openai` ou `anthropic`

### 5. Configure o Banco de Dados

#### SQLite (Desenvolvimento — Padrão, sem configuração extra)
```env
DATABASE_URL=sqlite:///./backend/edugrade.db
```
As tabelas são criadas automaticamente na primeira execução. Os usuários de demonstração também são inseridos automaticamente.

#### PostgreSQL (Produção)
```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/edugrade
```
Crie o banco antes de iniciar:
```bash
createdb edugrade
```

### 6. Execute as Migrações (opcional para desenvolvimento)
```cmd
cd backend
alembic upgrade head
cd ..
```
> Para desenvolvimento com SQLite, as tabelas são criadas automaticamente pelo sistema na inicialização — o Alembic não é obrigatório.

### 7. Crie os Diretórios de Armazenamento

**Windows (CMD):**
```cmd
mkdir storage\exams
mkdir storage\processed
mkdir storage\temp
mkdir storage\backups
mkdir logs
```

> O servidor também cria esses diretórios automaticamente na inicialização.

---

## 🏃 Executando a Aplicação

> ⚠️ **IMPORTANTE:** Execute sempre a partir da **pasta raiz** do projeto (`EduGrade\`), não de dentro de `backend\`.

### Desenvolvimento (com recarregamento automático)
```cmd
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Produção (sem recarregamento, múltiplos workers)
```cmd
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Com Docker (opcional)
```bash
# Build
docker build -t edugrade .

# Execução
docker run -d -p 8000:8000 --env-file .env edugrade
```

---

## 🌐 Acessando o Sistema

| URL | Descrição |
|-----|-----------|
| http://localhost:8000 | Página inicial (redireciona para login) |
| http://localhost:8000/login.html | Tela de login |
| http://localhost:8000/dashboard.html | Painel principal |
| http://localhost:8000/docs | Swagger UI — documentação interativa da API |
| http://localhost:8000/redoc | ReDoc — documentação alternativa |
| http://localhost:8000/health | Status do servidor |

### Usuários de Demonstração (criados automaticamente)

O seed contém contas e registros demonstrativos para desenvolvimento. Não
considere essas contas credenciais administrativas próprias e nunca use o seed
em um banco com dados reais.

---

## 🤖 Configuração de IA (Opcional)

### Tesseract OCR no Windows

Para instalar o executável, configurar o idioma português e verificar o
processamento de provas, siga o [guia de instalação do OCR para Windows](INSTALAR_OCR_WINDOWS.md).

### Ollama (IA Local — gratuito)
```bash
# Instale o Ollama: https://ollama.ai/
ollama pull llama3.1
ollama pull llava
```
No `.env`:
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TEXT_MODEL=llama3.1
OLLAMA_MULTIMODAL_MODEL=llava
```

### OpenAI
No `.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### Anthropic
No `.env`:
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Simulado (padrão — sem custo, para testes)
```env
AI_PROVIDER=mock
```

---

## 🧪 Executando Testes

```cmd
:: A partir da raiz do projeto, com o venv ativado

:: Todos os testes
pytest

:: Com relatório de cobertura
pytest --cov=backend/app --cov-report=html --cov-report=term

:: Testes específicos
pytest tests\test_auth.py -v
pytest tests\test_batch_grading.py -v
```

---

## 📦 Estrutura do Projeto

```
EduGrade\
├── backend\
│   ├── app\
│   │   ├── api\routes\          # Rotas da API REST
│   │   ├── core\                # Config, BD, Segurança, Exceções, Seed
│   │   ├── models\              # Modelos SQLAlchemy
│   │   ├── schemas\             # Schemas Pydantic
│   │   ├── repositories\        # Padrão Repository
│   │   ├── services\            # Lógica de Negócio
│   │   ├── integrations\        # PDF, QR Code, OCR, IA
│   │   └── main.py              # Ponto de entrada FastAPI
│   ├── migrations\              # Migrações Alembic
│   ├── tests\                   # Testes Pytest
│   └── alembic.ini
├── frontend\                    # HTML, CSS e JavaScript (interface)
├── scripts\                     # Scripts utilitários
│   └── seed_db.py               # Popular banco de dados manualmente
├── storage\                     # Arquivos enviados
├── logs\                        # Registros da aplicação
├── .env.example                 # Exemplo de configuração
├── requirements.txt             # Dependências Python
└── README.md
```

---

## 🔧 Comandos Úteis

### Banco de Dados (Alembic)
```cmd
cd backend

:: Criar nova migração
alembic revision --autogenerate -m "descricao da mudanca"

:: Aplicar todas as migrações pendentes
alembic upgrade head

:: Reverter a última migração
alembic downgrade -1

:: Ver histórico de migrações
alembic history
```

### Popular o Banco Manualmente
```cmd
:: A partir da raiz do projeto
python scripts\seed_db.py
```

### Desenvolvimento e Qualidade de Código
```cmd
:: Verificar tipos (mypy)
mypy backend\app\

:: Formatar código (black)
black backend\app\

:: Verificar lint (ruff)
ruff check backend\app\
```

### Limpeza segura

**Windows (CMD):**
```cmd
:: Remover cache Python (PowerShell)
Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
```

**Linux/macOS:**
```bash
# Remover cache Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Não remova o banco para "resetar" o sistema: isso apaga dados.
```

Para testar o seed sem tocar no banco existente, use um arquivo SQLite novo e
explicitamente descartável. No PowerShell, antes de iniciar o servidor:

```powershell
$env:DATABASE_URL = "sqlite:///./DADO_DE_TESTE_EDUGRADE.db"
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
```

Esse banco contém apenas dados de teste. Não aponte `DATABASE_URL` para um banco
com dados reais ao executar o seed, testes ou comandos de inicialização.

---

## 📚 Documentação da API

Após iniciar o servidor, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🐛 Solução de Problemas

### `ModuleNotFoundError: No module named 'backend'`
**Causa:** O comando está sendo executado de dentro da pasta `backend\` em vez da raiz.
```cmd
cd ..
python -m uvicorn backend.app.main:app --reload
```

### `sqlite3.OperationalError: no such table`
**Causa:** Tabelas ainda não foram criadas.
```cmd
cd backend
alembic upgrade head
cd ..
```
Ou simplesmente inicie o servidor normalmente — as tabelas são criadas automaticamente.

### `Tesseract not found`
```cmd
:: Windows: Verifique se C:\Program Files\Tesseract-OCR está no PATH do sistema
:: Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por
:: macOS: brew install tesseract tesseract-lang
```

### `Poppler not found` (processamento de PDF)
```cmd
:: Windows: Adicione poppler\Library\bin ao PATH do sistema
:: Linux: sudo apt-get install poppler-utils
:: macOS: brew install poppler
```

### Porta 8000 já está em uso
```cmd
:: Use outra porta
python -m uvicorn backend.app.main:app --reload --port 8001
```

### `venv\Scripts\activate` não funciona no PowerShell
**Causa:** Política de execução de scripts bloqueando.
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Ou use o **CMD** puro em vez do PowerShell.

### Banco de dados vazio (usuários não existem)
**Causa:** O banco foi criado antes do seed automático.
```cmd
python -m uvicorn backend.app.main:app --reload
```
Antes de iniciar, confirme que `DATABASE_URL` aponta para o banco correto. Não
apague nem recrie um banco existente para corrigir esse problema; faça backup e
investigue a inicialização.

---

## 📝 Checklist para Produção

- [ ] `SECRET_KEY` forte e única (mínimo 32 caracteres)
- [ ] `DATABASE_URL` configurado para PostgreSQL
- [ ] `DEBUG=false`
- [ ] `CORS_ORIGINS` restrito apenas aos domínios permitidos
- [ ] HTTPS configurado (ex: nginx como proxy reverso + certbot)
- [ ] Backup automático do banco configurado
- [ ] Monitoramento de logs configurado (ex: Loki, ELK, Graylog)
- [ ] Rate limiting ativado
- [ ] Variáveis de e-mail/SMTP configuradas
- [ ] `AI_PROVIDER` configurado com chaves de API válidas
- [ ] Contas demonstrativas desativadas/removidas e contas administrativas próprias provisionadas

---

## 📞 Suporte

Em caso de dúvidas ou problemas:
1. Verifique os logs em `logs\edugrade.log`
2. Consulte a documentação interativa da API em http://localhost:8000/docs
3. Abra uma *issue* no repositório do projeto

---

*Documentação do EduGrade v0.1.0 — Português Brasil*
