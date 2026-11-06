🎓 EduGrade — Guia Completo: Como Rodar o Projeto no CMD

IMPORTANT

Todos os comandos devem ser executados a partir da pasta raiz do projeto (EduGrade\), não de dentro da pasta backend\.

✅ Pré-requisitos

Antes de começar, verifique se você tem instalado:

Ferramenta	Versão mínima	Como verificar
Python	3.11+	python --version
Git	qualquer	git --version
Tesseract OCR (opcional)	qualquer	Para reconhecimento de texto em imagens de provas
Poppler (opcional)	qualquer	Para converter PDFs em imagens

NOTE

Tesseract e Poppler são opcionais. O sistema funciona sem eles; apenas as funcionalidades de OCR e PDF não estarão disponíveis.

📥 Passo 1 — Clonar o Repositório
cmd
git clone https://github.com/1Gapril/EduGrade.git
cd EduGrade

Se você já tem o projeto na máquina, apenas navegue até a pasta:

cmd
cd caminho\para\EduGrade
🐍 Passo 2 — Criar o Ambiente Virtual (venv)
cmd
python -m venv venv

Isso cria a pasta venv\ dentro do projeto com uma instalação Python isolada.

▶️ Passo 3 — Ativar o Ambiente Virtual
cmd
venv\Scripts\activate

Você verá o prefixo (venv) aparecer no prompt, indicando que o ambiente está ativo:

(venv) E:\Projetos GitHub\EduGrade>

TIP

Para desativar o ambiente virtual a qualquer momento, use: deactivate

📦 Passo 4 — Instalar as Dependências
cmd
pip install -r requirements.txt

Este comando instala todas as bibliotecas necessárias. Pode demorar alguns minutos na primeira vez.

NOTE

Dependências principais instaladas: FastAPI, SQLAlchemy, Pydantic, Uvicorn, Passlib (senhas), PyJWT, entre outras.

⚙️ Passo 5 — Configurar as Variáveis de Ambiente
cmd
copy .env.example .env

Abra o arquivo .env em qualquer editor de texto e altere ao menos a SECRET_KEY:

env
# Gere uma chave segura (exemplo):
SECRET_KEY=sua_chave_super_secreta_aqui_min_32_chars
# Banco de dados — SQLite (padrão, sem configuração extra):
DATABASE_URL=sqlite:///./backend/edugrade.db
# Ou PostgreSQL (opcional):
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/edugrade

TIP

Para gerar uma SECRET_KEY segura no CMD:

cmd
python -c "import secrets; print(secrets.token_hex(32))"
🗂️ Passo 6 — Criar as Pastas de Armazenamento
cmd
mkdir storage\exams
mkdir storage\processed
mkdir storage\temp
mkdir storage\backups
mkdir logs

NOTE

O servidor cria essas pastas automaticamente na inicialização, mas criá-las manualmente evita qualquer problema de permissão.

🚀 Passo 7 — Iniciar o Servidor
cmd
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

Você verá uma saída parecida com:

INFO  - Iniciando EduGrade...
INFO  - Banco de dados populado com sucesso!
INFO  - Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO  - Started reloader process [XXXX]

IMPORTANT

ATENÇÃO: Execute este comando a partir da pasta raiz EduGrade\, não de dentro de backend\. O módulo deve ser backend.app.main:app (com ponto, não barra).

TIP

O flag --reload reinicia o servidor automaticamente quando você editar arquivos. Para produção, remova esse flag.

🌐 Passo 8 — Acessar o Sistema

Abra o navegador e acesse:

URL	Descrição
http://localhost:8000
	Página inicial (redireciona para o login)
http://localhost:8000/login.html
	Tela de login
http://localhost:8000/dashboard.html
	Dashboard principal
http://localhost:8000/docs
	Documentação interativa da API (Swagger UI)
http://localhost:8000/redoc
	Documentação alternativa (ReDoc)
http://localhost:8000/health
	Status do servidor (JSON)
👤 Passo 9 — Contas de desenvolvimento

