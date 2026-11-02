# EduGrade — Sistema de Gestão e Desempenho Acadêmico com Correção Assistida por Inteligência Artificial

**Trabalho A3 Prático — Gestão e Qualidade de Software (GQS)**
**Professor:** Daniel Henrique Matos de Paiva
**ODS 4:** Educação de Qualidade

**Integrantes**

| Nome | RA | Responsabilidade principal |
|---|---|---|
| Fernando Almeida | 326132695 | Desenvolvimento com Claude Code, QA e integração |
| Lucas Henrique Miranda | 325131396 | Requisitos, regras de negócio e validação funcional |
| Caio Duraes | 325132875 | Arquitetura, banco de dados e validação técnica |
| Gabriel Ferreira | 325140970 | GitHub, documentação, DevOps e apresentação |

**Versão:** rascunho 1.0 — 02/11/2026

---

## 1. Introdução

A avaliação da aprendizagem é uma das atividades que mais consomem o tempo do professor e, ao mesmo tempo, uma das que mais impactam o aluno: dela dependem a nota, a aprovação e a percepção de justiça no processo. Em grande parte das instituições, as provas continuam sendo aplicadas em papel, de forma presencial, enquanto a preparação, a correção e o lançamento das notas dependem de planilhas, arquivos soltos e conferências manuais.

O **EduGrade** é uma plataforma acadêmica que mantém a aplicação das provas em papel e presencial, mas digitaliza e apoia todo o restante do processo: o professor monta a prova e o gabarito no sistema, imprime as cópias identificadas, digitaliza as folhas respondidas e recebe sugestões de correção geradas por inteligência artificial (IA). A decisão final é sempre do professor, e a nota só é publicada ao aluno depois de revisada e aprovada.

Este documento apresenta o problema, a justificativa, os objetivos, o público-alvo, os requisitos e a solução proposta, relacionando o projeto à ODS 4. Foi desenvolvido no contexto da disciplina de Gestão e Qualidade de Software, de modo que a **qualidade do processo** (requisitos, regras de negócio, testes, versionamento e integração contínua) é tão importante quanto o produto.

## 2. Problema identificado

1. **Tempo de correção.** A correção manual de provas, principalmente discursivas, é demorada e repetitiva, o que reduz o tempo disponível para planejar aulas e acompanhar os alunos.
2. **Risco de inconsistência.** Somas de pontos, critérios de correção e aplicação de gabaritos feitos manualmente estão sujeitos a erro e a variação de critério entre provas e entre corretores.
3. **Falta de rastreabilidade.** Quando uma nota é questionada, nem sempre há registro de qual gabarito foi usado, quem alterou a nota e por quê.
4. **Demora e pouca transparência para o aluno.** O aluno costuma receber a nota sem acompanhar seu desempenho ao longo do período.
5. **Dados sensíveis.** Provas e notas são dados pessoais e acadêmicos que exigem controle de acesso, o que ferramentas improvisadas raramente garantem.

## 3. Justificativa

- **Relevância social e institucional:** reduzir a carga operacional do professor e melhorar o retorno ao aluno contribui diretamente para a qualidade do ensino.
- **Respeito ao contexto real:** o projeto não exige que a escola abandone a prova em papel; ele se adapta ao modelo presencial já existente, o que facilita a adoção.
- **Uso responsável de IA:** a IA atua como **assistente** (sugere nota e justificativa), nunca como decisora. Essa escolha de projeto responde aos riscos de erro de leitura de manuscritos, de viés e de manipulação por texto escrito na prova.
- **Relevância para a disciplina de GQS:** o projeto exige requisitos rastreáveis, regras de negócio explícitas, testes automatizados e funcionais, controle de versão, cobertura mínima de testes e integração contínua, ou seja, a aplicação prática dos conceitos de qualidade de software.

## 4. Objetivos

### 4.1 Objetivo geral

Desenvolver e documentar uma plataforma acadêmica integrada (frontend, backend e banco de dados) que permita ao professor criar, imprimir e corrigir provas presenciais com apoio de inteligência artificial, e ao aluno acompanhar o seu desempenho, com qualidade de software comprovada por testes e evidências.

### 4.2 Objetivos específicos

