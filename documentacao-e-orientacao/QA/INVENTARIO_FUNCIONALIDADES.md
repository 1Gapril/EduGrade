# Inventário funcional EduGrade

**Estado:** inventário estático com E2E parcial; não é certificação de funcionamento.
**Data:** 2026-11-01.

## Evidência e limites

O inventário foi montado a partir da documentação, dos arquivos de tela, do
código das rotas e de uma navegação parcial em browser integrado com banco e
storage temporários. “Implementada no código” não significa fluxo E2E aprovado.

O banco SQLite local contém registros e foi preservado; não foi usado para
testes nem para login. O `.env` está ignorado e não foi alterado; foram
verificados apenas indicadores não secretos, sem exibir valores de segredo.

## Telas e rotas

| Tela / fluxo | Perfil previsto | Endpoint / camada observada | Entidade | Situação observada |
|---|---|---|---|---|
| `frontend/index.html` | Público | Redirecionamento para login | — | IMPLEMENTADA como redirecionamento estático; sem teste visual |
| `frontend/login.html` | Todos | `POST /api/v1/auth/login`; `GET /auth/me`; `POST /auth/refresh` | `users` | Login válido passou para os três perfis; login inválido exibe erro. E2E parcial; refresh não testado |
| `frontend/register.html` | Público | `POST /api/v1/access-requests` | `access_requests` | PARCIALMENTE IMPLEMENTADA; submissão HTTP existe, aprovação e envio de credenciais não foram testados |
| `frontend/dashboard.html` | Autenticado | Shell e navegação para painéis | — | PARCIALMENTE IMPLEMENTADA; o conteúdo depende de telas físicas ou do workspace virtual |
| `frontend/admin/dashboard.html` | Administrador | `/api/v1/auth/me`, `/api/v1/access-requests/pending-count`, consultas de usuários | `users`, `access_requests` | Login/dashboard passou; tabela exibiu usuários do banco isolado; métricas sem endpoint aparecem indisponíveis |
| `frontend/admin/settings.html` | Administrador | `/api/v1/admin/settings/*` | `ai_provider_configs`, `admin_settings`, auditoria | IMPLEMENTADA no código; integração externa não significa credencial ou conexão verificada |
| `frontend/professor/dashboard.html` | Professor | `/api/v1/auth/me`, `/api/v1/materials/teacher*`, `POST /api/v1/materials` | `users`, `study_materials` | Login/dashboard passaram; materiais carregam; sem disciplina atribuída, envio fica desabilitado com orientação ao administrador |
| `frontend/aluno/dashboard.html` | Aluno | `/api/v1/auth/me`, `/api/v1/materials/student*`, `/api/v1/materials/{id}/download` | `users`, `study_materials` | Login/dashboard passaram; materiais vazios sem conteúdo fictício; notas/frequência sem fonte confiável aparecem indisponíveis |
| `frontend/workspace.html` + `frontend/js/workspace.js` | Vários | Rotas virtuais de usuários, chamados, acadêmico, provas, correção, aluno e professor | Modelos do módulo correspondente | PARCIALMENTE IMPLEMENTADA; várias páginas são apenas templates, o controle global de perfil é desigual e há uma colisão de rota de configurações |

As rotas virtuais mapeadas pelo workspace incluem administração de usuários,
solicitações de acesso, dados acadêmicos, períodos, auditoria, IA, logs e
armazenamento; criação/edição/listagem/impressão de provas; correção em lote e
revisão; e consultas de notas, frequência e horários. Algumas dessas telas
exibem explicitamente estado “não implementado” no próprio código. O mapa não
é evidência de operação funcional.

## Backend por módulo

Prefixo comum: `/api/v1`.

| Módulo / rotas | Perfil indicado no código | Serviço / modelos principais | Situação e ressalvas |
|---|---|---|---|
| `/auth` | Público para login/refresh; autenticado para perfil, logout e senha | `auth_service`, `users` | Login implementado no código; logout não revoga tokens no servidor |
| `/access-requests` | Público para criar; admin para listar/aprovar/rejeitar | Solicitações e usuários | Fluxo existe no código; notificações/entrega de credenciais e persistência não foram confirmadas E2E |
| `/users` | Maioria admin; leituras específicas para professor/aluno | `user_service`, `users`, `students`, `teachers`, `administrators` | CRUD declarado; autorização por objeto/perfil precisa de testes |
| `/academic` | Admin para cadastros; professor/admin para notas e frequência; leituras autenticadas | `academic_service`, cursos, disciplinas, turmas, matrículas, avaliações e notas | Endpoints existem; isolamento e publicação exigem testes |
| `/exams` | Escrita professor/admin; leitura protegida por perfil | `exam_service`, provas, questões, gabaritos, cópias e submissões | Questões omitem gabarito para aluno e submissões são isoladas; testes unitários focados passaram |
| `/ai` | Saúde/modelos autenticados; correção/revisão professor/admin | `ai_correction_service`, `ai_corrections`, avaliações | OpenAI/Anthropic sem provider correspondente agora falham explicitamente; provider real não configurado/testado |
| `/batch-grading` | Professor/admin | `batch_grading_service`, lotes, arquivos, páginas e grupos | Upload de arquivos responde `501 Not Implemented`; fluxo de lote não está completo |
| `/materials` | Professor/admin para publicar; aluno para listar; download autenticado | `material_service`, `study_materials` | Rotas existem; escopo de download e acesso a arquivos precisam de verificação |
| `/audit` | Admin | `audit_logs`, registros de auditoria | Consulta implementada no código; cobertura E2E ausente |
| `/admin/settings` | Admin | `admin_settings_service`, provedores e configurações | Status FCC E2E confirmado após normalização do endereço local; teste autenticado NVIDIA e sincronização exigem chave e confirmação |

## Dados e infraestrutura observados

- O SQLite configurado localmente existe e não está vazio. Sua origem não foi
  determinada; nenhum registro foi lido individualmente ou alterado.
- A configuração local não tem `CREDENTIAL_ENCRYPTION_KEY`; o cofre não pode
  salvar novas credenciais até ser inicializado.
- O FCC `free-claude-code` versão 6.18.1 responde em loopback na porta 8082.
  `GET /admin/api/status` e `GET /admin/api/models` responderam HTTP 200; o
  catálogo atual informou 38 modelos. Isso não comprova chamada de geração pelo
  cliente FCC nem validação de chave NVIDIA do EduGrade.
- O PDF `SimuladoA1GQSQuestes_20261019142118(2).pdf` não foi localizado nos
  diretórios do projeto nem no perfil pesquisado.
- O executável Tesseract configurado não foi encontrado; Poppler (`pdfinfo`,
  `pdftoppm`) também não está disponível. As bibliotecas Python de PDF/imagem
  consultadas estão instaladas.
- Os pacotes locais Python/Node de Playwright não estão instalados; o browser
  integrado foi usado para login válido/inválido e dashboards em E2E parcial.

## Critério de conclusão

Este inventário é preliminar. Ainda faltam operações de persistência,
autorização E2E, logout/revogação, uploads, impressão, OCR e correção em banco e
storage isolados com dados `DADO_DE_TESTE_EDUGRADE`. O teste de login/dashboard
não aprova esses outros fluxos.
