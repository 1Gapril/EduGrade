# EduGrade — Documento de Entrega A3

**Trabalho A3 Prático — Gestão e Qualidade de Software (GQS)**
**Professor:** Daniel Henrique Matos de Paiva
**ODS 4:** Educação de Qualidade

---

## Integrantes

| Nome | RA | Responsabilidade principal |
|---|---|---|
| Fernando Almeida | 326132695 | Desenvolvimento com Claude Code, QA e integração |
| Lucas Henrique Miranda | 325131396 | Requisitos, regras de negócio e validação funcional |
| Caio Duraes | 325132875 | Arquitetura, banco de dados e validação técnica |
| Gabriel Ferreira | 325140970 | GitHub, documentação, DevOps e apresentação |

**Versão:** 1.1 — 05/11/2026 (atualizado pós-validação 04/11/2026)

---

## 1. Entregáveis Obrigatórios

| # | Entregável | Arquivo | Status |
|---|---|---|---|
| 1 | Plataforma funcional (Frontend + Backend + DB) | `backend/`, `frontend/`, `DADO_DE_TESTE_EDUGRADE.db` | ⚠️ Parcial |
| 2 | Requisitos Funcionais | `docs/REQUISITOS_FUNCIONAIS.md` | ✅ Completo |
| 3 | Regras de Negócio | `docs/REGRAS_DE_NEGOCIO.md` | ✅ Completo |
| 4 | Checklist Validação Funcional | `docs/CHECKLIST_VALIDACAO_FUNCIONAL.md` | ✅ Executado (24%) |
| 5 | Registro de Problemas | `docs/REGISTRO_PROBLEMAS.md` | ✅ Atualizado |
| 6 | Evidências Funcionais | `docs/evidencias/funcional/CVxx.png` | ⚠️ 8/25 coletadas |
| 7 | Testes unitários/integração (≥80% cobertura) | `tests/unit/`, `htmlcov/` | ❌ 55,50% |
| 8 | Relatório HTML de cobertura | `htmlcov/index.html` | ❌ Não gerado |
| 9 | Pipeline CI/CD (GitHub Actions) | `.github/workflows/ci.yml` | ⚠️ YAML com erro (BUG-16) |
| 10 | Documento acadêmico (este arquivo) | `docs/DOCUMENTO_ENTREGA_A3.md` | ✅ Atualizado |
| 11 | Roteiro de Apresentação | `docs/ROTEIRO_APRESENTACAO_A3.md` | ✅ Existe |

---

## 2. Funcionalidades Principais — Estado Atual

| Funcionalidade | Requisitos | Regras | Status | Evidência |
|---|---|---|---|---|
| **Autenticação** (login aluno/professor/admin) | RF01–RF03 | RN42 | ✅ Funciona (CV01, CV04) | `CV01a.png`, `CV01b.png`, `CV04.png` |
| **Consulta notas aluno** | RF04 | RN01, RN14 | ❌ **FALHA** (FUNC-01) | `CV02.png` |
| **Acesso professor às turmas** | — | RN11 | ⚠️ **PARCIAL** (FUNC-02) | `CV05a-c.png` |
| **Criação de prova + validação soma** | RF10 | RN16–RN19 | ⬜ Não testado | — |
| **Cadastro gabarito + versionamento** | RF12 | RN05, RN20, RN22 | ⬜ Não testado | — |
| **Impressão PDF + QR Code** | RF11 | RN25, RN27, RN28 | ⬜ Não testado | — |
| **Upload digitalizado + OCR** | RF13 | RN29–RN33 | 🚫 **BLOQUEADO** (BUG-14) | — |
| **Correção assistida por IA** | RF14, RF15 | RN34–RN40 | 🚫 **BLOQUEADO** (BUG-15) | — |
| **Publicação notas + auditoria** | RF16 | RN07, RN08, RN41 | ⬜ Não testado | — |
| **Segurança: isolamento por perfil** | — | RN11, RN13, RN15 | ⚠️ **PARCIAL** (FUNC-03) | `CV21.png` |
| **Admin: bloqueio/publicação notas** | — | RN12, RN02 | 🚫 **BLOQUEADO** (sem tela) | `CV20.png` |

---

## 3. Validação Funcional — Resumo Executado (04/11/2026)

### Cenários testados: 6/25 (24%)