1. Permitir que o professor crie provas, cadastre gabaritos e rubricas e distribua a pontuação livremente, com validação automática da soma.
2. Garantir que cada prova publicada gere uma versão imutável, preservando a ligação entre a prova aplicada e o gabarito usado.
3. Gerar a prova em PDF para impressão individual e em lote, com identificação única de cada cópia (QR Code), sem expor o gabarito.
4. Receber provas digitalizadas e processá-las com leitura de imagens (OCR) e IA, produzindo sugestões de nota com justificativa e indicador de confiança.
5. Exigir revisão e aprovação do professor antes da publicação de qualquer nota.
6. Permitir ao aluno consultar apenas as suas próprias notas e o seu histórico.
7. Registrar em auditoria as operações relevantes.
8. Demonstrar a qualidade do software por meio de testes unitários e de integração, cobertura mínima de 80%, relatório HTML e pipeline de integração contínua.

## 5. Público-alvo

| Público | Necessidade | Como o EduGrade atende |
|---|---|---|
| **Professores** | Reduzir o tempo de correção e manter critérios consistentes | Construtor de provas, gabarito com rubrica, correção sugerida e revisão assistida |
| **Alunos** | Acompanhar desempenho e receber notas com clareza | Portal de consulta de notas, médias, histórico e situação acadêmica |
| **Administração acadêmica** | Cadastros, permissões, auditoria e configuração institucional | Painel administrativo, regras acadêmicas configuráveis, auditoria |
| **Instituição** | Segurança, rastreabilidade e conformidade com a LGPD | Controle de acesso por perfil, auditoria, proteção de arquivos |

## 6. Requisitos

O detalhamento completo está em dois documentos complementares:

- **`REQUISITOS_FUNCIONAIS.md`**: 17 requisitos funcionais definidos pelo grupo (RF01–RF17), mais requisitos adicionais (RF18–RF29) e requisitos não funcionais (RNF01–RNF13).
- **`REGRAS_DE_NEGOCIO.md`**: 45 regras (RN01–RN45) que definem os limites do comportamento do sistema.

**Resumo dos requisitos principais**

| Área | Requisitos |
|---|---|
| Acesso | Login por perfil (aluno, professor, administrador), com controle de permissões no backend |
| Acadêmico | Cadastro de disciplinas, turmas, matrículas, períodos, notas e frequência; regras de média configuráveis |
| Provas | Criação de avaliações e provas, cadastro de gabaritos, pontuação com soma validada, versionamento |
| Impressão | PDF da prova do aluno e do gabarito do professor, impressão individual e em lote, QR Code por cópia |
| Correção | Envio de provas digitalizadas, correção assistida por IA, revisão do professor, publicação das notas |
| Governança | Auditoria, proteção de dados, testes e cobertura mínima |

**Regras de negócio mais importantes**

- O aluno **não** faz prova pela plataforma; a prova é presencial, em papel (RN03, RN04).
- A IA **apenas sugere**; o professor revisa e aprova (RN06, RN07, RN36, RN39).
- A nota só é publicada após aprovação e só então aparece para o aluno (RN08, RN14).
- A soma das questões deve igualar o valor total da prova (RN16).
- A prova mantém a versão do gabarito usada na aplicação (RN09, RN21, RN22).
- Alterações relevantes geram auditoria (RN10, RN40, RN41).

## 7. Solução proposta

### 7.1 Fluxo geral

1. O professor cria a prova e cadastra as questões.
2. O professor cadastra e confirma o gabarito e as rubricas.
3. O sistema calcula e valida a pontuação total.
4. O professor publica a prova; o sistema salva a **versão oficial imutável**.
5. O professor imprime as cópias, cada uma com identificador e QR Code próprios.
6. Os alunos respondem **no papel**, presencialmente.
7. O professor recolhe e **digitaliza** as folhas e envia ao sistema.
8. O sistema identifica a prova e o aluno, prepara as imagens e lê as respostas (OCR).
9. A IA compara as respostas com o gabarito e a rubrica e **sugere** pontuação e justificativa por questão, sinalizando baixa confiança.
10. O professor **revisa**: aprova, altera, rejeita, pede nova leitura ou marca como ilegível.
11. O professor aprova e o sistema **publica** a nota oficial.
12. O aluno consulta o resultado no portal.

### 7.2 Arquitetura

O sistema é organizado em camadas, com separação de responsabilidades:

| Camada | Tecnologia | Papel |
|---|---|---|
| Frontend | HTML, CSS e JavaScript | Telas do aluno, professor e administrador |
| Backend / API | Python com FastAPI | Regras de negócio, autenticação, permissões e serviços |
| Banco de dados | SQLite com SQLAlchemy | Persistência de usuários, estrutura acadêmica, provas, versões, correções e auditoria |
| Integrações | PDF, QR Code, OCR e IA | Geração de documentos, identificação, leitura de imagens e sugestão de correção |
| Qualidade | Pytest, Pytest-Cov e GitHub Actions | Testes, cobertura e integração contínua |

