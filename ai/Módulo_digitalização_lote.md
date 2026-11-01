# ADENDO OFICIAL — EDUGRADE
## Módulo de digitalização em lote, identificação automática de alunos e correção inteligente por IA

### 1. Objetivo da funcionalidade

Implementar no EduGrade um módulo que permita ao professor digitalizar e enviar várias provas simultaneamente, utilizando câmera do celular, computador, scanner ou seleção de uma pasta contendo imagens e documentos.

A inteligência artificial deverá analisar cada imagem, identificar automaticamente o aluno por meio do RA e/ou número de matrícula, localizar seu cadastro no banco de dados, organizar as provas e realizar a correção conforme o gabarito e os critérios previamente cadastrados pelo professor.

O objetivo é eliminar a necessidade de o professor identificar manualmente cada prova e cadastrar individualmente cada nota.

### 2. Formas de envio das provas

O sistema deverá oferecer as seguintes opções:

**Opção A — Tirar fotos pelo próprio sistema**
- Abrir a câmera do celular ou dispositivo compatível.
- Tirar várias fotos em sequência.
- Permitir fotografar todas as páginas de uma prova.
- Permitir continuar fotografando outras provas sem reiniciar o processo.
- Exibir pré-visualização das imagens.
- Permitir excluir ou substituir uma foto antes do envio.
- Enviar todas as imagens selecionadas em um único lote.

**Opção B — Selecionar várias imagens**
- Permitir selecionar múltiplos arquivos.
- Aceitar JPG, JPEG, PNG e PDF.
- Permitir enviar provas de vários alunos simultaneamente.
- Exibir quantidade de arquivos selecionados.
- Permitir remover arquivos antes do processamento.

**Opção C — Enviar uma pasta inteira**
- Permitir selecionar uma pasta contendo imagens de várias provas.
- Processar os arquivos em lote.
- Identificar automaticamente quais imagens pertencem a cada aluno.
- Agrupar as páginas de uma mesma prova.
- Organizar os resultados por aluno e RA/matrícula.

**Opção D — Scanner**
- Receber documentos digitalizados.
- Suportar PDFs com várias páginas.
- Separar e processar as páginas individualmente.
- Agrupar automaticamente as páginas correspondentes a cada prova.

### 3. Identificação automática obrigatória do aluno

A identificação do aluno será uma etapa obrigatória do processamento.

A IA deverá analisar as imagens e localizar:
- RA do aluno.
- Número de matrícula.
- Nome do aluno, quando disponível.
- Disciplina.
- Turma.
- Identificação da avaliação.
- Número da página, quando disponível.

**Regra principal:** a identificação deverá utilizar prioritariamente o RA e/ou número de matrícula, confrontando as informações extraídas com os registros oficiais do banco de dados.

Se ambos estiverem presentes, o sistema deverá verificar se pertencem ao mesmo cadastro.

Se somente um identificador estiver legível, poderá utilizá-lo para localizar o aluno, desde que exista correspondência única e válida no banco de dados.

Não poderá associar uma prova a um aluno apenas por semelhança de nome.

### 4. Funcionamento da identificação e distribuição automática

Após receber as imagens, a IA deverá executar o seguinte fluxo:

1. Ler todos os arquivos enviados.
2. Separar PDFs em páginas individuais.
3. Processar e melhorar a qualidade das imagens.
4. Identificar regiões que contenham RA e matrícula.
5. Extrair os identificadores por OCR e visão computacional.
6. Consultar os cadastros de alunos no banco de dados.
7. Conferir se o RA e a matrícula correspondem ao mesmo aluno.
8. Identificar disciplina, turma e avaliação.
9. Identificar quais páginas pertencem à mesma prova.
10. Agrupar automaticamente as páginas.
11. Criar um registro individual de prova por aluno.
12. Encaminhar cada prova identificada para a fila de correção.

A organização deverá ocorrer automaticamente, sem exigir que o professor selecione manualmente o aluno de cada imagem.

### 5. Agrupamento inteligente das páginas

O sistema deverá compreender que uma prova pode possuir várias páginas e que uma pasta pode conter provas de diversos alunos.

Exemplo de envio:

