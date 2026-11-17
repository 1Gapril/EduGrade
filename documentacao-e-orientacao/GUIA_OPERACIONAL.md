# 📢 GUIA OPERACIONAL DO GRUPO — EDUGRADE
## Plano de desenvolvimento, divisão de tarefas e integração com Claude Code

**Trabalho A3 Prático — Gestão e Qualidade de Software (GQS)**  
**Professor:** Daniel Henrique Matos de Paiva  
**Projeto:** EduGrade — Sistema de Gestão e Desempenho Acadêmico  
**ODS 4:** Educação de Qualidade

---

# 1. ORGANIZAÇÃO GERAL DO DESENVOLVIMENTO

A partir desta etapa, o desenvolvimento será organizado da seguinte maneira:

**Fernando será o responsável pelo desenvolvimento técnico e pela integração do sistema utilizando Claude Code.**

Os outros integrantes trabalharão em paralelo, preparando requisitos, documentação, validações, materiais acadêmicos e atividades de versionamento.

Isso significa que todos terão entregas próprias e participarão efetivamente do projeto.

| Integrante | Responsabilidade principal | Entrega |
|---|---|---|
| Fernando Almeida | Desenvolvimento com Claude Code, QA e integração | Sistema completo e testado |
| Lucas Henrique Miranda | Requisitos, regras acadêmicas e validação funcional | Documentação dos requisitos |
| Caio Duraes | Arquitetura, banco de dados e validação técnica | Modelo de dados e documentação técnica |
| Gabriel Ferreira | GitHub, documentação, DevOps e apresentação | Repositório organizado e materiais de entrega |

**Importante:** Fernando coordena a integração técnica, mas os demais integrantes devem revisar, testar e validar suas respectivas entregas.

---

# 2. RESPONSABILIDADES INDIVIDUAIS E PASSO A PASSO

## 2.1. FERNANDO ALMEIDA — RA 326132695

<badge color="success">Responsável pelo desenvolvimento com Claude Code</badge>

**Função:** Desenvolvedor principal, integração, qualidade de software e automação de testes.

### O que Fernando deverá fazer

1. Preparar o ambiente de desenvolvimento.
2. Abrir o projeto no Claude Code.
3. Fazer o levantamento da documentação e dos arquivos existentes.
4. Solicitar ao Claude Code a implementação do backend.
5. Solicitar a implementação do frontend.
6. Implementar e integrar o banco de dados.
7. Implementar autenticação e permissões.
8. Desenvolver o sistema de provas presenciais.
9. Integrar o serviço de correção assistida por IA.
10. Criar os testes unitários e de integração.
11. Gerar o relatório HTML de cobertura.
12. Configurar e validar o CI/CD.
13. Integrar as entregas dos outros integrantes.
14. Preparar a versão final para apresentação.

### Sequência de trabalho de Fernando

**ETAPA 1 — Diagnóstico**

Antes de programar, solicitar ao Claude Code que:
- Leia toda a documentação disponível.
- Examine a estrutura do projeto.
- Identifique tecnologias já utilizadas.
- Verifique arquivos existentes.
- Identifique funcionalidades já implementadas.
- Identifique falhas, duplicações e pendências.
- Não apague nem substitua arquivos sem necessidade.
- Apresente um plano de implementação.

**ETAPA 2 — Backend**

Desenvolver:
- API com FastAPI.
- Modelos e validações.
- Autenticação.
- Controle de permissões.
- Regras acadêmicas.
- Serviços de alunos, professores e administradores.
- Gerenciamento de disciplinas, turmas e avaliações.
- Serviços de notas e frequência.
- Persistência no banco de dados.

**ETAPA 3 — Frontend**

Desenvolver:
- Tela de login.
- Painel do aluno.
- Painel do professor.
- Painel administrativo.
- Formulários de cadastro.
- Consulta de notas.
- Gerenciamento de avaliações.
- Construtor de provas.
- Revisão de correções.
- Painel de qualidade.

