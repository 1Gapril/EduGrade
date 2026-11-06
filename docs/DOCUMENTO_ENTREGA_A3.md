# EduGrade — Documento de Entrega A3

**Trabalho A3 Prático — Gestão e Qualidade de Software (GQS)**
**Professor:** Daniel Henrique Matos de Paiva
**ODS 4:** Educação de Qualidade

---

## Integrantes

| Nome | RA | Responsabilidade principal |
|---|---|---|
| Fernando Almeida | 326132695 | Desenvolvimento, QA e integração |
| Lucas Henrique Miranda | 325131396 | Requisitos, regras de negócio e validação funcional |
| Caio Duraes | 325132875 | Arquitetura, banco de dados e validação técnica |
| Gabriel Ferreira | 325140970 | GitHub, documentação, DevOps e apresentação |

**Versão:** 1.2 — 05/11/2026 

---

## 1. Entregáveis Obrigatórios

| # | Entregável | Arquivo | Status |
|---|---|---|---|
| 1 | Plataforma funcional (Frontend + Backend + DB) | `backend/`, `frontend/`, `DADO_DE_TESTE_EDUGRADE.db` |  Parcial |
| 2 | Requisitos Funcionais | `docs/REQUISITOS_FUNCIONAIS.md` |  Completo |
| 3 | Regras de Negócio | `docs/REGRAS_DE_NEGOCIO.md` |  Completo |
| 4 | Checklist Validação Funcional | `docs/CHECKLIST_VALIDACAO_FUNCIONAL.md` |  Executado (56% com evidência) |
| 5 | Registro de Problemas | `docs/REGISTRO_PROBLEMAS.md` |  Atualizado (23 FUNCs + 8 BUGs herdados) |
| 6 | Evidências Funcionais | `docs/EVIDENCIAS_FUNCIONAIS.md` |  14/25 cenários com print registrado |
| 7 | Testes unitários/integração (≥80% cobertura) | `tests/unit/`, `htmlcov/` | apenas 55,50% |
| 8 | Relatório HTML de cobertura | `htmlcov/index.html` |  Não gerado |
| 9 | Pipeline CI/CD (GitHub Actions) | `.github/workflows/ci.yml` |  YAML com erro (BUG-16) |
| 10 | Documento acadêmico (este arquivo) | `docs/DOCUMENTO_ENTREGA_A3.md` |  Atualizado |
| 11 | Roteiro de Apresentação | `docs/ROTEIRO_APRESENTACAO_A3.md` |  Existe |

---

## 2. Funcionalidades Principais — Estado Atual (Atualizado 05/11/2026)

| Funcionalidade | Requisitos | Regras | Status | Evidência |
|---|---|---|---|---|
| **Autenticação** (login aluno/professor/admin) | RF01–RF03 | RN42 |  Funciona (CV01, CV04) | `CV01a.png`, `CV01b.png`, `CV04.png` |
| **Consulta notas aluno** | RF04 | RN01, RN14 |  **FALHA** (FUNC-01) | `CV02.png` |
| **Acesso professor às turmas** | — | RN11 |  **PARCIAL** (FUNC-02) | `CV05a-c.png` |
| **Criação de prova + validação soma** | RF10 | RN16–RN19 |  **FALHA** (FUNC-11) | `CV06.png` |
| **Cadastro gabarito + versionamento** | RF12 | RN05, RN20, RN22 |  **PARCIAL** (FUNC-12) | `CV07.png` |
| **Impressão PDF + QR Code** | RF11 | RN25, RN27, RN28 |  **FALHA** (FUNC-13) | `CV08.png` |
| **Upload digitalizado + OCR** | RF13 | RN29–RN33 |  **BLOQUEADO** (BUG-14) | `CV09.png` |
| **Correção assistida por IA** | RF14, RF15 | RN34–RN40 |  **BLOQUEADO** (BUG-15 + FUNC-14) | `CV10.png` |
| **Publicação notas + auditoria** | RF16 | RN07, RN08, RN41 |  **FALHA** (FUNC-18) | `CV22.png` |
| **Segurança: isolamento por perfil** | — | RN11, RN13, RN15 |  **PARCIAL** (FUNC-03, FUNC-15) | `CV21.png` |
| **Admin: bloqueio/publicação notas** | — | RN12, RN02 |  **BLOQUEADO** (sem tela) | `CV20.png` |
| **Admin: gestão usuários/filtros** | RF18 | — |  **FALHA** (FUNC-06, FUNC-19) | `ADMIN_EVIDENCIA.md` |
| **Admin: UI/UX (idiomas, campos técnicos)** | RNF13 | — |  **PARCIAL** (FUNC-08, FUNC-21) | `ADMIN_EVIDENCIA.md` |

---

## 3. Validação Funcional — Resumo Executado (04/11/2026)

### Cenários com evidência registrada: 14/25 (56%)