```text
LOTE_PROVAS/
│
├── foto_001.jpg
├── foto_002.jpg
├── foto_003.jpg
├── foto_004.jpg
├── foto_005.jpg
├── foto_006.jpg
├── prova_007.pdf
└── prova_008.pdf
```

A IA deverá identificar e organizar automaticamente:

```text
PROCESSAMENTO_EDUGRADE/
│
├── ALUNO_RA_325131396/
│   ├── pagina_01.jpg
│   └── pagina_02.jpg
│
├── ALUNO_RA_325132875/
│   ├── pagina_01.jpg
│   └── pagina_02.jpg
│
└── ALUNO_RA_325140970/
    ├── pagina_01.jpg
    └── pagina_02.jpg
```

Os nomes acima são exemplos ilustrativos. A associação real deverá utilizar os registros do banco de dados, e não o nome do arquivo.

O agrupamento deverá considerar:
- RA e matrícula.
- Código da avaliação.
- Código da cópia impressa, quando disponível.
- Numeração das páginas.
- Continuidade do conteúdo.
- Indícios visuais da mesma prova.

O sistema não deverá misturar páginas de alunos diferentes.

### 6. Correção automática após identificação

Depois de identificar e agrupar a prova, a IA deverá iniciar a correção utilizando:
- Gabarito oficial da avaliação.
- Versão exata da prova aplicada.
- Enunciados das questões.
- Respostas esperadas.
- Critérios de avaliação.
- Rubricas.
- Pontuação máxima de cada questão.
- Regras de pontuação parcial.

A IA deverá analisar:
- Respostas objetivas.
- Respostas discursivas.
- Cálculos.
- Fórmulas.
- Respostas manuscritas.
- Questões com pontuação parcial.

Para cada questão, deverá gerar:
- Resposta reconhecida.
- Interpretação da resposta.
- Pontuação sugerida.
- Pontuação máxima.
- Justificativa.
- Critérios atendidos.
- Critérios não atendidos.
- Confiança na leitura do texto.
- Confiança na avaliação.
- Necessidade de revisão.

A correção deve respeitar a pontuação definida pelo professor.

### 7. Painel de processamento em lote do professor

Criar uma interface específica:

`frontend/professor/correcao-lote.html`

O painel deverá apresentar:

**Resumo do processamento**
- Total de arquivos enviados.
- Total de páginas processadas.
- Total de provas identificadas.
- Total de alunos identificados.
- Total de provas corrigidas pela IA.
- Total aguardando revisão.
- Total com identificação pendente.
- Total com falha de leitura.

**Exemplo ilustrativo:**

| Indicador | Quantidade |
|---|---:|
| Arquivos recebidos | 120 |
| Páginas processadas | 120 |
| Alunos identificados | 40 |
| Provas agrupadas | 40 |
| Correções sugeridas | 40 |
| Aguardando aprovação | 40 |
| Identificações pendentes | 0 |

Os valores acima são apenas um exemplo visual, não resultados reais.

**Lista de resultados:**

| Aluno | RA/Matrícula | Prova | Nota sugerida | Situação |
|---|---|---|---:|---|
| Aluno A | RA identificado | Prova 1 | 8,5 | Aguardando revisão |
| Aluno B | RA identificado | Prova 1 | 7,0 | Aguardando revisão |
| Aluno C | Matrícula identificada | Prova 1 | 9,0 | Aguardando revisão |

O professor deverá conseguir abrir cada prova para visualizar as páginas, respostas, gabarito e justificativas da IA.

### 8. Revisão e aprovação do professor

Mesmo com identificação e correção automáticas, a publicação da nota dependerá obrigatoriamente da aprovação do professor.

Para cada prova, disponibilizar:
- Imagens originais.
- Imagens processadas.
- Identificação do aluno.
- RA e matrícula reconhecidos.
- Respostas extraídas.
- Gabarito.
- Pontuação sugerida.
- Justificativas.
- Pontuação final editável.
- Botão para aprovar.
- Botão para corrigir manualmente.
- Botão para solicitar nova leitura.
- Botão para rejeitar a identificação.
- Campo para observações.

O professor poderá revisar as provas individualmente.

