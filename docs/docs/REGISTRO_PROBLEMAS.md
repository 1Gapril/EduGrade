# Registro de Problemas — Validação Funcional

**Projeto:** EduGrade — **Responsável:** Lucas Henrique Miranda (RA 325131396)
**Versão:** 1.2 — 05/11/2026 (atualizado com análise completa do RTF 31 páginas)

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

---

## 2. Problemas encontrados pela validação funcional (04/11/2026 + análise RTF 05/11/2026)

| ID | Data | Cenário | Descrição | Passos para reproduzir | Esperado | Obtido | Severidade | Regra/RF | Responsável | Status | Evidência |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FUNC-01 | 04/11/2026 | CV02 | Aluno não consegue consultar notas | Login aluno → Minhas notas | Lista das notas publicadas do aluno | Tela informa que não há consulta de notas; nada é listado; cabeçalho mostra RA/curso/turma "Não disponível" | **Alta** | RF04, RN01, RN14 | Fernando | Aberto | `CV02.png` |
| FUNC-02 | 04/11/2026 | CV05 | "Minhas turmas" do professor lista as turmas do sistema, com 0 matriculados | Login professor → Minhas turmas | Só turmas autorizadas, com alunos | Lista "turmas disponíveis no sistema"; matriculados = 0 | **Alta** (confirmar no CV12) | RN11 | Fernando | Aberto | `CV05a-c.png` |
| FUNC-03 | 04/11/2026 | CV21 | Layout de admin/professor aparece por alguns segundos para o aluno antes do redirecionamento | Logado como aluno, abrir `/admin/dashboard.html` | Negar ou redirecionar **antes de exibir** | Exibe a tela e depois redireciona | **Média** | RN15, RNF02 | Fernando | Aberto (testar API) | `CV21.png` |
| FUNC-04 | 04/11/2026 | CV05 | Tabelas mostram JSON bruto, cabeçalhos em inglês, datas ISO e "true" | Professor → Minhas turmas, rolar a tabela | Dados formatados em português | Texto técnico bruto | **Média** | RNF13 | Fernando | Aberto | `CV05a-c.png` |
| FUNC-05 | 04/11/2026 | CV01/CV02 | Telas exibem mensagens técnicas ("A API não disponibiliza...") e aviso quase ilegível | Abrir painéis do aluno e do professor | Linguagem para o usuário, texto legível | Mensagens técnicas; baixo contraste | **Baixa** | RNF13 | Fernando | Aberto | `CV02.png` |
| FUNC-06 | 04/11/2026 | RF18 | Gestão de usuários não filtra por perfil | Admin → Usuários → clicar "Professores" | Só o perfil escolhido (professores) | Lista alunos, professores e administradores juntos | **Média** | RF18 | Fernando | Aberto | — |
| FUNC-07 | 04/11/2026 | painel admin | Armazenamento mostra "a consulta de uso e gerenciamento de arquivos ainda não está implementada" | Admin → Armazenamento | Funcionalidade implementada | Funcionalidade ausente | **Média** | — | Fernando | Aberto | — |
| FUNC-08 | 04/11/2026 | RNF13 | "Períodos letivos" está em inglês | Admin → Períodos letivos | Interface toda em português | Texto em inglês fora de jargão quebra a consistência | **Baixa** | RNF13 | Fernando | Aberto | — |
| FUNC-09 | 04/11/2026 | RF24 | Criar conta a partir do chamado de acesso falha sem SMTP configurado | Admin → Chamados de acesso → Criar conta e enviar senha | Conta criada e credenciais entregues | Erro "configure SMTP_HOST no servidor"; chamados continuam abertos | **Média** | RF24, RNF07 | Gabriel/Fernando | Aberto (config/documentação) | Print 2 |
| FUNC-10 | 04/11/2026 | RF24 | Formulário de solicitação aceita usuário com espaço ("Junior Teste") e telefone sem formato válido | register.html → preencher e enviar | Validar os campos | Aceitou e criou o chamado | **Baixa** | RNF13 | Fernando | Aberto | Print 1 |
| **FUNC-11** | 05/11/2026 | CV06 | Botão "Gerar prova do aluno em PDF" não funciona | Professor → Criar prova → clicar "Gerar prova do aluno em PDF" | PDF gerado para o aluno | Botão não responde; nada acontece | **Alta** | RF10, RN16–RN19 | Fernando | Aberto | `CV06.png` |
| **FUNC-12** | 05/11/2026 | CV07 | PDF gerado mostra "(multiple choice)" e "(short answer)" ao lado dos textos | Professor → Cadastrar gabarito → Gerar PDF | PDF limpo sem termos técnicos internos | Termos técnicos vazam no PDF do aluno | **Média** | RF12, RN05, RN20, RNF13 | Fernando | Aberto | `CV07.png` |
| **FUNC-13** | 05/11/2026 | CV08 | Impressão não reconhece prova do banco de provas | Professor → Banco de provas → Imprimir | PDF gerado com QR/identificador | Prova não é reconhecida; falha na impressão | **Alta** | RF11, RN27 | Fernando | Aberto | `CV08.png` |
| **FUNC-14** | 05/11/2026 | CV10 | IA: sem barra de progresso, texto azul ilegível, status confuso | Professor → Revisão IA → aguardar análise | Feedback visual de progresso, contraste acessível, status claro | 1. Sem barra progresso 2. Texto azul claro ilegível 3. Status IA não informa o que acontece | **Média** | RF14, RF15, RN39, RN40, RNF13 | Fernando | Aberto | `CV10.png` |
| **FUNC-15** | 05/11/2026 | CV12 | API não lista provas/turmas existentes + mensagens técnicas vazam | Professor sem vínculo → tela inicial | Acesso negado limpo | Não lista provas/turmas; mostra erros técnicos da API pro usuário | **Alta** | RN11, RNF13 | Fernando | Aberto | `CV12.png` |
| **FUNC-16** | 05/11/2026 | CV13 | Aluno vê "comandos" técnicos na interface (banco de provas) | Aluno → Provas/Notas | Interface limpa para aluno | Comandos técnicos expostos ao aluno | **Média** | RN14, RNF13 | Fernando | Aberto | `CV13.png` |
| **FUNC-17** | 05/11/2026 | CV15 | PDF da prova do aluno mostra códigos técnicos misturados | Professor → Banco de provas/Minhas provas → Visualizar PDF | PDF sem gabarito, sem códigos | Resposta em inglês com códigos misturados ao texto | **Alta** | RN25, RNF13 | Fernando | Aberto | `CV15.png` |
| **FUNC-18** | 05/11/2026 | CV22 | Botão "Ver auditoria" não abre (recarrega pág), auditoria ilegível, métricas quebradas | Admin → Auditoria → Ver auditoria | Auditoria legível com quem alterou, valor IA, valor final, data | Botão não funciona; layout confuso; métricas não funcionam | **Alta** | RN10, RN40, RN41 | Fernando | Aberto | `CV22.png` |
| **FUNC-19** | 05/11/2026 | Admin | Filtros de Gestão de Usuários não funcionam (todos retornam mesmo resultado) | Admin → Usuários → clicar qualquer filtro | Cada filtro mostra só o perfil correspondente | Todos os filtros retornam resultado misturado idêntico | **Média** | RF18 | Fernando | Aberto | `ADMIN_EVIDENCIA.md` |
| **FUNC-20** | 05/11/2026 | Admin | Cursos e Disciplinas fundidos na Gestão Acadêmica | Admin → Gestão Acadêmica | Cursos e Disciplinas separados | Fundidos no mesmo local sem separação clara | **Média** | — | Fernando/Caio | Aberto | `ADMIN_EVIDENCIA.md` |
| **FUNC-21** | 05/11/2026 | Admin | Perfil mostra inglês+português simultâneo + expõe `is_superuser` e `role` | Admin → Meu perfil | Apenas username, data criação, info básica usuário | Mistura idiomas; expõe campos técnicos internos | **Baixa** | RNF13, RN15 | Fernando | Aberto | `ADMIN_EVIDENCIA.md` |
| **FUNC-22** | 05/11/2026 | Admin | Botão hambúrguer (3 tracinhos) sem função + Sidebar bug (setinha esconde botões) | Admin → Dashboard lateral | Hambúrguer expande/colapsa sidebar; setinha não esconde botões | Hambúrguer inútil; setinha some todos os botões | **Baixa** | RNF13 | Fernando | Aberto | `ADMIN_EVIDENCIA.md` |
| **FUNC-23** | 05/11/2026 | Admin | Notificações: sino não abre nada (sem sistema) + Refresh sem feedback visual | Admin → Sino notificações / Botão refresh | Sino abre lista notificações; refresh dá feedback | Sino não funciona; refresh sem sinal visível | **Média** | — | Fernando | Aberto | `ADMIN_EVIDENCIA.md` |

