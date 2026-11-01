# PROMPT MESTRE DEFINITIVO — EDUGRADE
## Sistema Full Stack de Gestão Acadêmica com Inteligência Artificial para Correção de Provas Físicas

**Projeto:** EduGrade — Gestão e Desempenho Acadêmico  
**Módulo de IA:** EduGrade IA  
**Tipo:** Aplicação Full Stack  
**Objetivo:** Sistema acadêmico real, com backend, frontend, banco de dados, autenticação, inteligência artificial, geração de provas, impressão, correção automatizada, testes e documentação.

---

# 1. MISSÃO DO PROJETO

Atue como uma equipe profissional de engenharia de software, formada por:

- Arquiteto de software.
- Desenvolvedor Backend.
- Desenvolvedor Frontend.
- Engenheiro de banco de dados.
- Engenheiro de Inteligência Artificial.
- Especialista em OCR e visão computacional.
- Engenheiro de testes e qualidade.
- Engenheiro DevOps.
- Especialista em segurança da informação.

Desenvolva uma aplicação completa chamada EduGrade.

O projeto deverá funcionar de verdade, com integração entre frontend, backend, banco de dados e serviços de inteligência artificial.

Não entregar apenas protótipo, demonstração visual, telas estáticas ou funcionalidades simuladas.

Todas as funcionalidades deverão possuir implementação real, validações, persistência, controle de permissões e testes.

Utilize o Free Claude Code (FCC) como ambiente de conexão com os modelos de IA disponíveis. Não confunda o FCC com o provedor de IA utilizado pela aplicação.

O sistema EduGrade deverá funcionar independentemente do agente de desenvolvimento utilizado.

# 2. OBJETIVO PRINCIPAL

Criar uma plataforma acadêmica que permita:

1. Cadastro e gerenciamento de alunos.
2. Cadastro e gerenciamento de professores.
3. Cadastro de cursos, disciplinas e turmas.
4. Gerenciamento de matrículas.
5. Cadastro de avaliações.
6. Criação de provas diretamente pelo professor.
7. Cadastro e armazenamento de gabaritos.
8. Geração de provas em PDF.
9. Impressão individual e em lote.
10. Aplicação presencial das avaliações em papel.
11. Digitalização das provas respondidas.
12. Leitura de respostas por OCR e IA.
13. Correção automatizada sugerida pela IA.
14. Revisão obrigatória pelo professor.
15. Publicação das notas oficiais.
16. Consulta das notas pelo aluno.
17. Relatórios acadêmicos.
18. Auditoria.
19. Painel administrativo.
20. Monitoramento de testes e qualidade do software.

# 3. REGRA FUNDAMENTAL: PROVAS PRESENCIAIS

O aluno não fará provas online.

A avaliação será realizada em papel, presencialmente.

O EduGrade será utilizado pelo professor para preparar, imprimir, corrigir e publicar as notas.

O aluno utilizará o portal somente para consultar suas informações acadêmicas.

O fluxo principal será:

1. Professor cria a prova.
2. Professor cadastra as questões.
3. Professor cadastra o gabarito.
4. Sistema calcula e valida a pontuação.
5. Professor publica a avaliação.
6. Sistema salva a versão oficial.
7. Professor imprime as provas.
8. Alunos respondem no papel.
9. Professor recolhe as folhas.
10. Professor digitaliza as provas.
11. Sistema identifica os alunos e as avaliações.
12. IA lê e corrige as respostas.
13. Professor revisa as sugestões.
14. Professor aprova as notas.
15. Sistema publica as notas.
16. Alunos consultam os resultados.

# 4. TECNOLOGIAS

Utilizar preferencialmente:

## Backend

- Python 3.
- FastAPI.
- Pydantic.
- SQLAlchemy.
- Alembic.
- Pytest.
- Pytest-Cov.
- Argon2id.
- JWT ou sessão segura.

## Frontend

- HTML5.
- CSS3.
- JavaScript.
- Bootstrap ou CSS responsivo.
- Chart.js.
- Fetch API.

## Banco de dados

- SQLite.
- SQLAlchemy.
- Migrações.
- Chaves primárias e estrangeiras.
- Índices.
- Transações.
- Integridade referencial.

## Inteligência artificial