**ETAPA 4 — Provas presenciais**

Implementar:
- Editor de provas.
- Cadastro de questões.
- Gabarito e critérios.
- Distribuição de pontuação.
- Validação automática da soma dos pontos.
- Versionamento das provas.
- Geração de PDF.
- Impressão individual e em lote.
- Identificação das cópias por código ou QR Code.
- Envio das provas digitalizadas.

**ETAPA 5 — Inteligência artificial**

Implementar uma camada independente do provedor de IA, com:
- Leitura de documentos.
- OCR e processamento de imagens.
- Análise das respostas.
- Comparação com gabaritos e rubricas.
- Sugestão de pontuação.
- Justificativa da correção.
- Identificação de baixa confiança.
- Encaminhamento para revisão manual.

A IA não pode publicar notas automaticamente. A aprovação final será sempre do professor.

**ETAPA 6 — Testes e qualidade**

- Criar testes unitários.
- Criar testes de integração.
- Testar permissões.
- Testar regras acadêmicas.
- Testar criação e impressão de provas.
- Testar a integração da IA utilizando mocks nos testes automatizados.
- Buscar cobertura mínima de 80%.
- Gerar o relatório HTML.
- Configurar GitHub Actions.

### Entregas de Fernando

- Código-fonte do backend.
- Código-fonte do frontend.
- Banco de dados funcional.
- Testes automatizados.
- Relatório HTML de cobertura.
- Pipeline CI/CD.
- Aplicação executável.
- Documentação técnica da implementação.

---

## 2.2. LUCAS HENRIQUE MIRANDA — RA 325131396

**Função:** Product Owner, requisitos e validação funcional.

Lucas será responsável por definir com clareza o que o sistema precisa fazer e conferir se o que foi desenvolvido atende às necessidades acadêmicas.

### PASSO A PASSO DE LUCAS

**Passo 1 — Preparar os requisitos**

Criar o arquivo:

`docs/REQUISITOS_FUNCIONAIS.md`

Documentar as funcionalidades:

- RF01 — Login de aluno.
- RF02 — Login de professor.
- RF03 — Login administrativo.
- RF04 — Consulta de notas.
- RF05 — Cadastro de disciplinas.
- RF06 — Cadastro de turmas.
- RF07 — Lançamento de notas.
- RF08 — Consulta do histórico acadêmico.
- RF09 — Criação de avaliações.
- RF10 — Criação de provas presenciais.
- RF11 — Impressão das provas.
- RF12 — Cadastro de gabaritos.
- RF13 — Envio de provas digitalizadas.
- RF14 — Correção assistida por IA.
- RF15 — Revisão da correção pelo professor.
- RF16 — Publicação das notas.
- RF17 — Auditoria das alterações.

**Passo 2 — Documentar as regras de negócio**

Criar:

`docs/REGRAS_DE_NEGOCIO.md`

Exemplos:

| Código | Regra |
|---|---|
| RN01 | O aluno consulta somente suas próprias notas |
| RN02 | Somente professor autorizado pode lançar notas |
| RN03 | O aluno não realiza provas pela plataforma |
| RN04 | Provas são aplicadas presencialmente em papel |
| RN05 | O professor cadastra previamente o gabarito |
| RN06 | A IA apenas sugere a correção |
| RN07 | O professor precisa aprovar as notas |
| RN08 | Notas oficiais só são publicadas após aprovação |
| RN09 | A prova deve manter a versão do gabarito utilizado |
| RN10 | Alterações relevantes devem gerar auditoria |

**Passo 3 — Validar os fluxos**

Lucas deverá testar o sistema com os seguintes cenários:

1. Aluno entra com RA e senha.
2. Aluno consulta suas notas.
3. Aluno tenta acessar as notas de outro aluno.
4. Professor entra no sistema.
5. Professor acessa uma turma autorizada.
6. Professor cria uma prova.
7. Professor cadastra o gabarito.
8. Professor imprime a prova.
9. Professor envia a prova digitalizada.
10. Professor revisa a correção sugerida pela IA.
11. Professor publica as notas.

