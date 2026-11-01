# Relatório de testes — Professor

**Status:** E2E parcial em ambiente isolado; provas e CRUD geral não validados.

## Superfícies encontradas

- `frontend/professor/dashboard.html`: materiais publicados por chamadas reais
  para `/api/v1/materials`; estatísticas e alguns cartões eram estáticos.
- Workspace virtual: turmas, provas, correções, notas e chamadas de lote.
- API: `/api/v1/academic`, `/api/v1/exams`, `/api/v1/ai`,
  `/api/v1/batch-grading` e `/api/v1/materials`.

## Resultado E2E e bloqueios

Login e dashboard do professor passaram com conta isolada
`DADO_DE_TESTE_EDUGRADE`. As chamadas de materiais e revisões responderam HTTP
200. O toast de erro foi corrigido; sem disciplina vinculada, o upload fica
desabilitado e a tela orienta pedir vínculo ao administrador. Os KPIs e ações
rápidas passaram a usar cartões alinhados.

Screenshot: `docs/QA/evidencias/professor-dashboard.png`.

As rotas para provas, questões, gabaritos, impressão, submissões, OCR e correção
existem no código, mas ainda não foram exercitadas pelo navegador. O upload do
módulo de lote retorna `501 Not Implemented`. A identificação e o escopo do
professor por turma/objeto precisam de testes de autorização.

O executável Tesseract configurado e o Poppler não foram encontrados. O PDF
solicitado não foi localizado nos diretórios pesquisados. Não foi feita
correção nem publicação de nota.

## Próximos testes

Usar somente contas e dados isolados identificados
`DADO_DE_TESTE_EDUGRADE`; testar criação/edição de prova e pontuação, PDF do
aluno sem gabarito, submissão, múltiplos arquivos, identificação sem
aproximação pelo nome, revisão individual e publicação somente após aprovação.
