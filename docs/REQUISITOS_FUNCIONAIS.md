# Requisitos Funcionais — EduGrade

**Projeto:** EduGrade — Sistema de Gestão e Desempenho Acadêmico
**Trabalho:** A3 Prático — Gestão e Qualidade de Software (GQS) — Prof. Daniel Henrique Matos de Paiva
**Responsável pelo documento:** Lucas Henrique Miranda (RA 325131396) — Product Owner
**Versão:** 1.0 — 02/11/2026

## 1. Esquema:

- **RF** = Requisito Funcional (o que o sistema faz). **RNF** = Requisito Não Funcional (como ele deve se comportar).
- **RN** = Regra de Negócio (Será definida em `REGRAS_DE_NEGOCIO.md`).
- A coluna **Situação no repositório** é um retrato da revisão do código e da QA de **02/11/2026** (`docs/QA/`). Ela **não é aprovação**: "existe no código" não significa "funciona de ponta a ponta". A validação oficial é feita e anotada pelo `CHECKLIST_VALIDACAO_FUNCIONAL.md`.

Legenda de situação: **Código** = rota/serviço existe · **Parcial** = existe com limitação conhecida · **Ausente** = não identificado · **Não validado** = ainda sem teste.

Prefixo comum das rotas: `/api/v1`.

---

## 2. Requisitos funcionais

### 2.1 Acesso e autenticação

| ID | Requisito | Ator | Critério de aceitação | Regras | Situação no repositório |
|---|---|---|---|---|---|
| RF01 | **Login de aluno**: entrar com RA/RM e senha individual. | Aluno | Credenciais válidas abrem o painel do aluno; inválidas mostram erro sem criar sessão. | RN13, RN42, RN43 | `POST /auth/login`. Login válido e inválido exercitados pela QA em banco de teste. Demais fluxos não validados. |
| RF02 | **Login de professor**: login individual. | Professor | Idem, abrindo o painel do professor. | RN11, RN42 | Idem RF01. |
| RF03 | **Login administrativo**. | Administrador | Idem, abrindo o painel administrativo. | RN12, RN42 | Idem RF01. |

### 2.2 Cadastro acadêmico

| ID | Requisito | Ator | Critério de aceitação | Regras | Situação no repositório |
|---|---|---|---|---|---|
| RF05 | **Cadastro de disciplinas** (criar, listar, editar). | Administrador | Disciplina criada fica persistida e aparece na listagem. | RN15 | `POST/GET/PATCH /academic/subjects`. Código; não validado. |
| RF06 | **Cadastro de turmas** (criar, listar, editar). | Administrador | Turma criada fica vinculada a curso, disciplina e período. | RN15 | `POST/GET/PATCH /academic/classes`. Código; não validado. |

### 2.3 Notas e histórico

| ID | Requisito | Ator | Critério de aceitação | Regras | Situação no repositório |
|---|---|---|---|---|---|
| RF04 | **Consulta de notas**: o aluno vê suas notas e médias. | Aluno | Só vê as próprias notas e só as já publicadas; nunca as de outro aluno. | RN01, RN14 | Rotas de notas em `/academic/grades`. **Parcial**: o painel do aluno mostra notas como "indisponíveis" por falta de fonte confiável (QA STUD-01). |
| RF07 | **Lançamento de notas**: registrar e publicar notas. | Professor autorizado | Só professor vinculado à disciplina lança; a nota só fica visível ao aluno após publicar. Administrador não lança por padrão. | RN02, RN11, RN12, RN14 | `POST /academic/grades`, `/grades/bulk`, `PATCH /grades/{id}`, `POST /grades/{id}/publish`. Código; não validado. **Ver pendência P1.** |
| RF08 | **Consulta do histórico acadêmico**: disciplinas, notas, médias e situação (aprovado/recuperação/reprovado). | Aluno | Histórico mostra apenas dados próprios publicados. | RN01, RN14, RN23, RN24 | **Ausente**: não identifiquei rota de histórico dedicada na revisão estática. |

### 2.4 Avaliações e provas presenciais