**Passo 4 — Produzir o documento acadêmico**

Criar ou atualizar:

`docs/DOCUMENTO_ENTREGA_A3.md`

O documento deverá apresentar:
- Introdução.
- Problema identificado.
- Justificativa.
- Objetivos.
- Público-alvo.
- Requisitos.
- Solução proposta.
- Relação com a ODS 4.
- Resultados esperados.
- Considerações finais.

**Passo 5 — Entregar para Fernando**

Enviar os documentos finalizados para revisão e integração.

### Entregas de Lucas

- `REQUISITOS_FUNCIONAIS.md`
- `REGRAS_DE_NEGOCIO.md`
- `DOCUMENTO_ENTREGA_A3.md`
- Checklist de validação funcional.
- Registro dos problemas encontrados durante os testes.

---

## 2.3. CAIO DURAES — RA 325132875

**Função:** Arquitetura de software, modelagem de dados e validação técnica.

Caio ficará responsável por revisar a arquitetura e garantir que a estrutura de dados faça sentido para o funcionamento do EduGrade.

### PASSO A PASSO DE CAIO

**Passo 1 — Estudar a arquitetura**

Analisar a estrutura proposta:

- Backend.
- Frontend.
- Banco de dados.
- API.
- Camada de serviços.
- Camada de persistência.
- Autenticação.
- Integração com IA.

**Passo 2 — Criar o modelo de dados**

Criar:

`docs/MODELO_BANCO_DE_DADOS.md`

Documentar as tabelas:

- users
- students
- teachers
- administrators
- courses
- classes
- subjects
- enrollments
- teacher_subjects
- academic_periods
- assessments
- grades
- attendance
- exams
- exam_versions
- exam_questions
- answer_keys
- grading_rubrics
- exam_copies
- exam_submissions
- submission_pages
- extracted_answers
- ai_corrections
- correction_reviews
- audit_logs

Para cada tabela, especificar:
- Finalidade.
- Campos.
- Tipos de dados.
- Chave primária.
- Chaves estrangeiras.
- Restrições.
- Relacionamentos.

**Passo 3 — Criar os diagramas**

Produzir:
- Diagrama entidade-relacionamento.
- Diagrama de arquitetura.
- Diagrama de fluxo de autenticação.
- Diagrama do fluxo de correção de provas.

**Passo 4 — Validar o banco de dados**

Verificar:
- Integridade referencial.
- Relacionamentos.
- Restrições de unicidade.
- Índices.
- Persistência.
- Migrações.
- Consistência das pontuações.
- Versionamento de provas.

**Passo 5 — Revisar o backend**

Depois que Fernando disponibilizar as primeiras versões:
- Revisar os endpoints.
- Conferir os modelos.
- Conferir os relacionamentos.
- Validar as regras de negócio.
- Verificar possíveis falhas de segurança.
- Executar os testes de integração disponíveis.

**Passo 6 — Entregar para Fernando**

Enviar o modelo de dados, diagramas e observações técnicas.

### Entregas de Caio

- `MODELO_BANCO_DE_DADOS.md`
- Diagrama entidade-relacionamento.
- Diagrama de arquitetura.
- Diagrama de fluxos.
- Checklist técnico.
- Relatório de revisão do backend.

**Importante:** Caio não deve criar um segundo banco ou uma implementação paralela. O modelo deverá ser validado com Fernando antes de qualquer alteração na estrutura real do banco.

---

## 2.4. GABRIEL FERREIRA — RA 325140970

**Função:** GitHub, versionamento, documentação, DevOps e apresentação.

Gabriel ficará responsável por manter o projeto organizado e preparar a entrega acadêmica.

### PASSO A PASSO DE GABRIEL

**Passo 1 — Preparar o repositório**

Verificar:
- Repositório GitHub.
- Acesso de todos os integrantes.
- Branch principal.
- Branch de desenvolvimento.
- Proteção da branch principal, quando disponível.
- README.
- `.gitignore`.