Também poderá aprovar várias provas em sequência, mas o sistema deverá registrar a aprovação individual de cada aluno, preservando a responsabilidade e a trilha de auditoria.

Nenhuma nota poderá ser publicada antes da aprovação.

### 9. Tratamento de falhas de identificação

Criar uma fila específica de pendências.

Situações possíveis:
- RA ilegível.
- Matrícula ilegível.
- RA inexistente.
- Matrícula inexistente.
- RA e matrícula divergentes.
- Dois alunos com identificação conflitante.
- Prova sem identificação.
- Página sem correspondência.
- Página duplicada.
- Avaliação não identificada.
- Imagem de baixa qualidade.

Nessas situações:

1. A IA deverá informar o motivo da pendência.
2. O sistema não deverá atribuir a prova automaticamente a outro aluno.
3. O professor poderá consultar a imagem original.
4. O professor poderá informar manualmente o RA ou matrícula.
5. O sistema deverá validar a correspondência no banco.
6. Depois da validação, a prova poderá seguir para correção.

A identificação automática é obrigatória como etapa de processamento, mas a confirmação manual deverá estar disponível para situações de incerteza.

### 10. Requisitos de segurança e integridade

- Os arquivos enviados deverão ser armazenados em local protegido.
- Validar extensão, MIME type e tamanho dos arquivos.
- Evitar execução de conteúdo enviado pelos usuários.
- Registrar o professor responsável pelo lote.
- Registrar data e horário do envio.
- Registrar identificadores reconhecidos.
- Registrar associação realizada.
- Preservar imagens originais.
- Registrar versão do modelo de IA utilizado.
- Registrar resultados originais da IA.
- Impedir acesso de alunos a provas de terceiros.
- Impedir que a IA altere o gabarito oficial.
- Impedir publicação automática de notas.
- Garantir rastreabilidade de todas as alterações.

As informações acadêmicas deverão permanecer protegidas, respeitando a LGPD e as regras institucionais de acesso.

### 11. Estrutura técnica sugerida

Criar os seguintes serviços no backend:

```text
backend/app/
│
├── ai/
│   ├── ai_provider.py
│   ├── image_analysis.py
│   ├── answer_evaluation.py
│   └── confidence_service.py
│
├── exams/
│   ├── exam_service.py
│   ├── exam_version_service.py
│   ├── exam_pdf_service.py
│   └── answer_key_service.py
│
├── grading/
│   ├── batch_upload_service.py
│   ├── image_preprocessing_service.py
│   ├── ocr_service.py
│   ├── student_identification_service.py
│   ├── page_grouping_service.py
│   ├── automatic_grading_service.py
│   ├── teacher_review_service.py
│   └── grade_publication_service.py
│
└── storage/
    ├── file_validation_service.py
    └── exam_storage_service.py
```

Criar endpoints de referência:

```text
POST   /api/teacher/grading/batches
POST   /api/teacher/grading/batches/{batch_id}/files
POST   /api/teacher/grading/batches/{batch_id}/process

GET    /api/teacher/grading/batches/{batch_id}
GET    /api/teacher/grading/batches/{batch_id}/results
GET    /api/teacher/grading/pending-identifications

POST   /api/teacher/grading/submissions/{id}/identify
GET    /api/teacher/grading/submissions/{id}/review

POST   /api/teacher/grading/submissions/{id}/approve
POST   /api/teacher/grading/submissions/{id}/request-reprocessing

POST   /api/teacher/grading/submissions/{id}/publish
```

Os endpoints são uma referência de contrato; deverão ser ajustados à arquitetura efetivamente implementada.

### 12. Novas entidades do banco de dados

Adicionar ou adaptar as seguintes entidades:

- `grading_batches`: lotes enviados pelo professor.
- `grading_batch_files`: arquivos recebidos.
- `exam_submission_pages`: páginas de cada prova.
- `student_identification_results`: resultados da identificação por IA.
- `exam_page_groups`: agrupamentos de páginas.
- `exam_submissions`: provas individuais identificadas.
- `extracted_answers`: respostas reconhecidas.
- `ai_corrections`: sugestões de pontuação.
- `correction_reviews`: revisões e aprovações.
- `grading_audit_logs`: histórico do processamento e das decisões.