| ID | Requisito | Ator | Critério de aceitação | Regras | Situação no repositório |
|---|---|---|---|---|---|
| RF09 | **Criação de avaliações** (A1, A2, A3 etc.) com valor e peso. | Professor / Administrador | Avaliação criada e vinculada à turma; publicação registrada. | RN23, RN24 | `POST/GET /academic/assessments`, `POST /assessments/{id}/publish`. Código; não validado. |
| RF10 | **Criação de provas presenciais**: editor com adição, remoção, duplicação e reordenação de questões; tipos objetiva, discursiva, resposta curta, cálculo e múltiplos critérios; pontuação livre com soma validada; salvamento automático e manual; estados da prova; versionamento. | Professor | Prova salva; soma ≠ total bloqueia publicação; publicação gera versão imutável. | RN03, RN04, RN16–RN19, RN21, RN22 | `POST /exams`, `/exams/complete`, `/{id}/questions`, `/questions/reorder`, `GET /{id}/validate`, `POST /{id}/publish`. Código; testes unitários focados existem; fluxo completo **não validado**. |
| RF12 | **Cadastro de gabaritos**: resposta correta, resposta esperada, alternativas aceitas, rubrica, pontuação parcial, palavras-chave, conceitos obrigatórios e justificativa. | Professor | Gabarito salvo por questão; professor confirma antes de publicar a prova; aluno nunca o enxerga. | RN05, RN20, RN25 | `POST/PATCH /questions/{id}/answer-key` e `/rubric`. Código. Correção de exposição a aluno testada por unitário (BUG-01). Fluxo completo não validado. |
| RF11 | **Impressão das provas**: PDF da prova do aluno (sem gabarito) e do gabarito do professor; pré-visualização, download, impressão individual e em lote, reimpressão e histórico; identificador individual por cópia e QR Code. | Professor | PDF do aluno sem gabarito; cada cópia com QR/identificador único; impressões registradas. | RN25–RN29 | `POST /versions/{id}/copies`, `/versions/{id}/pdf-teacher`, `/copies/{id}/pdf-student`, `/print-log`, `/qr/generate`. Código. QA PROF-01 **pendente** (não executado). |

### 2.5 Digitalização, correção e publicação

| ID | Requisito | Ator | Critério de aceitação | Regras | Situação no repositório |
|---|---|---|---|---|---|
| RF13 | **Envio de provas digitalizadas**: PDF (inclusive multipágina), JPG, JPEG e PNG; arquivos únicos ou múltiplos; identificação do aluno/prova. | Professor | Arquivo válido é aceito e preservado; arquivo inválido é recusado; identificação falha → associação manual. | RN29–RN31 | `POST /submissions`, `/submissions/{id}/pages`, `/identify`. **Parcial**: o upload do módulo de lote (`/batch-grading/{id}/files`) responde **501 Não implementado** (BUG-04); validação de conteúdo/MIME em aberto (BUG-08). |
| RF14 | **Correção assistida por IA**: leitura (OCR), análise, comparação com gabarito/rubrica, sugestão de pontuação, justificativa e indicador de baixa confiança. | Professor (solicita) | A IA devolve apenas sugestões estruturadas; objetiva é determinística; baixa confiança vai para revisão manual. | RN06, RN32–RN38 | `POST /ai/correct`, `/ai/batch-correct`, `/submissions/{id}/request-correction`, `/process-ocr`. **Parcial**: provedor padrão é `mock`; provedor real não configurado; Tesseract/Poppler ausentes no ambiente da QA (BUG-14, BUG-15). |
| RF15 | **Revisão da correção pelo professor**: ver imagem, resposta reconhecida, gabarito, rubrica, nota sugerida e justificativa; aprovar, alterar nota, corrigir texto, rejeitar, pedir nova leitura, marcar ilegível, comentar. | Professor | Nenhuma nota é publicada sem a revisão; toda ação fica auditada. | RN07, RN39, RN40 | `POST /ai/corrections/{id}/review`, `GET /ai/reviews/pending`, `PATCH /reviews/{id}`. Código; QA PROF-03 **pendente**. |
| RF16 | **Publicação das notas**: após revisão, o sistema valida totais e limites e publica a nota oficial; o aluno passa a consultá-la. | Professor | Só publica após aprovação; registra versão do gabarito, professor, data/hora, sugestão original e nota final. | RN08, RN14, RN18, RN41 | `POST /submissions/{id}/publish-grades` e `/academic/grades/{id}/publish`. Código; não validado. |
| RF17 | **Auditoria das alterações**: registro de quem fez o quê e quando nas operações relevantes; consulta pelo administrador. | Administrador | Alterações de prova, gabarito, nota e configuração geram registro consultável. | RN10, RN40, RN41 | `GET /audit/*`; tabelas `audit_logs`, `correction_audit_logs`, `grading_audit_logs`. Consulta no código; sem teste . |

### 2.6 À Acrescentar:

