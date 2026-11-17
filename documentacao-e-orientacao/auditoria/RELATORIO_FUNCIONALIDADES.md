# Relatório de funcionalidades — EduGrade

**Data:** 05/11/2026

“Aprovada” abaixo significa apenas que há evidência da execução indicada; inspeção de código isolada não comprova o fluxo completo.

| Funcionalidade | Estado | Evidência / pendência |
|---|---|---|
| Vínculo professor-disciplina pela API | PARCIAL | Endpoints administrativos existem. Foram corrigidos persistência por requisição e detecção de duplicidade por período; testes unitários passaram. |
| Gestão de vínculos na interface administrativa | PARCIAL | Incluídos formulário e ações de coordenação/remoção em `/admin/academic.html`; JavaScript passou em `node --check`. Não houve teste E2E no navegador. |
| Consulta de disciplinas pelo professor | PARCIAL | Listagem e detalhe foram restringidos a disciplinas associadas; testes unitários cobrem a negação do detalhe não autorizado. Sem teste com banco conectado. |
| Consulta de turmas | PARCIAL | Listagem agora aplica filtros e escopo para professor/aluno; detalhe valida vínculo do professor ou matrícula ativa do aluno. Testes unitários verificam restrição do professor; fluxo completo não executado. |
| Permissões de acesso a turmas | PARCIAL | `PermissionService` usa repositórios de perfil existentes; caminhos de autorização aluno/professor cobertos por testes unitários. |
| Criação/edição/publicação de provas | PARCIAL | Há rotas, serviços, telas e testes existentes. Não foi executado fluxo E2E de login até publicação. |
| Questões, gabaritos e validação de pontuação | PARCIAL | Código e testes unitários existentes; integração persistente e interface completa não foram confirmadas nesta execução. |
| PDF e impressão | PARCIAL | Há serviços e rotas; sem geração/abertura real em navegador nesta auditoria. |
| Upload, OCR e correção assistida por IA | PARCIAL | Matrícula sem campo correspondente no modelo não leva mais a falha nem a identificação automática incorreta; vira conflito para revisão manual. Provedores reais não foram usados. |
| Revisão humana e publicação de notas | PARCIAL | Após revisão completa, calcula a nota e publica registro oficial apenas se aluno, matrícula ativa e avaliação correspondente forem confirmados. Testes unitários passaram; fluxo autenticado em banco persistente não foi executado. |
| Painéis de aluno e privacidade entre alunos | PARCIAL | Não foi realizada tentativa E2E com duas contas e banco de teste. |
| Painel administrativo de qualidade/cobertura | PARCIAL | `/admin/quality.html` apresenta cobertura/linhas, contagem real do JUnit e link para HTML. Não mantém histórico entre execuções. |

O funcionamento de uma tela, rota ou função não foi tratado como evidência suficiente de conclusão.