**Passo 2 — Organizar o GitFlow**

Utilizar:

```text
main
develop
feature/backend
feature/frontend
feature/tests
feature/documentation
fix/corrections
```

O desenvolvimento de Fernando deve ser integrado por etapas, com commits identificáveis.

**Passo 3 — Padronizar os commits**

Exemplos:

```bash
git add .
git commit -m "feat: implement academic dashboard"

git add .
git commit -m "feat: add exam builder"

git add .
git commit -m "test: add authentication tests"

git add .
git commit -m "docs: update project documentation"

git add .
git commit -m "ci: configure automated tests"
```

**Passo 4 — Organizar o README**

O arquivo `README.md` deverá conter:
- Nome do projeto.
- Descrição.
- Objetivo.
- Tecnologias.
- Funcionalidades.
- Estrutura de pastas.
- Requisitos de instalação.
- Comandos para execução.
- Comandos para testes.
- Como visualizar a cobertura.
- Como configurar o ambiente.
- Integrantes da equipe.

**Passo 5 — Acompanhar o CI/CD**

Gabriel deverá verificar:
- Se o GitHub Actions está executando.
- Se os testes passam.
- Se a cobertura é calculada.
- Se o pipeline falha quando a cobertura fica abaixo de 80%.
- Se os relatórios são armazenados como artefatos.

**Passo 6 — Preparar a apresentação**

Criar:

`docs/ROTEIRO_APRESENTACAO_A3.md`

Organizar os slides:
1. Capa.
2. Problema.
3. Objetivo.
4. ODS 4.
5. Público-alvo.
6. Arquitetura.
7. Banco de dados.
8. Funcionalidades do aluno.
9. Funcionalidades do professor.
10. Criação e impressão das provas.
11. Correção assistida por IA.
12. Segurança.
13. Testes.
14. Cobertura.
15. CI/CD.
16. Resultados.
17. Conclusão.

**Passo 7 — Preparar os materiais finais**

- PowerPoint.
- Roteiro de apresentação.
- Roteiro do vídeo pitch.
- Capturas de tela reais do sistema.
- Evidências dos testes.
- Evidências do GitHub Actions.

### Entregas de Gabriel

- Repositório organizado.
- README atualizado.
- Branches e commits organizados.
- Pipeline acompanhado.
- `ROTEIRO_APRESENTACAO_A3.md`
- Slides.
- Roteiro do vídeo pitch.

---

# 3. COMO A EQUIPE VAI TRABALHAR JUNTA

Para evitar conflitos, o trabalho será dividido em ciclos.

## Ciclo 1 — Planejamento e diagnóstico

| Integrante | Atividade |
|---|---|
| Fernando | Diagnosticar o projeto com Claude Code |
| Lucas | Especificar requisitos e regras acadêmicas |
| Caio | Modelar o banco e a arquitetura |
| Gabriel | Organizar GitHub e documentação |

**Condição para avançar:** requisitos e arquitetura revisados pela equipe.

## Ciclo 2 — Estrutura inicial

| Integrante | Atividade |
|---|---|
| Fernando | Implementar estrutura do backend e frontend |
| Lucas | Validar telas e fluxos esperados |
| Caio | Revisar modelos e relacionamentos |
| Gabriel | Organizar branches e README |

**Condição para avançar:** aplicação inicial executável e banco persistente.

## Ciclo 3 — Funcionalidades acadêmicas

| Integrante | Atividade |
|---|---|
| Fernando | Implementar autenticação, perfis, notas e avaliações |
| Lucas | Validar regras de negócio |
| Caio | Revisar persistência e integração |
| Gabriel | Documentar funcionalidades e commits |

**Condição para avançar:** os três perfis funcionando com permissões corretas.

## Ciclo 4 — Provas e inteligência artificial

| Integrante | Atividade |
|---|---|
| Fernando | Implementar provas, PDF, OCR e integração com IA |
| Lucas | Validar questões, gabaritos e fluxo de correção |
| Caio | Revisar versionamento e banco de dados |
| Gabriel | Documentar o fluxo e preparar demonstração |