- Ollama.
- Modelos multimodais compatíveis.
- Provedores externos configuráveis.
- OpenCV.
- PaddleOCR ou alternativa.
- Tesseract como alternativa para texto impresso.
- Camada abstrata de IA.

## PDF e impressão

Utilizar bibliotecas Python adequadas, como ReportLab, para gerar documentos de impressão.

## DevOps

- Git.
- GitHub Actions.
- CI/CD.
- Pytest-Cov.
- Documentação automatizada.

Antes de escolher versões, verificar compatibilidade entre dependências e ambiente.

# 5. ARQUITETURA DO PROJETO

Criar uma arquitetura modular:

EduGrade/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── security/
│   │   ├── database/
│   │   ├── integrations/
│   │   │   ├── ai/
│   │   │   ├── ocr/
│   │   │   ├── pdf/
│   │   │   └── storage/
│   │   └── main.py
│   ├── migrations/
│   └── requirements.txt
│
├── frontend/
│   ├── aluno/
│   ├── professor/
│   ├── admin/
│   ├── assets/
│   ├── css/
│   └── js/
│
├── ai/
│   ├── providers/
│   ├── prompts/
│   ├── schemas/
│   ├── pipelines/
│   └── evaluation/
│
├── storage/
│   ├── exams/
│   ├── processed/
│   ├── backups/
│   └── temp/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── security/
│   ├── ai/
│   └── fixtures/
│
├── reports/
│   └── coverage/
│
├── docs/
├── scripts/
├── .github/
│   └── workflows/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md

Ajustar a estrutura quando necessário, preservando separação de responsabilidades.

# 6. AUTENTICAÇÃO E PERFIS

Implementar três perfis independentes.

## 6.1 ALUNO

Login por RA ou RM e senha individual.

Funcionalidades:

- Consultar notas.
- Consultar médias.
- Consultar disciplinas.
- Consultar avaliações.
- Consultar histórico.
- Consultar situação acadêmica.
- Visualizar resultados publicados.
- Alterar senha.
- Atualizar dados permitidos.

O aluno não poderá:
- Criar avaliações.
- Alterar gabaritos.
- Lançar notas.
- Alterar resultados.
- Visualizar informações de outros alunos.

## 6.2 PROFESSOR

Login individual.

Funcionalidades:

- Consultar turmas.
- Consultar alunos matriculados.
- Gerenciar disciplinas autorizadas.
- Criar avaliações.
- Criar provas.
- Cadastrar gabaritos.
- Definir pontuações.
- Gerar PDF.
- Imprimir provas.
- Fazer upload das provas respondidas.
- Solicitar correção da IA.
- Revisar respostas.
- Alterar pontuação sugerida.
- Aprovar notas.
- Publicar resultados.
- Consultar relatórios.

Um professor somente poderá operar nas turmas e disciplinas autorizadas.

## 6.3 ADMINISTRADOR

Funcionalidades:

- Gerenciar usuários.
- Gerenciar professores.
- Gerenciar alunos.
- Gerenciar cursos.
- Gerenciar disciplinas.
- Gerenciar turmas.
- Gerenciar matrículas.
- Gerenciar períodos.
- Gerenciar configurações.
- Consultar auditoria.
- Gerenciar provedores de IA.
- Consultar relatórios.
- Acessar painel de qualidade.

O administrador não terá automaticamente autorização para lançar notas.

## 6.4 Segurança

- Hash de senha.
- Controle RBAC.
- Proteção dos endpoints.
- Expiração de sessão.
- Logs de acesso.
- Auditoria.
- Validação no backend.
- Proteção contra SQL Injection.
- Proteção de arquivos.
- Limitação de requisições.
- Tratamento seguro de erros.

# 7. MÓDULO ACADÊMICO

Implementar:

- Cursos.
- Disciplinas.
- Turmas.
- Alunos.
- Professores.
- Matrículas.
- Períodos letivos.
- Avaliações.
- Notas.
- Frequência.
- Histórico.
- Situação acadêmica.

Criar regras configuráveis para:

- A1.
- A2.
- A3.
- Recuperação.
- Exame final.
- Avaliações complementares.

Não impor pesos acadêmicos fixos.

O administrador deverá poder configurar os critérios institucionais.

Implementar cálculos de:

- Média ponderada.
- Nota necessária.
- Situação de aprovação.
- Recuperação.
- Histórico de desempenho.

