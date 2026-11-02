# Registro de Problemas — Validação Funcional

**Projeto:** EduGrade — **Responsável:** Lucas Henrique Miranda (RA 325131396)
**Versão:** 1.0 — 02/11/2026

Regra do grupo: **toda falha identificada deve ser registrada** (Guia Operacional, §5).

## 1. Como registrar

Cada problema encontrado durante o `CHECKLIST_VALIDACAO_FUNCIONAL.md` ganha uma linha na tabela da seção 2, com ID `FUNC-NN`.

**Severidade**
- **Crítica**: quebra segurança, expõe dados de outros alunos ou impede o fluxo principal.
- **Alta**: funcionalidade importante não funciona.
- **Média**: funciona com limitação ou comportamento incorreto contornável.
- **Baixa**: detalhe visual ou de texto.

**Status do problema:** `Aberto` · `Em correção` · `Corrigido (reteste pendente)` · `Fechado` · `Não será corrigido (justificar)`.

Quando o problema for de código, avisar o Fernando; quando for de banco/modelo, avisar o Caio. Não corrigir diretamente na branch `main`.

## 2. Problemas encontrados pela validação funcional

| ID | Data | Cenário | Descrição | Passos para reproduzir | Esperado | Obtido | Severidade | Regra/RF | Responsável | Status | Evidência |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FUNC-01 | | | | | | | | | | | |
| FUNC-02 | | | | | | | | | | | |

> Nenhum problema próprio foi registrado ainda: a execução do checklist **não foi feita**. Esta tabela deve ser preenchida a partir dos resultados reais.

## 3. Pendências já conhecidas (herdadas da QA de 01/11/2026)

Fonte: `docs/QA/BUGS_ENCONTRADOS.md` e `docs/QA/RELATORIO_FINAL.md`. Não são resultados desta validação; servem para **não duplicar** registro e para saber o que esperar nos cenários.

| ID (QA) | Prioridade | Problema | Estado informado | Cenário relacionado |
|---|---|---|---|---|
| BUG-04 | Alta | Upload de arquivos no processamento em lote retorna `501 Não implementado` | Aberto | CV09, CV17 |
| BUG-07 | Média | Logout não revoga o token no servidor | Aberto | CV25 |
| BUG-08 | Média | Validação de upload não verifica conteúdo/MIME | Aberto | CV19 |
| BUG-11 | Média | Migração inicial não contém todas as tabelas dos modelos atuais | Aberto | — (revisão do Caio) |
| BUG-12 | Média | Falha na inicialização pode manter o servidor ativo | Aberto | — |
| BUG-14 | Bloqueio | Tesseract e Poppler ausentes; impede teste real de OCR | Aberto | CV09, CV10, CV17 |
| BUG-15 | Bloqueio | Sem chave de criptografia de credenciais e sem chave externa de IA | Aberto | CV10 |
| BUG-16 | Média | README cita CI/CD; o workflow `ci.yml` foi adicionado à main, mas com erro de indentação YAML | Parcial: execução não confirmada | — (Gabriel) |
| — | Alta | Cobertura de testes em **55,50%**, abaixo da meta de 80% | Aberto | — (Fernando) |

## 4. Inconsistências de documentação percebidas na revisão (para o Gabriel)

Observações de leitura do repositório, ainda não verificadas por execução:

| Item | Observação |
|---|---|
| Comandos de teste no README | O README manda executar `pytest --cov=backend backend/tests/`, mas os testes estão em `tests/unit/` na raiz do repositório. |
| Integrantes no README | A lista de integrantes está incompleta (Fernando sem sobrenome/RA; Lucas e Caio ausentes). |
| Documentos duplicados na raiz | Existem `GUIA OPERACIONAL .md`, `guia completo.md` e `prompt.md` na raiz; confirmar com o grupo se devem ficar na raiz ou em `docs/`. |