| ID | Requisito | Ator | Critério de aceitação | Situação no repositório |
|---|---|---|---|---|
| RF18 | **Gestão de usuários** (alunos, professores, administradores): criar, listar, editar, desativar. | Administrador | Operações persistem; perfis têm permissões distintas. | `/users`, `/students`, `/teachers`, `/administrators`. Código; QA ADMIN-01 **parcial** (só listagem). |
| RF19 | **Gestão de matrículas** (individual e em lote). | Administrador | Aluno matriculado aparece na turma. | `POST /academic/enrollments` e `/bulk`. Código; não validado. |
| RF20 | **Gestão de períodos letivos** e definição do período atual. | Administrador | Um período fica como atual. | `/academic/periods`, `/periods/{id}/set-current`. Código; não validado. |
| RF21 | **Regras acadêmicas configuráveis** (pesos de A1, A2, A3, recuperação, exame final), sem pesos fixos. | Administrador | Alterar a regra altera o cálculo de média e situação. | `/academic/rules`. Código; **cálculo de média ponderada, nota necessária e situação não validados**. |
| RF22 | **Frequência**: lançar e consultar presença e percentual. | Professor / Aluno | Percentual calculado por matrícula. | `/academic/attendance`, `/attendance/bulk`, `/attendance/percentage/{id}`. Código; painel do aluno mostra como indisponível. |
| RF23 | **Alteração de senha** pelo próprio usuário. | Todos | Senha nova passa a valer; a antiga deixa de valer. | `POST /auth/change-password`. Código; não validado. |
| RF24 | **Solicitação de acesso** (cadastro público) e aprovação pelo administrador, que cria a conta. | Visitante / Administrador | Solicitação fica pendente até aprovada ou rejeitada. | `POST /access-requests`, `/{id}/create-account`, `/{id}/reject`. **Parcial**: entrega de credenciais por e-mail não confirmada. |
| RF25 | **Materiais de estudo**: professor publica por disciplina; aluno lista e baixa. | Professor / Aluno | Aluno só vê materiais das suas disciplinas; download exige autenticação. | `/materials`. Dashboard de professor e aluno carregaram na QA; escopo de download precisa de verificação. |
| RF26 | **Gestão de provedores de IA** (modelo, URL, credenciais, limites; status de saúde). | Administrador | Credenciais ficam protegidas e nunca aparecem em texto claro. | `/admin/settings/*`, `/ai/health`, `/ai/models`. Código; integração externa **não validada** (sem chave nem `CREDENTIAL_ENCRYPTION_KEY`). |
| RF27 | **Relatórios academicos** (desempenho por turma/aluno). | Professor / Administrador | Relatórios refletem dados reais. | **Ausente**: |
| RF28 | **Painel de qualidade** com cobertura de testes, protegido por backend. | Administrador | Exibe dados reais do Pytest-Cov. | **Ausente**:  |
| RF29 | **Backup e recuperação** do banco e dos arquivos. | Administrador | Rotina documentada e testada. | **Ausente**:  |

---

## 3. Requisitos não funcionais

| ID | Requisito | Situação (QA de 02/11/2026) |
|---|---|---|
| RNF01 | **Hash de senha** (Argon2id previsto no prompt). | Não verificado por mim; revisão técnica do Caio. |
| RNF02 | **Controle de acesso por perfil (RBAC) validado no backend** em todos os endpoints. | **Parcial**: RBAC incompleto em testes (QA ADMIN-02 pendente). |
| RNF03 | **Sessão com expiração**; logout invalida o acesso. | **Defeito aberto**: logout não revoga token no servidor (BUG-07). |
| RNF04 | **Arquivos privados** só por rota autenticada. | Corrigido (BUG-03), com teste unitário. |
| RNF05 | **Validação de upload** por extensão, MIME, tamanho e integridade. | **Aberto**: conteúdo/MIME não verificado (BUG-08). |
| RNF06 | **LGPD**: dados de alunos não saem para provedores externos sem autorização; IA local priorizada. | Depende da configuração do provedor; padrão atual é `mock`. |
| RNF07 | **Credenciais fora do código**; `.env` não versionado. | `.env` ignorado pelo Git (QA). |
| RNF08 | **Precisão decimal** em notas (`Decimal`). | Não verificado. |
| RNF09 | **Cobertura mínima de testes de 80%**, com o relatório em HTML. | **Não atendido**: 55,50% em 02/11/2026 (15 testes passando). |
| RNF10 | **CI/CD** (GitHub Actions) com lint, testes e falha abaixo de 80%. | **Não identificado**: nenhum workflow rastreado (BUG-16). |
| RNF11 | **Migrações de banco** versionadas. | **Aberto**: migração inicial não contém todas as tabelas (BUG-11). |
| RNF12 | **Interface responsiva e sem botões inativos**; dados indisponíveis são sinalizados, não inventados. | Dashboards sem números fictícios (BUG-05 corrigido). |
| RNF13 | **Usabilidade**: mensagens de erro claras e estados de carregamento. | Corrigido nos dashboards testados (BUG-17). |

---

## 4. Pendências de definição

| ID | Pergunta | Por que importa |
|---|---|---|
| P1 | **RF07 (lançamento de notas)** inclui lançamento **manual** além da nota vinda da correção por IA? | O Guia usa "lançamento de notas"; o fluxo do prompt é "IA sugere → professor aprova → publica". As duas coisas precisam estar consistentes com RN02, RN07 e RN08. |
| P2 | **RF08 (histórico)**, **RF27 (relatórios)**, **RF28 (painel de qualidade)** e **RF29 (backup)** entram na entrega A3? | Não foram identificados no código; ou entram no escopo e viram trabalho, ou saem do escopo e ficam registrados como limitação. |
| P3 | O upload em lote (`501`) será implementado antes da entrega? | Afeta RF13 e os cenários CV09 e CV17. |
| P4 | Haverá provedor de IA real na demonstração ou será usado o `mock`? | Afeta RF14, RN44 e como o resultado da correção deve ser descrito na apresentação. |
