# Barra global de progresso — EduGrade

Documentação da infraestrutura de acompanhamento de operações de longa duração
(uploads, importações, análise de PDF e correção por IA).

## 1. Arquitetura

```
┌──────────────────────┐    POST (upload XHR)     ┌──────────────────────────┐
│  ProgressManager     │ ───────────────────────▶ │  Rota da operação        │
│  (frontend global)   │                          │  (exams/imports)         │
│                      │ ◀─── 202 { job_id } ──── │                          │
│                      │                          │  cria OperationJob        │
│  polling 700 ms      │ ── GET /jobs/{id} ─────▶ │  + BackgroundTasks       │
│                      │ ◀── snapshot JSON ────── │                          │
└──────────────────────┘                          └────────────┬─────────────┘
                                                               │
                                                    ┌──────────▼─────────────┐
                                                    │ operation_runner       │
                                                    │ (OCR, IA, importação)  │
                                                    └────────────────────────┘
```

- **Fonte oficial do progresso:** tabela `operation_jobs` (backend).
- **Upload:** o percentual vem do `XMLHttpRequest.upload.onprogress` (bytes
  reais transferidos), nunca de um temporizador.
- **Processamento:** o runner atualiza a etapa e os contadores; o percentual só
  existe quando há medida real (`processados / total`). Sem medida confiável,
  `progress = null` e a barra fica indeterminada mostrando a etapa atual.
- **Transporte:** *polling* a cada 700 ms em `GET /jobs/{id}`.
  Escolhido em vez de SSE/WebSocket porque:
  - o token JWT vai no cabeçalho `Authorization` (EventSource não permite
    cabeçalhos e exigiria token na URL, que fica registrado em logs);
  - funciona atrás de proxy/reload sem configuração extra;
  - reconecta sozinho e permite retomar o painel após recarregar a página.

## 2. Modelo de dados

Tabela `operation_jobs` (criada automaticamente pelo `create_all`, sem migração
obrigatória):

| Campo | Descrição |
|---|---|
| `kind` | `exam_pdf_import`, `submission_upload`, `ai_correction`, `student_import`, `grade_import`, `quality_run` |
| `status` | `pending`, `running`, `succeeded`, `succeeded_with_warnings`, `failed`, `cancelled` |
| `step_key` / `step_label` | etapa atual legível |
| `progress` | 0–100 real ou `NULL` (indeterminado) |
| `processed` / `total` | contadores reais |
| `succeeded` / `failed` / `skipped` | resultado por registro/arquivo |
| `payload` / `result` | contexto de entrada e resultado final |
| `warnings` | avisos não fatais (ex.: OCR indisponível) |
| `cancel_requested` | cancelamento cooperativo |
| `created_by` | dono da operação (isolamento de acesso) |

## 3. Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/jobs?limit=20` | operações recentes do usuário (recuperação após recarregar) |
| `GET` | `/api/v1/jobs/{job_id}` | snapshot do progresso (somente dono ou admin) |
| `POST` | `/api/v1/jobs/{job_id}/cancel` | solicita cancelamento |
| `POST` | `/api/v1/exams/import/pdf` | envia PDF e inicia análise em segundo plano (202) |
| `POST` | `/api/v1/exams/uploads` | recebe **um** arquivo (progresso real por arquivo) |
| `POST` | `/api/v1/exams/submissions/from-uploads` | compõe a submissão com os arquivos recebidos |
| `POST` | `/api/v1/exams/submissions/{id}/correction-jobs` | OCR + correção por IA em segundo plano (202) |
| `POST` | `/api/v1/imports/students` | importa alunos via CSV (202) |
| `POST` | `/api/v1/imports/grades` | importa notas via CSV (202) |
| `POST` | `/api/v1/quality/run` | executa pytest + cobertura em segundo plano (admin, 202) |
| `GET` | `/api/v1/imports/templates/{students\|grades}.csv` | modelo de CSV |

Os endpoints antigos (`/exams/analyze-pdfs`, `/exams/submissions`, `/ai/batch-correct`)
continuam funcionando para compatibilidade.

## 4. Etapas exibidas

**Importação de prova (PDF):** leitura do PDF → extração de texto → análise com
IA → conferência de questões/gabaritos.

**Upload de fotos:** envio por arquivo (percentual real) → montagem da submissão
→ correção. O painel lista cada arquivo com estado `Aguardando`, `Enviando N%`,
`Enviada` ou `Erro`. Ao reenviar, os arquivos já recebidos **não** são enviados
de novo.

