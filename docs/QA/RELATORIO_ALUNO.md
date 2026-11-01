# Relatório de testes — Aluno

**Status:** E2E parcial; notas, frequência e dados acadêmicos reais não foram
consultados.

## Superfície encontrada

`frontend/aluno/dashboard.html` apresenta perfil, avaliações, notas,
frequência e materiais. As telas de notas/frequência continham valores
hardcoded; a consulta/baixa de materiais tem chamadas à API. O backend expõe
rotas acadêmicas, de provas, materiais e submissões.

## Riscos a validar

- Questões com gabarito eram retornadas por rotas que exigiam apenas
  autenticação.
- Consulta de submissões por ID/listagem não aplicava consistentemente o
  isolamento do aluno.
- Estatísticas e notas estáticas não são fonte real e não devem ser exibidas
  como resultado acadêmico.

Login e dashboard do aluno passaram em navegador integrado com conta isolada.
Os indicadores sem dados/API disponíveis aparecem como indisponíveis e a
listagem de materiais vem vazia, sem números ou notas fictícias.
Screenshot: `docs/QA/evidencias/aluno-dashboard.png`. Não foram acessadas
notas ou informações de alunos reais.

## Próximos testes

Com perfil e dados `DADO_DE_TESTE_EDUGRADE`, testar disciplinas, matrícula,
resultados publicados próprios e downloads. Os testes unitários de autorização
para gabarito e submissão alheia passaram; ainda falta E2E com prova criada.