Os relacionamentos deverão preservar a associação entre lote, arquivo, página, prova, aluno, avaliação e versão do gabarito.

### 13. Processamento assíncrono

Como um lote pode conter muitas imagens, o sistema não deverá depender de uma única requisição HTTP para concluir todo o processamento.

Implementar:
- Processamento assíncrono.
- Controle de fila.
- Indicador de progresso.
- Retentativas controladas.
- Tratamento de falhas por arquivo.
- Possibilidade de retomar um lote interrompido.
- Prevenção de processamento duplicado.
- Registro de arquivos já processados.

Uma falha em uma imagem não deverá interromper todo o lote.

### 14. Testes obrigatórios

Criar testes unitários e de integração para:

1. Envio de várias fotos.
2. Envio de uma pasta com várias imagens.
3. Upload de PDF multipágina.
4. Identificação de RA.
5. Identificação de matrícula.
6. Validação de RA e matrícula no banco.
7. Divergência entre identificadores.
8. Agrupamento de páginas do mesmo aluno.
9. Separação de provas de alunos diferentes.
10. Detecção de páginas duplicadas.
11. Tratamento de imagem ilegível.
12. Identificação pendente.
13. Associação manual.
14. Correção utilizando a versão correta do gabarito.
15. Geração de notas sugeridas.
16. Revisão pelo professor.
17. Aprovação individual.
18. Publicação somente após aprovação.
19. Processamento de lote com falhas parciais.
20. Retomada de processamento interrompido.

A implementação deverá integrar a suíte geral do projeto e respeitar a meta mínima de 80% de cobertura de testes.

---

# 15. INSTRUÇÃO DIRETA PARA O CLAUDE CODE

Fernando deverá incorporar este adendo ao escopo oficial do EduGrade e solicitar ao Claude Code:

```text
Leia integralmente o adendo do módulo de digitalização em lote,
identificação automática de alunos e correção inteligente por IA.

Integre todos os requisitos à arquitetura atual do EduGrade.

O professor deve conseguir:
1. Tirar várias fotos pelo sistema.
2. Selecionar várias imagens.
3. Enviar uma pasta com várias provas.
4. Enviar PDFs multipágina.
5. Processar todos os arquivos em lote.

A IA deve obrigatoriamente tentar identificar cada prova pelo RA
e/ou número de matrícula, consultando o banco de dados oficial.

Quando ambos os identificadores estiverem disponíveis,
verifique se correspondem ao mesmo aluno.

A IA deve agrupar as páginas de cada prova, separar os alunos,
identificar a avaliação, consultar o gabarito correto e gerar
uma sugestão de nota para cada aluno.

Após a correção, o resultado deverá aparecer no painel do professor,
organizado por aluno, RA/matrícula, avaliação e nota sugerida.

Não atribua provas a alunos quando houver identificação ambígua,
divergente ou sem correspondência única.

Crie uma fila de identificação pendente e permita associação manual.

Não permita publicação automática de notas.
O professor deve revisar e aprovar as correções.

Implemente o processamento em lote de forma assíncrona,
com progresso, retentativas, controle de duplicidade e recuperação
de falhas.

Preserve as imagens originais e registre toda a trilha de auditoria.

Antes de alterar o código:
- Analise a arquitetura existente.
- Identifique os serviços que podem ser reutilizados.
- Identifique alterações necessárias no banco.
- Apresente o plano de implementação.

Depois implemente por módulos, executando testes em cada etapa.

Não crie funcionalidades fictícias.
Não simule identificação real sem deixar claro que se trata de mock.
Não declare a funcionalidade concluída sem testar o fluxo completo.

Mantenha a meta de cobertura mínima de 80%.
Atualize a documentação, os diagramas, o README e o relatório
de qualidade.
```

**Critério de aceite:** o professor envia um lote com provas de vários alunos; o EduGrade identifica os alunos pelos identificadores acadêmicos, agrupa as páginas, corrige as respostas e apresenta as notas sugeridas no painel do professor. O professor consegue revisar e aprovar cada resultado antes da publicação. 