A camada de IA é **independente do provedor**, com adaptadores intercambiáveis (inclusive um adaptador simulado para testes), o que permite usar modelos locais, priorizando a proteção dos dados dos alunos.

### 7.3 Segurança e proteção de dados

Controle de acesso por perfil validado no backend, senhas armazenadas com hash, sessões com expiração, proteção de arquivos privados, validação de uploads, auditoria de operações e política de não enviar dados de alunos a provedores externos sem autorização institucional (LGPD).

### 7.4 Garantia de qualidade

- **Requisitos e regras rastreáveis** (RF e RN com códigos).
- **Testes unitários e de integração** (Fernando e Caio).
- **Testes funcionais** com 25 cenários, incluindo tentativas que o sistema deve bloquear (Lucas) — `CHECKLIST_VALIDACAO_FUNCIONAL.md`.
- **Registro de problemas** — `REGISTRO_PROBLEMAS.md`.
- **Cobertura mínima de 80%** com relatório HTML e pipeline que falha abaixo da meta.
- **Versionamento** com GitFlow e commits padronizados (Gabriel).

## 8. Relação com a ODS 4 — Educação de Qualidade

A ODS 4 busca assegurar uma educação inclusiva, equitativa e de qualidade. O EduGrade contribui de forma indireta, mas concreta, ao:

- **Liberar tempo do professor** de tarefas repetitivas para que ele possa dedicá-lo ao ensino e ao acompanhamento dos alunos;
- **Padronizar critérios de correção** por meio de gabaritos e rubricas, favorecendo avaliações mais justas e consistentes;
- **Dar transparência ao aluno**, que acompanha suas notas, médias e histórico e pode identificar dificuldades mais cedo;
- **Manter a avaliação presencial em papel**, sem exigir que o aluno tenha dispositivo ou conexão para fazer a prova, o que reduz barreiras de acesso;
- **Usar a IA com supervisão humana**, promovendo uma adoção responsável da tecnologia na educação.

> Os efeitos acima são **resultados esperados** do projeto; não há, neste trabalho, medição com usuários reais.

## 9. Resultados esperados

| Dimensão | Resultado esperado |
|---|---|
| Para o professor | Menos tempo na conferência e na correção; prova e gabarito organizados e versionados |
| Para o aluno | Consulta clara e segura das próprias notas e do histórico |
| Para a instituição | Rastreabilidade das notas, controle de acesso e conformidade com a proteção de dados |
| Para a disciplina de GQS | Projeto com requisitos, regras, testes (unitários, de integração e funcionais), cobertura ≥ 80%, relatório HTML, versionamento e pipeline de CI/CD, tudo com evidências reais |

## 10. Considerações finais

O EduGrade propõe um uso equilibrado da inteligência artificial na educação: ganhar velocidade e consistência na correção **sem retirar do professor a responsabilidade pela nota**. A decisão de manter a prova em papel e presencial aproxima a solução da realidade das escolas, e a exigência de revisão humana, versionamento e auditoria torna o processo verificável.

Do ponto de vista da Gestão e Qualidade de Software, o projeto mostra que um sistema só pode ser considerado pronto quando suas funcionalidades têm **evidência**: requisito definido, regra de negócio clara, teste executado e resultado registrado. Por isso este documento acompanha os arquivos de requisitos, regras de negócio, checklist de validação funcional e registro de problemas.

### 10.1 Limitações conhecidas

> **Atualizar esta seção antes da entrega**, com base no estado real da versão entregue.

Na revisão do repositório de 01/11/2026 (`docs/QA/`), constavam entre as pendências: cobertura de testes abaixo de 80%; upload de arquivos no processamento em lote ainda não implementado; correção por IA operando com provedor simulado, sem provedor real validado; dependências de OCR indisponíveis no ambiente de teste; logout sem revogação de token no servidor; e pipeline de CI versionado, mas ainda sem execução confirmada. Itens como histórico acadêmico dedicado, relatórios, painel de qualidade e rotina de backup não foram identificados no código e dependem de confirmação do grupo sobre o escopo da entrega. 

### 10.2 Trabalhos futuros

Relatórios analíticos por turma e por aluno, evolução da leitura de respostas manuscritas, avaliação institucional do uso de IA externa e ampliação dos testes de ponta a ponta.

---

## Referências internas

- `docs/REQUISITOS_FUNCIONAIS.md`
- `docs/REGRAS_DE_NEGOCIO.md`
- `docs/CHECKLIST_VALIDACAO_FUNCIONAL.md`
- `docs/REGISTRO_PROBLEMAS.md`
- `docs/QA/` (relatórios de auditoria e matriz de testes do grupo)
