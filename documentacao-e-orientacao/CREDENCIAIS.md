# 🔐 Credenciais de Acesso — EduGrade

> **Contas de demonstração.** Este arquivo reúne os usuários e senhas criados pelo
> seed do banco de dados. Cada perfil (administrador, professor e aluno) possui
> **duas contas**. Em produção, altere todas as senhas e remova as contas
> demonstrativas.

---

## 1. Como acessar

1. Inicie o servidor a partir da **raiz do projeto**:

   ```cmd
   venv\Scripts\activate
   python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Abra no navegador: <http://localhost:8000/login.html>

3. Use **usuário ou e-mail** + senha da tabela abaixo. O sistema redireciona
   automaticamente para o painel do perfil autenticado:

   | Perfil | Painel |
   |---|---|
   | Administrador | <http://localhost:8000/admin/dashboard.html> |
   | Professor | <http://localhost:8000/professor/dashboard.html> |
   | Aluno | <http://localhost:8000/aluno/dashboard.html> |

   Documentação interativa da API: <http://localhost:8000/docs>

---

## 2. Administradores (2 contas)

| Usuário | Senha | E-mail | Nome | Matrícula funcional |
|---|---|---|---|---|
| `admin` | `admin123` | `admin@edugrade.local` | Administrador do Sistema | ADM001 |
| `admin2` | `admin123` | `admin2@edugrade.local` | Coordenação Acadêmica | ADM002 |

**Funções disponíveis:** gestão de usuários, professores, alunos, cursos,
disciplinas, turmas, matrículas e períodos; atribuições acadêmicas; notas;
auditoria; configurações de IA e OCR; painel de qualidade; chamados de acesso;
armazenamento e erros do sistema.

---

## 3. Professores (2 contas)

| Usuário | Senha | E-mail | Nome | Disciplina | Turma | Horário | Sala |
|---|---|---|---|---|---|---|---|
| `professor` | `prof123` | `professor@edugrade.local` | Prof. Carlos Silva | IA101 — Inteligência Artificial Aplicada | ES-IA-20261-A | Seg/Qua 19:00-20:40 | Lab 04 |
| `professor2` | `prof123` | `professor2@edugrade.local` | Profa. Ana Souza | ES201 — Engenharia de Software | ES-ES-20261-A | Ter/Qui 19:00-20:40 | Sala 12 |

**Funções disponíveis:** turmas e alunos autorizados, criação e edição de provas,
questões e gabarito, validação da pontuação, publicação e versionamento,
impressão individual e em lote (PDF + QR Code), envio de provas digitalizadas,
OCR, correção assistida por IA, revisão, publicação de notas, materiais de estudo
e relatórios.

> O professor só opera nas turmas/disciplinas atribuídas a ele. As atribuições
> do seed já incluem todas as permissões contextuais.

---

## 4. Alunos (2 contas)

| Usuário | Senha | E-mail | Nome | RA | Matrícula | Turmas |
|---|---|---|---|---|---|---|
| `aluno` | `aluno123` | `aluno@edugrade.local` | Lucas Santos | RA123456 | 2026001 | ES-IA-20261-A e ES-ES-20261-A |
| `aluno2` | `aluno123` | `aluno2@edugrade.local` | Marina Oliveira | RA123457 | 2026002 | ES-IA-20261-A e ES-ES-20261-A |

**Funções disponíveis:** painel acadêmico, notas publicadas e médias, provas das
suas turmas, frequência detalhada, grade horária, materiais de estudo, perfil e
alteração de senha.

> O aluno **não** cria provas, lança notas nem acessa dados de outros alunos.
> Notas só aparecem depois da publicação pelo professor.

---

## 5. Resumo rápido

| Perfil | 1ª conta | 2ª conta | Senha |
|---|---|---|---|
| Administrador | `admin` | `admin2` | `admin123` |
| Professor | `professor` | `professor2` | `prof123` |
| Aluno | `aluno` | `aluno2` | `aluno123` |

---

## 6. Dados acadêmicos criados junto com as contas

- **Período letivo:** 2026.1 (atual)
- **Curso:** ES01 — Engenharia de Software
- **Disciplinas:** IA101 (Inteligência Artificial Aplicada) e ES201 (Engenharia de Software)
- **Turmas:** ES-IA-20261-A e ES-ES-20261-A
- **Matrículas:** os dois alunos estão matriculados nas duas turmas
- **Atribuições acadêmicas:** cada professor recebe a sua turma com todas as permissões

O banco é criado apenas com o necessário para o sistema funcionar. Provas, notas,
materiais e submissões são gerados pelo uso do sistema.

---

## 7. Recriar o banco com estas contas

O seed roda automaticamente na inicialização apenas quando o banco ainda não
possui a conta `admin`. Para limpar tudo e recriar do zero:

```cmd
venv\Scripts\activate
python scripts\reset_db.py
```

O comando:

1. copia o banco atual para `storage/backups/`;
2. apaga todas as tabelas e os dados;
3. recria a estrutura e as contas desta página.

Para apenas garantir os dados iniciais sem apagar nada:

```cmd
python scripts\seed_db.py
```

---

## 8. Segurança

- As senhas são armazenadas com hash Argon2id — nunca em texto puro no banco.
- O login aceita usuário **ou** e-mail.
- Sessões expiram em 30 minutos (token de acesso) e podem ser renovadas por 7 dias.
- Toda operação relevante gera registro de auditoria (login, notas, provas, permissões).
- **Antes de publicar o sistema:** troque as senhas destas contas, defina uma
  `SECRET_KEY` forte e desative ou remova as contas de demonstração.
