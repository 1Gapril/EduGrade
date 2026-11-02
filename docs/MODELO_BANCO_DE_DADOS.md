
# EduGrade — Modelo de Banco de Dados

## 1. Introdução

Este documento apresenta a proposta de modelagem do banco de dados do sistema EduGrade.

O objetivo é organizar as informações acadêmicas, definir as tabelas necessárias e estabelecer os relacionamentos entre elas.

A modelagem contempla alunos, professores, cursos, disciplinas, turmas, avaliações, notas e os demais recursos previstos no projeto.

## 2. Tecnologia utilizada

- Banco de dados previsto: SQLite
- Linguagem de consulta: SQL
- Integração com o backend: SQLAlchemy
- Controle de alterações na estrutura: Alembic

## 3. Regras de modelagem

- Cada tabela deverá possuir uma chave primária (PK).
- As chaves estrangeiras (FK) serão utilizadas para relacionar tabelas.
- Os relacionamentos deverão respeitar a integridade referencial.
- Campos que exigem valores únicos deverão possuir restrições de unicidade.
- A estrutura definitiva deverá ser validada com o responsável pelo backend antes da implementação.


## 4. Modelagem das tabelas


### 4.1. Tabela users (Usuários)

**Finalidade:** armazenar os usuários cadastrados no EduGrade, incluindo informações de autenticação, identificação e controle de acesso.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do usuário |
| email | VARCHAR(255) | NOT NULL, UNIQUE | E-mail do usuário |
| username | VARCHAR(100) | NOT NULL, UNIQUE | Nome de usuário |
| hashed_password | VARCHAR(255) | NOT NULL | Hash da senha do usuário |
| full_name | VARCHAR(255) | NOT NULL | Nome completo |
| role | ENUM | NOT NULL, padrão STUDENT | Papel do usuário no sistema |
| is_active | BOOLEAN | NOT NULL, padrão TRUE | Indica se o usuário está ativo |
| is_superuser | BOOLEAN | NOT NULL, padrão FALSE | Indica privilégios de superusuário |
| last_login | DATETIME com fuso horário | Opcional | Data e hora do último acesso |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Um usuário poderá possuir um perfil de aluno (1:1).
- Um usuário poderá possuir um perfil de professor (1:1).
- Um usuário poderá possuir um perfil de administrador (1:1).
- Os relacionamentos utilizam `uselist=False`, indicando um único perfil de cada tipo por usuário.
- Os relacionamentos possuem `cascade="all, delete-orphan"` no ORM.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O e-mail deverá ser único e obrigatório.
- O nome de usuário deverá ser único e obrigatório.
- A senha deverá ser armazenada no campo `hashed_password`.
- O nome completo é obrigatório.
- O papel padrão do usuário é `STUDENT`.
- O usuário é criado como ativo por padrão.
- O campo `is_superuser` possui valor padrão `FALSE`.
- O último acesso poderá permanecer vazio.
- Existem índices compostos para `email` + `is_active` e `role` + `is_active`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/user.py.

Os demais valores permitidos para `role` precisam ser conferidos na definição de UserRole.

O modelo apresenta três relacionamentos de perfil, mas não demonstra, isoladamente, uma regra que impeça um usuário de possuir perfis de tipos diferentes simultaneamente.




### 4.2. Tabela students (Alunos)

**Finalidade:** armazenar os dados acadêmicos dos alunos cadastrados no EduGrade, vinculando cada perfil a um usuário do sistema.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do aluno |
| user_id | UUID | FK, NOT NULL, UNIQUE | Referência ao usuário na tabela users |
| ra | VARCHAR(50) | NOT NULL, UNIQUE | Registro acadêmico do aluno |
| course_id | UUID | Opcional, indexado | Identificador de curso, sem FK declarada |
| class_id | UUID | Opcional, indexado | Identificador de turma, sem FK declarada |
| enrollment_date | DATETIME com fuso horário | NOT NULL | Data de matrícula cadastrada no perfil |
| status | VARCHAR(50) | NOT NULL, padrão "active" | Situação do aluno |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Cada aluno possui um usuário associado (1:1).
- Um usuário poderá possuir um perfil de aluno.
- Um aluno poderá possuir várias matrículas na tabela enrollments (1:N).
- Os campos `course_id` e `class_id` não possuem relacionamentos ORM declarados neste modelo.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O usuário associado é obrigatório e único.
- O registro acadêmico (`ra`) é obrigatório e único.
- Os identificadores de curso e turma são opcionais.
- O status possui valor padrão `active`.
- A exclusão do usuário poderá excluir o perfil de aluno automaticamente (`ON DELETE CASCADE`).
- Existe um índice composto para `course_id` e `class_id`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/user.py.

Os campos `course_id` e `class_id` utilizam UUID, mas não possuem ForeignKey declarada. Portanto, não devemos documentá-los como chaves estrangeiras implementadas.

O modelo também não apresenta uma lista fechada de valores permitidos para o campo `status`.



### 4.3. Tabela teachers (Professores)

**Finalidade:** armazenar os dados profissionais dos professores cadastrados no EduGrade, vinculando cada professor a um usuário do sistema.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do professor |
| user_id | UUID | FK, NOT NULL, UNIQUE | Referência ao usuário na tabela users |
| employee_id | VARCHAR(50) | NOT NULL, UNIQUE | Identificação funcional do professor |
| department | VARCHAR(100) | Opcional | Departamento do professor |
| hire_date | DATETIME com fuso horário | NOT NULL | Data de contratação cadastrada |
| status | VARCHAR(50) | NOT NULL, padrão "active" | Situação do professor |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Cada professor possui um usuário associado (1:1).
- Um usuário poderá possuir um perfil de professor.
- Um professor poderá possuir várias associações com disciplinas na tabela teacher_subjects (1:N).
- A tabela teacher_subjects permite representar o relacionamento N:N entre professores e disciplinas.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O usuário associado é obrigatório e único.
- O identificador funcional (`employee_id`) é obrigatório e único.
- O departamento é opcional.
- A data de contratação é obrigatória e possui como valor padrão a data e hora atuais.
- O status possui valor padrão `active`.
- A exclusão do usuário poderá excluir o perfil de professor automaticamente (`ON DELETE CASCADE`).
- O relacionamento com teacher_subjects possui `cascade="all, delete-orphan"` no ORM.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/user.py.

O campo `status` utiliza VARCHAR(50), sem uma lista fechada de valores definida neste modelo.

O modelo não declara diretamente um relacionamento ORM entre professores e turmas, embora a tabela classes possua a chave estrangeira teacher_id.



### 4.4. Tabela administrators (Administradores)

**Finalidade:** armazenar os dados dos administradores do EduGrade, vinculando cada administrador a um usuário do sistema e registrando suas permissões.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do administrador |
| user_id | UUID | FK, NOT NULL, UNIQUE | Referência ao usuário na tabela users |
| employee_id | VARCHAR(50) | NOT NULL, UNIQUE | Identificação funcional do administrador |
| department | VARCHAR(100) | Opcional | Departamento do administrador |
| permissions | VARCHAR(500) | NOT NULL, padrão "full" | Permissões atribuídas ao administrador |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Cada administrador possui um usuário associado (1:1).
- Um usuário poderá possuir um perfil de administrador.
- O relacionamento utiliza `back_populates="admin_profile"`.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O usuário associado é obrigatório e único.
- O identificador funcional (`employee_id`) é obrigatório e único.
- O departamento é opcional.
- O campo `permissions` é obrigatório e possui valor padrão `full`.
- A exclusão do usuário poderá excluir o perfil de administrador automaticamente (`ON DELETE CASCADE`).
- As datas de criação e atualização são obrigatórias.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/user.py.

O campo `permissions` utiliza VARCHAR(500). O modelo não apresenta uma lista fechada de permissões nem uma validação explícita de seus valores.

A aplicação efetiva dessas permissões deverá ser verificada posteriormente nos serviços de autenticação e autorização.



### 4.5. Tabela courses (Cursos)

**Finalidade:** armazenar os cursos cadastrados no EduGrade, permitindo a associação com disciplinas e turmas.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do curso |
| code | VARCHAR(20) | NOT NULL, UNIQUE | Código do curso |
| name | VARCHAR(255) | NOT NULL | Nome do curso |
| description | TEXT | Opcional | Descrição do curso |
| duration_semesters | INTEGER | NOT NULL, padrão 8 | Duração do curso em semestres |
| is_active | BOOLEAN | NOT NULL, padrão TRUE | Indica se o curso está ativo |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Um curso poderá possuir várias disciplinas (1:N).
- Um curso poderá possuir várias turmas (1:N).
- Cada disciplina pertence a um curso.
- Cada turma pertence a um curso.

**Regras e restrições:**
- O identificador do curso é uma chave primária UUID.
- O código do curso é obrigatório e único.
- O nome do curso é obrigatório.
- A duração possui valor padrão de 8 semestres.
- O curso é cadastrado como ativo por padrão.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.




### 4.6. Tabela classes (Turmas)

**Finalidade:** armazenar as turmas e ofertas de disciplinas vinculadas aos cursos e períodos acadêmicos do EduGrade.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da turma |
| code | VARCHAR(20) | NOT NULL, UNIQUE | Código da turma |
| name | VARCHAR(255) | NOT NULL | Nome da turma |
| course_id | UUID | FK, NOT NULL | Referência ao curso na tabela courses |
| subject_id | UUID | FK, NOT NULL | Referência à disciplina na tabela subjects |
| academic_period_id | UUID | FK, NOT NULL | Referência ao período na tabela academic_periods |
| teacher_id | UUID | FK, opcional | Referência ao professor na tabela teachers |
| semester | INTEGER | NOT NULL | Semestre da turma |
| year | INTEGER | NOT NULL | Ano da turma |
| schedule | VARCHAR(500) | Opcional | Horários das aulas |
| classroom | VARCHAR(100) | Opcional | Sala de aula |
| max_students | INTEGER | NOT NULL, padrão 50 | Quantidade máxima de alunos |
| is_active | BOOLEAN | NOT NULL, padrão TRUE | Indica se a turma está ativa |
| created_at | DATETIME | NOT NULL | Data de criação |
| updated_at | DATETIME | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Um curso poderá possuir várias turmas.
- Uma disciplina poderá estar vinculada a várias turmas.
- Um período acadêmico poderá possuir várias turmas.
- Um professor poderá estar associado a várias turmas.
- Uma turma poderá possuir várias matrículas, avaliações e provas.

**Regras de validação:**
- O código da turma deverá ser único.
- O curso, a disciplina e o período acadêmico deverão existir.
- O professor, quando informado, deverá existir.
- A quantidade máxima de alunos deverá ser maior que zero.
- A combinação de curso, disciplina, período acadêmico e código deverá respeitar a restrição de unicidade definida no backend.

**Observação técnica:**
Esta estrutura foi documentada com base no modelo SQLAlchemy existente em backend/app/models/academic.py.




### 4.7. Tabela subjects (Disciplinas)