| Status | Quantidade | Cenários |
|---|---|---|
| **PASSOU** | 3 | CV01a, CV01b, CV04 |
| **FALHOU** | 1 | CV02 (notas aluno não listam) |
| **PARCIAL** | 2 | CV05 (turmas erradas), CV21 (layout vaza) |
| **BLOQUEADO** | 5 | CV09, CV10, CV17, CV19, CV20 |
| **NÃO EXECUTADO** | 14 | CV03, CV06–CV08, CV11–CV16, CV18, CV22–CV25 |

### Evidências coletadas: 8 prints
`CV01a.png`, `CV01b.png`, `CV02.png`, `CV04.png`, `CV05a.png`, `CV05b.png`, `CV05c.png`, `CV20.png`, `CV21.png`

---

## 4. Problemas Identificados (Registro Consolidado)

### 4.1 Da Validação Funcional (10 novos — FUNC-01 a FUNC-10)

| ID | Severidade | Título | Responsável | Bloqueia |
|---|---|---|---|---|
| **FUNC-01** | **Alta** | Aluno não consulta notas (CV02) | Fernando | CV02, CV11, CV13 |
| **FUNC-02** | **Alta** | Turmas listam sistema todo, 0 matriculados (CV05) | Fernando | CV05, CV12 |
| **FUNC-03** | **Média** | Layout admin vaza antes do redirect (CV21) | Fernando | CV21, CV25 |
| **FUNC-04** | **Média** | JSON bruto, headers inglês, datas ISO (CV05) | Fernando | CV05 |
| **FUNC-05** | **Baixa** | Mensagens técnicas + baixo contraste | Fernando | CV01, CV02 |
| **FUNC-06** | **Média** | Gestão usuários não filtra por perfil | Fernando | RF18 |
| **FUNC-07** | **Média** | Painel admin: armazenamento não implementado | Fernando | — |
| **FUNC-08** | **Baixa** | "Períodos letivos" em inglês | Fernando | RNF13 |
| **FUNC-09** | **Média** | Criar conta por chamado falha sem SMTP | Gabriel/Fernando | RF24 |
| **FUNC-10** | **Baixa** | Formulário aceita dados inválidos | Fernando | RF24, RNF13 |

### 4.2 Pendências Herdadas da QA (01/11/2026)

| ID | Prioridade | Problema | Estado | Bloqueia |
|---|---|---|---|---|
| **BUG-04** | Alta | Upload lote retorna 501 | Aberto | CV09, CV17 |
| **BUG-07** | Média | Logout não revoga token | Aberto | CV25 |
| **BUG-08** | Média | Upload sem validação MIME | Aberto | CV19 |
| **BUG-11** | Média | Migração incompleta | Aberto | Caio |
| **BUG-12** | Média | Falha init mantém server ativo | Aberto | — |
| **BUG-14** | **Bloqueio** | Tesseract/Poppler ausentes | Aberto | CV09, CV10, CV17 |
| **BUG-15** | **Bloqueio** | Sem chaves criptografia/IA | Aberto | CV10 |
| **BUG-16** | Média | CI YAML com erro indentação | Parcial | Gabriel |
| — | **Alta** | Cobertura 55,50% < 80% | Aberto | Fernando |

---

## 5. Gaps Conhecidos para Entrega (Atualizar antes da entrega final)

| Dimensão | Gap | Ação Necessária | Responsável | Prazo |
|---|---|---|---|---|
| **Funcionalidade core** | Aluno não vê notas (FUNC-01) | Corrigir endpoint `/aluno/minhas-notas` | Fernando | Crítico |
| **Funcionalidade core** | Professor vê turmas erradas (FUNC-02) | Filtrar por `professor_id` no backend | Fernando | Crítico |
| **Segurança** | Auth no frontend (FUNC-03) | Mover para middleware/backend | Fernando | Crítico |
| **Infra/OCR** | Tesseract/Poppler (BUG-14) | Instalar no ambiente teste | Gabriel/DevOps | Alto |
| **Infra/IA** | Chave NVIDIA NIM (BUG-15) | Configurar no `.env` | Fernando | Alto |
| **Auth** | Token revocation (BUG-07) | Implementar blacklist/Redis | Fernando | Alto |
| **Qualidade** | Cobertura 55,5% (meta 80%) | Escrever testes unitários/integração | Fernando | Obrigatório |
| **CI/CD** | Pipeline não confirmado (BUG-16) | Corrigir YAML + rodar | Gabriel | Obrigatório |
| **Validação** | 14/25 CVs não executados | Completar checklist | Lucas | Obrigatório |
| **Evidências** | 17/25 prints faltando | Coletar durante validação | Lucas | Obrigatório |
| **Docs** | README incompleto (integrantes, comandos) | Atualizar | Gabriel | Médio |