> **Nota sobre CV20 (Admin lançar notas):** Sem tela de lançar notas para o admin, ele não consegue lançar pela interface. Marcar **PASSOU** com a observação: *"bloqueado pela ausência da tela; falta confirmar pela API"* (RN15). Confirmar na API é o que vale pela RN15.

---

## 3. Pendências já conhecidas (herdadas da QA de 01/11/2026)

Fonte: `docs/QA/BUGS_ENCONTRADOS.md` e `docs/QA/RELATORIO_FINAL.md`. Não são resultados desta validação; servem para **não duplicar** registro e para saber o que esperar nos cenários.

| ID (QA) | Prioridade | Problema | Estado informado | Cenário relacionado |
|---|---|---|---|---|---|
| BUG-04 | Alta | Upload de arquivos no processamento em lote retorna `501 Não implementado` | Aberto | CV09, CV17 |
| BUG-07 | Média | Logout não revoga o token no servidor | Aberto | CV25 |
| BUG-08 | Média | Validação de upload não verifica conteúdo/MIME | Aberto | CV19 |
| BUG-11 | Média | Migração inicial não contém todas as tabelas dos modelos atuais | Aberto | — (revisão do Caio) |
| BUG-12 | Média | Falha na inicialização pode manter o servidor ativo | Aberto | — |
| BUG-14 | Bloqueio | Tesseract e Poppler ausentes; impede teste real de OCR | Aberto | CV09, CV10, CV17 |
| BUG-15 | Bloqueio | Sem chave de criptografia de credenciais e sem chave externa de IA | Aberto | CV10 |
| BUG-16 | Média | Workflow `ci.yml` foi adicionado à main, mas com erro de indentação YAML | Parcial: execução não confirmada | — (Gabriel) |
| — | Alta | Cobertura de testes em **55,50%**, abaixo da meta de 80% | Aberto | — (Fernando) |