**Finalidade:** armazenar as disciplinas oferecidas pelos cursos do EduGrade.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da disciplina |
| code | VARCHAR(20) | NOT NULL, UNIQUE | Código da disciplina |
| name | VARCHAR(255) | NOT NULL | Nome da disciplina |
| description | TEXT | Opcional | Descrição da disciplina |
| workload_hours | INTEGER | NOT NULL, padrão 60 | Carga horária em horas |
| credits | INTEGER | NOT NULL, padrão 4 | Quantidade de créditos |
| course_id | UUID | FK, NOT NULL | Referência ao curso na tabela courses |
| is_active | BOOLEAN | NOT NULL, padrão TRUE | Indica se a disciplina está ativa |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Um curso poderá possuir várias disciplinas.
- Uma disciplina pertence a um curso.
- Uma disciplina poderá estar vinculada a várias turmas.
- Uma disciplina poderá possuir várias associações com professores.
- Uma disciplina poderá possuir várias avaliações.

**Regras e restrições:**
- O código da disciplina é obrigatório e possui restrição de unicidade.
- O nome da disciplina é obrigatório.
- O curso informado deverá existir.
- A combinação de código e curso também possui uma restrição de unicidade.
- A carga horária e os créditos possuem valores padrão definidos no backend.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.


### 4.8. Tabela enrollments (Matrículas)


### 4.8. Tabela enrollments (Matrículas)

**Finalidade:** registrar as matrículas dos alunos nas turmas e períodos acadêmicos do EduGrade, permitindo acompanhar notas, frequência e situação acadêmica.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da matrícula |
| student_id | UUID | FK, NOT NULL | Referência ao aluno na tabela students |
| class_id | UUID | FK, NOT NULL | Referência à turma na tabela classes |
| academic_period_id | UUID | FK, NOT NULL | Referência ao período na tabela academic_periods |
| status | ENUM | NOT NULL, padrão ACTIVE | Status da matrícula |
| enrolled_at | DATETIME com fuso horário | NOT NULL | Data da matrícula |
| final_grade | NUMERIC(5,2) | Opcional | Nota final do aluno |
| attendance_percentage | NUMERIC(5,2) | Opcional | Percentual de frequência |
| situation | VARCHAR(50) | Opcional | Situação acadêmica |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Um aluno poderá possuir várias matrículas (1:N).
- Uma turma poderá possuir várias matrículas (1:N).
- Um período acadêmico poderá possuir várias matrículas (1:N).
- Uma matrícula poderá possuir várias notas (1:N).
- Uma matrícula poderá possuir vários registros de frequência (1:N).

**Regras e restrições:**
- A chave primária utiliza UUID.
- O aluno, a turma e o período acadêmico são obrigatórios.
- A combinação de `student_id` e `class_id` deverá ser única.
- O status possui o valor padrão `ACTIVE`.
- A nota final e o percentual de frequência poderão permanecer vazios.
- As chaves estrangeiras de aluno, turma e período acadêmico possuem exclusão em cascata (`ON DELETE CASCADE`).
- Existe um índice composto para `student_id` e `academic_period_id`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.

Os demais valores permitidos para `status` ainda precisam ser conferidos na definição de EnrollmentStatus.



### 4.9. Tabela teacher_subjects (Professores e Disciplinas)

**Finalidade:** registrar as associações entre professores e disciplinas, permitindo identificar os professores vinculados a cada disciplina e período acadêmico.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da associação |
| teacher_id | UUID | FK, NOT NULL | Referência ao professor na tabela teachers |
| subject_id | UUID | FK, NOT NULL | Referência à disciplina na tabela subjects |
| academic_period_id | UUID | FK, opcional | Referência ao período na tabela academic_periods |
| is_coordinator | BOOLEAN | NOT NULL, padrão FALSE | Indica se o professor é coordenador |
| assigned_at | DATETIME com fuso horário | NOT NULL | Data da associação |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |

**Relacionamentos implementados:**
- Um professor poderá estar associado a várias disciplinas.
- Uma disciplina poderá estar associada a vários professores.
- O relacionamento entre professores e disciplinas é N:N, intermediado por esta tabela.
- Uma associação poderá estar vinculada a um período acadêmico.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O professor e a disciplina são obrigatórios.
- O período acadêmico é opcional.
- A combinação de `teacher_id`, `subject_id` e `academic_period_id` possui uma restrição de unicidade.
- O campo `is_coordinator` possui valor padrão `FALSE`.
- A exclusão de um professor ou disciplina poderá excluir suas associações automaticamente (`ON DELETE CASCADE`).
- A exclusão de um período acadêmico poderá definir `academic_period_id` como `NULL` (`ON DELETE SET NULL`).

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.

A restrição de unicidade composta poderá permitir múltiplos registros com a mesma combinação de professor e disciplina quando academic_period_id for NULL, dependendo do comportamento do banco de dados.



### 4.10. Tabela academic_periods (Períodos Acadêmicos)

**Finalidade:** armazenar os períodos acadêmicos do EduGrade, permitindo organizar turmas e matrículas conforme o calendário letivo.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do período |
| name | VARCHAR(100) | NOT NULL | Nome do período acadêmico |
| code | VARCHAR(20) | NOT NULL, UNIQUE | Código do período |
| start_date | DATE | NOT NULL | Data de início do período |
| end_date | DATE | NOT NULL | Data de término do período |
| enrollment_start | DATE | Opcional | Início das matrículas |
| enrollment_end | DATE | Opcional | Encerramento das matrículas |
| status | ENUM | NOT NULL, padrão PLANNED | Situação do período acadêmico |
| is_current | BOOLEAN | NOT NULL, padrão FALSE | Indica se é o período atual |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Um período acadêmico poderá possuir várias turmas (1:N).
- Um período acadêmico poderá possuir várias matrículas (1:N).
- Cada turma pertence a um período acadêmico.
- Cada matrícula pertence a um período acadêmico.

**Regras e restrições:**
- O identificador do período é uma chave primária UUID.
- O código do período é obrigatório e único.
- As datas de início e término são obrigatórias.
- A data de término deverá ser igual ou posterior à data de início.
- O status possui o valor padrão `PLANNED`.
- O campo `is_current` possui o valor padrão `FALSE`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.

Os demais valores permitidos para o campo `status` ainda precisam ser conferidos na definição de AcademicPeriodStatus.




### 4.11. Tabela assessments (Avaliações)

**Finalidade:** armazenar avaliações acadêmicas, como provas e trabalhos, vinculadas às turmas, disciplinas e períodos acadêmicos do EduGrade.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da avaliação |
| title | VARCHAR(255) | NOT NULL | Título da avaliação |
| description | TEXT | Opcional | Descrição da avaliação |
| type | ENUM | NOT NULL | Tipo da avaliação |
| weight | NUMERIC(5,2) | NOT NULL, padrão 1.00 | Peso da avaliação |
| max_score | NUMERIC(5,2) | NOT NULL, padrão 10.00 | Pontuação máxima |
| class_id | UUID | FK, NOT NULL | Referência à turma na tabela classes |
| subject_id | UUID | FK, NOT NULL | Referência à disciplina na tabela subjects |
| academic_period_id | UUID | FK, NOT NULL | Referência ao período na tabela academic_periods |
| scheduled_date | DATE | NOT NULL | Data prevista da avaliação |
| is_published | BOOLEAN | NOT NULL, padrão FALSE | Indica se a avaliação está publicada |
| created_by | UUID | FK, NOT NULL | Referência ao usuário criador na tabela users |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Uma turma poderá possuir várias avaliações (1:N).
- Uma disciplina poderá possuir várias avaliações (1:N).
- Um período acadêmico poderá estar associado a várias avaliações.
- Uma avaliação poderá possuir várias notas (1:N).
- Cada avaliação possui um usuário criador, identificado por `created_by`.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O título, o tipo e a data prevista são obrigatórios.
- A turma, a disciplina, o período acadêmico e o usuário criador são obrigatórios.
- O peso da avaliação deverá ser maior que zero.
- A pontuação máxima deverá ser maior que zero.
- O peso padrão é 1.00.
- A pontuação máxima padrão é 10.00.
- A avaliação é criada como não publicada por padrão.
- A exclusão da turma poderá excluir suas avaliações automaticamente (`ON DELETE CASCADE`).
- As referências à disciplina, ao período acadêmico e ao usuário criador possuem `ON DELETE RESTRICT`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.

Os valores permitidos para o campo `type` ainda precisam ser conferidos na definição de AssessmentType.

O modelo apresentado não possui uma restrição explícita garantindo que a disciplina e o período informados sejam os mesmos da turma.




### 4.12. Tabela grades (Notas)

**Finalidade:** armazenar as notas obtidas pelos alunos nas avaliações acadêmicas, vinculando cada resultado à matrícula e à avaliação correspondente.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da nota |
| enrollment_id | UUID | FK, NOT NULL | Referência à matrícula na tabela enrollments |
| assessment_id | UUID | FK, NOT NULL | Referência à avaliação na tabela assessments |
| score | NUMERIC(5,2) | NOT NULL | Nota obtida na avaliação |
| is_official | BOOLEAN | NOT NULL, padrão FALSE | Indica se a nota é oficial |
| graded_by | UUID | FK, opcional | Referência ao usuário responsável pela correção |
| graded_at | DATETIME com fuso horário | Opcional | Data e hora da correção |
| published_at | DATETIME com fuso horário | Opcional | Data e hora da publicação |
| notes | TEXT | Opcional | Observações sobre a nota |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Uma matrícula poderá possuir várias notas (1:N).
- Uma avaliação poderá possuir várias notas (1:N).
- Cada nota pertence a uma matrícula e a uma avaliação.
- O campo `graded_by` referencia um usuário responsável pela correção, quando informado.

**Regras e restrições:**
- A chave primária utiliza UUID.
- A matrícula e a avaliação são obrigatórias.
- A combinação de `enrollment_id` e `assessment_id` deverá ser única.
- A nota deverá ser maior ou igual a zero.
- O campo `is_official` possui valor padrão `FALSE`.
- A exclusão da matrícula ou avaliação poderá excluir suas notas automaticamente (`ON DELETE CASCADE`).
- Se o usuário responsável pela correção for excluído, `graded_by` poderá ser definido como `NULL` (`ON DELETE SET NULL`).

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.

O modelo possui uma restrição para impedir notas negativas, mas não apresenta uma restrição explícita garantindo que `score` seja menor ou igual à pontuação máxima da avaliação.

Também não há, nesta tabela, uma restrição explícita garantindo que a matrícula pertença à mesma turma da avaliação. Essas validações precisam ser conferidas nas demais camadas do sistema.



### 4.13. Tabela attendance (Frequência)

**Finalidade:** registrar a presença ou ausência dos alunos nas aulas, permitindo acompanhar a frequência acadêmica e eventuais justificativas.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do registro |
| enrollment_id | UUID | FK, NOT NULL | Referência à matrícula na tabela enrollments |
| class_date | DATE | NOT NULL | Data da aula |
| is_present | BOOLEAN | NOT NULL, padrão FALSE | Indica se o aluno esteve presente |
| justified | BOOLEAN | NOT NULL, padrão FALSE | Indica se a ausência foi justificada |
| justification | TEXT | Opcional | Descrição da justificativa |
| recorded_by | UUID | FK, NOT NULL | Referência ao usuário que registrou a frequência |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Uma matrícula poderá possuir vários registros de frequência (1:N).
- Cada registro de frequência pertence a uma matrícula.
- Cada registro possui um usuário responsável, identificado por `recorded_by`.

