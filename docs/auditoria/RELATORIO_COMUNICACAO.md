# Relatório de comunicação entre camadas — EduGrade

**Data:** 05/11/2026

## Validado

- Import da aplicação: `python -c "import backend.app.main"` — aprovado.
- Rotas `/quality/summary` e `/quality/report/...` registradas e cobertas por testes com XML temporário; tentativa de path traversal é rejeitada.
- Sintaxe dos arquivos JavaScript: `node --check` em todos os arquivos sob `frontend/js` — aprovado.
- Integração da dependência SQLAlchemy `get_db()` com transação SQLite em memória: commit em sucesso e rollback em erro — coberta por testes.
- A tela administrativa de disciplinas já consumia API e passou a incluir operações de vínculo professor-disciplina.
- O workflow foi ajustado para executar pytest a partir da raiz do repositório, onde `tests/` é coletado, e armazenar HTML/XML de cobertura.

## Corrigido nesta execução

- `get_db()` agora confirma a transação quando a requisição termina com sucesso, reverte em exceção e sempre fecha a sessão.
- A consulta de associação professor-disciplina compara também `academic_period_id`, incluindo o caso sem período.
- As rotas de disciplinas e turmas filtram o acesso de professores por vínculo e o de alunos por matrícula ativa; o detalhe da turma também valida autorização.
- Corrigidos perfil de professor/aluno no `PermissionService`, modelo padrão da rota de correção IA e gabarito na geração de PDF.
- Criado endpoint administrativo para resumo real do coverage XML e entrega controlada dos arquivos HTML.
- Publicação de notas agora exige identificador de aluno confirmado, matrícula ativa e uma avaliação única que combine título, disciplina e período; gera/atualiza a nota oficial após todas as revisões humanas.
- Identificação OCR com RA mais matrícula não validável é encaminhada como conflito, sem atribuir automaticamente um aluno.

## Não validado / pendente

- Banco de dados persistente configurado no ambiente, migrações e comunicação real API↔banco.
- Upload de arquivos e armazenamento externo.
- Provedor de IA/OCR e correção de documentos reais.
- Fluxo de interface em navegador, incluindo autenticação e atualização após operações.
- Integração real de publicação com banco persistente.
- Histórico de execução de CI remoto. O workflow foi corrigido no checkout, mas não foi disparado no GitHub.

Esses itens permanecem parciais ou bloqueados; não há evidência para declará-los aprovados.