---

## 4. Inconsistências de documentação percebidas na revisão (para o Gabriel)

Observações de leitura do repositório, ainda não verificadas por execução:

| Item | Observação |
|---|---|
| Comandos de teste no README | O README manda executar `pytest --cov=backend backend/tests/`, mas os testes estão em `tests/unit/` na raiz do repositório. |
| Integrantes no README | A lista de integrantes está incompleta (Fernando sem sobrenome/RA; **Lucas e Caio ausentes**). |
| Documentos duplicados na raiz | Existem `GUIA OPERACIONAL .md`, `guia completo.md` e `prompt.md` na raiz; confirmar com o grupo se devem ficar na raiz ou em `docs/`. |

---

## 5. Rastreabilidade: Problemas ↔ Cenários de Validação (ATUALIZADO)

| Cenário | Problemas relacionados | Status do cenário |
|---|---|---|
| CV01 | FUNC-05 | PASSOU |
| CV02 | FUNC-01, FUNC-05 | **FALHOU** |
| CV03 | — | NÃO EXECUTADO |
| CV04 | — | PASSOU |
| CV05 | FUNC-02, FUNC-04 | PARCIAL |
| CV06 | FUNC-11 | **FALHOU** |
| CV07 | FUNC-12 | PARCIAL |
| CV08 | FUNC-13 | **FALHOU** |
| CV09 | BUG-04, BUG-14, FUNC-07 | BLOQUEADO |
| CV10 | BUG-15, BUG-08, FUNC-14 | BLOQUEADO/PARCIAL |
| CV11 | — | NÃO EXECUTADO |
| CV12 | FUNC-02, FUNC-15 | **FALHOU** |
| CV13 | FUNC-16 | **FALHOU** |
| CV14 | — | NÃO EXECUTADO |
| CV15 | FUNC-17 | **FALHOU** |
| CV16 | — | NÃO EXECUTADO |
| CV17 | BUG-14 | BLOQUEADO |
| CV18 | — | NÃO EXECUTADO |
| CV19 | BUG-08 | BLOQUEADO |
| CV20 | — (testar API) | BLOQUEADO |
| CV21 | FUNC-03 | PARCIAL |
| CV22 | FUNC-18 | **FALHOU** |
| CV23 | — | NÃO EXECUTADO |
| CV24 | — | NÃO EXECUTADO |
| CV25 | BUG-07 | NÃO EXECUTADO |