**Regras e restrições:**
- A chave primária utiliza UUID.
- A matrícula, a data da aula e o usuário responsável são obrigatórios.
- A combinação de `enrollment_id` e `class_date` deverá ser única.
- Os campos `is_present` e `justified` possuem valor padrão `FALSE`.
- A justificativa é opcional.
- A exclusão da matrícula poderá excluir seus registros de frequência automaticamente (`ON DELETE CASCADE`).
- A exclusão do usuário responsável é restringida enquanto existir um registro que o referencie (`ON DELETE RESTRICT`).

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.

O modelo não apresenta uma restrição explícita exigindo uma justificativa quando `justified` for TRUE. Essa validação poderá existir em outra camada do sistema e deverá ser conferida posteriormente.



### 4.14. Tabela academic_rules (Regras Acadêmicas)

**Finalidade:** armazenar regras acadêmicas configuráveis do EduGrade, como critérios de aprovação, recuperação e exames finais.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da regra |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Nome da regra acadêmica |
| description | TEXT | Opcional | Descrição da regra |
| rule_type | VARCHAR(50) | NOT NULL | Categoria da regra acadêmica |
| config | TEXT | NOT NULL | Configurações da regra em formato JSON textual |
| is_active | BOOLEAN | NOT NULL, padrão TRUE | Indica se a regra está ativa |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- O modelo não declara relacionamentos com outras tabelas.
- Cada regra possui um identificador próprio.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O nome da regra é obrigatório e único.
- O tipo da regra é obrigatório.
- O campo `config` é obrigatório.
- O campo `is_active` possui valor padrão `TRUE`.
- A descrição é opcional.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/academic.py.

O campo `config` utiliza TEXT para armazenar configurações em formato JSON. O modelo não apresenta uma restrição explícita que valide se o conteúdo armazenado é um JSON válido.

O campo `rule_type` é uma string, não um ENUM. Os exemplos identificados no código são approval, recovery e final_exam, mas não há uma lista fechada de valores definida neste modelo.



### 4.15. Tabela exams (Provas)

**Finalidade:** armazenar as provas acadêmicas do EduGrade, incluindo informações de criação, configuração, publicação e vínculos com turmas e disciplinas.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da prova |
| title | VARCHAR(255) | NOT NULL | Título da prova |
| description | TEXT | Opcional | Descrição da prova |
| instructions | TEXT | Opcional | Instruções para realização |
| class_id | UUID | FK, NOT NULL | Referência à turma na tabela classes |
| subject_id | UUID | FK, NOT NULL | Referência à disciplina na tabela subjects |
| academic_period_id | UUID | FK, NOT NULL | Referência ao período na tabela academic_periods |
| created_by | UUID | FK, NOT NULL | Referência ao usuário criador na tabela users |
| total_score | NUMERIC(5,2) | NOT NULL, padrão 10.00 | Pontuação total da prova |
| scheduled_date | DATE | Opcional | Data prevista da prova |
| duration_minutes | INTEGER | NOT NULL, padrão 120 | Duração em minutos |
| status | ENUM | NOT NULL, padrão DRAFT | Situação da prova |
| version | INTEGER | NOT NULL, padrão 1 | Número da versão |
| is_template | BOOLEAN | NOT NULL, padrão FALSE | Indica se a prova é um modelo |
| print_config | JSON | NOT NULL, padrão objeto vazio | Configurações de impressão |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |
| published_at | DATETIME com fuso horário | Opcional | Data de publicação |

**Relacionamentos implementados:**
- Uma turma poderá possuir várias provas (1:N).
- Uma disciplina poderá estar associada a várias provas (1:N).
- Um período acadêmico poderá estar associado a várias provas (1:N).
- Cada prova possui um usuário criador.
- Uma prova poderá possuir várias questões na tabela exam_questions (1:N).
- Uma prova poderá possuir várias versões na tabela exam_versions (1:N).
- Uma prova poderá possuir vários registros de impressão na tabela exam_print_logs (1:N).

**Regras e restrições:**
- A chave primária utiliza UUID.
- O título, a turma, a disciplina, o período acadêmico e o usuário criador são obrigatórios.
- A pontuação total deverá ser maior que zero.
- A duração deverá ser maior que zero.
- O status inicial é `DRAFT`.
- A versão inicial é 1.
- O campo `is_template` possui valor padrão `FALSE`.
- O campo `print_config` armazena dados JSON.
- A exclusão da turma poderá excluir suas provas (`ON DELETE CASCADE`).
- As referências à disciplina, ao período acadêmico e ao usuário criador possuem `ON DELETE RESTRICT`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

Os demais valores permitidos para o campo `status` precisam ser conferidos na definição de ExamStatus.

O modelo não apresenta uma restrição explícita garantindo que a disciplina e o período acadêmico informados correspondam aos da turma.


### 4.16. Tabela exam_versions (Versões de Provas)

**Finalidade:** armazenar versões publicadas das provas, preservando cópias das questões, gabaritos e critérios de correção utilizados em cada publicação.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da versão |
| exam_id | UUID | FK, NOT NULL | Referência à prova na tabela exams |
| version_number | INTEGER | NOT NULL | Número da versão da prova |
| title | VARCHAR(255) | NOT NULL | Título registrado na versão |
| description | TEXT | Opcional | Descrição da prova |
| instructions | TEXT | Opcional | Instruções da prova |
| total_score | NUMERIC(5,2) | NOT NULL | Pontuação total registrada na versão |
| questions_snapshot | JSON | NOT NULL | Cópia das questões da prova |
| answer_key_snapshot | JSON | NOT NULL | Cópia do gabarito |
| rubrics_snapshot | JSON | NOT NULL | Cópia dos critérios de correção |
| published_by | UUID | FK, NOT NULL | Referência ao usuário que publicou a versão |
| published_at | DATETIME com fuso horário | NOT NULL | Data e hora da publicação |
| is_active | BOOLEAN | NOT NULL, padrão TRUE | Indica se a versão está ativa |

**Relacionamentos implementados:**
- Uma prova poderá possuir várias versões (1:N).
- Cada versão pertence a uma única prova.
- Cada versão possui um usuário responsável pela publicação.
- Uma versão poderá possuir várias cópias na tabela exam_copies (1:N).

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a prova é obrigatório.
- O número da versão é obrigatório.
- A combinação de `exam_id` e `version_number` deve ser única.
- O título e a pontuação total são obrigatórios.
- Os campos de snapshot são obrigatórios e utilizam JSON.
- O usuário responsável pela publicação é obrigatório.
- A data de publicação é obrigatória e recebe automaticamente a data e hora atuais na criação pelo modelo.
- O campo `is_active` possui valor padrão `TRUE`.
- A exclusão da prova poderá excluir suas versões (`ON DELETE CASCADE`).
- A exclusão do usuário responsável pela publicação é restringida (`ON DELETE RESTRICT`).

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

O modelo descreve a versão como imutável, porém não apresenta uma restrição explícita de imutabilidade. Essa regra depende de verificação nos serviços da aplicação.

Também não foram identificadas restrições explícitas que exijam `version_number > 0` ou `total_score > 0` nesta tabela.

Os campos de snapshot preservam os dados da versão em formato JSON, em vez de depender exclusivamente dos registros atuais das questões e gabaritos.



### 4.17. Tabela exam_questions (Questões das Provas)

**Finalidade:** armazenar as questões associadas às provas do EduGrade, incluindo enunciados, tipos, pontuações e configurações específicas.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da questão |
| exam_id | UUID | FK, NOT NULL | Referência à prova na tabela exams |
| question_order | INTEGER | NOT NULL | Posição da questão na prova |
| type | ENUM | NOT NULL | Tipo da questão |
| statement | TEXT | NOT NULL | Enunciado da questão |
| score | NUMERIC(5,2) | NOT NULL | Pontuação atribuída à questão |
| config | JSON | NOT NULL, padrão objeto vazio | Configurações específicas da questão |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Uma prova poderá possuir várias questões (1:N).
- Cada questão pertence a uma única prova.
- Uma questão poderá possuir um gabarito associado na tabela answer_keys (1:1).
- Uma questão poderá possuir um critério de correção associado na tabela grading_rubrics (1:1).

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a prova é obrigatório.
- A ordem da questão deve ser maior que zero.
- A pontuação da questão deve ser maior que zero.
- A combinação de `exam_id` e `question_order` deve ser única.
- O tipo e o enunciado são obrigatórios.
- O campo `config` utiliza JSON e possui objeto vazio como valor padrão.
- A exclusão da prova poderá excluir suas questões (`ON DELETE CASCADE`).
- Os relacionamentos com gabarito e critério de correção utilizam `cascade="all, delete-orphan"` no SQLAlchemy.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

Os valores permitidos para o campo `type` precisam ser conferidos na definição de QuestionType.

O modelo não apresenta uma restrição explícita garantindo que a soma das pontuações das questões corresponda à pontuação total da prova.

Os relacionamentos com answer_keys e grading_rubrics são configurados como individuais (`uselist=False`). As restrições de unicidade dessas tabelas serão verificadas em suas respectivas seções.



### 4.18. Tabela answer_keys (Gabaritos)

**Finalidade:** armazenar os gabaritos das questões das provas, incluindo respostas corretas, respostas esperadas, alternativas aceitas e informações auxiliares para correção.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do gabarito |
| question_id | UUID | FK, NOT NULL, UNIQUE | Referência à questão na tabela exam_questions |
| correct_answer | TEXT | Opcional | Resposta correta da questão |
| expected_answer | TEXT | Opcional | Resposta esperada para a questão |
| accepted_alternatives | JSON | NOT NULL, padrão lista vazia | Alternativas de resposta aceitas |
| keywords | JSON | NOT NULL, padrão lista vazia | Palavras-chave relacionadas à resposta |
| required_concepts | JSON | NOT NULL, padrão lista vazia | Conceitos esperados na resposta |
| justification | TEXT | Opcional | Justificativa da resposta |
| partial_scoring | JSON | NOT NULL, padrão objeto vazio | Informações para atribuição de pontuação parcial |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Cada gabarito pertence a uma única questão.
- Uma questão poderá possuir no máximo um gabarito (1:1).
- O relacionamento utiliza `back_populates="answer_key"` no SQLAlchemy.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a questão é obrigatório.
- O campo `question_id` possui restrição UNIQUE, impedindo dois gabaritos para a mesma questão.
- Os campos `correct_answer`, `expected_answer` e `justification` são opcionais.
- Os campos `accepted_alternatives`, `keywords` e `required_concepts` utilizam JSON, com lista vazia como valor padrão.
- O campo `partial_scoring` utiliza JSON, com objeto vazio como valor padrão.
- As datas de criação e atualização são obrigatórias.
- A exclusão da questão poderá excluir seu gabarito (`ON DELETE CASCADE`).

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

O modelo não exige que `correct_answer` ou `expected_answer` sejam preenchidos.

