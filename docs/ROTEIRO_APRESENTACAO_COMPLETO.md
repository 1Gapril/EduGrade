# Roteiro de apresentação — EduGrade

**Trabalho A3 — Gestão e Qualidade de Software (GQS)**
**Tema:** EduGrade — Sistema de Gestão e Desempenho Acadêmico com IA para correção de provas presenciais
**Duração alvo:** 15 a 20 minutos + 5 minutos de perguntas
**Integrantes:** Fernando Almeida · Lucas Henrique Miranda · Caio Duraes · Gabriel Ferreira

---

## Como usar este roteiro

- Cada seção corresponde a **um slide** (ou dois, quando indicado).
- O bloco **“Fala”** é o texto sugerido — adapte para o seu jeito de falar.
- O bloco **“Evidência”** indica o que mostrar na tela (sistema, terminal, GitHub).
- Os tempos somam ~17 minutos; se a banca for rígida, corte a seção 13 (IA em detalhe) pela metade.

| Slide | Tema | Tempo |
|---|---|---|
| 1 | Capa e equipe | 0:30 |
| 2 | Problema | 1:00 |
| 3 | Objetivo e ODS 4 | 1:00 |
| 4 | Público-alvo e perfis | 1:00 |
| 5 | Visão geral da solução | 1:00 |
| 6 | Arquitetura | 1:30 |
| 7 | Tecnologias | 1:30 |
| 8 | Banco de dados | 1:00 |
| 9 | Segurança e LGPD | 1:00 |
| 10 | Portal do aluno | 1:30 |
| 11 | Portal do professor | 2:30 |
| 12 | Painel administrativo | 1:30 |
| 13 | IA, OCR e revisão humana | 1:30 |
| 14 | Barra global de progresso | 1:00 |
| 15 | Testes e cobertura | 1:30 |
| 16 | Git, branches e CI/CD | 1:00 |
| 17 | Demonstração ao vivo | 2:00 |
| 18 | Resultados e limitações | 1:00 |
| 19 | Conclusão | 0:30 |

---

## Slide 1 — Capa

**Fala:**
> “Boa noite. Somos o grupo do EduGrade, um sistema acadêmico full stack para gestão de alunos, provas presenciais e correção assistida por inteligência artificial. Eu sou o(a) [nome] e vou apresentar o problema, a solução, as tecnologias, as funções de cada perfil, os testes e o processo de versionamento.”

**Evidência:** slide com nome do projeto, integrantes, RA, disciplina e ODS 4.

---

## Slide 2 — Problema

**Fala:**
> “Corrigir provas em papel consome muito tempo do professor: ele elabora a prova, monta o gabarito, imprime, recolhe, confere questão por questão e ainda lança as notas à mão. Isso gera três problemas: retrabalho, risco de erro no lançamento e demora no retorno ao aluno.
>
> Nossa proposta não é digitalizar a prova — a avaliação continua presencial e no papel. O que automatizamos é o **processo em volta**: criação, gabarito, impressão, leitura das respostas e correção assistida, sempre com revisão humana.”

**Evidência:** imagem de provas empilhadas ou gráfico “tempo gasto por etapa”.

---

## Slide 3 — Objetivo e ODS 4

**Fala:**
> “O objetivo é entregar um sistema real, com backend, frontend, banco, autenticação, IA, testes e documentação, alinhado ao ODS 4 — Educação de Qualidade.
>
> Meta prática: reduzir o tempo entre a aplicação da prova e a devolução da nota, mantendo o professor no controle de todas as decisões.”

**Evidência:** destaque do ODS 4 e dos três pilares: **eficiência**, **qualidade** e **segurança dos dados**.

---

## Slide 4 — Público-alvo e perfis

**Fala:**
> “O sistema tem três perfis independentes, com permissões diferentes:
> - **Aluno:** consulta apenas os próprios dados — notas, médias, provas, frequência e grade horária.
> - **Professor:** gerencia as turmas autorizadas, cria provas e gabaritos, imprime, recebe as digitalizações, revisa a correção da IA e publica as notas.
> - **Administrador:** cuida dos usuários, cursos, disciplinas, turmas, matrículas, períodos, configurações de IA, auditoria e painel de qualidade.
>
> Nenhum perfil herda permissão de outro: o administrador, por exemplo, **não** lança notas automaticamente.”

**Evidência:** três cartões com os perfis e suas funções.

---

## Slide 5 — Visão geral da solução

**Fala:**
> “O fluxo principal é este: o professor cria a prova e o gabarito no sistema; o sistema valida a soma dos pontos e gera uma versão imutável; imprime em PDF com QR Code; o aluno responde no papel; o professor digitaliza; o sistema lê as respostas, compara com o gabarito e sugere uma nota com justificativa; o professor revisa e publica; o aluno consulta.”

