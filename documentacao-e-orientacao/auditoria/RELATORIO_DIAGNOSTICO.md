# Relatório de diagnóstico — EduGrade

**Data da execução:** 05/11/2026  
**Base examinada:** checkout local do repositório, com alterações já existentes no diretório de trabalho.

## Escopo e método

Foram inspecionados os manifests e a estrutura do backend FastAPI/SQLAlchemy, páginas HTML/JavaScript, rotas acadêmicas, serviços/repositórios de provas, configuração de pytest/coverage e workflow do GitHub Actions. A validação local usou a suíte existente, Ruff, import do backend e verificação sintática do JavaScript.

O diretório já continha alterações staged e unstaged em vários arquivos antes desta execução. Elas foram preservadas; portanto, este diagnóstico não atribui todas as diferenças locais a esta auditoria. Nenhuma migração foi executada e nenhum banco de dados persistente foi aberto ou alterado.

## Estado inicial verificado

- `python -m pytest -q`: 53 testes aprovados, 4 avisos; cobertura de **58,19%**, abaixo do limite de 80%.
- O comando de testes configurado no CI, executado como estava no workflow (`cd backend; pytest --cov=app ...`), coletou **zero testes** e calculou 0% de cobertura.
- `ruff check backend/app tests`: 1.289 violações antes das alterações desta auditoria.
- Import da aplicação FastAPI e sintaxe dos scripts JavaScript passaram.
- A interface não continha ferramenta administrativa para associar professores e disciplinas; a API existia.

## Atualização após a rodada de correções

Foram confirmados e corrigidos defeitos adicionais: referências indefinidas em IA/PDF, métodos inexistentes de busca de perfil no `PermissionService`, publicação de submissão sem criar nota oficial e identificação automática baseada em matrícula que não existe no modelo de aluno. Foi criada também a página de qualidade administrativa, servida apenas a administradores e alimentada pelos XMLs reais do pytest-cov/pytest.

## Defeitos confirmados

1. A dependência HTTP `get_db()` encerrava sessões sem `commit` nem `rollback`; serviços acadêmicos fazem `flush`, portanto mudanças de requisição podiam ser descartadas ao fechar a sessão.
2. A detecção de associação professor-disciplina ignorava o período acadêmico, apesar de a chave da associação incluir esse período.
3. Professores autenticados podiam consultar a listagem e o detalhe de disciplinas sem verificar a associação.
4. A listagem geral de turmas não aplicava todos os filtros nem limitava os resultados ao perfil autenticado; o detalhe da turma também não validava vínculo/enrollment.
5. Faltava uma tela administrativa para criar, atualizar coordenação e remover associações professor-disciplina.
6. O job de testes do CI executava do diretório errado e não encontrava os testes localizados em `tests/`.

## Limitações de evidência

As provas locais são unitárias e de integração em SQLite em memória para o ciclo transacional. Não foi feita validação contra um banco de dados persistente, provedor real de IA/OCR, navegador com contas reais ou execução remota do GitHub Actions. Esses fluxos não são marcados como aprovados.