Utilizar Decimal para valores de notas e pontuações.

# 8. CONSTRUTOR DE PROVAS DO PROFESSOR

Implementar um módulo completo de criação de avaliações.

O professor deverá conseguir criar uma prova inteira dentro do sistema, sem depender de ferramentas externas.

## 8.1 Informações da avaliação

- Título.
- Descrição.
- Curso.
- Disciplina.
- Turma.
- Professor.
- Data.
- Valor total.
- Instruções.
- Quantidade de questões.
- Configuração de impressão.

## 8.2 Editor de questões

Permitir:

- Adicionar questões.
- Remover questões.
- Duplicar questões.
- Reordenar questões.
- Editar enunciados.
- Configurar alternativas.
- Definir tipos.
- Definir pontuação.

Tipos:

- Objetiva.
- Discursiva.
- Resposta curta.
- Cálculo.
- Questão com múltiplos critérios.

## 8.3 Gabarito

Para cada questão, armazenar:

- Resposta correta.
- Resposta esperada.
- Alternativas aceitas.
- Critérios.
- Rubrica.
- Pontuação parcial.
- Palavras-chave.
- Conceitos obrigatórios.
- Justificativa.

O professor deverá revisar e confirmar o gabarito oficial.

## 8.4 Pontuação livre

O professor determina livremente os valores.

Exemplo:

Valor total: 10 pontos.

- Q1: 0,5.
- Q2: 1,5.
- Q3: 2,0.
- Q4: 3,0.
- Q5: 3,0.

O sistema deverá somar automaticamente e validar o valor total.

Não permitir publicação quando os valores não corresponderem ao total configurado.

Cada questão deve possuir pontuação positiva.

A pontuação sugerida nunca poderá ultrapassar o máximo da questão.

## 8.5 Salvamento automático

Implementar salvamento automático e manual.

Estados:

- Rascunho.
- Em edição.
- Aguardando validação.
- Publicada.
- Impressa.
- Em aplicação.
- Aguardando correção.
- Em correção.
- Aguardando revisão.
- Finalizada.
- Cancelada.

## 8.6 Versionamento

Toda publicação deverá gerar uma versão imutável.

Guardar:
- Questões.
- Gabarito.
- Pontuação.
- Rubricas.
- Professor.
- Data.
- Identificador da versão.

Alterações posteriores deverão gerar uma nova versão.

A prova já aplicada deverá continuar vinculada à versão original.

# 9. GERAÇÃO DE PDF E IMPRESSÃO

O professor deverá conseguir visualizar e imprimir a prova diretamente pelo EduGrade.

Criar dois documentos distintos.

## 9.1 Prova do aluno

Deverá conter:

- Cabeçalho.
- Nome da instituição.
- Curso.
- Disciplina.
- Professor.
- Turma.
- Avaliação.
- Campo para nome.
- Campo para RA/RM.
- Data.
- Instruções.
- Questões.
- Alternativas.
- Espaço para respostas manuscritas.
- Numeração de páginas.
- QR Code.

Não incluir gabarito.

## 9.2 Gabarito do professor

Deverá conter:

- Questões.
- Respostas corretas.
- Critérios.
- Rubricas.
- Pontuações.
- Respostas alternativas aceitas.

O documento deve ser protegido por autorização do professor.

## 9.3 Impressão

Permitir:

- Visualização prévia.
- Download PDF.
- Impressão direta.
- Impressão individual.
- Impressão em lote.
- Reimpressão.
- Histórico de impressão.

Criar um identificador individual para cada cópia.

## 9.4 QR Code

Gerar QR Code com identificador seguro.

Associar:
- Avaliação.
- Versão.
- Turma.
- Identificador da cópia.
- Aluno, quando individualizada.

Não colocar gabarito, senha ou dados sensíveis diretamente no QR Code.

Permitir associação manual quando a identificação falhar.

# 10. DIGITALIZAÇÃO E UPLOAD

Aceitar:

- PDF.
- JPG.
- JPEG.
- PNG.

Suportar arquivos únicos e múltiplos.

Suportar PDF com várias páginas.

Validar:
- Extensão.
- MIME.
- Tamanho.
- Integridade.
- Tipo de arquivo.

Preservar os originais.

Implementar armazenamento protegido e acesso restrito.

# 11. PROCESSAMENTO DE IMAGENS E OCR