**Evidência:** diagrama do fluxo em 8 passos com ícones.

---

## Slide 6 — Arquitetura

**Fala:**
> “A arquitetura é modular, em camadas:
> - **Frontend** estático (HTML/CSS/JS) servido pelo próprio FastAPI, com três portais e um workspace compartilhado.
> - **API REST** em FastAPI com rotas por domínio: autenticação, acadêmico, provas, correção por IA, importações, operações, auditoria, administração e qualidade.
> - **Serviços** com a regra de negócio; **repositórios** com o acesso a dados; **modelos** SQLAlchemy.
> - **Integrações**: PDF (ReportLab), QR Code, OCR (Tesseract/OpenCV), IA (Ollama, FCC/Claude, mock) e armazenamento de arquivos.
> - **Operações de longa duração** com registro no banco e acompanhamento em tempo real.
>
> Essa separação permitiu testar a regra de negócio sem subir servidor e trocar o provedor de IA sem mexer no restante.”

**Evidência:** diagrama de camadas (frontend → rotas → serviços → repositórios → banco/integrações).

---

## Slide 7 — Tecnologias

**Backend**
| Tecnologia | Uso |
|---|---|
| Python 3.12 | linguagem do backend |
| FastAPI + Uvicorn | API REST assíncrona e servidor ASGI |
| Pydantic v2 | validação de entrada/saída |
| SQLAlchemy 2 | ORM e mapeamento |
| Alembic | migrações de banco |
| Passlib + Argon2id | hash de senhas |
| python-jose (JWT) | autenticação por token |
| Pytest + Pytest-Cov | testes e cobertura |
| ReportLab | geração de PDF |
| qrcode + Pillow | QR Code e imagens |
| PyMuPDF | leitura de PDF |
| OpenCV + pytesseract | OCR e visão computacional |
| httpx | cliente HTTP dos provedores de IA |

**Frontend**
| Tecnologia | Uso |
|---|---|
| HTML5 + CSS3 (design system próprio) | interface responsiva e acessível |
| JavaScript (ES2020, sem framework) | lógica das telas |
| Fetch API + XMLHttpRequest | requisições e progresso de upload |
| Server-side rendering de assets com versão | cache correto após atualização |

**Banco e IA**
| Tecnologia | Uso |
|---|---|
| SQLite (dev) / PostgreSQL (produção) | persistência |
| Ollama (local) | IA gratuita opcional |
| FCC/Claude e NVIDIA NIM | provedores configuráveis |
| MockProvider | testes automatizados sem custo |
| Tesseract | OCR de texto impresso |

**DevOps**
Git · GitHub · GitHub Actions · Pytest-Cov (XML/JUnit) · README/roteiros.

**Fala:**
> “A escolha foi guiada por compatibilidade e simplicidade de execução: tudo roda localmente, sem depender de serviços pagos. A IA é opcional e configurável pelo administrador.”

**Evidência:** slide em três colunas.

---

## Slide 8 — Banco de dados

**Fala:**
> “O banco tem mais de 40 tabelas, com chaves primárias UUID, chaves estrangeiras, índices e restrições de unicidade. Os grupos principais são: usuários e perfis; estrutura acadêmica (curso, disciplina, turma, período, matrícula, atribuição); avaliações e notas; provas (questões, gabaritos, rubricas, versões, cópias, impressão); correção (submissões, páginas, respostas extraídas, correções, revisões, auditoria) e operações de longa duração.
>
> Destaques de integridade: `versão da prova` é imutável depois de publicada; a nota é única por matrícula/avaliação; a frequência é única por matrícula/data; e toda alteração relevante gera registro de auditoria.”

**Evidência:** diagrama ER simplificado com as 8 entidades centrais.

---

## Slide 9 — Segurança e LGPD

**Fala:**
> “Segurança foi tratada em camadas: senha com hash Argon2id, JWT de acesso e refresh, RBAC por perfil e **permissões contextuais** por turma/disciplina/período, auditoria de login e de operações sensíveis, validação de uploads por extensão, tamanho e tipo real, proteção contra path traversal na entrega de PDFs e isolamento de dados do aluno.
>
> Sobre LGPD: os dados de aluno não são enviados a provedores externos por padrão; o administrador escolhe o provedor de IA e pode usar Ollama local. O conteúdo das provas é tratado como **dado não confiável** — instruções escritas na folha não alteram prompt, regras ou permissões.”

**Evidência:** tabela “ameaça → controle”.

---

## Slide 10 — Portal do aluno

