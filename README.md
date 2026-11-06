# EduGrade — Sistema de Gestão e Desempenho Acadêmico com IA

  Plataforma completa para gestão acadêmica, aplicação de provas e correção
  automatizada com Inteligência Artificial.

  ## 🎯 Objetivo
  Otimizar o tempo do corpo docente na criação, aplicação e correção de
  avaliações, além de fornecer relatórios analíticos precisos sobre os pontos
  de dificuldade e evolução dos estudantes por meio de IA.

  ## 🛠️ Tecnologias Utilizadas
  * **Backend:** Python (FastAPI / Poetry)
  * **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
  * **Processamento:** Bibliotecas de OCR (Optical Character Recognition) e
  Modelos de Linguagem (LLMs)
  * **Gerenciamento de Dependências:** `pyproject.toml` / `requirements.txt`

  ## 🚀 Funcionalidades Principais
  * **Portal do Aluno:** Dashboard acadêmico integrado com consulta rápida de
  notas e relatórios preditivos gerados por IA.
  * **Portal do Professor:** Gerenciamento completo de turmas, criação
  padronizada de avaliações e visualização de métricas de desempenho
  consolidadas.
  * **Correção Assistida:** Módulo inteligente de leitura de
  imagens/documentos via OCR para apoio na correção de questões discursivas e
  objetivas.

  ## 📂 Estrutura de Pastas
  ```text
  EduGrade/
  ├── .github/workflows/    # Configurações do pipeline de CI/CD
  ├── backend/              # Código-fonte da API em Python
  ├── frontend/             # Interface web do usuário (HTML, CSS, JS)
  ├── docs/                 # Documentações e roteiros acadêmicos
  ├── scripts/              # Scripts auxiliares e automações
  ├── tests/unit/           # Arquivos de testes unitários do sistema
  ├── .gitignore            # Arquivos ignorados pelo Git
  └── README.md             # Instruções e documentação principal do projeto

  💻 Requisitos de Instalação e Configuração

  Para rodar o ambiente localmente, certifique-se de ter o Python 3.10+
  instalado.

  1. Clone o repositório e acesse a pasta:
  git clone https://github.com/1Gapril/EduGrade
  cd EduGrade
  2. Configure as variáveis de ambiente baseando-se no arquivo de exemplo:
  cp .env.example .env
  3. Instale as dependências necessárias:
  pip install -r requirements.txt

  🔐 Acesso Rápido (contas de demonstração)

  Após iniciar o servidor, acesse http://localhost:8000/login.html e use as
  contas criadas pelo seed — duas para cada perfil:

  | Perfil | Usuário | Senha |
  |---|---|---|
  | Administrador | admin / admin2 | admin123 |
  | Professor | professor / professor2 | prof123 |
  | Aluno | aluno / aluno2 | aluno123 |

  A lista completa está em `CREDENCIAIS.md`. Para limpar o banco e recriar
  apenas o necessário: `python scripts\reset_db.py`.

  ⚙️ Comandos para Execução e Testes

  - Executar o Backend:
  python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
  - Executar os Testes Unitários:
  pytest
  - Visualizar a Cobertura de Testes (Coverage):
  pytest --cov=backend backend/tests/
  - Gerar relatório HTML de cobertura:
  pytest --cov=backend backend/tests/ --cov-report=html

  👥 Integrantes da Equipe 
- Gabriel Ferreira — RA 325140970 — (GitHub, Versionamento, Documentação, DevOps e Apresentação)

- Fernando Almeida — RA 326132695 — (Desenvolvimento Backend, Frontend e Testes)

- Lucas Henrique — RA 325131396 — (QA, Testes, Validação Funcional e Documentação Técnica)

- Caio Durães — RA 325132875 — (IA/OCR, Modelos de Linguagem, Correção Assistida e Integrações)

  ---
   📚 Documentação Adicional

  ┌───────────────────────────────────────────┬───────────────────────────┐
  │                 Documento                 │         Descrição         │
  ├───────────────────────────────────────────┼───────────────────────────┤
  │ SETUP.md                                  │ Guia completo de          │
  │                                           │ instalação e configuração │
  ├───────────────────────────────────────────┼───────────────────────────┤
  │ CREDENCIAIS.md                            │ Usuários e senhas das     │
  │                                           │ contas de demonstração    │
  ├───────────────────────────────────────────┼───────────────────────────┤
  │ docs/PROGRESSO_GLOBAL.md                  │ Barra global de progresso:│
  │                                           │ uploads, importações e IA │
  ├───────────────────────────────────────────┼───────────────────────────┤
  │ docs/COMANDOS_TESTES_E_COBERTURA.md       │ Comandos de testes        │
  │                                           │ unitários e cobertura     │
  ├───────────────────────────────────────────┼───────────────────────────┤
  │ docs/ROTEIRO_APRESENTACAO_COMPLETO.md     │ Roteiro de apresentação   │
  │                                           │ (tecnologias, telas, Git, │
  │                                           │ testes e demonstração)    │
  ├───────────────────────────────────────────┼───────────────────────────┤
  │ como_rodar.md                             │ Passo a passo para rodar  │
  │                                           │ no CMD                    │
  ├───────────────────────────────────────────┼───────────────────────────┤
  │                                           │ Instruções para           │
  │ INSTALAR_OCR_WINDOWS.md                   │ configuração do OCR no    │
  │                                           │ Windows                   │
  ├───────────────────────────────────────────┼───────────────────────────┤
  │ ROTEIRO_APRESENTACAO_A3.md                │ Roteiro estruturado da    │
  │ (docs/ROTEIRO_APRESENTACAO_A3.md)         │ apresentação acadêmica do │
  │                                           │  projeto                  │
  └───────────────────────────────────────────┴───────────────────────────┘