**Condição para avançar:** prova criada, impressa, digitalizada, corrigida e revisada pelo professor em ambiente de teste.

## Ciclo 5 — Testes e qualidade

| Integrante | Atividade |
|---|---|
| Fernando | Desenvolver e executar testes |
| Lucas | Executar testes funcionais |
| Caio | Executar testes de integração e persistência |
| Gabriel | Verificar pipeline e artefatos |

**Condição para avançar:** cobertura mínima de 80%, sem falhas críticas conhecidas.

## Ciclo 6 — Entrega

| Integrante | Atividade |
|---|---|
| Fernando | Preparar versão estável |
| Lucas | Revisar documento acadêmico |
| Caio | Revisar documentação técnica |
| Gabriel | Finalizar slides, README e repositório |

**Condição final:** todos os documentos, evidências e funcionalidades conferidos.

---

# 4. COMO FERNANDO DEVE UTILIZAR O CLAUDE CODE

O Claude Code será utilizado como agente de desenvolvimento, mas o código deverá ser revisado e testado antes de ser considerado concluído.

## Etapa 1 — Abrir o projeto

Abrir o terminal na pasta do EduGrade e executar o Claude Code conforme a instalação existente.

Exemplo:

```bash
cd caminho/do/projeto/EduGrade
claude
```

## Etapa 2 — Fazer o diagnóstico antes de alterar arquivos

Enviar ao Claude Code:

```text
Você será o engenheiro de software responsável por analisar o projeto EduGrade.

Antes de modificar qualquer arquivo:

1. Leia toda a documentação disponível.
2. Analise a estrutura completa do repositório.
3. Identifique a stack existente.
4. Identifique funcionalidades implementadas.
5. Identifique funcionalidades pendentes.
6. Identifique problemas de arquitetura.
7. Identifique riscos de segurança.
8. Identifique problemas no banco de dados.
9. Identifique testes existentes.
10. Identifique a cobertura atual.

Não apague arquivos.
Não substitua a arquitetura sem justificativa.
Não invente funcionalidades já implementadas.
Não declare testes aprovados sem executá-los.

Primeiro, produza um relatório de diagnóstico e um plano de execução dividido em etapas.

Aguarde minha aprovação antes de iniciar mudanças estruturais.
```

## Etapa 3 — Implementar por módulos

Depois do diagnóstico, Fernando deverá solicitar a implementação em etapas:

1. Estrutura do projeto.
2. Banco de dados e migrações.
3. Backend.
4. Autenticação e permissões.
5. Frontend.
6. Regras acadêmicas.
7. Construtor de provas.
8. Geração de PDF.
9. Upload e processamento de provas.
10. Integração com IA.
11. Revisão e publicação de notas.
12. Testes automatizados.
13. Cobertura HTML.
14. CI/CD.
15. Documentação final.

**Não solicitar que o Claude altere tudo de uma só vez.** Cada etapa deverá ser implementada, executada, testada e revisada antes de avançar.

## Etapa 4 — Utilizar os documentos dos integrantes

Quando Lucas entregar os requisitos:

```text
Leia docs/REQUISITOS_FUNCIONAIS.md e
docs/REGRAS_DE_NEGOCIO.md.

Compare os documentos com o sistema implementado.

Identifique funcionalidades ausentes, divergências e regras não atendidas.

Implemente somente após apresentar um plano de correção.
```

Quando Caio entregar o modelo de dados:

```text
Leia docs/MODELO_BANCO_DE_DADOS.md.

Compare o modelo com a estrutura real do banco.

Verifique chaves primárias, estrangeiras, índices,
restrições, relacionamentos e integridade referencial.

Não recrie o banco se ele já estiver implementado.

Apresente as divergências e proponha migrações seguras.
```

Quando Gabriel entregar a documentação:

