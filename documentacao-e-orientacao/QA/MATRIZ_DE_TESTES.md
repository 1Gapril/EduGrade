# Matriz de testes EduGrade

**Estado:** execução em andamento; não usar como aprovação final.
**Data:** 2026-11-01.

Todos os testes com persistência devem usar um banco e diretórios descartáveis.
O banco local existente não é massa de teste. Dados criados para testes devem
ser identificados como `DADO_DE_TESTE_EDUGRADE`, com origem e finalidade
registradas. Não usar contas presumidas nem expor senhas.

| ID | Perfil | Funcionalidade | Pré-condições | Passos executados | Resultado esperado | Resultado obtido | Status | Evidência | Defeito |
|---|---|---|---|---|---|---|---|---|---|
| QA-BASE-01 | — | Suíte unitária completa | Ambiente Python atual | `venv\\Scripts\\python.exe -m pytest tests/ -v` | Todos passam e cobertura >= 80% | 15 passaram; cobertura 55,50%; comando saiu com código 1 | FALHOU GATE DE COBERTURA | Saída pytest 2026-11-01; `pyproject.toml` | Cobertura abaixo de 80% |
| AUTH-01 | Público | Login inválido | Aplicação e banco isolados | Submeter conta QA inexistente | Erro explícito, sem sessão | HTTP 401; mensagem “Credenciais inválidas”; permaneceu no login | PASSOU | Navegador integrado, 2026-11-01 | Nenhum |
| AUTH-02 | Admin/professor/aluno | Login válido e sessão após refresh | Contas `DADO_DE_TESTE_EDUGRADE` em banco isolado | Login nos três perfis, abrir dashboard e recarregar | Perfil correto e sessão consistente | Os três perfis abriram seus dashboards; reload professor manteve sessão | PASSOU (LOGIN/SESSÃO) | Screenshots em `docs/QA/evidencias/`; navegador integrado | CRUD/refresh ainda não exercitados |
| AUTH-03 | Autenticado | Logout e reutilização do token | Token de teste | Logout e tentar reusar token | Backend rejeita token | Código indica logout client-side | COM DEFEITO / PENDENTE | Rotas/auth e serviço citados no relatório de segurança | Sem revogação no servidor |
| ADMIN-01 | Admin | CRUD de usuário | Banco isolado e conta de teste | Consultar listagem de usuários | A lista deve vir da API e refletir a base de teste | Tabela mostrou os três usuários QA da API; CRUD não exercitado | PARCIAL | `admin-dashboard.png` | Edição/exclusão/persistência ainda não testadas |
| ADMIN-02 | Professor/aluno | Bloqueio de operações admin | Tokens de perfis de teste | Requisitar endpoints administrativos diretamente | HTTP 403 no backend | Somente testes da central existentes; demais pendentes | PENDENTE | `tests/unit/test_admin_settings.py` | Cobertura de RBAC incompleta |
| PROF-01 | Professor | Criar prova e imprimir | Prova de teste isolada | Criar questões/gabarito e gerar PDF do aluno | Persistência e PDF sem gabarito | Não executado; PDF indicado indisponível | PENDENTE | Não coletada | OCR/PDF externo indisponível |
| PROF-DASH-01 | Professor | Dashboard e materiais | Professor isolado sem disciplina | Login, aguardar chamadas de materiais e revisar estados | Erro explícito, sem carregamento infinito ou dados fictícios | APIs responderam HTTP 200; erro de tela corrigido; envio desabilitado por falta de disciplina atribuída | PASSOU (DASHBOARD) | `professor-dashboard.png`; navegador integrado | Provas/materiais reais não criados |
| PROF-02 | Professor | Upload batch | Lote isolado | Enviar vários arquivos e consultar progresso | Arquivos persistidos e processados | Rota observada retorna `501` | BLOQUEADO POR IMPLEMENTAÇÃO | Inventário estático do backend | Upload batch ausente |
| PROF-03 | Professor | Revisão e publicação | Correção de teste pendente | Revisar, editar nota e aprovar | Nota só publica após aprovação; auditoria individual | Não executado | PENDENTE | Não coletada | Não determinado |
| STUD-01 | Aluno | Consultar dados próprios publicados | Aluno e nota de teste | Login e abrir painel | Dados reais próprios apenas; indisponíveis claramente identificados | Dashboard sem números fictícios; métricas e notas sem endpoint aparecem indisponíveis; sem registros QA publicados | PARCIAL | `aluno-dashboard.png`; navegador integrado | Persistência/consulta de notas não testada |
| STUD-02 | Aluno | Acesso a gabarito/submissão alheia | Dois alunos de teste | Testes unitários de autorização | Conteúdo alheio negado e gabarito omitido | Correção coberta por testes unitários; sem tentativa E2E com prova criada | PASSOU (UNITÁRIO) | `tests/unit/test_authorization_private_files.py` | E2E com prova/submissões pendente |
| FILE-01 | Anônimo/aluno | Download de arquivo privado | Arquivo marcador em storage de teste | Testes unitários de arquivo privado | HTTP 401/403; arquivo não servido | Mount público removido; testes unitários focados passaram; download E2E não executado | PASSOU (UNITÁRIO) | `tests/unit/test_authorization_private_files.py` | Fluxos completos de download pendentes |
| OCR-01 | Professor | OCR de imagem/PDF | Tesseract/idioma e PDF de teste | Enviar arquivo e processar OCR | Texto/estado de revisão persistidos | Tesseract/Poppler ausentes; PDF não localizado | BLOQUEADO POR DEPENDÊNCIA | Verificação local de ferramentas | Dependências/arquivo ausentes |
| AI-01 | Professor | Correção por provider real | Chave autorizada e provedor acessível | Teste unitário do factory e checagem redigida do ambiente | Erro explícito sem provider; sugestão nunca publica sozinha | Provider local `mock`; OpenAI/Anthropic sem chave; provider ausente agora falha explicitamente nos testes | BLOQUEADO POR CREDENCIAL | `tests/unit/test_ai_provider_factory.py`; indicadores não secretos do ambiente | Sem integração autenticada/real |
| FCC-01 | Admin | Status e catálogo FCC | Serviço local disponível | GET status e models; testar pela central e salvar URL terminando em `/admin` | HTTP válido, URL canônica e sem expor segredo | FCC status/catalog HTTP 200 (38 modelos); endereço normalizado para origem e comunicação confirmada | PASSOU (somente leitura do FCC) | `fcc-settings.png`; navegador integrado, 2026-11-01 | Não prova geração nem chave direta NVIDIA |
| FCC-02 | Admin | Sincronizar NVIDIA e gerar via FCC | Chave NVIDIA e autorização de sincronização | Sincronizar modelo e executar cliente real | Resposta real válida do cliente | Não executado; sem chave fornecida | BLOQUEADO POR CREDENCIAL | Nenhuma | Credencial/consentimento ausentes |
| DATA-01 | — | Preservar dados locais | Banco existente | Inspecionar apenas presença/contagens agregadas | Não alterar nem expor dados sem origem conhecida | Banco não vazio; preservado | NÃO TESTÁVEL SEM VALIDAÇÃO | Verificação SQLite read-only | Origem dos registros desconhecida |

## Evidências automatizadas anteriores

Na execução completa final, **15 testes passaram**. O comando retornou código
1 porque a cobertura agregada foi **55,50%**, abaixo do limite
de 80% em `pyproject.toml`. `git diff --check` e `node --check` para os dois
arquivos JavaScript passaram.

## Evidências do navegador

O login válido admin/professor/aluno, os dashboards e o login inválido foram
exercitados com banco/storage isolados. Screenshots: `admin-dashboard.png` e
`aluno-dashboard.png` em `docs/QA/evidencias/`. Nenhuma operação de publicação
ou exclusão foi feita em dados reais.