Utilizar OpenCV para:

- Corrigir rotação.
- Corrigir perspectiva.
- Remover ruído.
- Ajustar contraste.
- Preparar imagens.
- Identificar regiões.
- Recortar questões.

Implementar camada abstrata de OCR.

Avaliar:
- PaddleOCR.
- Tesseract.
- Modelos multimodais.

Diferenciar texto impresso de manuscrito.

Não considerar OCR tradicional suficiente para todas as respostas manuscritas.

Separar confiança da leitura e confiança da avaliação.

Quando a leitura estiver ilegível, encaminhar para revisão manual.

# 12. EDUGRADE IA — CORREÇÃO AUTOMATIZADA

Implementar uma camada independente de inteligência artificial.

A IA receberá:

- Enunciado.
- Gabarito.
- Pontuação máxima.
- Rubrica.
- Critérios.
- Resposta identificada.
- Imagem da resposta, quando necessário.

A IA deverá devolver dados estruturados:

- Resposta reconhecida.
- Interpretação.
- Pontuação sugerida.
- Pontuação máxima.
- Justificativa.
- Critérios atendidos.
- Critérios não atendidos.
- Erros conceituais.
- Confiança OCR.
- Confiança da avaliação.
- Indicador de revisão.

## 12.1 Questões objetivas

Corrigir deterministicamente quando a alternativa estiver identificada com segurança.

## 12.2 Questões discursivas

Reconhecer:

- Sinônimos.
- Explicações equivalentes.
- Conceitos corretos.
- Respostas parciais.
- Erros conceituais.
- Contradições.
- Respostas incompletas.

Não exigir texto idêntico ao gabarito.

Não penalizar gramática ou ortografia se não fizer parte da rubrica.

## 12.3 Questões de cálculo

Analisar:
- Fórmulas.
- Desenvolvimento.
- Operações.
- Resultado.
- Unidades.
- Etapas intermediárias.

Conceder pontos parciais conforme a rubrica.

## 12.4 Controle da IA

A IA não poderá:

- Modificar o gabarito.
- Alterar os pesos.
- Alterar o valor total.
- Publicar notas.
- Aprovar a própria correção.
- Alterar permissões.

O backend deverá validar todos os valores.

A IA somente produz sugestões.

# 13. INTERAÇÃO ENTRE PROFESSOR E IA

Criar uma interface própria de revisão.

O professor deverá visualizar:

- Imagem original.
- Imagem processada.
- Recorte da questão.
- Resposta reconhecida.
- Gabarito.
- Rubrica.
- Pontuação sugerida.
- Justificativa.
- Indicadores de confiança.

Ações disponíveis:

- Aprovar sugestão.
- Alterar pontuação.
- Corrigir texto reconhecido.
- Rejeitar sugestão.
- Solicitar nova leitura.
- Marcar ilegível.
- Adicionar comentário.

Toda alteração deverá gerar auditoria.

Mesmo quando a IA tiver alta confiança, a publicação dependerá da revisão humana.

# 14. PUBLICAÇÃO DAS NOTAS

Após revisão:

1. Validar todas as questões.
2. Calcular o total.
3. Validar os limites.
4. Registrar a versão do gabarito.
5. Registrar o professor.
6. Registrar data e horário.
7. Registrar sugestão original da IA.
8. Registrar pontuação final.
9. Registrar alterações.
10. Publicar a nota oficial.

O aluno poderá consultar a nota somente depois da publicação.

# 15. PROVEDORES DE INTELIGÊNCIA ARTIFICIAL

Criar adaptadores:

- OllamaProvider.
- CloudProvider.
- MockProvider.

Criar interface com métodos:

- generate_text.
- analyze_image.
- analyze_document.
- health_check.
- get_available_models.

Permitir configurar:

- Provedor.
- Modelo.
- URL.
- Credenciais.
- Timeout.
- Limites.
- Tentativas.
- Modelo textual.
- Modelo multimodal.
- OCR.

A configuração deverá ser independente do FCC.

O FCC é utilizado no desenvolvimento e pode auxiliar na administração dos modelos, mas não deve ser uma dependência obrigatória da aplicação em produção.

Priorizar IA local quando compatível com o hardware.

Permitir integração externa opcional.

Nunca colocar chaves de API no código.