O seed cria duas contas para cada perfil (administrador, professor e aluno).
A lista completa de usuários e senhas está em CREDENCIAIS.md, na raiz do
projeto. Use essas contas apenas em desenvolvimento/teste e troque as senhas
antes de publicar o sistema.

Para limpar o banco e recriar apenas o necessário (com backup automático):

cmd
python scripts\reset_db.py

🛑 Passo 10 — Parar o Servidor

Pressione Ctrl + C no CMD onde o servidor está rodando.

🔄 Próximas Execuções

Após a configuração inicial, para rodar o projeto novamente basta:

cmd
cd caminho\para\EduGrade
venv\Scripts\activate
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
🧩 Comandos Opcionais
Popular o banco manualmente (seed)

Se precisar recriar os dados de demonstração:

cmd
python scripts\seed_db.py
Criar um banco isolado para testes

cmd
$env:DATABASE_URL = "sqlite:///./DADO_DE_TESTE_EDUGRADE.db"
venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001

Não remova nem recrie o banco configurado para a aplicação: isso pode apagar
dados acadêmicos existentes. O nome acima identifica um banco exclusivamente
de teste.
Executar migrações com Alembic
cmd
cd backend
alembic upgrade head
cd ..

NOTE

Para desenvolvimento com SQLite, as tabelas são criadas automaticamente pelo SQLAlchemy na inicialização. O Alembic é mais relevante para ambientes com PostgreSQL ou para rastrear mudanças de schema.

Rodar em modo de produção (sem reload)
cmd
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
🐛 Resolução de Problemas
ModuleNotFoundError: No module named 'backend'

Causa: Você está rodando o comando de dentro da pasta backend\ em vez da raiz.
Solução: Volte para a pasta raiz:

cmd
cd ..
python -m uvicorn backend.app.main:app --reload
Address already in use / Porta 8000 já em uso

Causa: Outro processo está usando a porta 8000.
Solução: Use uma porta diferente:

cmd
python -m uvicorn backend.app.main:app --reload --port 8001
venv\Scripts\activate não funciona no PowerShell

Causa: Política de execução de scripts do Windows bloqueando.
Solução: Execute no PowerShell como administrador:

powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Ou use o CMD puro (não o PowerShell).

Erro de senha / autenticação com argon2

Causa: A variável HASH_ALGORITHM no .env está configurada como argon2id.
Solução: Altere para argon2 (sem o "id"):

env
HASH_ALGORITHM=argon2
O banco de dados parece vazio (usuários não existem)

Causa: O banco existente foi criado antes do seed automático.
Solução:

cmd
python -m uvicorn backend.app.main:app --reload

Antes de iniciar, confirme `DATABASE_URL`. Não apague o banco para tentar
recriar usuários; preserve os dados e investigue o seed/migração.

📁 Estrutura do Projeto
EduGrade\
├── backend\
│   ├── app\
│   │   ├── api\          # Rotas da API (FastAPI)
│   │   ├── core\         # Config, DB, segurança, seed
│   │   ├── models\       # Modelos SQLAlchemy
│   │   ├── schemas\      # Schemas Pydantic
│   │   ├── services\     # Lógica de negócio
│   │   └── main.py       # Ponto de entrada da aplicação
│   └── edugrade.db       # Banco SQLite (criado automaticamente)
├── frontend\
│   ├── *.html            # Páginas do sistema
│   ├── css\              # Estilos
│   └── js\               # JavaScript do frontend
├── scripts\
│   └── seed_db.py        # Script para popular o banco
├── storage\              # Arquivos enviados (provas, PDFs)
├── logs\                 # Logs da aplicação
├── venv\                 # Ambiente virtual Python
├── .env                  # Variáveis de ambiente (não comitar!)
├── .env.example          # Exemplo de configuração
└── requirements.txt      # Dependências Python
🔗 URLs Rápidas de Referência
Login:        http://localhost:8000/login.html
Dashboard:    http://localhost:8000/dashboard.html
API Docs:     http://localhost:8000/docs
Health:       http://localhost:8000/health