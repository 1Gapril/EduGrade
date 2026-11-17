# Relatório de correções — EduGrade

**Data:** 05/11/2026

## Alterações realizadas

1. Corrigida a transação da dependência `get_db`: commit após sucesso, rollback em exceção e fechamento garantido. Testes usam SQLite em memória e confirmam persistência/rollback reais.
2. Tornada a busca por associação professor-disciplina específica ao período letivo, incluindo a associação sem período.
3. Limitadas as listagens/detalhes de disciplinas e turmas aos vínculos do perfil autenticado; alunos veem somente turmas com matrícula ativa.
4. Adicionada interface administrativa de associação em `/admin/academic.html`, com criação, alternância de coordenador e remoção.
5. Corrigido o job de testes do GitHub Actions para executar a suíte da raiz e publicar relatórios HTML/XML como artefato.
6. Adicionados testes para transação, período, autorização de disciplina e escopo de turmas.
7. Corrigidas referências indefinidas descobertas pelo Ruff na rota de correção IA e no gerador PDF; o gabarito passou a ser fornecido explicitamente ao renderizador.
8. Corrigida a busca de perfis do `PermissionService`, que chamava métodos inexistentes no `UserRepository`.
9. Criado painel administrativo de qualidade e endpoint restrito a admin que lê XML real e serve HTML de cobertura com proteção contra traversal.
10. Adicionados testes para autenticação/permissões, gerador PDF e endpoint de qualidade.
11. Implementada publicação real da nota revisada no registro acadêmico, com validação da matrícula ativa e avaliação correspondente; não marca a submissão como publicada quando a associação estiver ausente/ambígua.
12. Corrigida identificação OCR que tentava consultar campo `matricula` inexistente; quando RA e matrícula não podem ser verificados em conjunto, o caso exige revisão manual.

## Resultado da validação após correções

- Suíte completa: 83 aprovados; nenhuma falha de teste.
- Gate de cobertura: ainda falha em **60,34%**, ante 80% exigidos.
- Ruff: 1.165 violações no checkout atual; o lint integral do CI continua sem aprovação.
- Import da aplicação: aprovado.
- Sintaxe JavaScript: aprovada.
- Relatórios HTML e XML de cobertura gerados em `reports/coverage/` e `reports/coverage.xml`.

As demais alterações staged/unstaged preexistentes foram mantidas; ajustes automáticos de imports/linhas finais foram limitados aos arquivos tocados nesta rodada.
