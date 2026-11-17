# Relatório de testes — Administrador

**Status:** E2E parcial em ambiente isolado; CRUD geral ainda não validado.

## Superfícies encontradas

- `frontend/admin/dashboard.html`: visão administrativa, chamadas para perfil e
  contagem de solicitações pendentes; havia cartões/listas estáticos.
- `frontend/admin/settings.html`: configurações de provedores, sistema e FCC.
- Workspace virtual: gestão de usuários, solicitações, dados acadêmicos,
  períodos, auditoria, logs e storage.
- API: `/api/v1/users`, `/api/v1/access-requests`, `/api/v1/academic`,
  `/api/v1/audit` e `/api/v1/admin/settings`.

## Situação e riscos

O código declara operações administrativas e RBAC nas rotas. Há testes
unitários específicos para a Central de Configurações, mas não há evidência
E2E de CRUD geral, persistência após reload, auditoria, filtros ou respostas
negativas para todos os endpoints.

O login admin E2E e a abertura do dashboard passaram com usuário de teste.
A tabela exibiu os três usuários do banco isolado através da API; os cartões
sem fonte confiável não foram apresentados como métricas reais. Screenshot:
`docs/QA/evidencias/admin-dashboard.png`. Credenciais reais não foram usadas.

## Próximos testes

Continuar em ambiente isolado com conta marcada
`DADO_DE_TESTE_EDUGRADE`: criar/editar/desativar usuários, matrículas,
disciplinas, turmas, permissões, configurações, auditoria, erros e refresh.
Confirmar cada persistência sem tocar no banco local.