---

## 6. Ações recomendadas por prioridade (ATUALIZADO)

| # | Ação | Responsável | Bloqueia |
|---|---|---|---|---|
| 1 | Corrigir endpoint `/api/v1/aluno/minhas-notas` (FUNC-01) | Fernando | CV02, CV11, CV13 |
| 2 | Filtrar turmas por `professor_id` no backend (FUNC-02) | Fernando | CV05, CV12 |
| 3 | Mover verificação de permissão para **middleware/backend** antes de renderizar HTML (FUNC-03) | Fernando | CV21, CV25 |
| 4 | Formatters frontend: datas (pt-BR), booleanos (Sim/Não), headers traduzidos (FUNC-04) | Fernando | CV05 |
| 5 | Substituir mensagens técnicas por linguagem de usuário + contraste acessível (FUNC-05) | Fernando | CV01, CV02 |
| 6 | Adicionar filtro por perfil na gestão de usuários (FUNC-06, FUNC-19) | Fernando | RF18 |
| 7 | Implementar tela de armazenamento no painel admin (FUNC-07) | Fernando | — |
| 8 | Traduzir "Períodos letivos" e revisar toda a UI para pt-BR (FUNC-08, FUNC-21) | Fernando | RNF13 |
| 9 | Documentar requisito de SMTP_HOST ou implementar fallback de senha temporária na tela (FUNC-09) | Gabriel/Fernando | RF24 |
| 10 | Adicionar validação frontend/backend: nome (sem espaços excessivos), telefone (máscara/regex) (FUNC-10) | Fernando | RF24, RNF13 |
| 11 | Corrigir botão "Gerar prova PDF" (FUNC-11) | Fernando | CV06, CV08, CV11 |
| 12 | Remover termos técnicos "(multiple choice)", "(short answer)" do PDF (FUNC-12) | Fernando | CV07, CV15 |
| 13 | Corrigir impressão: reconhecer prova do banco de provas (FUNC-13) | Fernando | CV08, CV15, CV24 |
| 14 | IA: adicionar barra de progresso, corrigir contraste azul, melhorar status (FUNC-14) | Fernando | CV10 |
| 15 | Corrigir API: listar provas/turmas corretamente + não vazar erros técnicos (FUNC-15) | Fernando | CV12, CV05, CV06 |
| 16 | Limpar interface do aluno: remover "comandos" técnicos (FUNC-16) | Fernando | CV13 |
| 17 | Corrigir PDF aluno: remover códigos técnicos misturados (FUNC-17) | Fernando | CV15 |
| 18 | Corrigir auditoria: botão abrir, layout legível, métricas funcionais (FUNC-18) | Fernando | CV22 |
| 19 | Separar Cursos e Disciplinas na Gestão Acadêmica (FUNC-20) | Fernando/Caio | — |
| 20 | Corrigir botão hambúrguer + sidebar bug (FUNC-22) | Fernando | — |
| 21 | Implementar sistema de notificações + feedback no refresh (FUNC-23) | Fernando | — |
| 22 | Instalar Tesseract + Poppler no ambiente de teste (BUG-14) | Gabriel/DevOps | CV09, CV10, CV17 |
| 23 | Configurar `ENCRYPTION_KEY` e `NVIDIA_NIM_API_KEY` no `.env` (BUG-15) | Fernando | CV10 |
| 24 | Implementar revogação de token no logout / blacklist Redis (BUG-07) | Fernando | CV25 |
| 25 | Corrigir indentação YAML do `ci.yml` e confirmar execução (BUG-16) | Gabriel | CI/CD |
| 26 | Elevar cobertura de testes para ≥ 80% (BUG QA) | Fernando | Qualidade |