Também não apresenta validações explícitas para a estrutura interna dos campos JSON. A interpretação desses dados e as regras de correção precisam ser verificadas nos serviços da aplicação.



### 4.19. Tabela grading_rubrics (Critérios de Correção)

**Finalidade:** armazenar os critérios de avaliação utilizados na correção das questões das provas, especialmente questões discursivas e de cálculo.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da rubrica |
| question_id | UUID | FK, NOT NULL, UNIQUE | Referência à questão na tabela exam_questions |
| criteria | JSON | NOT NULL, padrão lista vazia | Lista de critérios utilizados na correção |
| max_score | NUMERIC(5,2) | NOT NULL, CHECK > 0 | Pontuação máxima da rubrica |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Cada rubrica pertence a uma única questão.
- Uma questão poderá possuir no máximo uma rubrica de correção (1:1).
- O relacionamento utiliza `back_populates="grading_rubric"` no SQLAlchemy.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a questão é obrigatório.
- O campo `question_id` possui restrição UNIQUE, impedindo duas rubricas para a mesma questão.
- O campo `criteria` é obrigatório e possui uma lista vazia como valor padrão.
- A pontuação máxima (`max_score`) deve ser maior que zero.
- As datas de criação e atualização são obrigatórias.
- A exclusão da questão poderá excluir sua rubrica (`ON DELETE CASCADE`).

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

O modelo não apresenta uma validação explícita para a estrutura interna dos critérios armazenados em JSON.

Também não foi identificada uma restrição que obrigue `max_score` a ser igual à pontuação (`score`) definida na tabela exam_questions.

Essas validações, caso existam, deverão ser verificadas nos serviços da aplicação.



### 4.20. Tabela exam_copies (Cópias das Provas)

**Finalidade:** armazenar as cópias individuais das provas, permitindo sua identificação, personalização, associação com estudantes e registro de informações de impressão.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da cópia |
| version_id | UUID | FK, NOT NULL | Referência à versão da prova na tabela exam_versions |
| copy_identifier | VARCHAR(100) | NOT NULL, UNIQUE | Código único de identificação da cópia |
| qr_code_data | TEXT | NOT NULL | Dados utilizados para gerar ou identificar o QR Code |
| student_id | UUID | FK, opcional | Referência ao estudante na tabela students |
| is_personalized | BOOLEAN | NOT NULL, padrão FALSE | Indica se a cópia é personalizada |
| pdf_path | VARCHAR(500) | Opcional | Caminho do arquivo PDF da cópia |
| printed_at | DATETIME com fuso horário | Opcional | Data e hora da impressão |
| printed_by | UUID | FK, opcional | Referência ao usuário responsável pela impressão |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação da cópia |

**Relacionamentos implementados:**
- Cada cópia pertence a uma única versão da prova.
- Uma versão poderá possuir várias cópias (1:N).
- Uma cópia poderá estar associada a um estudante.
- Um estudante poderá estar associado a várias cópias (1:N).
- Uma cópia poderá possuir vários registros na tabela exam_submissions (1:N).
- O campo `printed_by` referencia um usuário do sistema.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a versão da prova é obrigatório.
- O identificador da cópia é obrigatório e único.
- Os dados do QR Code são obrigatórios.
- A associação com um estudante é opcional.
- O campo `is_personalized` possui valor padrão `FALSE`.
- O caminho do PDF e os dados de impressão são opcionais.
- A data de criação é obrigatória.
- A exclusão da versão poderá excluir suas cópias (`ON DELETE CASCADE`).
- A exclusão de um estudante associado define `student_id` como NULL (`ON DELETE SET NULL`).
- A exclusão do usuário responsável pela impressão define `printed_by` como NULL (`ON DELETE SET NULL`).
- Existe um índice composto sobre `version_id` e `student_id`, para auxiliar consultas por versão e estudante.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

O modelo não exige que uma cópia personalizada esteja obrigatoriamente associada a um estudante.

Também não apresenta uma restrição explícita que impeça múltiplos registros de entrega para a mesma cópia.

O campo `qr_code_data` armazena dados textuais relacionados ao QR Code, não necessariamente a imagem do código.

As regras de geração dos PDFs, personalização e impressão deverão ser verificadas nos serviços da aplicação.



### 4.21. Tabela exam_print_logs (Registros de Impressão)

**Finalidade:** armazenar o histórico das operações de impressão das provas, registrando a versão utilizada, o usuário responsável, a quantidade de cópias e o resultado da operação.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do registro de impressão |
| exam_id | UUID | FK, NOT NULL | Referência à prova na tabela exams |
| version_id | UUID | FK, NOT NULL | Referência à versão na tabela exam_versions |
| printed_by | UUID | FK, NOT NULL | Referência ao usuário responsável pela impressão |
| copy_count | INTEGER | NOT NULL | Quantidade de cópias da operação |
| copy_identifiers | JSON | NOT NULL, padrão lista vazia | Lista de identificadores das cópias |
| status | ENUM | NOT NULL, padrão PENDING | Situação da operação de impressão |
| pdf_path | VARCHAR(500) | Opcional | Caminho do arquivo PDF gerado |
| error_message | TEXT | Opcional | Mensagem de erro da operação |
| started_at | DATETIME com fuso horário | NOT NULL | Data e hora de início da operação |
| completed_at | DATETIME com fuso horário | Opcional | Data e hora de conclusão da operação |

**Relacionamentos implementados:**
- Uma prova poderá possuir vários registros de impressão (1:N).
- Cada registro de impressão pertence a uma única prova.
- Uma versão poderá estar associada a vários registros de impressão (1:N).
- Cada registro possui um usuário responsável pela impressão.

**Regras e restrições:**
- A chave primária utiliza UUID.
- Os vínculos com a prova, a versão e o usuário responsável são obrigatórios.
- A quantidade de cópias é obrigatória.
- O campo `copy_identifiers` utiliza JSON e possui lista vazia como valor padrão.
- O status inicial é `PENDING`.
- O caminho do PDF e a mensagem de erro são opcionais.
- A data de início é obrigatória e recebe automaticamente a data e hora atuais na criação pelo modelo.
- A data de conclusão é opcional.
- A exclusão da prova poderá excluir seus registros de impressão (`ON DELETE CASCADE`).
- A exclusão da versão poderá excluir seus registros de impressão (`ON DELETE CASCADE`).
- A exclusão do usuário responsável é restringida (`ON DELETE RESTRICT`).

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

Os demais valores permitidos para o campo `status` precisam ser conferidos na definição de PrintStatus.

O modelo não apresenta uma restrição explícita exigindo que `copy_count` seja maior que zero.

Também não foi identificada uma restrição que garanta que a versão informada pertença à prova indicada em `exam_id`.

As regras de atualização do status e de tratamento dos erros deverão ser verificadas nos serviços da aplicação.



### 4.22. Tabela exam_submissions (Entregas das Provas)

**Finalidade:** armazenar os registros das provas respondidas e enviadas para processamento, identificação dos estudantes e correção.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da entrega |
| copy_id | UUID | FK, opcional | Referência à cópia na tabela exam_copies |
| batch_id | UUID | FK, opcional | Referência ao lote na tabela grading_batches |
| version_id | UUID | FK, NOT NULL | Referência à versão na tabela exam_versions |
| student_id | UUID | FK, opcional | Referência ao estudante associado à entrega |
| status | ENUM | NOT NULL, padrão UPLOADED | Situação do processamento da entrega |
| original_files | JSON | NOT NULL, padrão lista vazia | Arquivos originais enviados |
| processed_files | JSON | NOT NULL, padrão lista vazia | Arquivos resultantes do processamento |
| identified_student_id | UUID | FK, opcional | Estudante identificado durante o processamento |
| identification_confidence | NUMERIC(5,2) | Opcional | Valor de confiança da identificação |
| manual_identification | BOOLEAN | NOT NULL, padrão FALSE | Indica se a identificação foi manual |
| submitted_at | DATETIME com fuso horário | NOT NULL | Data e hora da entrega |
| processed_at | DATETIME com fuso horário | Opcional | Data e hora do processamento |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação do registro |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- Cada entrega pertence a uma única versão da prova.
- Uma versão poderá possuir várias entregas (1:N).
- Uma cópia poderá estar associada a várias entregas (1:N).
- Um lote de correção poderá possuir várias entregas (1:N).
- Uma entrega poderá estar associada a um estudante.
- Uma entrega poderá possuir um estudante identificado durante o processamento.
- Uma entrega poderá possuir várias páginas na tabela submission_pages (1:N).
- Uma entrega poderá possuir várias correções na tabela ai_corrections (1:N).

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a versão da prova é obrigatório.
- Os vínculos com a cópia, o lote e os estudantes são opcionais.
- O status inicial é `UPLOADED`.
- Os campos `original_files` e `processed_files` utilizam JSON e possuem listas vazias como padrão.
- O campo `manual_identification` possui valor padrão `FALSE`.
- A data da entrega e as datas de criação e atualização são obrigatórias.
- A data de processamento é opcional.
- A exclusão da versão poderá excluir suas entregas (`ON DELETE CASCADE`).
- A exclusão da cópia, do lote ou dos estudantes associados define suas respectivas referências como NULL (`ON DELETE SET NULL`).
- Os relacionamentos com páginas e correções por IA utilizam `cascade="all, delete-orphan"` no SQLAlchemy.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

Os demais valores permitidos para o campo `status` precisam ser conferidos na definição de SubmissionStatus.

O modelo não apresenta uma restrição explícita que impeça múltiplas entregas associadas à mesma cópia.

O campo `identification_confidence` utiliza NUMERIC(5,2), mas não apresenta uma restrição explícita de intervalo.

Também não foi identificada uma regra no modelo exigindo que `student_id` e `identified_student_id` tenham o mesmo valor.

A lógica de identificação, processamento e correção deverá ser verificada nos serviços da aplicação.



### 4.23. Tabela submission_pages (Páginas das Provas Digitalizadas)

**Finalidade:** armazenar as páginas individuais das provas digitalizadas, incluindo caminhos das imagens e informações relacionadas ao processamento e reconhecimento de texto.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da página |
| submission_id | UUID | FK, NOT NULL | Referência à entrega na tabela exam_submissions |
| page_number | INTEGER | NOT NULL | Número da página dentro da entrega |
| original_image_path | VARCHAR(500) | NOT NULL | Caminho da imagem original |
| processed_image_path | VARCHAR(500) | Opcional | Caminho da imagem processada |
| rotation_angle | FLOAT | NOT NULL, padrão 0.0 | Ângulo de rotação aplicado ou registrado |
| perspective_corrected | BOOLEAN | NOT NULL, padrão FALSE | Indica se houve correção de perspectiva |
| ocr_confidence | NUMERIC(5,2) | Opcional | Valor de confiança do reconhecimento de texto |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação do registro |