**Fala:**
> “O aluno entra com usuário ou RA e vê apenas o que é dele:
> - **Início:** curso, turma, período, média geral, frequência e provas da turma.
> - **Minhas notas:** nota, avaliação, data e status de publicação.
> - **Minhas provas:** somente provas publicadas das turmas em que está matriculado.
> - **Frequência:** presenças, faltas, justificativas e percentual por disciplina.
> - **Grade horária:** dias, horários, sala e professor.
> - **Materiais** publicados pelos professores e **alteração de senha**.
>
> Nota só aparece depois que o professor publica — antes disso, o aluno não vê nada.”

**Evidência:** abrir `/aluno/dashboard.html` com o usuário `aluno`.

---

## Slide 11 — Portal do professor

**Fala:**
> “É o coração do sistema. O professor trabalha somente nas turmas atribuídas a ele:
>
> 1. **Criar prova:** dados da avaliação, questões (objetiva, discursiva, curta, cálculo, múltiplos critérios), pontuação livre e gabarito com rubrica, palavras-chave e conceitos obrigatórios.
> 2. **Importar de PDF:** envia a prova e o gabarito; a IA extrai enunciados e respostas para um rascunho que o professor confere.
> 3. **Publicar:** o sistema valida a soma das pontuações, gera a versão imutável e libera impressão e correção.”
> 4. **Imprimir:** prova do aluno (sem gabarito) e gabarito do professor, com QR Code de identificação, individual ou em lote.
> 5. **Enviar provas respondidas:** PDF ou várias fotos, com identificação do aluno por RA/matrícula.
> 6. **Correção por IA:** leitura das respostas, comparação com o gabarito e sugestão de nota com justificativa e confiança.
> 7. **Revisão obrigatória:** aprovar, ajustar a nota, corrigir o texto reconhecido, marcar ilegível ou rejeitar — tudo auditado.
> 8. **Notas:** lançar, revisar e publicar; relatórios e materiais de estudo.

**Evidência:** mostrar `/professor/dashboard.html` e a lista de provas com o botão **Publicar**.

---

## Slide 12 — Painel administrativo

**Fala:**
> “O administrador garante a estrutura e a qualidade:
> - **Usuários, professores, alunos e chamados de acesso.**
> - **Cursos, disciplinas, turmas, matrículas e períodos letivos.**
> - **Atribuições acadêmicas** e permissões por turma.
> - **Notas e publicações**, auditoria e erros do sistema.
> - **Configurações de IA:** provedor, modelo, chave (criptografada), teste de conexão e sincronização com o FCC.
> - **Armazenamento:** uso por pasta e banco.
> - **Qualidade:** executa a suíte de testes com cobertura e publica o relatório HTML.”

**Evidência:** `/admin/dashboard.html` e `/admin/quality.html`.

---

## Slide 13 — IA, OCR e revisão humana

**Fala:**
> “A camada de IA é independente do provedor: a mesma interface atende Ollama local, FCC/Claude, NVIDIA NIM e o modo simulado dos testes. Ela recebe enunciado, gabarito, rubrica, pontuação e a resposta reconhecida, e devolve dados estruturados: texto reconhecido, interpretação, nota sugerida, justificativa, critérios atendidos e não atendidos, erros conceituais e confiança da leitura e da avaliação.
>
> No OCR, usamos Tesseract e OpenCV para corrigir rotação, perspectiva e contraste. E há um fallback importante: se o PDF já tem texto selecionável, lemos a camada de texto — foi o que permitiu corrigir a prova digital sem depender do Tesseract.
>
> A IA **nunca** altera gabarito, pesos ou notas oficiais: ela sugere, o professor decide. Baixa confiança sempre vai para revisão manual.”

**Evidência:** exemplo de correção com justificativa e confiança em `/professor/corrections.html`.

---

## Slide 14 — Barra global de progresso

**Fala:**
> “Operações demoradas precisam de transparência. Implementamos um componente único, reutilizável, que acompanha quatro operações: envio de prova em PDF, upload de várias fotos, correção por IA e importação de alunos/notas.
>
> O percentual é **real**: nos uploads vem dos bytes transferidos; no processamento, da contagem de registros/questões concluídas. Quando não existe medida confiável, a barra fica indeterminada e mostra a etapa — nunca um percentual inventado. O backend é a fonte da verdade, o painel retoma a operação após recarregar e o cancelamento é cooperativo.”

**Evidência:** iniciar um upload e mostrar o painel com etapas e tempo.

---

## Slide 15 — Testes e cobertura

**Fala:**
> “A qualidade é medida de verdade:
> - **262 testes automatizados**, **0 reprovados**.
> - **Cobertura global de 81,32%**, acima da meta de 80%.
> - Cobertura inclui autenticação, permissões, cálculos acadêmicos, criação e versionamento de provas, PDF, QR, upload, OCR, correção, importações, operações de progresso e isolamento entre perfis.
> - Testes de IA usam provedor simulado; testes com IA real ficam separados.
> - O relatório HTML é gerado com `pytest-cov` e pode ser aberto pelo painel administrativo.”

