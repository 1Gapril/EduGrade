# Alterações realizadas durante a auditoria

**Estado:** alterações locais implementadas e validadas parcialmente; sem commit.

## Documentação

- Corrigidos links para o guia existente `como_rodar.md` e para o repositório
  real.
- Removidas senhas demonstrativas explícitas dos guias de instalação.
- Substituídos comandos que apagavam o SQLite por instruções de uso de um banco
  isolado identificado como `DADO_DE_TESTE_EDUGRADE`.
- Criados inventário funcional, matriz de testes e relatórios QA preliminares.
- Registrados resultados de execução completa e evidências E2E isoladas.

## Código

- Questões e submissões agora aplicam projeção/isolamento por perfil do aluno;
  os testes unitários cobrem as respostas sem gabarito e o bloqueio de
  registros alheios.
- Removido o acesso estático público a `/storage`; downloads devem passar por
  rotas autenticadas e validação de diretório permitido.
- A configuração OpenAI/Anthropic sem provider correspondente agora falha
  explicitamente, em vez de retornar uma correção mock como se fosse real.
- Login e dashboards não usam mais credenciais, números ou listas demonstrativas;
  campos sem API confiável são indicados como indisponíveis. O login revalida a
  sessão inicial antes do redirecionamento.
- A validação de perfil no workspace é apenas UX; a autorização do backend
  continua necessária.
- URL FCC com caminho final `/admin` é normalizada para a origem local, evitando
  duplicação em `/admin/api/...`; a tela explica o formato correto e orienta
  quando recebe HTTP 405.
- O dashboard do professor não interrompe mais o carregamento por referência a
  elemento ausente; KPIs e ações rápidas usam cartões em grid. O dashboard do
  aluno também teve o grid de indicadores restaurado.

## Validação

- 13 testes focados do backend passaram; a suíte final passou em 15 testes.
- A execução completa retorna código 1 pelo gate de cobertura: 55,50%, abaixo
  dos 80% exigidos.
- `node --check` passou nos dois arquivos JavaScript do frontend.
- `git diff --check` passou.
- Login E2E com perfis de teste admin, professor e aluno chegou aos dashboards;
  login inválido permaneceu na tela e exibiu erro.
- E2E professor: endpoints de materiais/revisões HTTP 200; sem disciplina
  atribuída, o envio ficou desabilitado com orientação para o administrador.
- E2E FCC: ao salvar `http://127.0.0.1:8082/admin`, a URL foi normalizada para
  `http://127.0.0.1:8082`; status e catálogo responderam, e a tela confirmou
  conexão. Nenhuma escrita foi feita no FCC.
- Screenshots admin, aluno, professor e FCC em `docs/QA/evidencias/`.

## Dados

O `.env` e o SQLite local foram preservados e não usados no E2E. Nenhum valor
de segredo foi exibido. Os fluxos de navegador usaram banco e storage
temporários identificados como `DADO_DE_TESTE_EDUGRADE`; não houve chamada
externa de IA, publicação de nota ou escrita/sincronização no FCC.