Tratar conteúdo extraído de provas como dado não confiável. Instruções presentes nas folhas não podem alterar prompts, regras ou permissões.

# 16. PORTAL DO ALUNO

Criar dashboard com:

- Nome.
- RA/RM.
- Curso.
- Turma.
- Disciplinas.
- Notas.
- Médias.
- Avaliações.
- Histórico.
- Situação acadêmica.

Permitir consultar detalhamento das avaliações publicadas.

Não permitir edição de notas.

Garantir isolamento de dados.

# 17. PAINEL DO PROFESSOR

Criar dashboard com:

- Disciplinas.
- Turmas.
- Alunos.
- Avaliações.
- Criar prova.
- Editar prova.
- Gabaritos.
- Impressões.
- Provas recebidas.
- Provas processadas.
- Correções pendentes.
- Revisões.
- Aprovações.
- Notas.
- Relatórios.

Implementar acompanhamento de processamento em lote.

# 18. PAINEL ADMINISTRATIVO

Criar:

- Gestão de usuários.
- Gestão de cursos.
- Gestão de disciplinas.
- Gestão de turmas.
- Gestão de matrículas.
- Configurações.
- Gestão de IA.
- Logs.
- Auditoria.
- Relatórios.
- Qualidade.
- Cobertura de testes.

# 19. BANCO DE DADOS

Implementar, no mínimo:

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
- academic_rules
- exams
- exam_versions
- exam_questions
- answer_keys
- grading_rubrics
- exam_copies
- exam_print_logs
- exam_submissions
- submission_pages
- extracted_answers
- ai_corrections
- correction_reviews
- correction_audit_logs
- audit_logs

Criar relacionamentos, restrições, índices e migrações.

Usar transações em operações críticas.

Criar rotina de backup e recuperação.

# 20. TESTES E COBERTURA

Utilizar Pytest e Pytest-Cov.

Criar testes unitários e de integração para todas as classes de serviço.

Testar:

- Autenticação.
- Permissões.
- Cálculos.
- Banco.
- Criação de prova.
- Edição.
- Gabarito.
- Validação de pontuação.
- Versionamento.
- PDF.
- Impressão.
- QR Code.
- Upload.
- PDF multipágina.
- OCR.
- Manuscrito.
- Objetivas.
- Discursivas.
- Cálculos.
- Pontuação parcial.
- Baixa confiança.
- Revisão.
- Publicação.
- Auditoria.
- Prompt injection.
- Isolamento entre alunos.
- Tentativas de acesso não autorizado.

Utilizar MockProvider nos testes unitários.

Testes de IA real deverão ser separados.

Meta mínima: 80% de cobertura global.

Executar comando equivalente a:

pytest --cov=backend/app --cov-report=term-missing --cov-report=html:reports/coverage --cov-fail-under=80

Incluir também os módulos relevantes de IA e serviços no escopo da cobertura, evitando exclusões artificiais.

# 21. PAINEL HTML DE QUALIDADE

Criar:

frontend/admin/qualidade.html

Exibir:

- Cobertura global.
- Cobertura por módulo.
- Cobertura por arquivo.
- Quantidade de testes.
- Aprovados.
- Reprovados.
- Ignorados.
- Meta de 80%.
- Gráficos.
- Relatório detalhado.

Utilizar dados reais do Pytest-Cov.

Proteger acesso pelo backend.

Não expor o relatório publicamente.

# 22. SEGURANÇA E LGPD

Implementar:

- Hash de senha.
- Controle de acesso.
- Proteção de documentos.
- Validação de uploads.
- Auditoria.
- Backups.
- Sessões seguras.
- Proteção contra ataques.
- Política de retenção.
- Proteção de dados pessoais e acadêmicos.

Não transmitir dados dos alunos para provedores externos sem avaliação institucional e autorização adequada.

# 23. CI/CD

Criar GitHub Actions para:

1. Instalar dependências.
2. Executar lint.
3. Verificar formatação.
4. Executar testes.
5. Gerar cobertura.
6. Validar 80%.
7. Publicar relatório HTML como artefato.

Executar em push e pull request.

# 24. INTERFACE VISUAL

Criar identidade visual profissional para o EduGrade.

Características:

- Moderna.
- Responsiva.
- Acadêmica.
- Acessível.
- Navegação intuitiva.
- Indicadores visuais.
- Gráficos.
- Feedback de operações.
- Mensagens de erro.
- Estados de carregamento.