**Correção por IA:** preparação → OCR → identificação do aluno → correção por
questão (percentual = questões concluídas / total) → encaminhamento para revisão.

**Importações:** leitura do CSV → processamento linha a linha → resumo com
importados, duplicados, ignorados e erros (linha + motivo).

## 5. Cancelamento

- `POST /jobs/{id}/cancel` marca `cancel_requested` e `status=cancelled`.
- O runner verifica entre etapas/linhas e interrompe (`OperationCancelled`),
  preservando o que já foi gravado.
- O painel mostra `Cancelado` e nunca fica em “carregando” indefinidamente.

## 6. Falhas tratadas

| Situação | Comportamento |
|---|---|
| Download/upload interrompido | erro no painel; arquivos já enviados são preservados |
| Timeout/rede perdida | mensagem “Sem conexão… tentando novamente”, com retomada |
| Servidor reiniciado | `GET /jobs/{id}` → 404; painel mostra “Operação não encontrada” |
| PDF inválido | job `failed` com mensagem do parser |
| OCR indisponível | tenta ler a camada de texto do próprio PDF; se não houver respostas, o job falha explicando como corrigir |
| Nenhuma resposta identificada | job `failed` com orientação (numeração das respostas e legibilidade) |
| CSV inválido | 422 antes de criar o job (cabeçalho/limite) |
| Linha inválida no CSV | registrada em `result.errors` sem interromper as demais |
| Nota duplicada | atualiza rascunho existente; nota já publicada é ignorada |

## 7. Segurança

- Todas as rotas exigem autenticação.
- `GET /jobs/{id}` devolve **404** para operações de outro usuário (não revela
  que existem). Administradores acessam qualquer operação.
- Uploads validam extensão, tamanho e o caminho retornado (não é possível
  referenciar arquivos fora de `storage/exams`).
- Importação exige permissão contextual na turma (`create_students` para alunos,
  `edit_grades` para notas).

## 8. Frontend

`frontend/js/progress.js` expõe `ProgressManager`:

```js
const op = ProgressManager.start({ title: 'Importação', subtitle: 'alunos.csv' });
await api.uploadForm('/imports/students', formData, {
  onProgress: ({ loaded, total, percent }) => op.setUpload({ loaded, total, percent }),
});
const job = await op.followJob(jobId);   // resolve no sucesso, rejeita em falha/cancelamento
```

Recursos do painel: barra animada (determinada ou indeterminada), operação,
etapa atual, contadores, tempo decorrido, lista de arquivos, cancelar,
minimizar, fechar, estados coloridos e mensagem final.

O painel é único por página (` .progress-stack`), suporta várias operações
simultâneas e é retomado automaticamente ao recarregar (`resumeActive`).

## 9. Telas atendidas

- Portal do professor → **Enviar Provas para Correção**
- Portal do professor → **Criar Prova** (importação de PDF)
- Portal do professor/admin → **Importar Alunos**
- Portal do professor/admin → **Importar Notas**
- Lista de provas → botão **Publicar** (rascunhos e provas importadas)

## 10. Leitura das respostas

1. **OCR (Tesseract)** nas imagens das páginas — usado quando há manuscrito.
2. **Camada de texto do PDF** (`integrations/ocr/text_layer.py`) — quando o PDF
   tem texto selecionável (prova digitada ou com OCR embutido). Lê padrões
   `Questão N ... Resposta: X` e cria as respostas com confiança de leitura 100.
   É o fallback automático quando o Tesseract não está instalado.

Se nenhuma das duas formas encontrar respostas, a correção **falha de forma
explícita** para o professor, sem gerar notas vazias.

## 11. Testes

`tests/unit/test_operation_jobs.py` cobre: progresso real × indeterminado,
cancelamento, isolamento de operações, parsing de CSV, importação de alunos
(conta + matrícula), importação de notas (duplicidade, faixa de nota, avaliação
inexistente, aluno inexistente), upload por arquivo, composição da submissão,
correção em segundo plano até o estado final e extração da camada de texto do PDF.

## 12. Atualização do frontend em produção

O servidor envia `Cache-Control: no-cache, no-store, must-revalidate` para
`.html`, `.css` e `.js`, então uma atualização normal do navegador (F5) já
carrega a versão nova. Se a página já estava aberta antes da atualização do
sistema, use **Ctrl+F5** uma vez para descartar o JavaScript antigo do cache.