| Status | Quantidade | Cenários |
|---|---|---|
| **PASSOU** | 3 | CV01a, CV01b, CV04 |
| **FALHOU** | 7 | CV02, CV06, CV08, CV12, CV13, CV15, CV22 |
| **PARCIAL** | 4 | CV05, CV07, CV10, CV21 |
| **BLOQUEADO** | 5 | CV09, CV17, CV19, CV20, CV25 |
| **NÃO EXECUTADO** | 6 | CV03, CV11, CV14, CV16, CV18, CV23, CV24 |

**Detalhamento das evidências:** consulte `docs/EVIDENCIAS_FUNCIONAIS.md` (lista completa com arquivos esperados, status e observações). **Nota:** 0 prints físicos na pasta `docs/evidencias/funcional/` — capturar e salvar como `CVXX.png` antes da entrega final. 

## 4. Problemas Identificados (Registro Consolidado)

### 4.1 Da Validação Funcional (23 novos — FUNC-01 a FUNC-23)

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
| **FUNC-11** | **Alta** | Botão "Gerar prova PDF" não funciona (CV06) | Fernando | CV06, CV08, CV11 |
| **FUNC-12** | **Média** | PDF mostra "(multiple choice)" / "(short answer)" (CV07) | Fernando | CV07, CV15 |
| **FUNC-13** | **Alta** | Impressão não reconhece banco de provas (CV08) | Fernando | CV08, CV15, CV24 |
| **FUNC-14** | **Média** | IA: sem barra progresso, azul ilegível, status confuso (CV10) | Fernando | CV10 |
| **FUNC-15** | **Alta** | API não lista provas/turmas + vazamento técnico (CV12) | Fernando | CV12, CV05, CV06 |
| **FUNC-16** | **Média** | Aluno vê comandos técnicos na interface (CV13) | Fernando | CV13 |
| **FUNC-17** | **Alta** | PDF aluno mostra códigos técnicos misturados (CV15) | Fernando | CV15 |
| **FUNC-18** | **Alta** | Auditoria: botão não abre, ilegível, métricas quebradas (CV22) | Fernando | CV22 |
| **FUNC-19** | **Média** | Filtros gestão usuários não funcionam (Admin) | Fernando | RF18 |
| **FUNC-20** | **Média** | Cursos/Disciplinas fundidos na Gestão Acadêmica | Fernando/Caio | — |
| **FUNC-21** | **Baixa** | Perfil admin: inglês+português + expõe is_superuser/role | Fernando | RNF13, RN15 |
| **FUNC-22** | **Baixa** | Botão hambúrguer sem função + sidebar bug | Fernando | RNF13 |
| **FUNC-23** | **Média** | Notificações sem sistema + refresh sem feedback | Fernando | — |

> **OBS da CV20 (Admin lançar notas):** Sem tela de lançar notas para o admin, ele não consegue lançar pela interface. Marcar **PASSOU** mascom a observação: *"bloqueado pela ausência da tela; falta confirmar pela API"* (RN15). Confirmar na API é o que vale pela RN15.

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
| **Funcionalidade core** | Criação prova/PDF/gabarito quebrados (FUNC-11,12,13) | Corrigir fluxo professor completo | Fernando | Crítico |
| **Segurança** | Auth no frontend (FUNC-03) | Mover para middleware/backend | Fernando | Crítico |
| **Segurança** | API vaza erros técnicos (FUNC-15) | Sanitizar respostas de erro | Fernando | Alto |
| **Infra/OCR** | Tesseract/Poppler (BUG-14) | Instalar no ambiente teste | Gabriel/DevOps | Alto |
| **Infra/IA** | Chave NVIDIA NIM (BUG-15) | Configurar no `.env` | Fernando | Alto |
| **Auth** | Token revocation (BUG-07) | Implementar blacklist/Redis | Fernando | Alto |
| **Qualidade** | Cobertura 55,5% (meta 80%) | Escrever testes unitários/integração | Fernando | Obrigatório |
| **CI/CD** | Pipeline não confirmado (BUG-16) | Corrigir YAML + rodar | Gabriel | Obrigatório |
| **Validação** | 6/25 CVs não executados | Completar checklist | Lucas | Obrigatório |
| **Evidências** | 11/25 prints faltando | Capturar nos cenários pendentes | Lucas | Obrigatório |
| **Docs** | README incompleto (integrantes, comandos) | Atualizar | Gabriel | Médio |

---

## 6. Critérios de Aceite do Guia Operacional — Verificação