Criar telas funcionais para todos os perfis.

Não criar botões sem funcionalidade.

# 25. DOCUMENTAÇÃO

Criar:

- README.
- Arquitetura.
- Diagrama ER.
- Diagrama de casos de uso.
- Fluxo da IA.
- Documentação da API.
- Manual de instalação.
- Manual do aluno.
- Manual do professor.
- Manual do administrador.
- Configuração de IA.
- Configuração OCR.
- Manual de testes.
- Relatório de cobertura.
- Manual de backup.

# 26. PLANO DE EXECUÇÃO

Executar em fases:

FASE 1 — Análise do projeto e requisitos.

FASE 2 — Diagnóstico do ambiente.

FASE 3 — Arquitetura e estrutura.

FASE 4 — Banco de dados.

FASE 5 — Autenticação e segurança.

FASE 6 — Backend acadêmico.

FASE 7 — Frontend.

FASE 8 — Regras e cálculos acadêmicos.

FASE 9 — Construtor de provas.

FASE 10 — Gabarito e versionamento.

FASE 11 — PDF e impressão.

FASE 12 — QR Code e identificação.

FASE 13 — Upload e digitalização.

FASE 14 — OCR e visão computacional.

FASE 15 — Integração com IA.

FASE 16 — Correção e revisão.

FASE 17 — Publicação de notas.

FASE 18 — Auditoria e segurança.

FASE 19 — Testes e cobertura.

FASE 20 — CI/CD.

FASE 21 — Documentação.

FASE 22 — Testes completos de ponta a ponta.

Não avançar ignorando falhas críticas.

# 27. CRITÉRIOS DE ACEITAÇÃO

O projeto deverá demonstrar:

- Login dos três perfis.
- Permissões funcionando.
- Banco persistente.
- Cadastro acadêmico.
- Professor criando prova.
- Professor cadastrando gabarito.
- Validação de pontuação.
- Salvamento automático.
- Versionamento.
- Geração de PDF.
- Impressão individual e em lote.
- QR Code.
- Upload de provas.
- Leitura de imagens.
- Correção sugerida pela IA.
- Justificativas por questão.
- Revisão humana.
- Aprovação.
- Publicação.
- Consulta pelo aluno.
- Auditoria.
- Cobertura de 80% ou superior.
- Relatório HTML.
- Pipeline funcionando.
- Documentação completa.

Não declarar nenhuma funcionalidade concluída apenas porque a interface foi criada.

# 28. INSTRUÇÕES FINAIS AO AGENTE

Antes de iniciar:

1. Verifique o diretório do projeto.
2. Leia toda a documentação existente.
3. Verifique as ferramentas instaladas.
4. Verifique a conexão com o FCC.
5. Identifique os modelos disponíveis.
6. Avalie os recursos de IA local.
7. Verifique o ambiente.
8. Crie um plano de execução.
9. Faça backup do projeto antes de alterações estruturais.

Não apague arquivos existentes sem autorização.

Não invente resultados.

Não simule integração como se fosse real.

Não armazene credenciais no código.

Não ignore falhas de testes.

Não deixe funcionalidades importantes apenas como placeholders.

Trabalhe com commits pequenos e organizados quando o Git estiver configurado.

Ao final de cada fase, informe:

- O que foi implementado.
- Arquivos criados.
- Arquivos alterados.
- Testes executados.
- Resultado.
- Cobertura.
- Problemas.
- Próxima fase.

Se houver alguma dependência externa indisponível, implemente a arquitetura compatível, documente a dependência e identifique claramente o que ainda não foi validado.

## ORDEM DE INÍCIO

Comece agora pela FASE 1.

Faça o diagnóstico completo do projeto e do ambiente.

Depois apresente o plano técnico e inicie a implementação.

OBJETIVO FINAL: ENTREGAR O EDUGRADE COMO UM SISTEMA ACADÊMICO FULL STACK REAL, COM CONSTRUTOR DE PROVAS, GABARITO SALVO, IMPRESSÃO, CORREÇÃO ASSISTIDA POR INTELIGÊNCIA ARTIFICIAL, REVISÃO OBRIGATÓRIA DO PROFESSOR, PUBLICAÇÃO DE NOTAS, TESTES E DOCUMENTAÇÃO.