**Relacionamentos implementados:**
- Uma entrega poderá possuir várias páginas (1:N).
- Cada página pertence a uma única entrega.
- Uma página poderá possuir várias respostas extraídas na tabela extracted_answers (1:N).

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a entrega é obrigatório.
- O número da página é obrigatório.
- A combinação de `submission_id` e `page_number` deve ser única.
- O caminho da imagem original é obrigatório.
- O caminho da imagem processada é opcional.
- O ângulo de rotação possui valor padrão `0.0`.
- O campo `perspective_corrected` possui valor padrão `FALSE`.
- O valor de confiança do OCR é opcional.
- A data de criação é obrigatória.
- A exclusão da entrega poderá excluir suas páginas (`ON DELETE CASCADE`).
- O relacionamento com respostas extraídas utiliza `cascade="all, delete-orphan"` no SQLAlchemy.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

O modelo não apresenta uma restrição explícita exigindo que `page_number` seja maior que zero.

O campo `ocr_confidence` não possui uma restrição explícita de intervalo.

O campo `rotation_angle` é declarado como float no Python, sem um tipo SQL explícito no trecho analisado.

A execução do processamento das imagens e do OCR deverá ser verificada nos serviços da aplicação.



### 4.24. Tabela extracted_answers (Respostas Extraídas)

**Finalidade:** armazenar as respostas extraídas das páginas digitalizadas das provas, incluindo textos, imagens e informações relacionadas ao reconhecimento por OCR.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da resposta extraída |
| page_id | UUID | FK, NOT NULL | Referência à página na tabela submission_pages |
| question_id | UUID | FK, NOT NULL | Referência à questão na tabela exam_questions |
| question_order | INTEGER | NOT NULL | Ordem da questão associada à resposta |
| extracted_text | TEXT | Opcional | Texto extraído da resposta |
| extracted_image_path | VARCHAR(500) | Opcional | Caminho da imagem da resposta extraída |
| ocr_confidence | NUMERIC(5,2) | Opcional | Valor de confiança do OCR |
| bounding_box | JSON | NOT NULL, padrão objeto vazio | Informações sobre a região da resposta na imagem |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação do registro |

**Relacionamentos implementados:**
- Uma página poderá possuir várias respostas extraídas (1:N).
- Cada resposta extraída pertence a uma única página.
- Uma questão poderá estar associada a várias respostas extraídas (1:N).
- Cada resposta extraída referencia uma única questão.

**Regras e restrições:**
- A chave primária utiliza UUID.
- Os vínculos com a página e a questão são obrigatórios.
- A ordem da questão é obrigatória.
- O texto e o caminho da imagem extraída são opcionais.
- O valor de confiança do OCR é opcional.
- O campo `bounding_box` utiliza JSON e possui objeto vazio como padrão.
- A data de criação é obrigatória.
- A exclusão da página poderá excluir suas respostas extraídas (`ON DELETE CASCADE`).
- A exclusão da questão poderá excluir suas respostas extraídas (`ON DELETE CASCADE`).
- Existe um índice declarado sobre `question_id`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/exam.py.

O modelo não apresenta uma restrição explícita exigindo que `question_order` seja maior que zero.

O campo `ocr_confidence` não possui uma restrição explícita de intervalo.

Não existe uma restrição de unicidade que impeça múltiplas respostas extraídas para a mesma questão.

Também não foi identificada uma restrição garantindo que a questão referenciada pertença à mesma prova da página digitalizada.

O formato interno de `bounding_box` e as regras de extração deverão ser verificados nos serviços da aplicação.




### 4.25. Tabela ai_corrections (Correções por Inteligência Artificial)

**Finalidade:** armazenar os resultados das correções realizadas por inteligência artificial, incluindo notas sugeridas, justificativas, critérios de avaliação, níveis de confiança e informações para revisão humana.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da correção |
| submission_id | UUID | FK, NOT NULL | Referência à entrega na tabela exam_submissions |
| question_id | UUID | FK, NOT NULL | Referência à questão na tabela exam_questions |
| extracted_answer_id | UUID | FK, opcional | Referência à resposta na tabela extracted_answers |
| provider | VARCHAR(50) | NOT NULL | Provedor de inteligência artificial utilizado |
| model | VARCHAR(100) | NOT NULL | Modelo de IA utilizado |
| status | ENUM | NOT NULL, padrão PENDING | Situação da correção |
| recognized_text | TEXT | Opcional | Texto reconhecido da resposta |
| interpretation | TEXT | Opcional | Interpretação da resposta realizada pela IA |
| suggested_score | NUMERIC(5,2) | Opcional, CHECK | Nota sugerida pela IA |
| max_score | NUMERIC(5,2) | NOT NULL | Pontuação máxima considerada na correção |
| justification | TEXT | Opcional | Justificativa da avaliação |
| criteria_met | JSON | NOT NULL, padrão lista vazia | Critérios atendidos pela resposta |
| criteria_not_met | JSON | NOT NULL, padrão lista vazia | Critérios não atendidos |
| conceptual_errors | JSON | NOT NULL, padrão lista vazia | Erros conceituais identificados |
| ocr_confidence | NUMERIC(5,2) | Opcional, CHECK | Confiança do reconhecimento de texto |
| evaluation_confidence | NUMERIC(5,2) | Opcional, CHECK | Confiança da avaliação da IA |
| requires_review | BOOLEAN | NOT NULL, padrão FALSE | Indica necessidade de revisão humana |
| review_reason | TEXT | Opcional | Motivo da necessidade de revisão |
| raw_response | JSON | NOT NULL, padrão objeto vazio | Resposta original estruturada do modelo de IA |
| prompt_used | TEXT | Opcional | Prompt utilizado na correção |
| processing_time_ms | INTEGER | Opcional | Tempo de processamento em milissegundos |
| error_message | TEXT | Opcional | Mensagem de erro do processamento |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação da correção |
| completed_at | DATETIME com fuso horário | Opcional | Data de conclusão da correção |

**Relacionamentos implementados:**
- Uma entrega poderá possuir várias correções por IA (1:N).
- Cada correção pertence a uma única entrega.
- Uma questão poderá estar associada a várias correções (1:N).
- Uma correção poderá estar associada a uma resposta extraída.
- Uma correção poderá possuir várias revisões na tabela correction_reviews (1:N).

**Regras e restrições:**
- A chave primária utiliza UUID.
- Os vínculos com a entrega e a questão são obrigatórios.
- O vínculo com a resposta extraída é opcional.
- O provedor e o modelo de IA são obrigatórios.
- O status inicial é `PENDING`.
- A nota sugerida, quando informada, deve ser maior ou igual a zero e menor ou igual a `max_score`.
- A confiança do OCR, quando informada, deve estar entre 0 e 100.
- A confiança da avaliação, quando informada, deve estar entre 0 e 100.
- Os campos `criteria_met`, `criteria_not_met` e `conceptual_errors` utilizam JSON, com listas vazias como padrão.
- O campo `raw_response` utiliza JSON, com objeto vazio como padrão.
- O campo `requires_review` possui valor padrão `FALSE`.
- A data de criação é obrigatória.
- A exclusão da entrega ou da questão poderá excluir suas correções (`ON DELETE CASCADE`).
- A exclusão da resposta extraída define `extracted_answer_id` como NULL (`ON DELETE SET NULL`).
- Existe um índice composto sobre `submission_id` e `question_id`.
- O relacionamento com revisões utiliza `cascade="all, delete-orphan"` no SQLAlchemy.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/ai_correction.py.

Os demais valores permitidos para `status` precisam ser conferidos na definição de AICorrectionStatus.

O modelo não apresenta uma restrição explícita exigindo que `max_score` seja maior que zero.

Também não existe uma restrição UNIQUE para a combinação de `submission_id` e `question_id`, permitindo múltiplos registros de correção para a mesma questão de uma entrega.

Não foi identificada uma restrição que garanta que a resposta extraída pertença à mesma entrega e questão referenciadas na correção.

As regras de comunicação com a IA, interpretação das respostas e encaminhamento para revisão humana deverão ser verificadas nos serviços da aplicação.



### 4.26. Tabela correction_reviews (Revisões das Correções)

**Finalidade:** armazenar as revisões humanas das correções realizadas por inteligência artificial, permitindo registrar notas finais, justificativas, alterações nos critérios e informações do responsável pela revisão.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da revisão |
| ai_correction_id | UUID | FK, NOT NULL, UNIQUE | Referência à correção na tabela ai_corrections |
| reviewed_by | UUID | FK, NOT NULL | Referência ao usuário responsável pela revisão |
| status | ENUM | NOT NULL, padrão PENDING | Situação da revisão |
| original_suggested_score | NUMERIC(5,2) | Opcional | Nota originalmente sugerida pela IA |
| final_score | NUMERIC(5,2) | Opcional, CHECK >= 0 | Nota final registrada na revisão |
| corrected_text | TEXT | Opcional | Texto corrigido ou ajustado pelo revisor |
| reviewer_justification | TEXT | Opcional | Justificativa apresentada pelo revisor |
| reviewer_notes | TEXT | Opcional | Observações adicionais do revisor |
| criteria_overrides | JSON | NOT NULL, padrão objeto vazio | Alterações realizadas nos critérios de avaliação |
| started_at | DATETIME com fuso horário | Opcional | Data e hora de início da revisão |
| completed_at | DATETIME com fuso horário | Opcional | Data e hora de conclusão da revisão |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação do registro |

**Relacionamentos implementados:**
- Cada revisão pertence a uma única correção por IA.
- Uma correção por IA poderá possuir no máximo uma revisão (1:1).
- Cada revisão possui um usuário responsável.
- Um usuário poderá ser responsável por várias revisões (1:N).
- Uma revisão poderá possuir vários registros de auditoria na tabela correction_audit_logs (1:N).

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a correção por IA é obrigatório.
- O campo `ai_correction_id` possui restrição UNIQUE, impedindo múltiplas revisões para a mesma correção.
- O usuário responsável pela revisão é obrigatório.
- O status inicial é `PENDING`.
- A nota originalmente sugerida pela IA é opcional.
- A nota final, quando informada, deve ser maior ou igual a zero.
- O texto corrigido, as justificativas e as observações são opcionais.
- O campo `criteria_overrides` utiliza JSON e possui objeto vazio como padrão.
- As datas de início e conclusão da revisão são opcionais.
- A data de criação é obrigatória.
- A exclusão da correção por IA poderá excluir sua revisão (`ON DELETE CASCADE`).
- A exclusão do usuário responsável é restringida (`ON DELETE RESTRICT`).
- O relacionamento com registros de auditoria utiliza `cascade="all, delete-orphan"` no SQLAlchemy.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/ai_correction.py.

Os demais valores permitidos para `status` precisam ser conferidos na definição de ReviewStatus.

Embora o relacionamento em AICorrection utilize uma lista (`reviews`), a restrição UNIQUE em `ai_correction_id` permite no máximo uma revisão por correção.

O modelo não apresenta uma restrição explícita garantindo que `final_score` seja menor ou igual à pontuação máxima da questão.

Também não exige o preenchimento da nota final ou da data de conclusão quando a revisão for finalizada.

Essas validações, caso existam, deverão ser verificadas nos serviços da aplicação.



### 4.27. Tabela correction_audit_logs (Auditoria das Correções)