```text
Revise o README e a documentação do projeto.

Compare todos os comandos documentados com os comandos reais.

Verifique se os caminhos dos arquivos existem.

Não documente funcionalidades que ainda não foram implementadas.
```

---

# 5. REGRAS DE INTEGRAÇÃO PARA EVITAR CONFLITOS

1. Fernando será o responsável por integrar o código principal.
2. Os outros integrantes não deverão modificar diretamente os mesmos arquivos que estiverem sendo trabalhados por Fernando.
3. Alterações no banco devem ser discutidas antes de criar migrações.
4. Os requisitos devem ser documentados antes de solicitar mudanças importantes.
5. Cada funcionalidade deverá ter uma evidência de implementação ou teste.
6. Nenhum integrante deve alterar a branch `main` diretamente.
7. Todo código integrado deverá passar por testes.
8. Toda falha identificada deverá ser registrada.
9. Não compartilhar senhas, tokens ou arquivos `.env`.
10. Os relatórios de testes devem corresponder à versão realmente executada.

## Comunicação da equipe

Manter um registro compartilhado com:

| Data | Responsável | Atividade | Status | Evidência |
|---|---|---|---|---|
| Data | Fernando | Backend | Em andamento | Commit/PR |
| Data | Lucas | Requisitos | Pendente | Documento |
| Data | Caio | Banco de dados | Pendente | Diagrama |
| Data | Gabriel | GitHub | Pendente | Repositório |

Status permitidos:
- Pendente.
- Em andamento.
- Em revisão.
- Concluído.
- Bloqueado.

---

# 6. CRITÉRIOS PARA CONSIDERAR O PROJETO CONCLUÍDO

## Sistema
- [ ] Backend funcional.
- [ ] Frontend funcional.
- [ ] Banco de dados persistente.
- [ ] Login de aluno, professor e administrador.
- [ ] Controle de permissões no backend.
- [ ] Consulta de notas.
- [ ] Lançamento de notas pelo professor autorizado.
- [ ] Criação de avaliações.
- [ ] Criação de provas presenciais.
- [ ] Gabarito salvo antes da aplicação.
- [ ] Impressão em PDF.
- [ ] Envio de provas digitalizadas.
- [ ] Correção assistida por IA.
- [ ] Revisão humana obrigatória.
- [ ] Publicação de notas oficiais.
- [ ] Auditoria das operações relevantes.

## Qualidade
- [ ] Testes unitários.
- [ ] Testes de integração.
- [ ] Testes de segurança e permissões.
- [ ] Cobertura mínima de 80%.
- [ ] Relatório HTML.
- [ ] GitHub Actions funcionando.
- [ ] Nenhuma falha crítica conhecida.

## Documentação
- [ ] Requisitos funcionais.
- [ ] Regras de negócio.
- [ ] Modelo de banco de dados.
- [ ] Arquitetura.
- [ ] README.
- [ ] Documento acadêmico.
- [ ] Roteiro de apresentação.
- [ ] Slides.
- [ ] Evidências reais do sistema.

---

# 7. RESULTADO ESPERADO

Ao final, a equipe deverá entregar um sistema acadêmico integrado, com frontend, backend e banco de dados, que permita ao aluno acompanhar seu desempenho e ao professor gerenciar avaliações, criar provas presenciais, imprimir documentos e utilizar inteligência artificial como apoio à correção.

A equipe também deverá comprovar a qualidade do desenvolvimento por meio de testes automatizados, cobertura mínima de 80%, relatório HTML, versionamento e integração contínua.

**Fernando será responsável por conduzir a implementação com Claude Code, enquanto Lucas, Caio e Gabriel trabalharão nas entregas paralelas e na validação do projeto.**

O trabalho é coletivo: cada integrante deve conhecer o funcionamento geral do EduGrade e estar preparado para explicar sua própria contribuição na apresentação.

**Objetivo final: entregar um software funcional, seguro, documentado e testável, alinhado à atividade A3 de Gestão e Qualidade de Software e à ODS 4 — Educação de Qualidade.**