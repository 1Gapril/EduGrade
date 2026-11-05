# Relatório de gestão institucional

## Resultado

O fluxo acadêmico está integrado ao cadastro central de usuários, às atribuições contextuais e ao módulo de avaliações e correções. A validação final executou **212 testes, todos aprovados** (`pytest --no-cov -q`).

## Evidências funcionais

| Área | Implementação e evidência |
|---|---|
| Usuários e perfis | Alunos e professores são perfis ligados a `User`, sem uma segunda conta por perfil. Provisionamento e edição de dados acadêmicos usam as rotas de usuários; ver [`users.py`](../../backend/app/api/routes/users.py) e [`user.py`](../../backend/app/models/user.py). |
| Matrícula institucional | `Student.registration_number` é distinto do RA, tem índice único e é solicitado nos novos cadastros administrativos. A migração é reversível; ver [`3d8b7a24c1f0_add_student_registration_number.py`](../../backend/migrations/versions/3d8b7a24c1f0_add_student_registration_number.py). |
| Matérias, turmas e períodos | As rotas acadêmicas oferecem criação, consulta e edição, com verificação de duplicidade e coerência de curso/turma/período. O acesso às matérias é limitado pelos vínculos acadêmicos ativos. |
| Matrículas de alunos | Matrículas vinculam aluno, turma e período; alterações passam pelo serviço acadêmico e geram auditoria. Consultas de matérias e notas do aluno respeitam seus próprios vínculos. |
| Atribuições e permissões | `AcademicAssignment` associa professor, matéria, turma e período, mantendo status e permissões no contexto. As rotas verificam as permissões no backend, incluindo operações de avaliação, gabarito, OCR, revisão, edição e publicação de notas. |
| Avaliações e correção | As rotas de prova verificam acesso no contexto da turma. OCR, identificação e solicitação de correção exigem a permissão correspondente. A identificação agora exige matrícula ativa do aluno na turma e no período da prova; cópias personalizadas não podem ser identificadas como outro aluno por leitura automática. Identificações são auditadas. |
| Privacidade e publicação | A consulta de notas do aluno é limitada às notas próprias publicadas. A publicação de notas e correções é protegida por autorização no backend; o aluno não recebe gabaritos privados. |
| Interface administrativa | As telas administrativas integram cadastro/edição de perfis e a gestão de matérias, turmas, atribuições e notas, reutilizando os perfis vinculados à conta central. Ver [`workspace.js`](../../frontend/js/workspace.js), [`assignments.html`](../../frontend/admin/assignments.html) e [`grades.html`](../../frontend/admin/grades.html). |

## Testes e verificações

- **212 testes aprovados**, incluindo serviços acadêmicos e de usuários, rotas de atribuições, publicação de notas, privacidade de provas e correções.
- Testes focados de submissão e autorização passaram após a validação de matrícula e de cópias personalizadas.
- A migração de matrícula foi exercitada em SQLite temporário: upgrade, downgrade e novo upgrade.
- JavaScript passou em `node --check`; 11 rotas selecionadas foram registradas no OpenAPI; `git diff --check` passou.
- Ruff não está instalado neste ambiente; a execução de lint com Ruff não foi feita.

## Compatibilidade e limites conhecidos

- `registration_number` permanece nullable no banco para preservar alunos legados; os novos cadastros administrativos exigem o número. Dados antigos sem matrícula precisam de saneamento institucional se a política exigir preenchimento retroativo.
- `Student.course_id` e `Student.class_id` são campos legados sem chaves estrangeiras. `Enrollment` é o vínculo normalizado e validado para turma e período; a migração dessas colunas legadas requer saneamento prévio dos dados existentes.
- Para compatibilidade com dados históricos, alguns acessos ainda podem usar `TeacherSubject` ou `Class.teacher_id` quando não há histórico de atribuição contextual. Atribuições contextuais existentes prevalecem sobre esse fallback.
- A suíte apresentou cinco avisos de dependências/esquemas (Starlette/httpx, campo `copy`, PyMuPDF/fitz, status HTTP deprecado e argon2); não impediram os testes.

## Referências técnicas

- Modelo acadêmico: [`academic.py`](../../backend/app/models/academic.py).
- Rotas acadêmicas: [`academic.py`](../../backend/app/api/routes/academic.py).
- Regras de submissão e identificação: [`exam_service.py`](../../backend/app/services/exam_service.py) e [`exams.py`](../../backend/app/api/routes/exams.py).
- Testes de autorização de arquivos e provas: [`test_authorization_private_files.py`](../../tests/unit/test_authorization_private_files.py) e [`test_exam_access_control.py`](../../tests/unit/test_exam_access_control.py).