**Finalidade:** armazenar o histórico de alterações realizadas durante as revisões das correções, permitindo identificar o que foi modificado, quem realizou a alteração e quando ela ocorreu.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do registro de auditoria |
| review_id | UUID | FK, NOT NULL | Referência à revisão na tabela correction_reviews |
| action | VARCHAR(50) | NOT NULL | Tipo de ação realizada |
| field_changed | VARCHAR(100) | NOT NULL | Nome do campo alterado |
| old_value | TEXT | Opcional | Valor anterior do campo |
| new_value | TEXT | Opcional | Novo valor do campo |
| changed_by | UUID | FK, NOT NULL | Referência ao usuário responsável pela alteração |
| changed_at | DATETIME com fuso horário | NOT NULL | Data e hora da alteração |
| ip_address | VARCHAR(45) | Opcional | Endereço IP relacionado à alteração |
| user_agent | VARCHAR(500) | Opcional | Informações do navegador ou cliente utilizado |

**Relacionamentos implementados:**
- Uma revisão poderá possuir vários registros de auditoria (1:N).
- Cada registro de auditoria pertence a uma única revisão.
- Cada registro referencia um usuário responsável pela alteração.
- Um usuário poderá ser responsável por vários registros de auditoria (1:N).

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com a revisão é obrigatório.
- O tipo de ação e o campo alterado são obrigatórios.
- Os valores anterior e novo são opcionais.
- O usuário responsável pela alteração é obrigatório.
- A data da alteração é obrigatória e recebe automaticamente a data e hora atuais na criação pelo modelo.
- O endereço IP e o user agent são opcionais.
- A exclusão da revisão poderá excluir seus registros de auditoria (`ON DELETE CASCADE`).
- A exclusão do usuário responsável é restringida (`ON DELETE RESTRICT`).

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/ai_correction.py.

O código apresenta exemplos de ações como:
- `score_change`: alteração de nota.
- `text_correction`: correção de texto.
- `criteria_override`: alteração de critérios.

Esses valores aparecem como exemplos em um comentário do código. Não existe uma restrição explícita que limite o campo `action` a eles.

Os campos `old_value` e `new_value` utilizam TEXT, independentemente do tipo original do dado alterado.

O modelo não apresenta mecanismos explícitos que impeçam a alteração ou exclusão posterior dos registros de auditoria.

A geração automática desses registros deverá ser verificada nos serviços da aplicação.


### 4.28. Tabela audit_logs (Auditoria Geral)

**Finalidade:** armazenar o histórico de ações e operações realizadas no EduGrade, permitindo identificar usuários responsáveis, entidades afetadas, alterações realizadas e possíveis erros.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do registro de auditoria |
| user_id | UUID | FK, opcional | Referência ao usuário na tabela users |
| action | ENUM | NOT NULL | Tipo de ação realizada |
| entity_type | VARCHAR(100) | Opcional | Tipo de entidade afetada |
| entity_id | UUID | Opcional | Identificador da entidade afetada |
| description | TEXT | NOT NULL | Descrição da ação realizada |
| old_values | JSON | Opcional | Valores anteriores à alteração |
| new_values | JSON | Opcional | Valores posteriores à alteração |
| ip_address | VARCHAR(45) | Opcional | Endereço IP relacionado à operação |
| user_agent | VARCHAR(500) | Opcional | Informações do navegador ou cliente |
| request_id | VARCHAR(100) | Opcional | Identificador da requisição |
| session_id | VARCHAR(100) | Opcional | Identificador da sessão |
| success | BOOLEAN | NOT NULL, padrão TRUE | Indica se a operação foi bem-sucedida |
| error_message | TEXT | Opcional | Mensagem de erro da operação |
| created_at | DATETIME com fuso horário | NOT NULL | Data e hora do registro |

**Relacionamentos implementados:**
- Cada registro de auditoria poderá estar associado a um usuário.
- Um usuário poderá possuir vários registros de auditoria (1:N).
- O campo `entity_id` identifica uma entidade afetada, mas não possui relacionamento por chave estrangeira declarado no modelo.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O vínculo com o usuário é opcional.
- O tipo de ação e a descrição são obrigatórios.
- Os valores anteriores e novos são opcionais e utilizam JSON.
- O endereço IP, o user agent e os identificadores de requisição e sessão são opcionais.
- O campo `success` possui valor padrão `TRUE`.
- A mensagem de erro é opcional.
- A data de criação é obrigatória.
- A exclusão do usuário associado define `user_id` como NULL (`ON DELETE SET NULL`).

**Índices implementados:**
- Índice composto sobre `user_id` e `created_at`.
- Índice composto sobre `entity_type` e `entity_id`.
- Índice composto sobre `action` e `created_at`.
- Índices individuais declarados para `user_id`, `action`, `entity_type`, `entity_id`, `request_id` e `created_at`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em backend/app/models/audit.py.

Os valores permitidos para o campo `action` precisam ser conferidos na definição de AuditActionType.

O campo `entity_id` não possui uma restrição de chave estrangeira, permitindo registrar identificadores de diferentes tipos de entidades.

O modelo não apresenta mecanismos explícitos que impeçam alterações ou exclusões posteriores dos registros de auditoria.

A geração automática dos registros e a classificação das ações deverão ser verificadas nos serviços da aplicação.


### 4.29. Tabela system_logs (Logs do Sistema)

**Finalidade:** armazenar registros técnicos relacionados ao funcionamento do EduGrade, incluindo mensagens informativas, avisos, erros e informações que auxiliam no diagnóstico de problemas.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do registro |
| level | VARCHAR(20) | NOT NULL | Nível de severidade do evento |
| logger | VARCHAR(255) | NOT NULL | Nome do logger responsável pelo registro |
| message | TEXT | NOT NULL | Mensagem do evento |
| module | VARCHAR(255) | Opcional | Módulo relacionado ao evento |
| function | VARCHAR(255) | Opcional | Função relacionada ao evento |
| line_number | INTEGER | Opcional | Número da linha relacionada ao evento |
| traceback | TEXT | Opcional | Rastreamento de erro ou exceção |
| context | JSON | Opcional | Informações adicionais sobre o evento |
| user_id | UUID | FK, opcional | Referência ao usuário associado ao evento |
| request_id | VARCHAR(100) | Opcional | Identificador da requisição |
| created_at | DATETIME com fuso horário | NOT NULL | Data e hora do registro |

**Relacionamentos implementados:**
- Cada registro poderá estar associado a um usuário da tabela `users`.
- Um usuário poderá estar associado a vários registros de logs (1:N).
- O relacionamento com o usuário é opcional.

**Regras e restrições:**
- A chave primária utiliza UUID.
- O nível, o logger e a mensagem são obrigatórios.
- O módulo, a função e o número da linha são opcionais.
- O traceback é opcional e permite armazenar informações sobre exceções.
- O contexto é opcional e utiliza o formato JSON.
- O vínculo com o usuário é opcional.
- O identificador da requisição é opcional.
- A data de criação é obrigatória e recebe automaticamente a data e hora atuais na criação pelo modelo.
- A exclusão do usuário associado define `user_id` como NULL (`ON DELETE SET NULL`).

**Índices implementados:**
- Índice individual sobre `level`.
- Índice individual sobre `request_id`.
- Índice individual sobre `created_at`.
- Índice composto sobre `level` e `created_at`, denominado `ix_system_logs_level_created`.

**Observação técnica:**
Estrutura baseada no modelo SQLAlchemy localizado em `backend/app/models/audit.py`.

O código apresenta os seguintes exemplos de níveis de log:
- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

Esses valores aparecem como exemplos em um comentário do código. Não existe uma restrição explícita que limite o campo `level` a eles.

O modelo não declara um relacionamento ORM explícito com a tabela `users`, mas estabelece uma chave estrangeira por meio do campo `user_id`.

A geração automática dos registros deverá ser verificada na implementação dos serviços e mecanismos de logging da aplicação.


### 4.30. Tabela access_requests (Solicitações de Acesso)

**Finalidade:** armazenar solicitações de acesso ao EduGrade, incluindo os dados do solicitante, o perfil desejado, a justificativa e a situação do pedido.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da solicitação |
| full_name | VARCHAR(255) | NOT NULL | Nome completo do solicitante |
| email | VARCHAR(255) | NOT NULL | E-mail do solicitante |
| username | VARCHAR(100) | NOT NULL | Nome de usuário solicitado |
| phone | VARCHAR(40) | Opcional | Telefone do solicitante |
| requested_role | VARCHAR(20) | NOT NULL | Perfil de acesso solicitado |
| justification | TEXT | NOT NULL | Justificativa para solicitar acesso |
| status | ENUM | NOT NULL, padrão OPEN | Situação da solicitação |
| account_id | UUID | FK, opcional | Conta associada na tabela users |
| created_at | DATETIME com fuso horário | NOT NULL | Data e hora de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data e hora da última atualização |

**Relacionamentos implementados:**
- `account_id` referencia `users.id`.
- Uma conta poderá ser referenciada por várias solicitações (1:N).
- A associação com uma conta é opcional.
- Não existe relacionamento ORM explícito com User nesta classe.

**Regras e restrições:**
- O identificador utiliza UUID como chave primária.
- Nome, e-mail, username, perfil e justificativa são obrigatórios.
- O telefone e a conta associada são opcionais.
- O status inicial é OPEN.
- A exclusão da conta associada define `account_id` como NULL (`ON DELETE SET NULL`).
- Existem índices individuais sobre `email` e `status`.
- `updated_at` possui atualização automática configurada no modelo.

**Valores da enumeração AccessRequestStatus:**
- OPEN: solicitação aberta.
- APPROVED: solicitação aprovada.
- REJECTED: solicitação rejeitada.

**Observação técnica:**
Estrutura baseada em `backend/app/models/access_request.py`.

O campo `requested_role` é uma string sem enumeração declarada neste modelo. Também não existem restrições UNIQUE declaradas para `email` ou `username`.

---

### 4.31. Tabela ai_provider_configs (Configurações de Provedores de IA)

**Finalidade:** armazenar configurações de conexão e utilização dos provedores de inteligência artificial do EduGrade.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da configuração |
| provider_id | VARCHAR(80) | UNIQUE, NOT NULL | Identificador do provedor |
| provider_type | VARCHAR(30) | NOT NULL | Tipo de provedor |
| name | VARCHAR(120) | NOT NULL | Nome do provedor |
| base_url | VARCHAR(500) | NOT NULL | Endereço-base da API |
| encrypted_api_key | TEXT | Opcional | Credencial de API armazenada de forma criptografada |
| model | VARCHAR(255) | Opcional | Modelo principal |
| vision_model | VARCHAR(255) | Opcional | Modelo utilizado para visão |
| alternative_models | JSON | NOT NULL, padrão lista vazia | Modelos alternativos |
| available_models | JSON | NOT NULL, padrão lista vazia | Modelos disponíveis |
| timeout_seconds | INTEGER | NOT NULL, padrão 60 | Tempo limite em segundos |
| max_retries | INTEGER | NOT NULL, padrão 2 | Número máximo de tentativas adicionais |
| priority | INTEGER | NOT NULL, padrão 100 | Prioridade do provedor |
| is_enabled | BOOLEAN | NOT NULL, padrão FALSE | Indica se está habilitado |
| is_default | BOOLEAN | NOT NULL, padrão FALSE | Indica se é o provedor padrão |
| status | VARCHAR(30) | NOT NULL, padrão not_configured | Situação da configuração |
| last_checked_at | DATETIME com fuso horário | Opcional | Data da última verificação |
| last_error | VARCHAR(500) | Opcional | Último erro registrado |
| created_by | UUID | FK, NOT NULL | Usuário responsável pela criação |
| updated_by | UUID | FK, NOT NULL | Usuário responsável pela atualização |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- `created_by` referencia `users.id`.
- `updated_by` referencia `users.id`.
- Um usuário poderá criar ou atualizar várias configurações.
- Não existem relacionamentos ORM explícitos declarados nesta classe.