---

## 6. Critérios de Aceite do Guia Operacional — Verificação

| Critério | Obrigatório? | Atendido? | Evidência |
|---|---|---|---|
| Sistema funcional (3 perfis, ciclo prova, IA com aprovação humana) | Sim | ⚠️ Parcial | FUNC-01, FUNC-02, BUG-14, BUG-15 bloqueiam |
| Cobertura ≥ 80% com relatório HTML | Sim | ❌ **Não** | 55,50% (BUG QA) |
| GitHub Actions passando | Sim | ⚠️ Parcial | BUG-16 (YAML erro) |
| Documentação completa (requisitos, regras, checklist, registro, A3, slides) | Sim | ✅ Sim | Arquivos em `docs/` |
| Versionamento GitFlow + commits padronizados | Sim | ✅ Sim | Branches `feature/*`, `docs/*`, `fix/*` |
| Evidências reais (prints, logs, relatórios) | Sim | ⚠️ Parcial | 8/25 prints |

---

## 7. Próximos Passos Priorizados (Roteiro para Entrega)

### Semana 1 — Desbloquear Validação
- [ ] Fernando: Corrigir FUNC-01, FUNC-02, FUNC-03 (backend auth + queries)
- [ ] Fernando: Corrigir FUNC-04, FUNC-05 (frontend formatters + i18n)
- [ ] Gabriel/DevOps: Instalar Tesseract + Poppler (BUG-14)
- [ ] Fernando: Configurar `ENCRYPTION_KEY` + `NVIDIA_NIM_API_KEY` no `.env` (BUG-15)
- [ ] Gabriel/Fernando: Documentar SMTP_HOST ou implementar fallback (FUNC-09)

### Semana 2 — Completar Validação Funcional
- [ ] Lucas: Executar CV03, CV06–CV11 (fluxo principal professor)
- [ ] Lucas: Executar CV12–CV25 (cenários negativos/segurança)
- [ ] Lucas: Coletar 17 prints faltantes → `docs/evidencias/funcional/`
- [ ] Lucas: Atualizar `CHECKLIST_VALIDACAO_FUNCIONAL.md` com resultados finais
- [ ] Lucas: Fechar FUNCs resolvidos no `REGISTRO_PROBLEMAS.md`

### Semana 3 — Qualidade e Entrega
- [ ] Fernando: Implementar revogação token logout (BUG-07)
- [ ] Fernando: Elevar cobertura para ≥ 80% + gerar `htmlcov/`
- [ ] Gabriel: Corrigir `ci.yml` + confirmar execução no Actions
- [ ] Gabriel: Atualizar README (integrantes completos, comandos corretos)
- [ ] Gabriel: Decidir docs na raiz vs `docs/`
- [ ] Lucas: Atualizar seção "Limitações conhecidas" no `DOCUMENTO_ENTREGA_A3.md`
- [ ] Todos: Revisão cruzada + ensaio apresentação

---

## 8. Assinaturas

| Papel | Nome | RA | Assinatura | Data |
|---|---|---|---|---|
| **Product Owner / Validação** | Lucas Henrique Miranda | 325131396 | _______________ | ___/___/____ |
| **Desenvolvimento / QA** | Fernando Almeida | 326132695 | _______________ | ___/___/____ |
| **Arquitetura / Banco** | Caio Duraes | 325132875 | _______________ | ___/___/____ |
| **DevOps / Documentação** | Gabriel Ferreira | 325140970 | _______________ | ___/___/____ |

---

## 9. Referências Internas

- `docs/REQUISITOS_FUNCIONAIS.md` — 29 RFs + 13 RNFs + 4 itens em aberto
- `docs/REGRAS_DE_NEGOCIO.md` — 45 regras (RN01–RN45)
- `docs/CHECKLIST_VALIDACAO_FUNCIONAL.md` — 25 cenários + resultados 04/11/2026
- `docs/REGISTRO_PROBLEMAS.md` — 10 FUNCs novos + 8 BUGs herdados + rastreabilidade
- `docs/evidencias/funcional/` — 8 prints coletados, 17 pendentes
- `docs/QA/MATRIZ_DE_TESTES.md` — QA anterior (01/11/2026)
- `docs/ROTEIRO_APRESENTACAO_A3.md` — Slides da apresentação

---

**Última atualização:** 05/11/2026 — Lucas Henrique Miranda (RA 325131396)  
**Baseado na execução de:** 04/11/2026 (validação funcional) + revisão repositório 01/11/2026 (QA)