**Evidência:** terminal com `pytest` + print do relatório. Cite os comandos de `docs/COMANDOS_TESTES_E_COBERTURA.md`.

---

## Slide 16 — Git, branches e CI/CD

**Fala:**
> “Usamos GitFlow simplificado: `main` estável, `develop` de integração e branches `feature/*` por área (backend, frontend, testes, documentação) e `fix/*`. Os commits seguem `feat:`, `fix:`, `test:`, `docs:` e `ci:`, com mensagens no imperativo.
>
> O GitHub Actions roda em cada push e pull request: instala dependências, executa os testes unitários com cobertura, gera XML/JUnit e publica como artefato por sete dias. Nenhum integrante faz push direto na `main`.”

**Evidência:** aba **Actions** do GitHub e o `git log --oneline` com os prefixos.

---

## Slide 17 — Demonstração ao vivo (roteiro de 2 minutos)

> Ensaie antes. Se a internet falhar, use os prints como plano B.

1. **Login administrador** (`admin` / `admin123`) → abrir **Qualidade** e mostrar a cobertura gerada (10 s).
2. **Login professor** (`professor` / `prof123`):
   - lista de provas → clicar **Publicar** em um rascunho (15 s);
   - **Impressão & QR Codes** → gerar 1 cópia e baixar o PDF (15 s);
   - **Enviar Provas para Correção** → escolher prova + aluno, anexar o PDF respondido → mostrar a barra com etapas (25 s);
   - **Correções Pendentes** → abrir uma correção, mostrar nota sugerida + justificativa + confiança e aprovar (25 s);
   - **Lançar Notas** → publicar a nota (10 s).
3. **Login aluno** (`aluno` / `aluno123`) → **Minhas notas** mostra a nota publicada, **Frequência** e **Grade horária** (20 s).
4. Fechar com o **relatório de cobertura** aberto no navegador (10 s).

---

## Slide 18 — Resultados e limitações

**Fala:**
> “Resultados: fluxo completo funcionando — login nos três perfis, criação e publicação de prova, impressão com QR, envio de prova respondida, correção assistida, revisão humana, publicação e consulta pelo aluno, tudo com auditoria e cobertura acima da meta.
>
> Limitações honestas:
> - o OCR de **manuscrito** depende do Tesseract instalado; sem ele, funcionam PDFs com texto selecionável;
> - a IA pode errar: por isso a revisão humana é obrigatória;
> - a importação CSV tem limite de 2.000 linhas por arquivo;
> - o painel de qualidade executa a suíte no servidor e leva de 4 a 5 minutos.”

**Evidência:** tabela “entregue / não entregue / próximo passo”.

---

## Slide 19 — Conclusão

**Fala:**
> “O EduGrade mostra que é possível automatizar a parte pesada da correção sem tirar o professor da decisão final, com segurança, rastreabilidade e qualidade medida. Obrigado — estamos à disposição para perguntas.”

---

## Perguntas prováveis (e respostas curtas)

| Pergunta | Resposta |
|---|---|
| O aluno pode fazer prova online? | Não. A prova é presencial e em papel; o portal do aluno é só consulta. |
| A IA pode publicar nota sozinha? | Não. Ela sugere; a publicação exige revisão e ação do professor, com auditoria. |
| Como garantem que um professor não acessa a turma de outro? | Permissões contextuais em `academic_assignments` (turma + disciplina + período) verificadas em cada rota. |
| E se o OCR falhar? | A resposta vai para revisão manual com confiança baixa; há fallback para a camada de texto do PDF. |
| Onde ficam as chaves de IA? | Em variáveis de ambiente ou cadastro no painel administrativo, com criptografia — nunca no código-fonte. |
| Como a cobertura é calculada? | `pytest-cov` mede as linhas de `backend/app` executadas pelos testes; o painel lê o XML gerado. |
| Dá para usar PostgreSQL? | Sim: basta ajustar `DATABASE_URL`; o código usa SQLAlchemy e migrações Alembic. |
| O que acontece se o servidor reiniciar durante uma operação? | O painel detecta a operação perdida e informa; nada fica preso em “carregando”. |

---

## Checklist de evidências para entregar

- [ ] Repositório GitHub organizado (README, `.gitignore`, branches).
- [ ] Prints dos três painéis e do fluxo de correção.
- [ ] Saída do `pytest` com 262 testes e cobertura ≥ 80%.
- [ ] Relatório HTML de cobertura (`reports/coverage/index.html`).
- [ ] Print da execução do GitHub Actions com o artefato.
- [ ] Documentos: requisitos, regras de negócio, modelo de dados, roteiro (este), comandos de teste.
- [ ] vídeo pitch de 3 minutos: problema → solução → demonstração → resultado.