**Regras e restrições:**
- `provider_id` é obrigatório e único.
- `created_by` e `updated_by` são obrigatórios.
- A exclusão dos usuários referenciados é restringida (`ON DELETE RESTRICT`).
- Os campos JSON de modelos utilizam listas vazias como padrão.
- O provedor inicia desabilitado e não definido como padrão.
- `updated_at` possui atualização automática configurada no modelo.
- Existe índice composto sobre `is_enabled` e `priority`, denominado `ix_ai_provider_enabled_priority`.
- `provider_id` possui declarações de UNIQUE e índice individual.

**Observação técnica:**
Estrutura baseada em `backend/app/models/admin_settings.py`.

O modelo prevê o armazenamento da chave de API no campo `encrypted_api_key`, destinado a texto criptografado. A implementação efetiva da criptografia deve ser verificada nos serviços.

Não existe restrição explícita que garanta apenas um registro com `is_default = TRUE`.

---

### 4.32. Tabela admin_settings (Configurações Administrativas)

**Finalidade:** armazenar configurações administrativas não secretas, utilizando uma chave identificadora e um valor em formato JSON.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| key | VARCHAR(120) | PK | Identificador único da configuração |
| value | JSON | Opcional | Valor da configuração |
| updated_by | UUID | FK, opcional | Usuário responsável pela atualização |
| updated_at | DATETIME com fuso horário | NOT NULL | Data e hora da atualização |

**Relacionamentos implementados:**
- `updated_by` referencia `users.id`.
- Um usuário poderá estar associado a várias configurações (1:N).
- O relacionamento é opcional.
- Não existe relacionamento ORM explícito declarado nesta classe.

**Regras e restrições:**
- A chave primária é o campo `key`, do tipo VARCHAR(120).
- Não existe campo `id` nesta tabela.
- O valor utiliza JSON e pode ser nulo.
- O usuário responsável pela atualização é opcional.
- A exclusão do usuário define `updated_by` como NULL (`ON DELETE SET NULL`).
- `updated_at` é obrigatório e possui valor padrão com a data e hora atuais.

**Observação técnica:**
Estrutura baseada em `backend/app/models/admin_settings.py`.

O campo `value` permite armazenar objetos, listas, textos, números, valores booleanos ou NULL em formato JSON.

O modelo não declara `onupdate` para `updated_at`. Portanto, a atualização automática desse campo em alterações posteriores não está garantida por essa declaração.

---

### 4.33. Tabela grading_batches (Lotes de Correção)

**Finalidade:** registrar lotes de provas enviados para processamento, acompanhando o andamento da identificação de alunos, agrupamento de páginas e correção das submissões.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do lote |
| exam_id | UUID | FK, NOT NULL | Prova associada |
| version_id | UUID | FK, NOT NULL | Versão da prova |
| uploaded_by | UUID | FK, NOT NULL | Usuário responsável pelo envio |
| status | ENUM | NOT NULL, padrão UPLOADING | Situação do processamento |
| total_files | INTEGER | NOT NULL, padrão 0 | Quantidade total de arquivos |
| processed_files | INTEGER | NOT NULL, padrão 0 | Arquivos processados |
| total_pages | INTEGER | NOT NULL, padrão 0 | Quantidade total de páginas |
| identified_students | INTEGER | NOT NULL, padrão 0 | Estudantes identificados |
| grouped_submissions | INTEGER | NOT NULL, padrão 0 | Submissões agrupadas |
| graded_submissions | INTEGER | NOT NULL, padrão 0 | Submissões corrigidas |
| pending_review | INTEGER | NOT NULL, padrão 0 | Itens pendentes de revisão |
| failed_files | INTEGER | NOT NULL, padrão 0 | Arquivos com falha |
| error_message | TEXT | Opcional | Mensagem de erro |
| processing_started_at | DATETIME com fuso horário | Opcional | Início do processamento |
| processing_completed_at | DATETIME com fuso horário | Opcional | Término do processamento |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| updated_at | DATETIME com fuso horário | NOT NULL | Data da última atualização |

**Relacionamentos implementados:**
- `exam_id` referencia `exams.id`.
- `version_id` referencia `exam_versions.id`.
- `uploaded_by` referencia `users.id`.
- Um lote poderá possuir vários arquivos em `grading_batch_files` (1:N).
- Um lote poderá estar associado a várias submissões em `exam_submissions` (1:N).

**Regras e restrições:**
- Prova, versão e usuário responsável são obrigatórios.
- As três chaves estrangeiras utilizam `ON DELETE RESTRICT`.
- O status inicial é UPLOADING.
- Os contadores possuem valor padrão zero.
- A mensagem de erro e os horários de processamento são opcionais.
- Os arquivos relacionados possuem cascata ORM `all, delete-orphan`.
- Existem índices individuais sobre `exam_id`, `version_id` e `status`.
- `updated_at` possui atualização automática configurada no modelo.

**Valores da enumeração BatchStatus:**
- UPLOADING
- UPLOADED
- PROCESSING
- PROCESSING_PAGES
- IDENTIFYING
- GROUPING
- GRADING
- COMPLETED
- PARTIAL
- FAILED
- CANCELLED

**Observação técnica:**
Estrutura baseada em `backend/app/models/grading_batch.py`.

Os campos de contagem não apresentam restrições CHECK explícitas para impedir valores negativos.

---

### 4.34. Tabela grading_batch_files (Arquivos dos Lotes)

**Finalidade:** armazenar os metadados dos arquivos enviados em cada lote de correção e acompanhar seu processamento.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do arquivo |
| batch_id | UUID | FK, NOT NULL | Lote ao qual pertence |
| original_filename | VARCHAR(500) | NOT NULL | Nome original do arquivo |
| stored_path | VARCHAR(500) | NOT NULL | Caminho de armazenamento |
| content_type | VARCHAR(100) | NOT NULL | Tipo de conteúdo |
| file_size | INTEGER | NOT NULL | Tamanho do arquivo |
| file_type | VARCHAR(50) | NOT NULL | Categoria do arquivo |
| page_count | INTEGER | NOT NULL, padrão 1 | Número de páginas |
| status | ENUM | NOT NULL, padrão PENDING | Situação do processamento |
| processed_pages | INTEGER | NOT NULL, padrão 0 | Páginas processadas |
| error_message | TEXT | Opcional | Mensagem de erro |
| ocr_data | JSON | NOT NULL, padrão objeto vazio | Dados extraídos por OCR |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |
| processed_at | DATETIME com fuso horário | Opcional | Data de processamento |

**Relacionamentos implementados:**
- `batch_id` referencia `grading_batches.id`.
- Cada arquivo pertence a um lote.
- Um lote poderá conter vários arquivos (1:N).
- Um arquivo poderá conter várias páginas em `exam_submission_pages` (1:N).

**Regras e restrições:**
- O vínculo com o lote é obrigatório.
- A exclusão do lote poderá excluir seus arquivos (`ON DELETE CASCADE`).
- Os metadados principais do arquivo são obrigatórios.
- O número de páginas inicia em 1.
- A quantidade de páginas processadas inicia em 0.
- O status inicial é PENDING.
- Os dados OCR utilizam um objeto JSON vazio como padrão.
- As páginas relacionadas possuem cascata ORM `all, delete-orphan`.
- Existe índice individual sobre `batch_id`.

**Valores da enumeração FileStatus:**
- PENDING
- PROCESSING
- PROCESSED
- FAILED
- SKIPPED

**Observação técnica:**
Estrutura baseada em `backend/app/models/grading_batch.py`.

O código apresenta `image` e `pdf` como exemplos de `file_type`, mas não declara uma restrição explícita que limite o campo a esses valores.

---

### 4.35. Tabela exam_submission_pages (Páginas de Provas em Lote)

**Finalidade:** armazenar informações de páginas individuais extraídas dos arquivos de um lote, incluindo imagens, ajustes visuais e resultados de OCR.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único da página |
| batch_file_id | UUID | FK, NOT NULL | Arquivo de origem |
| submission_id | UUID | FK, opcional | Submissão associada |
| page_number | INTEGER | NOT NULL | Número da página |
| original_image_path | VARCHAR(500) | NOT NULL | Caminho da imagem original |
| processed_image_path | VARCHAR(500) | Opcional | Caminho da imagem processada |
| rotation_angle | FLOAT | NOT NULL, padrão 0.0 | Ângulo de rotação |
| perspective_corrected | BOOLEAN | NOT NULL, padrão FALSE | Indica correção de perspectiva |
| ocr_confidence | NUMERIC(5,2) | Opcional | Confiança do reconhecimento OCR |
| full_text | TEXT | Opcional | Texto completo reconhecido |
| ocr_data | JSON | NOT NULL, padrão objeto vazio | Dados detalhados de OCR |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |

**Relacionamentos implementados:**
- `batch_file_id` referencia `grading_batch_files.id`.
- `submission_id` referencia `exam_submissions.id`.
- Cada página pertence a um arquivo de lote.
- Uma página poderá estar associada a uma submissão.
- Uma página poderá possuir vários resultados de identificação em `student_identification_results` (1:N).

**Regras e restrições:**
- O vínculo com o arquivo é obrigatório.
- A exclusão do arquivo poderá excluir suas páginas (`ON DELETE CASCADE`).
- A exclusão da submissão associada define `submission_id` como NULL (`ON DELETE SET NULL`).
- O caminho da imagem original e o número da página são obrigatórios.
- O ângulo de rotação inicia em 0.0.
- A correção de perspectiva inicia como FALSE.
- Os dados OCR utilizam objeto JSON vazio como padrão.
- Os resultados de identificação relacionados possuem cascata ORM `all, delete-orphan`.
- Existem índices sobre `batch_file_id` e `submission_id`.
- Existe também o índice explícito `ix_submission_pages_batch_file` sobre `batch_file_id`.

**Observação técnica:**
Estrutura baseada em `backend/app/models/grading_batch.py`.

Esta tabela é diferente de `submission_pages`, declarada em `backend/app/models/exam.py`. São duas tabelas distintas no modelo.

O campo `ocr_confidence` não possui restrição CHECK explícita para limitar seu intervalo.

---

### 4.36. Tabela student_identification_results (Resultados de Identificação dos Alunos)