| Critério | Obrigatório? | Atendido? | Evidência |
|---|---|---|---|
| Sistema funcional (3 perfis, ciclo prova, IA com aprovação humana) | Sim |  Parcial | FUNC-01,02,11,12,13, BUG-14,15 bloqueiam |
| Cobertura ≥ 80% com relatório HTML | Sim |  **Não** | 55,50% (BUG QA) |
| GitHub Actions passando | Sim |  Parcial | BUG-16 (YAML erro) |
| Documentação completa (requisitos, regras, checklist, registro, A3, slides) | Sim |  Sim | Arquivos em `docs/` |
| Versionamento GitFlow + commits padronizados | Sim | Sim | Branches `feature/*`, `docs/*`, `fix/*` |
| Evidências reais (prints, logs, relatórios) | Sim |  Parcial | 14/25 prints registrados em `EVIDENCIAS_FUNCIONAIS.md` |

---

## 7. Próximos Passos Priorizados (Roteiro para Entrega)

### Parte 1 Desbloquear Validação 
- [ ] Fernando: Corrigir FUNC-01, FUNC-02, FUNC-03 (backend auth + queries + middleware)
- [ ] Fernando: Corrigir FUNC-04, FUNC-05 (frontend formatters + i18n + contraste)
- [ ] Fernando: Corrigir FUNC-11, FUNC-12, FUNC-13 (fluxo prova: gerar PDF, gabarito, impressão)
- [ ] Fernando: Corrigir FUNC-15 (API não lista provas/turmas + sanitizar erros)
- [ ] Fernando: Corrigir FUNC-14 (IA: barra progresso, contraste azul, status)
- [ ] Gabriel/DevOps: Instalar Tesseract + Poppler (BUG-14)
- [ ] Fernando: Configurar `ENCRYPTION_KEY` + `NVIDIA_NIM_API_KEY` no `.env` (BUG-15)
- [ ] Gabriel/Fernando: Documentar SMTP_HOST ou implementar fallback (FUNC-09)

### Parte 2 — Completar Validação Funcional 
- [ ] Lucas: Converter 23 WMFs → PNGs (Paint/ImageMagick)
- [ ] Lucas: Capturar CV24 (QR Code) e CV25 (logout token reuse)
- [ ] Lucas: Executar CV03, CV11, CV14, CV16, CV18, CV23 (cenários restantes)
- [ ] Lucas: Coletar prints dos cenários executados
- [ ] Lucas: Atualizar `CHECKLIST_VALIDACAO_FUNCIONAL.md` com resultados finais
- [ ] Lucas: Fechar FUNCs resolvidos no `REGISTRO_PROBLEMAS.md`

### Parte 3 — Correções de UI/Admin + Qualidade 
- [ ] Fernando: Corrigir FUNC-06, FUNC-19 (filtros gestão usuários)
- [ ] Fernando: Corrigir FUNC-20 (separar Cursos/Disciplinas)
- [ ] Fernando: Corrigir FUNC-21 (perfil admin: idiomas + campos técnicos)
- [ ] Fernando: Corrigir FUNC-22 (hambúrguer + sidebar)
- [ ] Fernando: Corrigir FUNC-23 (notificações + refresh)
- [ ] Fernando: Corrigir FUNC-16, FUNC-17 (interface aluno limpa)
- [ ] Fernando: Corrigir FUNC-18 (auditoria funcional + legível)
- [ ] Fernando: Implementar revogação token logout (BUG-07)
- [ ] Fernando: Elevar cobertura para ≥ 80% + gerar `htmlcov/`
- [ ] Gabriel: Corrigir `ci.yml` + confirmar execução no Actions
- [ ] Gabriel: Atualizar README (integrantes completos, comandos corretos)
- [ ] Gabriel: Decidir docs na raiz vs `docs/`

### Parte 4 — Ensaio + Entrega Final 
- [ ] Lucas: Atualizar seção "Limitações conhecidas" no `DOCUMENTO_ENTREGA_A3.md`
- [ ] Lucas: Revisar `ROTEIRO_APRESENTACAO_A3.md` com evidências reais
- [ ] Todos: Revisão cruzada + ensaio apresentação
- [ ] Commit final + tag de entrega



## 8. Referências Internas

- `docs/REQUISITOS_FUNCIONAIS.md` — 29 RFs + 13 RNFs + 4 itens em aberto
- `docs/REGRAS_DE_NEGOCIO.md` — 45 regras (RN01–RN45)
- `docs/CHECKLIST_VALIDACAO_FUNCIONAL.md` — 25 cenários + resultados 04/11/2026
- `docs/REGISTRO_PROBLEMAS.md` — 23 FUNCs novos + 8 BUGs herdados + rastreabilidade completa
- `docs/EVIDENCIAS_FUNCIONAIS.md` — 14/25 cenários com evidência registrada
- `docs/QA/MATRIZ_DE_TESTES.md` — QA anterior (01/11/2026)
- `docs/ROTEIRO_APRESENTACAO_A3.md` — Slides da apresentação

---

**Última atualização:** 05/11/2026 — Lucas Henrique Miranda (RA 325131396)  
**Baseado na execução de:** 04/11/2026 (validação funcional) + revisão repositório 01/11/2026 (QA) 