**Finalidade:** registrar resultados de identificação de estudantes a partir de páginas de provas, incluindo informações extraídas por IA, níveis de confiança, conflitos e possíveis intervenções manuais.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do resultado |
| page_id | UUID | FK, NOT NULL | Página analisada |
| submission_id | UUID | FK, opcional | Submissão associada |
| identified_ra | VARCHAR(50) | Opcional | RA identificado |
| identified_matricula | VARCHAR(50) | Opcional | Matrícula identificada |
| identified_name | VARCHAR(255) | Opcional | Nome identificado |
| identified_exam_code | VARCHAR(100) | Opcional | Código da prova identificado |
| identified_class_code | VARCHAR(100) | Opcional | Código da turma identificado |
| identified_copy_code | VARCHAR(100) | Opcional | Código da cópia identificado |
| matched_student_id | UUID | FK, opcional | Estudante correspondente |
| ra_confidence | NUMERIC(5,2) | Opcional | Confiança na identificação do RA |
| matricula_confidence | NUMERIC(5,2) | Opcional | Confiança na identificação da matrícula |
| match_type | VARCHAR(50) | NOT NULL | Método de correspondência |
| status | ENUM | NOT NULL, padrão PENDING | Situação da identificação |
| conflict_details | JSON | NOT NULL, padrão objeto vazio | Detalhes de conflitos |
| manual_override | BOOLEAN | NOT NULL, padrão FALSE | Indica intervenção manual |
| overridden_by | UUID | FK, opcional | Usuário responsável pela intervenção |
| overridden_at | DATETIME com fuso horário | Opcional | Data da intervenção |
| ai_provider | VARCHAR(50) | NOT NULL | Provedor de IA utilizado |
| ai_model | VARCHAR(100) | NOT NULL | Modelo de IA utilizado |
| raw_response | JSON | NOT NULL, padrão objeto vazio | Resposta original da IA |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |

**Relacionamentos implementados:**
- `page_id` referencia `exam_submission_pages.id`.
- `submission_id` referencia `exam_submissions.id`.
- `matched_student_id` referencia `students.id`.
- `overridden_by` referencia `users.id`.
- Uma página poderá possuir vários resultados de identificação (1:N).
- Um estudante poderá aparecer em vários resultados de identificação.
- Uma submissão poderá estar associada a vários resultados.

**Regras e restrições:**
- O vínculo com a página é obrigatório e utiliza `ON DELETE CASCADE`.
- As referências opcionais à submissão, ao estudante e ao usuário responsável utilizam `ON DELETE SET NULL`.
- O método de correspondência é obrigatório.
- O status inicial é PENDING.
- A intervenção manual inicia como FALSE.
- Os detalhes de conflito e a resposta original da IA utilizam objetos JSON vazios como padrão.
- O provedor e o modelo de IA são obrigatórios.
- Existem índices individuais sobre `page_id`, `submission_id` e `matched_student_id`.

**Valores da enumeração IdentificationStatus:**
- IDENTIFIED
- PENDING
- AMBIGUOUS
- NOT_FOUND
- CONFLICT
- MANUAL

**Exemplos de match_type apresentados no código:**
- ra_only
- matricula_only
- both
- name_fallback

**Observação técnica:**
Estrutura baseada em `backend/app/models/grading_batch.py`.

Os exemplos de `match_type` aparecem em comentário e não constituem uma restrição explícita.

Os campos de confiança utilizam NUMERIC(5,2), sem limites CHECK explícitos no modelo.

---

### 4.37. Tabela exam_page_groups (Agrupamentos de Páginas de Provas)

**Finalidade:** armazenar agrupamentos de páginas identificadas como pertencentes à mesma prova, vinculando o lote, o estudante, a versão da prova e a submissão criada, quando existente.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do agrupamento |
| batch_id | UUID | FK, NOT NULL | Lote associado |
| student_id | UUID | FK, opcional | Estudante identificado |
| exam_id | UUID | FK, NOT NULL | Prova associada |
| version_id | UUID | FK, NOT NULL | Versão da prova |
| copy_identifier | VARCHAR(100) | Opcional | Identificador da cópia |
| page_ids | JSON | NOT NULL, padrão lista vazia | Identificadores das páginas agrupadas |
| status | ENUM | NOT NULL, padrão PENDING | Situação do agrupamento |
| confidence | NUMERIC(5,2) | Opcional | Confiança no agrupamento |
| conflict_details | JSON | NOT NULL, padrão objeto vazio | Informações sobre conflitos |
| created_submission_id | UUID | FK, opcional | Submissão criada a partir do agrupamento |
| created_at | DATETIME com fuso horário | NOT NULL | Data de criação |

**Relacionamentos implementados:**
- `batch_id` referencia `grading_batches.id`.
- `student_id` referencia `students.id`.
- `exam_id` referencia `exams.id`.
- `version_id` referencia `exam_versions.id`.
- `created_submission_id` referencia `exam_submissions.id`.
- Cada agrupamento pertence a um lote.
- Um lote poderá possuir vários agrupamentos (1:N).
- Um estudante poderá estar associado a vários agrupamentos.

**Regras e restrições:**
- O lote, a prova e a versão são obrigatórios.
- A exclusão do lote poderá excluir seus agrupamentos (`ON DELETE CASCADE`).
- A exclusão do estudante ou da submissão associada define a respectiva referência como NULL (`ON DELETE SET NULL`).
- As referências à prova e à versão utilizam `ON DELETE RESTRICT`.
- O status inicial é PENDING.
- `page_ids` utiliza uma lista JSON vazia como padrão.
- `conflict_details` utiliza um objeto JSON vazio como padrão.
- Existem índices individuais sobre `batch_id` e `student_id`.

**Valores da enumeração PageGroupStatus:**
- PENDING
- GROUPED
- CONFLICT
- MANUAL_REVIEW

**Observação técnica:**
Estrutura baseada em `backend/app/models/grading_batch.py`.

O campo `page_ids` armazena identificadores em JSON, sem chaves estrangeiras individuais declaradas para cada página.

O modelo declara relacionamentos ORM com GradingBatch e Student, mas não declara relacionamentos ORM explícitos para todas as demais chaves estrangeiras.

---

### 4.38. Tabela grading_audit_logs (Auditoria do Processamento de Correções)

**Finalidade:** registrar eventos e alterações relacionados ao processamento de lotes de correção, permitindo acompanhar operações, entidades afetadas, resultados e possíveis erros.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do registro |
| batch_id | UUID | FK, NOT NULL | Lote associado |
| submission_id | UUID | FK, opcional | Submissão associada |
| action | VARCHAR(100) | NOT NULL | Ação realizada |
| entity_type | VARCHAR(50) | NOT NULL | Tipo de entidade afetada |
| entity_id | UUID | Opcional | Identificador da entidade afetada |
| description | TEXT | NOT NULL | Descrição da operação |
| old_values | JSON | Opcional | Valores anteriores |
| new_values | JSON | Opcional | Valores posteriores |
| performed_by | UUID | FK, opcional | Usuário responsável |
| ai_provider | VARCHAR(50) | Opcional | Provedor de IA relacionado |
| ai_model | VARCHAR(100) | Opcional | Modelo de IA relacionado |
| ip_address | VARCHAR(45) | Opcional | Endereço IP |
| user_agent | VARCHAR(500) | Opcional | Informações do navegador ou cliente |
| success | BOOLEAN | NOT NULL, padrão TRUE | Indica sucesso da operação |
| error_message | TEXT | Opcional | Mensagem de erro |
| created_at | DATETIME com fuso horário | NOT NULL | Data e hora do registro |

**Relacionamentos implementados:**
- `batch_id` referencia `grading_batches.id`.
- `submission_id` referencia `exam_submissions.id`.
- `performed_by` referencia `users.id`.
- Um lote poderá possuir vários registros de auditoria (1:N).
- Uma submissão poderá estar associada a vários registros.
- Um usuário poderá ser responsável por vários registros.

**Regras e restrições:**
- O vínculo com o lote é obrigatório.
- A exclusão do lote poderá excluir seus registros de auditoria (`ON DELETE CASCADE`).
- A exclusão da submissão ou do usuário associado define a respectiva referência como NULL (`ON DELETE SET NULL`).
- A ação, o tipo de entidade e a descrição são obrigatórios.
- O campo `entity_id` não possui chave estrangeira declarada.
- Os valores anteriores e novos são opcionais e utilizam JSON.
- `success` possui valor padrão TRUE.
- Existe índice composto sobre `batch_id` e `action`, denominado `ix_grading_audit_batch_action`.
- Existem índices individuais sobre `batch_id`, `submission_id` e `created_at`.

**Observação técnica:**
Estrutura baseada em `backend/app/models/grading_batch.py`.

Esta tabela é específica do processamento de correções e é diferente de `audit_logs`, utilizada para auditoria geral, e de `correction_audit_logs`, vinculada às revisões das correções.

O modelo não apresenta mecanismos explícitos para impedir alterações ou exclusões posteriores dos registros.

---

### 4.39. Tabela study_materials (Materiais de Estudo)

**Finalidade:** armazenar informações sobre materiais de estudo disponibilizados aos alunos de uma disciplina, incluindo identificação do arquivo, responsável pelo envio e dados de armazenamento.

| Campo | Tipo | Restrição | Descrição |
|---|---|---|---|
| id | UUID | PK | Identificador único do material |
| subject_id | UUID | FK, NOT NULL | Disciplina associada |
| uploaded_by | UUID | FK, NOT NULL | Usuário responsável pelo envio |
| title | VARCHAR(255) | NOT NULL | Título do material |
| description | TEXT | Opcional | Descrição do conteúdo |
| original_filename | VARCHAR(255) | NOT NULL | Nome original do arquivo |
| stored_filename | VARCHAR(255) | UNIQUE, NOT NULL | Nome utilizado no armazenamento |
| media_type | VARCHAR(100) | NOT NULL | Tipo de mídia do arquivo |
| file_size | INTEGER | NOT NULL | Tamanho do arquivo |
| created_at | DATETIME com fuso horário | NOT NULL | Data e hora de criação |

**Relacionamentos implementados:**
- `subject_id` referencia `subjects.id`.
- `uploaded_by` referencia `users.id`.
- Uma disciplina poderá possuir vários materiais de estudo (1:N).
- Um usuário poderá enviar vários materiais (1:N).
- Cada material pertence a uma disciplina e referencia um usuário responsável.

**Regras e restrições:**
- A chave primária utiliza UUID.
- A disciplina e o usuário responsável são obrigatórios.
- A exclusão da disciplina poderá excluir seus materiais (`ON DELETE CASCADE`).
- A exclusão do usuário responsável é restringida (`ON DELETE RESTRICT`).
- O título, os nomes do arquivo, o tipo de mídia e o tamanho são obrigatórios.
- A descrição é opcional.
- `stored_filename` possui restrição UNIQUE.
- Existe índice individual sobre `subject_id`.
- Existe índice composto sobre `subject_id` e `created_at`, denominado `ix_study_material_subject_created`.

**Observação técnica:**
Estrutura baseada em `backend/app/models/material.py`.

O modelo declara relacionamentos ORM com Subject e User.

O campo `file_size` não possui restrição CHECK explícita para impedir valores negativos.

A tabela armazena informações e referências aos arquivos. O conteúdo binário do material não é declarado como coluna neste modelo.

