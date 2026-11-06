const WORKSPACE_SCREENS = {
  '/admin/users.html': {
    title: 'Usuários',
    description: 'Contas cadastradas no EduGrade.',
    roles: ['admin'],
    endpoint: '/users?page=1&page_size=100',
  },
  '/admin/access-requests.html': {
    title: 'Chamados de acesso',
    description: 'Solicitações abertas de criação de conta.',
    roles: ['admin'],
    accessRequests: true,
  },
  '/admin/academic.html': {
    title: 'Cursos e disciplinas',
    description: 'Cursos e disciplinas cadastrados.',
    roles: ['admin'],
    teacherSubjects: true,
    subjectManagement: true,
    endpoints: [
      { title: 'Cursos', endpoint: '/academic/courses?page=1&page_size=100' },
      { title: 'Disciplinas', endpoint: '/academic/subjects?page=1&page_size=100' },
    ],
  },
  '/admin/classes.html': {
    title: 'Turmas',
    description: 'Turmas cadastradas no período letivo.',
    roles: ['admin'],
    endpoint: '/academic/classes?page=1&page_size=100',
    classManagement: true,
  },
  '/admin/periods.html': {
    title: 'Períodos letivos',
    description: 'Períodos letivos cadastrados.',
    roles: ['admin'],
    endpoint: '/academic/periods?page=1&page_size=100',
  },
  '/admin/audit.html': {
    title: 'Auditoria',
    description: 'Atividades recentes registradas no sistema.',
    roles: ['admin'],
    endpoint: '/audit/recent',
  },
  '/admin/quality.html': {
    title: 'Qualidade e cobertura de testes',
    description: 'Resultados reais da última execução de cobertura.',
    roles: ['admin'],
    quality: true,
  },
  '/admin/ai-status.html': {
    title: 'Status da inteligência artificial',
    description: 'Provedores e modelos de IA disponíveis.',
    roles: ['admin'],
    endpoints: [
      { title: 'Status', endpoint: '/ai/health' },
      { title: 'Modelos', endpoint: '/ai/models' },
    ],
  },
  '/admin/logs.html': {
    title: 'Erros do sistema',
    description: 'Erros registrados pela aplicação.',
    roles: ['admin'],
    endpoint: '/audit/system/errors',
  },
  '/admin/storage.html': {
    title: 'Armazenamento',
    description: 'Uso de disco das pastas de armazenamento e do banco de dados.',
    roles: ['admin'],
    storageUsage: true,
  },
  '/exams/list.html': {
    title: 'Banco de provas',
    description: 'Consulte as provas e acesse as opções disponíveis.',
    roles: ['admin', 'teacher'],
    endpoint: '/exams?page=1&page_size=100',
    examList: true,
  },
  '/exams/detail.html': {
    title: 'Detalhes da prova',
    description: 'Informações da prova selecionada.',
    roles: ['admin', 'teacher'],
    endpoint: '/exams?page=1&page_size=100',
    examDetail: true,
  },
  '/exams/edit.html': {
    title: 'Editar prova',
    description: 'Atualize os dados, as questões e os gabaritos de um rascunho.',
    roles: ['admin', 'teacher'],
    editExam: true,
  },
  '/professor/exams.html': {
    title: 'Minhas provas',
    description: 'Consulte suas provas e acesse as opções disponíveis.',
    roles: ['teacher'],
    endpoint: '/exams?page=1&page_size=100',
    examList: true,
  },
  '/aluno/exams.html': {
    title: 'Minhas provas',
    description: 'Consulte as informações das provas disponíveis.',
    roles: ['student'],
    endpoint: '/exams?page=1&page_size=100',
    examList: true,
  },
  '/exams/create.html': {
    title: 'Nova prova',
    description: 'Preencha os dados da prova para salvá-la como rascunho.',
    roles: ['admin', 'teacher'],
    createExam: true,
  },
  '/exams/print.html': {
    title: 'Impressão de provas',
    description: 'Geração de cópias e registro de impressão.',
    roles: ['admin', 'teacher'],
    printExams: true,
  },
  '/correcao-lote.html': {
    title: 'Correção em lote',
    description: 'Lotes de correção registrados no sistema.',
    roles: ['admin', 'teacher'],
    endpoint: '/batch-grading/?page=1&page_size=100',
  },
  '/professor/upload-exams.html': {
    title: 'Enviar provas para correção',
    description: 'Escolha uma prova publicada, identifique o aluno e envie a digitalização para correção.',
    roles: ['admin', 'teacher'],
    uploadExams: true,
  },
  '/ai/corrections.html': {
    title: 'Correções por IA',
    description: 'Revisões pendentes de correção.',
    roles: ['admin', 'teacher'],
    endpoint: '/ai/reviews/pending',
  },
  '/ai/review.html': {
    title: 'Revisões pendentes',
    description: 'Correções que aguardam revisão.',
    roles: ['admin', 'teacher'],
    endpoint: '/ai/reviews/pending',
  },
  '/professor/classes.html': {
    title: 'Minhas turmas',
    description: 'Turmas disponíveis no sistema.',
    roles: ['teacher'],
    endpoint: '/academic/classes/my?page=1&page_size=100',
  },
  '/professor/students.html': {
    title: 'Alunos das minhas turmas',
    description: 'Consulte e mantenha os dados acadêmicos de alunos nas turmas autorizadas.',
    roles: ['teacher'],
    teacherStudents: true,
  },
  '/professor/corrections.html': {
    title: 'Correções pendentes',
    description: 'Correções que aguardam revisão.',
    roles: ['teacher'],
    endpoint: '/ai/reviews/pending',
  },
  '/professor/grades.html': {
    title: 'Lançar notas',
    description: 'Registre, revise e publique notas das turmas em que possui autorização.',
    roles: ['teacher'],
    gradeManagement: true,
  },
  '/imports/students.html': {
    title: 'Importar alunos',
    description: 'Crie contas, perfis e matrículas em lote a partir de um arquivo CSV.',
    roles: ['admin', 'teacher'],
    importKind: 'students',
  },
  '/imports/grades.html': {
    title: 'Importar notas',
    description: 'Lance notas em lote a partir de um arquivo CSV.',
    roles: ['admin', 'teacher'],
    importKind: 'grades',
  },
  '/professor/class-detail.html': {
    title: 'Detalhes da turma',
    description: 'Turmas cadastradas no sistema.',
    roles: ['teacher'],
    endpoint: '/academic/classes/my?page=1&page_size=100',
    classDetail: true,
  },
  '/aluno/grades.html': {
    title: 'Minhas notas',
    description: 'Notas publicadas nas suas matrículas ativas.',
    roles: ['student'],
    endpoint: '/academic/grades/my?page=1&page_size=100',
  },
  '/aluno/attendance.html': {
    title: 'Minha frequência',
    description: 'Presenças e faltas registradas nas suas matrículas ativas.',
    roles: ['student'],
    myAttendance: true,
  },
  '/aluno/schedule.html': {
    title: 'Grade horária',
    description: 'Horários, salas e professores das suas turmas.',
    roles: ['student'],
    mySchedule: true,
  },
  '/profile.html': {
    title: 'Meu perfil',
    description: 'Dados da conta autenticada.',
    endpoint: '/auth/me',
  },
};

function showWorkspaceMessage(message, isError = false) {
  const element = document.getElementById('workspace-message');
  element.textContent = message;
  element.hidden = false;
  element.classList.toggle('workspace-error', isError);
}

function normalizeRows(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (data && typeof data === 'object') return [data];
  return [];
}

function renderWorkspaceTable(container, rows) {
  if (rows.length === 0) {
    container.textContent = 'Nenhum registro encontrado.';
    return;
  }

  const columns = Object.keys(rows[0]).filter(key => !key.endsWith('_id') && key !== 'id');
  if (columns.length === 0) {
    container.textContent = JSON.stringify(rows, null, 2);
    return;
  }

  const table = document.createElement('table');
  const head = document.createElement('thead');
  const headerRow = document.createElement('tr');
  for (const column of columns) {
    const cell = document.createElement('th');
    cell.textContent = column.replaceAll('_', ' ');
    headerRow.appendChild(cell);
  }
  head.appendChild(headerRow);
  table.appendChild(head);

  const body = document.createElement('tbody');
  for (const row of rows) {
    const tableRow = document.createElement('tr');
    for (const column of columns) {
      const cell = document.createElement('td');
      const value = row[column];
      cell.textContent = value === null || value === undefined
        ? '-'
        : typeof value === 'object'
          ? JSON.stringify(value)
          : String(value);
      tableRow.appendChild(cell);
    }
    body.appendChild(tableRow);
  }
  table.appendChild(body);
  container.replaceChildren(table);
}

function renderExamList(container, exams) {
  container.classList.add('workspace-exam-list');
  container.replaceChildren();

  if (exams.length === 0) {
    const emptyState = document.createElement('p');
    emptyState.className = 'workspace-empty-state';
    emptyState.textContent = 'Nenhuma prova foi encontrada.';
    container.appendChild(emptyState);
    return;
  }

  const statuses = {
    draft: 'Rascunho',
    in_edit: 'Em edição',
    awaiting_validation: 'Aguardando validação',
    published: 'Publicada',
    printed: 'Impressa',
    in_application: 'Em aplicação',
    awaiting_correction: 'Aguardando correção',
    in_correction: 'Em correção',
    awaiting_review: 'Aguardando revisão',
    finalized: 'Finalizada',
    cancelled: 'Cancelada',
  };
  const canPrint = State.hasRole('admin', 'teacher');

  for (const exam of exams) {
    const card = document.createElement('article');
    card.className = 'workspace-exam-card';

    const header = document.createElement('div');
    header.className = 'workspace-exam-card-header';
    const title = document.createElement('h2');
    title.className = 'workspace-exam-title';
    title.textContent = exam.title || 'Prova sem título';

    const status = document.createElement('span');
    status.className = `workspace-exam-status status-${exam.status || 'unknown'}`;
    status.textContent = statuses[exam.status] || 'Status não disponível';
    header.append(title, status);
    card.appendChild(header);

    const context = document.createElement('p');
    context.className = 'workspace-exam-context';
    context.textContent = [
      exam.subject?.name,
      exam.class_?.name,
    ].filter(Boolean).join(' · ') || 'Turma e disciplina não informadas';
    card.appendChild(context);

    const details = document.createElement('dl');
    details.className = 'workspace-exam-details';
    const values = [
      ['Questões', exam.questions_count ?? '—'],
      ['Valor total', exam.total_score != null
        ? `${Number(exam.total_score).toLocaleString('pt-BR')} pontos`
        : '—'],
      ['Duração', exam.duration_minutes ? `${exam.duration_minutes} min` : '—'],
      ['Data', exam.scheduled_date
        ? new Date(`${exam.scheduled_date}T00:00:00`).toLocaleDateString('pt-BR')
        : 'Não definida'],
    ];
    for (const [label, value] of values) {
      const item = document.createElement('div');
      const term = document.createElement('dt');
      term.textContent = label;
      const description = document.createElement('dd');
      description.textContent = String(value);
      item.append(term, description);
      details.appendChild(item);
    }
    card.appendChild(details);

    const actions = document.createElement('div');
    actions.className = 'workspace-exam-actions';
    if (canPrint && ['draft', 'in_edit'].includes(exam.status)) {
      const editLink = document.createElement('a');
      editLink.className = 'btn btn-secondary btn-sm';
      editLink.href = `/exams/edit.html?id=${encodeURIComponent(exam.id)}`;
      editLink.textContent = 'Editar';
      actions.appendChild(editLink);
    }
    if (canPrint && ['draft', 'in_edit', 'awaiting_validation'].includes(exam.status)) {
      const publishButton = document.createElement('button');
      publishButton.type = 'button';
      publishButton.className = 'btn btn-primary btn-sm';
      publishButton.textContent = 'Publicar';
      publishButton.addEventListener('click', async () => {
        publishButton.disabled = true;
        publishButton.textContent = 'Publicando...';
        try {
          const validation = await api.request(`/exams/${encodeURIComponent(exam.id)}/validate`);
          if (validation && validation.is_valid === false) {
            const details = Array.isArray(validation.differences) && validation.differences.length
              ? validation.differences.join(' ')
              : 'A soma das questões não confere com o valor total da prova.';
            showWorkspaceMessage(`Não foi possível publicar: ${details}`, true);
            return;
          }
          await api.request(`/exams/${encodeURIComponent(exam.id)}/publish`, { method: 'POST' });
          showWorkspaceMessage(
            `Prova "${exam.title}" publicada. Ela já está disponível para impressão e correção.`,
          );
          const refreshed = await api.request('/exams?page=1&page_size=100');
          renderExamList(container, normalizeRows(refreshed));
        } catch (error) {
          showWorkspaceMessage(error.message || 'Não foi possível publicar a prova.', true);
        } finally {
          publishButton.disabled = false;
          publishButton.textContent = 'Publicar';
        }
      });
      actions.appendChild(publishButton);
    }
    if (canPrint && exam.status === 'cancelled') {
      const restoreButton = document.createElement('button');
      restoreButton.type = 'button';
      restoreButton.className = 'btn btn-secondary btn-sm';
      restoreButton.textContent = 'Reativar';
      restoreButton.addEventListener('click', async () => {
        restoreButton.disabled = true;
        try {
          await api.request(`/exams/${encodeURIComponent(exam.id)}/restore`, { method: 'POST' });
          showWorkspaceMessage(
            `Prova "${exam.title}" reativada como rascunho. Use "Publicar" quando estiver pronta.`,
          );
          const refreshed = await api.request('/exams?page=1&page_size=100');
          renderExamList(container, normalizeRows(refreshed));
        } catch (error) {
          showWorkspaceMessage(error.message || 'Não foi possível reativar a prova.', true);
          restoreButton.disabled = false;
        }
      });
      actions.appendChild(restoreButton);
    }
    if (canPrint && ['published', 'printed'].includes(exam.status)) {
      const printLink = document.createElement('a');
      printLink.className = 'btn btn-secondary btn-sm';
      printLink.href = '/exams/print.html';
      printLink.textContent = 'Imprimir prova';
      actions.appendChild(printLink);
    }
    if (canPrint && exam.status !== 'cancelled') {
      const removeButton = document.createElement('button');
      removeButton.type = 'button';
      removeButton.className = 'btn btn-danger btn-sm';
      removeButton.textContent = 'Remover';
      removeButton.addEventListener('click', async () => {
        const action = ['published', 'printed'].includes(exam.status) ? 'cancelar' : 'remover';
        if (!window.confirm(`Deseja ${action} a prova "${exam.title}"? Ela deixará de aparecer nesta lista.`)) return;
        removeButton.disabled = true;
        try {
          await api.delete('/exams', exam.id);
          card.remove();
          if (!container.querySelector('.workspace-exam-card')) {
            renderExamList(container, []);
          }
          showWorkspaceMessage('A prova foi removida da lista.');
        } catch (error) {
          showWorkspaceMessage(error.message || 'Não foi possível remover a prova.', true);
          removeButton.disabled = false;
        }
      });
      actions.appendChild(removeButton);
    }
    if (actions.childElementCount) card.appendChild(actions);

    container.appendChild(card);
  }
}

function createUserCell(value) {
  const cell = document.createElement('td');
  cell.textContent = value === null || value === undefined ? '-' : String(value);
  return cell;
}

function renderUsersTable(container, users, profilesByUserId) {
  const table = document.createElement('table');
  table.innerHTML = `
    <thead>
      <tr>
        <th>Nome</th>
        <th>Usuário</th>
        <th>E-mail</th>
        <th>Perfil</th>
        <th>Status</th>
        <th>Ações</th>
      </tr>
    </thead>
  `;
  const body = document.createElement('tbody');
  const currentUserId = State.user?.id;

  for (const user of users) {
    const row = document.createElement('tr');
    row.append(
      createUserCell(user.full_name),
      createUserCell(user.username),
      createUserCell(user.email),
      createUserCell({ admin: 'Administrador', teacher: 'Professor', student: 'Aluno' }[user.role] || user.role),
    );

    const statusCell = document.createElement('td');
    const status = document.createElement('span');
    status.className = `workspace-user-status${user.is_active ? '' : ' inactive'}`;
    status.textContent = user.is_active ? 'Ativo' : 'Desativado';
    statusCell.appendChild(status);
    row.appendChild(statusCell);

    const actions = document.createElement('td');
    if (user.id === currentUserId) {
      const label = document.createElement('span');
      label.className = 'workspace-self-label';
      label.textContent = 'Conta atual';
      actions.appendChild(label);
    } else {
      const editButton = document.createElement('button');
      editButton.type = 'button';
      editButton.className = 'btn btn-secondary btn-sm';
      editButton.dataset.editUserId = user.id;
      editButton.textContent = 'Editar';
      actions.appendChild(editButton);

      const button = document.createElement('button');
      button.type = 'button';
      button.className = user.is_active ? 'btn btn-danger btn-sm' : 'btn btn-secondary btn-sm';
      button.dataset.userId = user.id;
      button.dataset.nextActive = String(!user.is_active);
      button.textContent = user.is_active ? 'Desativar' : 'Reativar';
      button.classList.add('workspace-user-status-action');
      actions.appendChild(button);
    }
    row.appendChild(actions);
    body.appendChild(row);
  }

  table.appendChild(body);
  container.replaceChildren(table);
}

async function loadAdminUsersScreen(container) {
  if (!State.hasRole('admin')) {
    window.location.replace(Auth.dashboardPath());
    return;
  }

  const form = document.createElement('form');
  form.className = 'workspace-form';
  form.id = 'create-user-form';
  form.innerHTML = `
    <div class="form-group">
      <label class="form-label" for="new-user-name">Nome completo</label>
      <input class="form-input" id="new-user-name" name="full_name" required minlength="2" maxlength="255">
    </div>
    <div class="form-group">
      <label class="form-label" for="new-user-username">Usuário</label>
      <input class="form-input" id="new-user-username" name="username" required minlength="3" maxlength="100" autocomplete="off">
    </div>
    <div class="form-group">
      <label class="form-label" for="new-user-email">E-mail</label>
      <input class="form-input" id="new-user-email" name="email" type="email" required>
    </div>
    <div class="form-group">
      <label class="form-label" for="new-user-password">Senha inicial</label>
      <input class="form-input" id="new-user-password" name="password" type="password" required minlength="8" maxlength="100" autocomplete="new-password">
    </div>
    <div class="form-group">
      <label class="form-label" for="new-user-role">Perfil</label>
      <select class="form-input" id="new-user-role" name="role" required>
        <option value="student">Aluno</option>
        <option value="teacher">Professor</option>
        <option value="admin">Administrador</option>
      </select>
    </div>
    <div class="form-group" id="student-profile-fields">
      <label class="form-label" for="new-student-ra">RA do aluno</label>
      <input class="form-input" id="new-student-ra" name="student_ra" maxlength="50">
      <label class="form-label" for="new-student-registration-number">Matrícula institucional</label>
      <input class="form-input" id="new-student-registration-number" name="student_registration_number" maxlength="50">
      <label class="form-label" for="new-student-class">Turma inicial (opcional)</label>
      <select class="form-input" id="new-student-class" name="student_class_id">
        <option value="">Sem turma inicial</option>
      </select>
    </div>
    <div class="form-group" id="teacher-profile-fields" hidden>
      <label class="form-label" for="new-teacher-employee-id">Identificação funcional</label>
      <input class="form-input" id="new-teacher-employee-id" name="teacher_employee_id" maxlength="50">
      <label class="form-label" for="new-teacher-department">Departamento</label>
      <input class="form-input" id="new-teacher-department" name="teacher_department" maxlength="100">
    </div>
    <div class="workspace-form-actions">
      <button class="btn btn-primary" type="submit">Criar usuário</button>
    </div>
  `;

  const message = document.createElement('div');
  message.className = 'workspace-message';
  message.id = 'users-message';
  message.hidden = true;
  const editForm = document.createElement('form');
  editForm.className = 'workspace-form';
  editForm.hidden = true;
  editForm.innerHTML = `
    <h2>Editar usuário e perfil acadêmico</h2>
    <div class="form-group">
      <label class="form-label" for="edit-user-name">Nome completo</label>
      <input class="form-input" id="edit-user-name" required minlength="2" maxlength="255">
    </div>
    <div class="form-group">
      <label class="form-label" for="edit-user-username">Usuário</label>
      <input class="form-input" id="edit-user-username" required minlength="3" maxlength="100">
    </div>
    <div class="form-group">
      <label class="form-label" for="edit-user-email">E-mail</label>
      <input class="form-input" id="edit-user-email" type="email" required>
    </div>
    <p id="edit-user-role"></p>
    <div class="form-group" id="edit-student-fields" hidden>
      <label class="form-label" for="edit-student-ra">RA</label>
      <input class="form-input" id="edit-student-ra" required maxlength="50">
      <label class="form-label" for="edit-student-registration">Matrícula institucional</label>
      <input class="form-input" id="edit-student-registration" maxlength="50">
      <label class="form-label" for="edit-student-status">Situação acadêmica</label>
      <input class="form-input" id="edit-student-status" required maxlength="50">
    </div>
    <div class="form-group" id="edit-teacher-fields" hidden>
      <label class="form-label" for="edit-teacher-employee-id">Identificação funcional</label>
      <input class="form-input" id="edit-teacher-employee-id" required maxlength="50">
      <label class="form-label" for="edit-teacher-department">Departamento</label>
      <input class="form-input" id="edit-teacher-department" maxlength="100">
      <label class="form-label" for="edit-teacher-status">Status do professor</label>
      <input class="form-input" id="edit-teacher-status" required maxlength="50">
    </div>
    <div class="workspace-form-actions">
      <button class="btn btn-primary" type="submit">Salvar alterações</button>
      <button class="btn btn-secondary" type="button" id="edit-user-cancel">Cancelar</button>
    </div>
  `;
  const tableContainer = document.createElement('div');
  tableContainer.className = 'workspace-table-wrap';
  container.replaceChildren(form, editForm, message, tableContainer);

  const showMessage = (text, isError = false) => {
    message.textContent = text;
    message.hidden = false;
    message.classList.toggle('workspace-error', isError);
  };

  const roleSelect = form.querySelector('#new-user-role');
  const studentFields = form.querySelector('#student-profile-fields');
  const studentRa = form.querySelector('#new-student-ra');
  const studentRegistrationNumber = form.querySelector('#new-student-registration-number');
  const teacherFields = form.querySelector('#teacher-profile-fields');
  const teacherEmployeeId = form.querySelector('#new-teacher-employee-id');
  const studentClass = form.querySelector('#new-student-class');
  let users = [];
  let profilesByUserId = new Map();
  let editingUser = null;
  const updateProfileFields = () => {
    studentFields.hidden = roleSelect.value !== 'student';
    studentRa.required = roleSelect.value === 'student';
    studentRegistrationNumber.required = roleSelect.value === 'student';
    teacherFields.hidden = roleSelect.value !== 'teacher';
    teacherEmployeeId.required = roleSelect.value === 'teacher';
  };
  const requestedRole = new URLSearchParams(window.location.search).get('role');
  if (['student', 'teacher', 'admin'].includes(requestedRole)) roleSelect.value = requestedRole;
  roleSelect.addEventListener('change', updateProfileFields);
  updateProfileFields();
  const classResponse = await api.request('/academic/classes?page=1&page_size=100');
  for (const classRecord of classResponse.items || []) {
    studentClass.add(new Option(`${classRecord.code} — ${classRecord.name}`, classRecord.id));
  }

  const refreshUsers = async () => {
    tableContainer.textContent = 'Carregando usuários...';
    const role = new URLSearchParams(window.location.search).get('role');
    const roleFilter = ['student', 'teacher', 'admin'].includes(role) ? `&role=${encodeURIComponent(role)}` : '';
    const [userResponse, studentResponse, teacherResponse] = await Promise.all([
      api.request(`/users?page=1&page_size=100&active_only=false${roleFilter}`),
      api.request('/users/students?page=1&page_size=100'),
      api.request('/users/teachers?page=1&page_size=100'),
    ]);
    users = userResponse.items || [];
    profilesByUserId = new Map([
      ...normalizeRows(studentResponse).map(profile => [profile.user_id, profile]),
      ...normalizeRows(teacherResponse).map(profile => [profile.user_id, profile]),
    ]);
    renderUsersTable(tableContainer, users, profilesByUserId);
  };

  const closeEditForm = () => {
    editingUser = null;
    editForm.reset();
    editForm.hidden = true;
  };
  editForm.querySelector('#edit-user-cancel').addEventListener('click', closeEditForm);
  editForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (!editingUser) return;
    const button = editForm.querySelector('button[type="submit"]');
    UI.setLoading(button, true);
    try {
      const user = {
        full_name: editForm.querySelector('#edit-user-name').value,
        username: editForm.querySelector('#edit-user-username').value,
        email: editForm.querySelector('#edit-user-email').value,
      };
      const profile = profilesByUserId.get(editingUser.id);
      const update = { user };
      if (editingUser.role === 'student' && profile) {
        update.student = {
          ra: editForm.querySelector('#edit-student-ra').value,
          registration_number: editForm.querySelector('#edit-student-registration').value || null,
          status: editForm.querySelector('#edit-student-status').value,
        };
      } else if (editingUser.role === 'teacher' && profile) {
        update.teacher = {
          employee_id: editForm.querySelector('#edit-teacher-employee-id').value,
          department: editForm.querySelector('#edit-teacher-department').value || null,
          status: editForm.querySelector('#edit-teacher-status').value,
        };
      }
      await api.request(`/users/${editingUser.id}/academic-profile`, {
        method: 'PATCH',
        body: update,
      });
      closeEditForm();
      showMessage('Usuário e perfil acadêmico atualizados com sucesso.');
      await refreshUsers();
    } catch (error) {
      showMessage(error.message || 'Não foi possível atualizar o perfil.', true);
    } finally {
      UI.setLoading(button, false);
    }
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    UI.setLoading(button, true);
    message.hidden = true;
    try {
      const data = Object.fromEntries(new FormData(form).entries());
      if (data.role === 'student' || data.role === 'teacher') {
        const user = {
          full_name: data.full_name,
          username: data.username,
          email: data.email,
          password: data.password,
          role: data.role,
        };
        const profile = data.role === 'student'
          ? {
              student_ra: data.student_ra,
              student_registration_number: data.student_registration_number,
              student_class_id: data.student_class_id || null,
            }
          : {
              teacher_employee_id: data.teacher_employee_id,
              teacher_department: data.teacher_department || null,
            };
        await api.create('/users/provision', { user, ...profile });
      } else {
        await api.create('/users', data);
      }
      form.reset();
      showMessage('Usuário criado com sucesso.');
      await refreshUsers();
    } catch (error) {
      showMessage(error.message || 'Não foi possível criar o usuário.', true);
    } finally {
      UI.setLoading(button, false);
    }
  });

  tableContainer.addEventListener('click', async event => {
    const editButton = event.target.closest('button[data-edit-user-id]');
    if (editButton) {
      editingUser = users.find(user => user.id === editButton.dataset.editUserId);
      if (!editingUser) return;
      const profile = profilesByUserId.get(editingUser.id);
      editForm.querySelector('#edit-user-name').value = editingUser.full_name;
      editForm.querySelector('#edit-user-username').value = editingUser.username;
      editForm.querySelector('#edit-user-email').value = editingUser.email;
      editForm.querySelector('#edit-user-role').textContent =
        `Perfil: ${{ admin: 'Administrador', teacher: 'Professor', student: 'Aluno' }[editingUser.role] || editingUser.role}`;
      const studentFields = editForm.querySelector('#edit-student-fields');
      const teacherFields = editForm.querySelector('#edit-teacher-fields');
      studentFields.hidden = editingUser.role !== 'student' || !profile;
      teacherFields.hidden = editingUser.role !== 'teacher' || !profile;
      editForm.querySelector('#edit-student-ra').required = !studentFields.hidden;
      editForm.querySelector('#edit-teacher-employee-id').required = !teacherFields.hidden;
      if (editingUser.role === 'student' && profile) {
        editForm.querySelector('#edit-student-ra').value = profile.ra;
        editForm.querySelector('#edit-student-registration').value = profile.registration_number || '';
        editForm.querySelector('#edit-student-status').value = profile.status;
      }
      if (editingUser.role === 'teacher' && profile) {
        editForm.querySelector('#edit-teacher-employee-id').value = profile.employee_id;
        editForm.querySelector('#edit-teacher-department').value = profile.department || '';
        editForm.querySelector('#edit-teacher-status').value = profile.status;
      }
      editForm.hidden = false;
      editForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    const button = event.target.closest('button[data-user-id]');
    if (!button) return;

    const nextActive = button.dataset.nextActive === 'true';
    const action = nextActive ? 'reativar' : 'desativar';
    if (!window.confirm(`Deseja ${action} este usuário?`)) return;

    button.disabled = true;
    message.hidden = true;
    try {
      if (nextActive) {
        await api.patch('/users', button.dataset.userId, { is_active: true });
      } else {
        await api.delete('/users', button.dataset.userId);
      }
      showMessage(`Usuário ${nextActive ? 'reativado' : 'desativado'} com sucesso.`);
      await refreshUsers();
    } catch (error) {
      showMessage(error.message || `Não foi possível ${action} o usuário.`, true);
      button.disabled = false;
    }
  });

  await refreshUsers();
}

function addRequestDetail(parent, label, value) {
  const paragraph = document.createElement('p');
  const title = document.createElement('strong');
  title.textContent = `${label}: `;
  paragraph.append(title, document.createTextNode(value || '-'));
  parent.appendChild(paragraph);
}

function createRequestAccountForm(request) {
  const form = document.createElement('form');
  form.className = 'workspace-form';
  form.innerHTML = `
    <div class="form-group">
      <label class="form-label">Usuário da conta</label>
      <input class="form-input" name="username" required minlength="3" maxlength="100">
    </div>
    <div class="form-group">
      <label class="form-label">Perfil aprovado</label>
      <select class="form-input" name="role" required>
        <option value="student">Aluno</option>
        <option value="teacher">Professor</option>
        <option value="admin">Administrador</option>
      </select>
    </div>
    <div class="workspace-form-actions">
      <button class="btn btn-primary" type="submit">Criar conta e enviar senha</button>
    </div>
  `;
  form.elements.username.value = request.username;
  form.elements.role.value = request.requested_role;
  return form;
}

async function loadAdminAccessRequestsScreen(container) {
  if (!State.hasRole('admin')) {
    window.location.replace(Auth.dashboardPath());
    return;
  }

  const message = document.createElement('div');
  message.className = 'workspace-message';
  message.hidden = true;
  const requestList = document.createElement('div');
  container.replaceChildren(message, requestList);

  const showMessage = (text, isError = false) => {
    message.textContent = text;
    message.hidden = false;
    message.classList.toggle('workspace-error', isError);
  };

  const refreshRequests = async () => {
    requestList.textContent = 'Carregando chamados...';
    const requests = await api.request('/access-requests?status=open');
    requestList.replaceChildren();

    if (requests.length === 0) {
      requestList.textContent = 'Não há chamados de acesso em aberto.';
      return;
    }

    for (const request of requests) {
      const card = document.createElement('article');
      card.className = 'card';
      card.style.marginBottom = 'var(--space-4)';
      const content = document.createElement('div');
      content.className = 'card-body';
      const heading = document.createElement('h2');
      heading.className = 'card-title';
      heading.textContent = request.full_name;
      content.appendChild(heading);
      addRequestDetail(content, 'E-mail', request.email);
      addRequestDetail(content, 'Usuário desejado', request.username);
      addRequestDetail(content, 'Telefone', request.phone);
      addRequestDetail(content, 'Perfil solicitado', {
        admin: 'Administrador',
        teacher: 'Professor',
        student: 'Aluno',
      }[request.requested_role] || request.requested_role);
      addRequestDetail(content, 'Motivo', request.justification);
      addRequestDetail(content, 'Recebido em', new Date(request.created_at).toLocaleString('pt-BR'));

      const accountForm = createRequestAccountForm(request);
      accountForm.addEventListener('submit', async event => {
        event.preventDefault();
        const button = accountForm.querySelector('button[type="submit"]');
        UI.setLoading(button, true);
        try {
          const accountData = Object.fromEntries(new FormData(accountForm).entries());
          await api.create(`/access-requests/${request.id}/create-account`, accountData);
          showMessage(`Conta criada. A senha temporária foi enviada para ${request.email}.`);
          await refreshRequests();
        } catch (error) {
          showMessage(error.message || 'Não foi possível criar a conta.', true);
          UI.setLoading(button, false);
        }
      });
      content.appendChild(accountForm);

      const rejectButton = document.createElement('button');
      rejectButton.type = 'button';
      rejectButton.className = 'btn btn-danger btn-sm';
      rejectButton.textContent = 'Recusar chamado';
      rejectButton.addEventListener('click', async () => {
        if (!window.confirm(`Deseja recusar o chamado de ${request.full_name}?`)) return;
        rejectButton.disabled = true;
        try {
          await api.create(`/access-requests/${request.id}/reject`, {});
          showMessage('Chamado recusado.');
          await refreshRequests();
        } catch (error) {
          showMessage(error.message || 'Não foi possível recusar o chamado.', true);
          rejectButton.disabled = false;
        }
      });
      content.appendChild(rejectButton);
      card.appendChild(content);
      requestList.appendChild(card);
    }
  };

  await refreshRequests();
}

function createExamQuestionCard(order) {
  const card = document.createElement('fieldset');
  card.className = 'workspace-question-card';
  card.dataset.questionCard = '';
  card.innerHTML = `
    <legend>Questão <span data-question-number>${order}</span></legend>
    <div class="workspace-question-fields">
      <div class="form-group">
        <label class="form-label">Tipo de questão</label>
        <select class="form-input" data-question-type required>
          <option value="multiple_choice">Múltipla escolha</option>
          <option value="essay">Dissertativa</option>
          <option value="short_answer">Resposta curta</option>
          <option value="calculation">Cálculo</option>
          <option value="multi_criteria">Múltiplos critérios</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Valor da questão</label>
        <input class="form-input" data-question-score type="number" min="0.01" max="999.99" step="0.01" value="10" required>
      </div>
      <div class="form-group workspace-question-statement">
        <label class="form-label">Enunciado</label>
        <textarea class="form-input" data-question-statement rows="3" required></textarea>
      </div>
      <div class="workspace-question-options" data-multiple-choice>
        <span class="form-label">Alternativas</span>
        <div class="workspace-question-alternatives">
          ${'ABCDEFGHIJ'.split('').map(letter => `
            <label class="workspace-alternative">
              <span>${letter}</span>
              <input class="form-input" data-alternative="${letter}" maxlength="500" ${letter === 'A' || letter === 'B' ? 'required' : ''}>
            </label>
          `).join('')}
        </div>
        <div class="form-group">
          <label class="form-label">Resposta correta</label>
          <select class="form-input" data-correct-answer required>
            <option value="">Selecione</option>
            ${'ABCDEFGHIJ'.split('').map(letter => `<option value="${letter}">${letter}</option>`).join('')}
          </select>
        </div>
      </div>
      <div class="workspace-question-expected" data-expected-answer-section hidden>
        <div class="form-group">
          <label class="form-label">Resposta esperada / gabarito</label>
          <textarea class="form-input" data-expected-answer rows="3"></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Palavras-chave (separadas por vírgula)</label>
          <input class="form-input" data-keywords>
        </div>
        <div class="form-group">
          <label class="form-label">Conceitos obrigatórios (separados por vírgula)</label>
          <input class="form-input" data-required-concepts>
        </div>
      </div>
      <div class="form-group workspace-question-accepted">
        <label class="form-label">Respostas alternativas aceitas (separadas por vírgula)</label>
        <input class="form-input" data-accepted-alternatives>
      </div>
      <div class="form-group workspace-question-justification">
        <label class="form-label">Critério / justificativa do gabarito</label>
        <textarea class="form-input" data-justification rows="2"></textarea>
      </div>
      <div class="workspace-form-actions">
        <button class="btn btn-danger btn-sm" data-remove-question type="button">Remover questão</button>
      </div>
    </div>
  `;

  const updateType = () => {
    const multipleChoice = card.querySelector('[data-question-type]').value === 'multiple_choice';
    card.querySelector('[data-multiple-choice]').hidden = !multipleChoice;
    card.querySelector('[data-expected-answer-section]').hidden = multipleChoice;
    card.querySelector('[data-correct-answer]').required = multipleChoice;
    card.querySelector('[data-expected-answer]').required = !multipleChoice;
    card.querySelectorAll('[data-multiple-choice] input, [data-multiple-choice] select')
      .forEach(element => { element.disabled = !multipleChoice; });
    card.querySelectorAll('[data-expected-answer-section] input, [data-expected-answer-section] textarea')
      .forEach(element => { element.disabled = multipleChoice; });
  };
  card.querySelector('[data-question-type]').addEventListener('change', updateType);
  updateType();
  return card;
}

function splitCommaSeparated(value) {
  return value.split(',').map(item => item.trim()).filter(Boolean);
}

async function loadCreateExamScreen(container, editExamId = null) {
  if (!State.hasRole('admin', 'teacher')) {
    window.location.replace(Auth.dashboardPath());
    return;
  }

  container.innerHTML = `
    <section class="workspace-question-list card" aria-labelledby="exam-pdf-import-title">
      <h2 id="exam-pdf-import-title">Criar prova a partir de PDFs</h2>
      <p>Envie a prova e, se tiver, o gabarito. A IA preencherá um rascunho para você revisar. Nada será publicado automaticamente.</p>
      <form id="exam-pdf-import-form" class="workspace-form">
        <div class="form-group">
          <label class="form-label" for="exam-pdf-file">Arquivo da prova (PDF)</label>
          <input class="form-input" id="exam-pdf-file" name="exam_file" type="file" accept=".pdf,application/pdf" required>
        </div>
        <div class="form-group">
          <label class="form-label" for="answer-key-pdf-file">Gabarito (PDF, opcional)</label>
          <input class="form-input" id="answer-key-pdf-file" name="answer_key_file" type="file" accept=".pdf,application/pdf">
        </div>
        <div class="workspace-form-actions">
          <button class="btn btn-secondary" type="submit">Ler PDFs e preencher rascunho</button>
        </div>
      </form>
      <div id="exam-import-status" class="workspace-message" role="status" hidden></div>
    </section>
    <form id="create-exam-form" class="workspace-form workspace-exam-form">
      <div class="form-group">
        <label class="form-label" for="exam-title">Título da prova</label>
        <input class="form-input" id="exam-title" name="title" required minlength="2" maxlength="255">
      </div>
      <div class="form-group">
        <label class="form-label" for="exam-class">Turma</label>
        <select class="form-input" id="exam-class" required>
          <option value="">Carregando turmas...</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Disciplina</label>
        <input class="form-input" id="exam-subject-name" readonly>
        <input type="hidden" name="subject_id">
      </div>
      <div class="form-group">
        <label class="form-label">Período letivo</label>
        <input class="form-input" id="exam-period-name" readonly>
        <input type="hidden" name="academic_period_id">
      </div>
      <div class="form-group">
        <label class="form-label" for="exam-total-score">Nota total</label>
        <input class="form-input" id="exam-total-score" name="total_score" type="number" min="0.01" step="0.01" value="10" readonly required>
        <small>Calculada pela soma dos valores das questões.</small>
      </div>
      <div class="form-group">
        <label class="form-label" for="exam-duration">Duração (minutos)</label>
        <input class="form-input" id="exam-duration" name="duration_minutes" type="number" min="10" max="480" value="120" required>
      </div>
      <div class="form-group">
        <label class="form-label" for="exam-date">Data agendada</label>
        <input class="form-input" id="exam-date" name="scheduled_date" type="date">
      </div>
      <div class="form-group">
        <label class="form-label" for="exam-description">Descrição</label>
        <textarea class="form-input" id="exam-description" name="description" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label" for="exam-instructions">Instruções</label>
        <textarea class="form-input" id="exam-instructions" name="instructions" rows="3"></textarea>
      </div>
      <fieldset class="workspace-print-options">
        <legend>Opções de impressão</legend>
        <div class="workspace-question-fields">
          <div class="form-group">
            <label class="form-label" for="exam-paper-size">Papel</label>
            <select class="form-input" id="exam-paper-size">
              <option value="A4">A4</option>
              <option value="LETTER">Carta (Letter)</option>
            </select>
          </div>
          <label class="workspace-checkbox">
            <input id="exam-identification" type="checkbox" checked>
            Incluir campos de identificação do aluno
          </label>
          <label class="workspace-checkbox">
            <input id="exam-qr-code" type="checkbox" checked>
            Incluir QR Code para identificar a cópia
          </label>
          <label class="workspace-checkbox">
            <input id="exam-page-numbers" type="checkbox" checked>
            Incluir numeração de páginas
          </label>
        </div>
      </fieldset>
      <section class="workspace-question-list">
        <div class="workspace-question-heading">
          <div>
            <h2>Questões e gabaritos</h2>
            <p>Informe o valor de cada questão e o gabarito que a IA usará na comparação.</p>
          </div>
          <button class="btn btn-secondary btn-sm" id="add-exam-question" type="button">Adicionar questão</button>
        </div>
        <div id="exam-questions"></div>
      </section>
      <div class="workspace-form-actions workspace-exam-actions">
        <button class="btn btn-primary" id="save-exam" type="submit">Salvar e publicar para correção por IA</button>
        <a class="btn btn-secondary" href="/exams/list.html">Voltar às provas</a>
      </div>
    </form>
    <section id="exam-published-actions"></section>
  `;

  const form = container.querySelector('#create-exam-form');
  const classSelect = form.querySelector('#exam-class');
  const subjectName = form.querySelector('#exam-subject-name');
  const periodName = form.querySelector('#exam-period-name');
  const subjectId = form.elements.subject_id;
  const periodId = form.elements.academic_period_id;
  const questionList = form.querySelector('#exam-questions');
  const totalScore = form.querySelector('#exam-total-score');
  const saveButton = form.querySelector('#save-exam');
  const importForm = container.querySelector('#exam-pdf-import-form');
  const importStatus = container.querySelector('#exam-import-status');
  if (editExamId) {
    importForm.hidden = true;
    saveButton.textContent = 'Salvar alterações';
  }
  let savedExam = null;
  let examVersion = null;
  let importedDraft = false;

  const updateQuestionTotals = () => {
    const cards = [...questionList.querySelectorAll('[data-question-card]')];
    const total = cards.reduce((sum, card) => (
      sum + (Number.parseFloat(card.querySelector('[data-question-score]').value) || 0)
    ), 0);
    totalScore.value = total.toFixed(2);
    cards.forEach((card, index) => {
      card.querySelector('[data-question-number]').textContent = String(index + 1);
      card.querySelector('[data-remove-question]').disabled = cards.length === 1;
    });
  };

  const addQuestion = () => {
    const card = createExamQuestionCard(questionList.children.length + 1);
    if (questionList.children.length > 0) card.querySelector('[data-question-score]').value = '1';
    card.querySelector('[data-question-score]').addEventListener('input', updateQuestionTotals);
    card.querySelector('[data-remove-question]').addEventListener('click', () => {
      card.remove();
      updateQuestionTotals();
    });
    questionList.appendChild(card);
    updateQuestionTotals();
    return card;
  };

  addQuestion();
  form.querySelector('#add-exam-question').addEventListener('click', addQuestion);

  importForm.addEventListener('submit', async event => {
    event.preventDefault();
    const button = importForm.querySelector('button[type="submit"]');
    const examFile = importForm.elements.exam_file.files[0];
    if (!examFile) return;
    const body = new FormData();
    body.append('exam_file', examFile);
    const answerKeyFile = importForm.elements.answer_key_file.files[0];
    if (answerKeyFile) body.append('answer_key_file', answerKeyFile);

    UI.setLoading(button, true);
    importStatus.hidden = false;
    importStatus.classList.remove('workspace-error');
    importStatus.textContent = 'Enviando o PDF da prova...';
    const operation = ProgressManager.start({
      title: `Importação de prova — ${examFile.name}`,
      subtitle: answerKeyFile ? `Prova + gabarito (${answerKeyFile.name})` : 'Prova em PDF',
    });
    try {
      const created = await api.uploadForm('/exams/import/pdf', body, {
        onProgress: ({ loaded, total, percent }) => {
          operation.setUpload({ loaded, total, percent });
          importStatus.textContent = `Enviando o PDF da prova... ${percent.toFixed(0)}%`;
        },
      });
      operation.setStep('PDF recebido. Analisando com a IA...');
      importStatus.textContent = 'PDF recebido. Analisando com a IA...';
      const job = await operation.followJob(created.job_id);
      const result = job.result;
      if (!result || !Array.isArray(result.questions)) {
        throw new Error('A análise não retornou questões. Tente novamente com outro PDF.');
      }

      form.elements.title.value = result.title;
      form.elements.description.value = result.description || '';
      form.elements.instructions.value = result.instructions || '';
      questionList.replaceChildren();
      for (const [index, question] of result.questions.entries()) {
        const card = addQuestion();
        const typeSelect = card.querySelector('[data-question-type]');
        const supportedTypes = ['multiple_choice', 'essay', 'short_answer', 'calculation', 'multi_criteria'];
        typeSelect.value = supportedTypes.includes(question.type) ? question.type : 'essay';
        typeSelect.dispatchEvent(new Event('change'));
        card.querySelector('[data-question-score]').value = question.score;
        card.querySelector('[data-question-statement]').value = question.statement || '';
        card.querySelector('[data-expected-answer]').value = question.expected_answer || '';
        card.querySelector('[data-keywords]').value = (question.keywords || []).join(', ');
        card.querySelector('[data-required-concepts]').value = (question.required_concepts || []).join(', ');
        card.querySelector('[data-accepted-alternatives]').value = (question.accepted_alternatives || []).join(', ');
        card.querySelector('[data-justification]').value = question.justification || '';

        const letters = 'ABCDEFGHIJ'.split('');
        const alternatives = question.alternatives || [];
        if (alternatives.length > letters.length) {
          if (!Array.isArray(result.review_notes)) result.review_notes = [];
          result.review_notes.push(
            'A questão ' + (index + 1) + ' tem mais alternativas do que o formulário comporta; confira o PDF.',
          );
        }
        alternatives.slice(0, letters.length).forEach((alternative, alternativeIndex) => {
          const input = card.querySelector(
            '[data-alternative="' + letters[alternativeIndex] + '"]',
          );
          input.value = alternative;
        });
        if (question.type === 'multiple_choice') {
          card.querySelector('[data-correct-answer]').value = question.correct_answer || '';
        } else if (!question.expected_answer && question.correct_answer) {
          card.querySelector('[data-expected-answer]').value = question.correct_answer;
        }
        if (question.answer_needs_review) {
          if (!Array.isArray(result.review_notes)) result.review_notes = [];
          result.review_notes.push('Confira o gabarito da questão ' + (index + 1) + '.');
        }
      }
      updateQuestionTotals();
      importedDraft = true;
      saveButton.textContent = 'Salvar rascunho para conferência';
      importStatus.textContent = [
        `Foram extraídas ${result.questions.length} questão(ões). Confira os enunciados, pontuações e gabaritos, selecione a turma e revise antes de salvar.`,
        ...(result.review_notes || []),
      ].join(' ');
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
      operation.fail(error.message || 'Não foi possível ler os PDFs.');
      importStatus.classList.add('workspace-error');
      importStatus.textContent = error.message || 'Não foi possível ler os PDFs.';
    } finally {
      UI.setLoading(button, false);
    }
  });

  try {
    // Professores veem apenas suas turmas; admins veem todas
    const isTeacher = State.hasRole('teacher') && !State.hasRole('admin');
    const classesEndpoint = isTeacher ? '/academic/classes/my?page=1&page_size=100' : '/academic/classes?page=1&page_size=100';
    const [classesResponse, periodsResponse] = await Promise.all([
      api.request(classesEndpoint),
      api.request('/academic/periods?page=1&page_size=100'),
    ]);
    const classes = classesResponse.items || [];
    const periods = new Map((periodsResponse.items || []).map(period => [period.id, period.name]));

    classSelect.replaceChildren(new Option('Selecione uma turma', ''));
    for (const classItem of classes) {
      const option = new Option(`${classItem.code} - ${classItem.name}`, classItem.id);
      option.dataset.subjectId = classItem.subject_id;
      option.dataset.subjectName = classItem.subject?.name || '';
      option.dataset.periodId = classItem.academic_period_id;
      option.dataset.periodName = periods.get(classItem.academic_period_id) || classItem.academic_period_id;
      classSelect.add(option);
    }

    classSelect.addEventListener('change', () => {
      const selected = classSelect.selectedOptions[0];
      subjectId.value = selected?.dataset.subjectId || '';
      subjectName.value = selected?.dataset.subjectName || '';
      periodId.value = selected?.dataset.periodId || '';
      periodName.value = selected?.dataset.periodName || '';
    });

    // Preseleciona a turma informada na URL (ex.: /exams/create.html?class_id=...)
    const preselectedClassId = new URLSearchParams(window.location.search).get('class_id');
    if (!editExamId && preselectedClassId) {
      const option = [...classSelect.options].find(item => item.value === preselectedClassId);
      if (option) {
        classSelect.value = preselectedClassId;
        classSelect.dispatchEvent(new Event('change'));
      }
    }

    if (classes.length === 0) {
      showWorkspaceMessage(
        isTeacher
          ? 'Você não possui turmas atribuídas. Peça ao administrador para vincular você a uma turma.'
          : 'Cadastre uma turma, disciplina e período letivo antes de criar uma prova.',
        true
      );
      classSelect.disabled = true;
      form.querySelector('#save-exam').disabled = true;
      return;
    }
  } catch (error) {
    showWorkspaceMessage(error.message || 'Não foi possível carregar turmas e períodos.', true);
    form.querySelector('#save-exam').disabled = true;
    return;
  }

  if (editExamId) {
    try {
      const exam = await api.request(`/exams/${encodeURIComponent(editExamId)}`);
      if (!['draft', 'in_edit'].includes(exam.status)) {
        throw new Error('Somente provas em rascunho podem ser editadas. Provas publicadas permanecem protegidas.');
      }
      savedExam = exam;
      form.elements.title.value = exam.title;
      form.elements.duration_minutes.value = exam.duration_minutes;
      form.elements.scheduled_date.value = exam.scheduled_date || '';
      form.elements.description.value = exam.description || '';
      form.elements.instructions.value = exam.instructions || '';
      form.querySelector('#exam-paper-size').value = exam.print_config?.page_size || 'A4';
      form.querySelector('#exam-identification').checked =
        exam.print_config?.include_student_identification ?? true;
      form.querySelector('#exam-qr-code').checked = exam.print_config?.include_qr_code ?? true;
      form.querySelector('#exam-page-numbers').checked = exam.print_config?.include_page_numbers ?? true;
      classSelect.value = exam.class_id;
      classSelect.dispatchEvent(new Event('change'));

      const questions = normalizeRows(
        await api.request(`/exams/${encodeURIComponent(editExamId)}/questions`),
      );
      questionList.replaceChildren();
      for (const [index, question] of questions.entries()) {
        const card = addQuestion();
        card.dataset.questionId = question.id;
        const typeSelect = card.querySelector('[data-question-type]');
        typeSelect.value = question.type;
        typeSelect.dispatchEvent(new Event('change'));
        card.querySelector('[data-question-score]').value = question.score;
        card.querySelector('[data-question-statement]').value = question.statement || '';
        card.querySelector('[data-expected-answer]').value = question.answer_key?.expected_answer || '';
        card.querySelector('[data-keywords]').value = (question.answer_key?.keywords || []).join(', ');
        card.querySelector('[data-required-concepts]').value =
          (question.answer_key?.required_concepts || []).join(', ');
        card.querySelector('[data-accepted-alternatives]').value =
          (question.answer_key?.accepted_alternatives || []).join(', ');
        card.querySelector('[data-justification]').value = question.answer_key?.justification || '';
        const alternatives = question.config?.alternatives || [];
        'ABCDEFGHIJ'.split('').forEach((letter, alternativeIndex) => {
          card.querySelector(`[data-alternative="${letter}"]`).value = alternatives[alternativeIndex] || '';
        });
        card.querySelector('[data-correct-answer]').value = question.answer_key?.correct_answer || '';
        if (index === 0) card.querySelector('[data-question-score]').dispatchEvent(new Event('input'));
      }
      updateQuestionTotals();
      saveButton.textContent = 'Salvar alterações';
    } catch (error) {
      form.remove();
      showWorkspaceMessage(error.message || 'Não foi possível carregar a prova para edição.', true);
      return;
    }
  }

  const generatePrintOptions = document.createElement('section');
  generatePrintOptions.className = 'workspace-published card';
  const renderPublishedActions = () => {
    const heading = document.createElement('h2');
    heading.textContent = `Prova publicada: ${savedExam.title}`;
    const description = document.createElement('p');
    description.textContent = 'A versão publicada guarda os enunciados e gabaritos para a correção por IA.';

    const keyButton = document.createElement('button');
    keyButton.className = 'btn btn-secondary';
    keyButton.type = 'button';
    keyButton.textContent = 'Baixar gabarito do professor';
    keyButton.addEventListener('click', async () => {
      keyButton.disabled = true;
      try {
        await api.download(
          `/exams/versions/${examVersion.version_id}/pdf-teacher`,
          `gabarito-${examVersion.version_id}.pdf`,
          { method: 'POST', body: {} },
        );
      } catch (error) {
        showWorkspaceMessage(error.message || 'Não foi possível gerar o gabarito.', true);
      } finally {
        keyButton.disabled = false;
      }
    });

    const copiesForm = document.createElement('form');
    copiesForm.className = 'workspace-form-actions';
    copiesForm.innerHTML = `
      <label class="workspace-copy-count">
        Quantidade de cópias
        <input class="form-input" name="count" type="number" min="1" max="20" value="1" required>
      </label>
      <button class="btn btn-primary" type="submit">Gerar prova do aluno em PDF</button>
    `;
    copiesForm.addEventListener('submit', async event => {
      event.preventDefault();
      const button = copiesForm.querySelector('button');
      UI.setLoading(button, true);
      try {
        const count = Number(copiesForm.elements.count.value);
        const copies = await api.create(
          `/exams/versions/${examVersion.version_id}/copies?count=${count}`,
          {},
        );
        for (const copy of copies) {
          await api.download(
            `/exams/copies/${copy.id}/pdf-student`,
            `prova-${copy.copy_identifier}.pdf`,
            { method: 'POST', body: {} },
          );
          uploadCopySelect.add(new Option(copy.copy_identifier, copy.id));
        }
        uploadForm.hidden = false;
        showWorkspaceMessage('PDFs das cópias gerados. Imprima e use o código de cópia ao enviar as respostas.');
      } catch (error) {
        showWorkspaceMessage(error.message || 'Não foi possível gerar as cópias.', true);
      } finally {
        UI.setLoading(button, false);
      }
    });

    const files = document.createElement('div');
    files.className = 'workspace-print-files';
    files.dataset.printFiles = '';

    const uploadHeading = document.createElement('h3');
    uploadHeading.textContent = 'Enviar prova respondida para processamento';
    const uploadDescription = document.createElement('p');
    uploadDescription.textContent = 'Selecione a cópia correspondente e envie imagens ou PDF digitalizado. A submissão ficará vinculada ao gabarito publicado.';
    uploadForm.hidden = true;

    generatePrintOptions.replaceChildren(
      heading,
      description,
      keyButton,
      copiesForm,
      files,
      uploadHeading,
      uploadDescription,
      uploadForm,
    );
    container.querySelector('#exam-published-actions').replaceChildren(generatePrintOptions);
  };

  const uploadForm = document.createElement('form');
  uploadForm.className = 'workspace-form';
  uploadForm.innerHTML = `
    <div class="form-group">
      <label class="form-label">Cópia identificada</label>
      <select class="form-input" name="copy_id" required>
        <option value="">Gere uma cópia antes de enviar respostas</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Prova respondida (PDF ou imagem)</label>
      <input class="form-input" name="files" type="file" accept=".pdf,.png,.jpg,.jpeg" multiple required>
    </div>
    <div class="workspace-form-actions">
      <button class="btn btn-secondary" type="submit">Enviar prova respondida</button>
    </div>
  `;
  const uploadCopySelect = uploadForm.elements.copy_id;
  uploadForm.addEventListener('submit', async event => {
    event.preventDefault();
    const button = uploadForm.querySelector('button[type="submit"]');
    UI.setLoading(button, true);
    const body = new FormData();
    body.append('copy_id', uploadCopySelect.value);
    for (const file of uploadForm.elements.files.files) {
      body.append('files', file);
    }

    try {
      const response = await fetch(`${api.baseURL}/exams/submissions`, {
        method: 'POST',
        headers: api.accessToken ? { Authorization: `Bearer ${api.accessToken}` } : {},
        body,
      });
      const result = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(result.detail)
          ? result.detail.map(item => item.msg).join('; ')
          : result.detail || result.message;
        throw new Error(detail || 'Não foi possível enviar a prova.');
      }
      showWorkspaceMessage(
        `Prova respondida salva. Submissão ${result.id} vinculada aos gabaritos da versão publicada.`,
      );
      uploadForm.reset();
      const correctionButton = document.createElement('button');
      correctionButton.className = 'btn btn-primary';
      correctionButton.type = 'button';
      correctionButton.textContent = 'Processar OCR e comparar com o gabarito';
      correctionButton.addEventListener('click', async () => {
        let comparisonCompleted = false;
        UI.setLoading(correctionButton, true);
        try {
          const ocrResult = await api.create(`/exams/submissions/${result.id}/process-ocr`, {});
          if (ocrResult.answers_extracted === 0) {
            throw new Error(
              'O OCR não identificou respostas numeradas nesta prova. Confira a legibilidade e a numeração das questões.',
            );
          }
          const correction = await api.create('/ai/batch-correct', {
            submission_id: result.id,
          });
          if (correction.total_processed === 0 && correction.failed === 0) {
            throw new Error(
              'O OCR não encontrou respostas legíveis. Confira a digitalização e tente novamente.',
            );
          }
          comparisonCompleted = correction.total_processed > 0;
          showWorkspaceMessage(
            `Comparação concluída: ${correction.total_processed} questão(ões), ${correction.requires_review_count} aguardando revisão, ${correction.skipped} sem resposta reconhecida e ${correction.failed} falha(s).`,
          );
        } catch (error) {
          showWorkspaceMessage(error.message || 'Não foi possível comparar a prova com o gabarito.', true);
        } finally {
          UI.setLoading(correctionButton, false);
          if (comparisonCompleted) {
            correctionButton.disabled = true;
            correctionButton.textContent = 'Comparação concluída';
          }
        }
      });
      uploadForm.appendChild(correctionButton);
    } catch (error) {
      showWorkspaceMessage(error.message || 'Não foi possível enviar a prova respondida.', true);
    } finally {
      UI.setLoading(button, false);
    }
  });

  const collectExamData = () => {
    const questions = [...questionList.querySelectorAll('[data-question-card]')].map(card => {
      const type = card.querySelector('[data-question-type]').value;
      const alternatives = 'ABCDEFGHIJ'.split('')
        .map(letter => card.querySelector(`[data-alternative="${letter}"]`).value.trim())
        .filter(Boolean);
      const expectedAnswer = card.querySelector('[data-expected-answer]').value.trim();
      const keywords = splitCommaSeparated(card.querySelector('[data-keywords]').value);
      const requiredConcepts = splitCommaSeparated(card.querySelector('[data-required-concepts]').value);
      const acceptedAlternatives = splitCommaSeparated(
        card.querySelector('[data-accepted-alternatives]').value,
      );

      return {
        ...(editExamId ? { id: card.dataset.questionId || null } : {}),
        type,
        statement: card.querySelector('[data-question-statement]').value.trim(),
        score: card.querySelector('[data-question-score]').value,
        config: type === 'multiple_choice'
          ? { alternatives }
          : { answer_lines: type === 'essay' ? 12 : 8 },
        correct_answer: type === 'multiple_choice'
          ? card.querySelector('[data-correct-answer]').value
          : null,
        expected_answer: type === 'multiple_choice' ? null : expectedAnswer,
        accepted_alternatives: acceptedAlternatives,
        keywords,
        required_concepts: requiredConcepts,
        justification: card.querySelector('[data-justification]').value.trim() || null,
      };
    });

    for (const [index, question] of questions.entries()) {
      if (question.type === 'multiple_choice' && !question.correct_answer) {
        showWorkspaceMessage(`Confira e selecione o gabarito da questão ${index + 1}.`, true);
        return null;
      }
      if (question.type !== 'multiple_choice'
        && !question.expected_answer
        && question.keywords.length === 0
        && question.required_concepts.length === 0) {
        showWorkspaceMessage(`Preencha o gabarito da questão ${index + 1}.`, true);
        return null;
      }
    }

    const examData = Object.fromEntries(new FormData(form).entries());
    examData.class_id = classSelect.value;
    examData.total_score = totalScore.value;
    examData.duration_minutes = Number(examData.duration_minutes);
    examData.print_config = {
      page_size: form.querySelector('#exam-paper-size').value,
      include_student_identification: form.querySelector('#exam-identification').checked,
      include_qr_code: form.querySelector('#exam-qr-code').checked,
      include_page_numbers: form.querySelector('#exam-page-numbers').checked,
    };
    examData.questions = questions;
    for (const key of ['description', 'instructions', 'scheduled_date']) {
      if (!examData[key]) examData[key] = null;
    }
    return examData;
  };

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (editExamId) {
      UI.setLoading(saveButton, true);
      try {
        const examData = collectExamData();
        if (!examData) return;
        await api.request(`/exams/${encodeURIComponent(editExamId)}/complete`, {
          method: 'PATCH',
          body: examData,
        });
        showWorkspaceMessage('As alterações da prova foram salvas.');
      } catch (error) {
        showWorkspaceMessage(error.message || 'Não foi possível salvar as alterações.', true);
      } finally {
        UI.setLoading(saveButton, false);
      }
      return;
    }

    if (!savedExam) {
      const examData = collectExamData();
      if (!examData) return;
      const questions = examData.questions;
      UI.setLoading(saveButton, true);
      try {
        savedExam = await api.create('/exams/complete', examData);
        importForm.querySelectorAll('input, button').forEach(element => {
          element.disabled = true;
        });
        if (importedDraft) {
          form.querySelectorAll('input, select, textarea, button').forEach(element => {
            if (element.id !== 'save-exam') element.disabled = true;
          });
          saveButton.textContent = 'Rascunho salvo para conferência';
          saveButton.disabled = true;
          showWorkspaceMessage(
            `Rascunho "${savedExam.title}" salvo com ${questions.length} questão(ões). Revise a prova antes de publicá-la.`,
          );
          UI.setLoading(saveButton, false);
          return;
        }
        // Auto-publica após salvar (para provas não importadas de PDF)
        form.querySelectorAll('input, select, textarea, button').forEach(element => {
          if (element.id !== 'save-exam') element.disabled = true;
        });
        saveButton.textContent = 'Publicando...';
        showWorkspaceMessage(
          `Prova salva com ${questions.length} questão(ões) e gabaritos. Publicando versão para impressão e correção.`,
        );
        // Continua para o bloco de publicação abaixo
      } catch (error) {
        showWorkspaceMessage(error.message || 'Não foi possível salvar a prova e os gabaritos.', true);
        UI.setLoading(saveButton, false);
        return;
      }
    }

    // Publica a prova (tanto para auto-publicação quanto para re-tentativa)
    try {
      UI.setLoading(saveButton, true);
      examVersion = await api.create(`/exams/${savedExam.id}/publish`, {});
      showWorkspaceMessage(
        `Prova "${savedExam.title}" salva e publicada. Gabaritos prontos para a correção por IA.`,
      );
      saveButton.textContent = 'Prova publicada';
      saveButton.disabled = true;
      renderPublishedActions();
    } catch (error) {
      saveButton.disabled = false;
      saveButton.textContent = 'Prova salva. Tentar publicar novamente';
      showWorkspaceMessage(error.message || 'A prova foi salva, mas não foi possível publicá-la.', true);
    } finally {
      UI.setLoading(saveButton, false);
      if (examVersion) saveButton.disabled = true;
    }
  });
}

async function loadUploadExamsScreen(container) {
  container.replaceChildren();
  const form = document.createElement('form');
  form.className = 'workspace-form workspace-exam-form';
  form.innerHTML = `
    <div class="form-group">
      <label class="form-label" for="upload-exam-version">Prova publicada</label>
      <select class="form-input" id="upload-exam-version" name="version_id" required>
        <option value="">Carregando provas...</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label" for="upload-exam-student">Aluno</label>
      <select class="form-input" id="upload-exam-student" name="student_id" required disabled>
        <option value="">Selecione primeiro uma prova</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label" for="upload-exam-files">Prova respondida (PDF ou imagem)</label>
      <input class="form-input" id="upload-exam-files" name="files" type="file"
        accept=".pdf,.png,.jpg,.jpeg" multiple required>
    </div>
    <div class="workspace-form-actions">
      <button class="btn btn-primary" type="submit" disabled>Enviar e corrigir</button>
    </div>
  `;
  const versionSelect = form.elements.version_id;
  const studentSelect = form.elements.student_id;
  const submitButton = form.querySelector('button[type="submit"]');
  const versionsById = new Map();
  let students = [];

  const setOptions = (select, placeholder, options) => {
    select.replaceChildren(new Option(placeholder, ''));
    for (const option of options) {
      select.add(new Option(option.label, option.value));
    }
  };

  form.addEventListener('change', async event => {
    if (event.target === studentSelect) {
      submitButton.disabled = !studentSelect.value;
      return;
    }
    if (event.target !== versionSelect) return;
    const selectedVersion = versionsById.get(versionSelect.value);
    students = [];
    studentSelect.disabled = true;
    submitButton.disabled = true;
    setOptions(studentSelect, selectedVersion ? 'Carregando alunos...' : 'Selecione primeiro uma prova', []);
    if (!selectedVersion) return;

    try {
      const result = await api.request(
        `/users/students?class_id=${encodeURIComponent(selectedVersion.class_id)}&page=1&page_size=100`,
      );
      students = normalizeRows(result).filter(student => student.status === 'active');
      setOptions(
        studentSelect,
        students.length ? 'Selecione o aluno' : 'Nenhum aluno ativo nesta turma',
        students.map(student => ({
          value: student.id,
          label: `${student.user.full_name} (RA: ${student.ra})`,
        })),
      );
      studentSelect.disabled = students.length === 0;
      submitButton.disabled = true;
    } catch (error) {
      setOptions(studentSelect, 'Não foi possível carregar os alunos', []);
      showWorkspaceMessage(error.message || 'Não foi possível carregar os alunos da turma.', true);
    }
  });

  // Arquivos enviados com sucesso ficam guardados para que uma nova tentativa
  // não reenvie o que já foi recebido pelo servidor.
  const uploadedByFile = new Map();

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const files = [...form.elements.files.files];
    if (!files.length) {
      showWorkspaceMessage('Selecione pelo menos um PDF ou uma imagem.', true);
      return;
    }
    const selectedVersion = versionsById.get(versionSelect.value);
    const selectedStudent = students.find(student => student.id === studentSelect.value);
    if (!selectedVersion || !selectedStudent) {
      showWorkspaceMessage('Selecione uma prova publicada e um aluno da turma.', true);
      return;
    }

    UI.setLoading(submitButton, true);
    const studentLabel = selectedStudent.user?.full_name || selectedStudent.ra || 'aluno';
    const operation = ProgressManager.start({
      title: `Prova de ${studentLabel}`,
      subtitle: `${files.length} arquivo(s) — ${selectedVersion.title}`,
    });
    const transfer = new Map();
    const fileIds = files.map((file, index) => `f${index}-${file.name}`);
    files.forEach((file, index) => operation.trackFile(fileIds[index], { name: file.name, size: file.size }));

    const updateAggregate = () => {
      let loaded = 0;
      let total = 0;
      for (const entry of transfer.values()) {
        loaded += entry.loaded;
        total += entry.total;
      }
      if (total > 0) operation.setUpload({ loaded, total, percent: (loaded / total) * 100 });
    };

    let submission = null;
    try {
      const copies = await api.create(
        `/exams/versions/${encodeURIComponent(selectedVersion.version_id)}/copies?count=1&student_ids=${encodeURIComponent(selectedStudent.id)}`,
        {},
      );
      if (!Array.isArray(copies) || !copies[0]?.id) {
        throw new Error('Não foi possível criar a cópia vinculada ao aluno.');
      }
      const copyId = copies[0].id;

      const uploaded = [];
      let failedFiles = 0;
      operation.setStep('Enviando arquivos da prova');
      for (const [index, file] of files.entries()) {
        const fileId = fileIds[index];
        const done = uploadedByFile.get(file);
        if (done) {
          uploaded.push(done);
          operation.setFileState(fileId, 'done', 100);
          continue;
        }
        operation.setFileState(fileId, 'uploading', 0);
        transfer.set(fileId, { loaded: 0, total: file.size });
        const body = new FormData();
        body.append('copy_id', copyId);
        body.append('file', file);
        try {
          const result = await api.uploadForm('/exams/uploads', body, {
            onProgress: ({ loaded, total }) => {
              transfer.set(fileId, { loaded, total });
              operation.setFileState(fileId, 'uploading', (loaded / total) * 100);
              updateAggregate();
            },
          });
          uploadedByFile.set(file, result);
          uploaded.push(result);
          transfer.set(fileId, { loaded: file.size, total: file.size });
          operation.setFileState(fileId, 'done', 100);
          updateAggregate();
        } catch (error) {
          failedFiles += 1;
          operation.setFileState(fileId, 'failed', null, error.message);
        }
      }

      if (failedFiles > 0) {
        throw new Error(
          `${failedFiles} arquivo(s) falharam. Corrija o problema e envie novamente: apenas os arquivos com erro serão reenviados.`,
        );
      }

      operation.setStep('Montando a submissão');
      submission = await api.request('/exams/submissions/from-uploads', {
        method: 'POST',
        body: { copy_id: copyId, uploads: uploaded, student_id: selectedStudent.id },
      });

      operation.setStep('Iniciando leitura e correção');
      const created = await api.request(
        `/exams/submissions/${encodeURIComponent(submission.id)}/correction-jobs`,
        { method: 'POST' },
      );
      const job = await operation.followJob(created.job_id);
      const summary = job.result || {};
      showWorkspaceMessage(
        `Correção de ${studentLabel} concluída: ${summary.corrected || 0} questão(ões) corrigida(s), `
        + `${summary.requires_review || 0} aguardando revisão do professor`
        + (summary.failed ? `, ${summary.failed} com falha.` : '.'),
      );
      uploadedByFile.clear();
      form.reset();
      studentSelect.disabled = true;
      submitButton.disabled = true;
    } catch (error) {
      const message = error.message || 'Não foi possível enviar e corrigir a prova.';
      if (error.cancelled) {
        operation.cancel();
      } else {
        operation.fail(message);
      }
      showWorkspaceMessage(
        submission
          ? `${message} A submissão ${submission.id} foi salva; confira o status antes de reenviar para evitar duplicidade.`
          : message,
        true,
      );
      // Mantém os arquivos selecionados para permitir reenviar apenas os que falharam.
      submitButton.disabled = false;
    } finally {
      UI.setLoading(submitButton, false);
      if (submission) submitButton.disabled = true;
    }
  });

  container.appendChild(form);
  try {
    const versions = normalizeRows(await api.request('/exams/versions/active'));
    for (const version of versions) versionsById.set(version.version_id, version);
    setOptions(
      versionSelect,
      versions.length ? 'Selecione uma prova publicada' : 'Nenhuma prova publicada disponível',
      versions.map(version => ({
        value: version.version_id,
        label: `${version.title} — ${version.class_name} / ${version.subject_name} (v${version.version_number})`,
      })),
    );
    versionSelect.disabled = versions.length === 0;
    submitButton.disabled = true;
    if (!versions.length) {
      showWorkspaceMessage('Publique uma prova antes de enviar respostas para correção.');
    }
  } catch (error) {
    form.remove();
    showWorkspaceMessage(error.message || 'Não foi possível carregar as provas publicadas.', true);
  }
}

async function loadPrintExamsScreen(container) {
  if (!State.hasRole('admin', 'teacher')) {
    window.location.replace(Auth.dashboardPath());
    return;
  }

  const form = document.createElement('form');
  form.className = 'workspace-form';
  form.innerHTML = `
    <div class="form-group">
      <label class="form-label" for="print-exam-version">Prova publicada</label>
      <select class="form-input" id="print-exam-version" name="version_id" required>
        <option value="">Carregando provas publicadas...</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label" for="print-exam-count">Quantidade de cópias</label>
      <input class="form-input" id="print-exam-count" name="count" type="number" min="1" max="500" step="1" value="1" required>
    </div>
    <div class="workspace-form-actions">
      <button class="btn btn-primary" type="submit">Gerar cópias em PDF</button>
    </div>
  `;

  const message = document.createElement('div');
  message.className = 'workspace-message';
  message.hidden = true;

  const resultList = document.createElement('div');
  resultList.className = 'workspace-table-wrap';
  container.replaceChildren(form, message, resultList);

  const showMessage = (text, isError = false) => {
    message.textContent = text;
    message.hidden = false;
    message.classList.toggle('workspace-error', isError);
  };

  const versionSelect = form.elements.version_id;
  const countInput = form.elements.count;
  const submitButton = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async event => {
    event.preventDefault();

    const versionId = versionSelect.value;
    const quantity = Number(countInput.value);
    if (!versionId) {
      showMessage('Selecione uma prova publicada antes de gerar cópias.', true);
      return;
    }
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 500) {
      showMessage('Informe uma quantidade válida entre 1 e 500 cópias.', true);
      return;
    }

    const selectedVersion = versions.find(item => item.version_id === versionId);
    if (!selectedVersion) {
      showMessage('Essa versão da prova não está disponível para impressão.', true);
      return;
    }

    UI.setLoading(submitButton, true);
    try {
      showMessage('Gerando as cópias da prova...');
      const copies = await api.request(`/exams/versions/${encodeURIComponent(versionId)}/copies?count=${quantity}`, {
        method: 'POST',
        body: {},
      });

      if (!Array.isArray(copies) || copies.length === 0) {
        throw new Error('Não foi possível gerar as cópias da prova.');
      }

      resultList.replaceChildren();
      const list = document.createElement('div');
      list.className = 'workspace-print-list';

      const teacherPdfButton = document.createElement('button');
      teacherPdfButton.type = 'button';
      teacherPdfButton.className = 'btn btn-secondary';
      teacherPdfButton.textContent = 'Baixar gabarito do professor';
      teacherPdfButton.addEventListener('click', async () => {
        await api.download(
          `/exams/versions/${encodeURIComponent(versionId)}/pdf-teacher`,
          `gabarito-${selectedVersion.title.toLowerCase().replace(/[^a-z0-9]+/g, '-') || 'prova'}.pdf`,
          { method: 'POST', body: {} },
        );
      });
      list.appendChild(teacherPdfButton);

      for (const copy of copies) {
        const item = document.createElement('div');
        item.className = 'workspace-print-item';
        const link = document.createElement('button');
        link.type = 'button';
        link.className = 'btn btn-secondary btn-sm';
        link.textContent = `Baixar ${copy.copy_identifier}.pdf`;
        link.addEventListener('click', async () => {
          await api.download(
            `/exams/copies/${encodeURIComponent(copy.id)}/pdf-student`,
            `prova-${copy.copy_identifier}.pdf`,
            { method: 'POST', body: {} },
          );
        });
        item.appendChild(link);
        list.appendChild(item);
      }

      resultList.appendChild(list);
      showMessage(`Foram geradas ${copies.length} cópia(s) da prova ${selectedVersion.title}.`);
    } catch (error) {
      showMessage(error.message || 'Não foi possível gerar as cópias da prova.', true);
    } finally {
      UI.setLoading(submitButton, false);
    }
  });

  let versions = [];
  try {
    versions = await api.request('/exams/versions/active');
    versionSelect.replaceChildren();
    if (!versions.length) {
      versionSelect.disabled = true;
      countInput.disabled = true;
      submitButton.disabled = true;
      showMessage('Ainda não há provas publicadas para impressão. Publique uma prova antes de gerar cópias.', true);
      return;
    }

    for (const version of versions) {
      const option = document.createElement('option');
      option.value = version.version_id;
      option.textContent = `${version.title} — ${version.class_name} / ${version.subject_name} (v${version.version_number})`;
      versionSelect.appendChild(option);
    }
    versionSelect.value = versions[0].version_id;
  } catch (error) {
    form.remove();
    showWorkspaceMessage(error.message || 'Não foi possível carregar as provas publicadas.', true);
  }
}

async function loadQualityScreen(container) {
  container.replaceChildren();

  const actions = document.createElement('section');
  actions.className = 'card';
  actions.innerHTML = `
    <h2 class="card-title">Gerar relatório de cobertura</h2>
    <p>Executa a suíte completa (pytest + pytest-cov) no servidor em segundo plano e publica o
    relatório HTML detalhado. Acompanhe as etapas no painel de progresso; pode minimizar.</p>
    <pre class="workspace-command">python -m pytest tests -q --cov=backend/app \\
  --cov-report=html:reports/coverage \\
  --cov-report=xml:reports/coverage.xml \\
  --junitxml=reports/junit.xml --cov-fail-under=80</pre>
    <div class="workspace-form-actions">
      <button class="btn btn-primary" type="button" id="run-quality">Executar testes agora</button>
      <a class="btn btn-secondary" href="/api/v1/quality/report/index.html" target="_blank" rel="noopener">Abrir último relatório HTML</a>
    </div>
  `;
  container.appendChild(actions);

  const runButton = actions.querySelector('#run-quality');
  runButton.addEventListener('click', async () => {
    runButton.disabled = true;
    const operation = ProgressManager.start({
      title: 'Testes e cobertura',
      subtitle: 'pytest + pytest-cov',
      cancelable: false,
    });
    try {
      const created = await api.request('/quality/run', { method: 'POST' });
      operation.setStep('Executando a suíte de testes...');
      const job = await operation.followJob(created.job_id);
      showWorkspaceMessage(job.message || 'Relatório de cobertura atualizado.');
      await loadQualityScreen(container);
    } catch (error) {
      operation.fail(error.message || 'Não foi possível executar os testes.');
      showWorkspaceMessage(
        error.status === 409
          ? 'Já existe uma execução em andamento. Aguarde a conclusão.'
          : error.message || 'Não foi possível executar os testes.',
        true,
      );
      runButton.disabled = false;
    }
  });

  const summary = await api.request('/quality/summary');
  const history = Array.isArray(summary.history) ? summary.history : [];
  if (!summary.available && history.length === 0) {
    showWorkspaceMessage(summary.message || 'Dados de qualidade indisponíveis.', true);
    return;
  }

  if (summary.available) {
    const card = document.createElement('section');
    card.className = 'card';
    const title = document.createElement('h2');
    title.className = 'card-title';
    title.textContent = `Cobertura: ${summary.coverage_percent}%`;
    const details = document.createElement('p');
    details.textContent = `${summary.lines_covered} de ${summary.lines_valid} linhas cobertas. Última execução: ${new Date(summary.generated_at).toLocaleString()}.`;
    card.append(title, details);
    if (summary.tests) {
      const tests = document.createElement('p');
      tests.textContent = `Testes: ${summary.tests.total} total, ${summary.tests.passed} aprovados, ${summary.tests.failed} reprovados, ${summary.tests.skipped} ignorados.`;
      card.appendChild(tests);
    } else {
      const tests = document.createElement('p');
      tests.textContent = 'Contagem de testes indisponível para esta execução.';
      card.appendChild(tests);
    }
    if (summary.html_report_available) {
      const link = document.createElement('a');
      link.className = 'btn btn-secondary';
      link.href = '/api/v1/quality/report/index.html';
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = 'Abrir relatório HTML detalhado';
      card.appendChild(link);
    }
    container.appendChild(card);
  }

  if (history.length > 0) {
    const historyCard = document.createElement('section');
    historyCard.className = 'card';
    const title = document.createElement('h2');
    title.className = 'card-title';
    title.textContent = 'Histórico das últimas execuções';
    const entries = document.createElement('ul');
    for (const run of history) {
      const item = document.createElement('li');
      const testCount = run.tests ? ` — ${run.tests.passed}/${run.tests.total} testes aprovados` : '';
      item.textContent = `${new Date(run.generated_at).toLocaleString()} — cobertura ${run.coverage_percent}% (${run.lines_covered}/${run.lines_valid} linhas)${testCount}`;
      entries.appendChild(item);
    }
    historyCard.append(title, entries);
    container.appendChild(historyCard);
  }
}

async function loadAcademicManagementScreen(container) {
  const section = document.createElement('section');
  section.className = 'card';
  const title = document.createElement('h2');
  title.className = 'card-title';
  title.textContent = 'Cursos';
  const courseForm = document.createElement('form');
  courseForm.className = 'workspace-form';
  courseForm.innerHTML = `
    <div class="form-group"><label class="form-label" for="course-code">Código</label><input class="form-input" id="course-code" required maxlength="20"></div>
    <div class="form-group"><label class="form-label" for="course-name">Nome do curso</label><input class="form-input" id="course-name" required minlength="2" maxlength="255"></div>
    <div class="form-group"><label class="form-label" for="course-description">Descrição</label><textarea class="form-input" id="course-description"></textarea></div>
    <div class="form-group"><label class="form-label" for="course-duration">Duração (semestres)</label><input class="form-input" id="course-duration" type="number" min="1" max="20" value="8" required></div>
    <button class="btn btn-primary" type="submit">Cadastrar curso</button>
  `;
  const courseMessage = document.createElement('p');
  courseMessage.setAttribute('role', 'status');
  const courseTable = document.createElement('div');
  courseTable.className = 'workspace-table-wrap';
  section.append(title, courseForm, courseMessage, courseTable);

  const subjectSection = document.createElement('section');
  subjectSection.className = 'card';
  const subjectTitle = document.createElement('h2');
  subjectTitle.className = 'card-title';
  subjectTitle.textContent = 'Matérias e Disciplinas';
  const subjectForm = document.createElement('form');
  subjectForm.className = 'workspace-form';
  subjectForm.innerHTML = `
    <div class="form-group"><label class="form-label" for="subject-code">Código</label><input class="form-input" id="subject-code" required maxlength="20"></div>
    <div class="form-group"><label class="form-label" for="subject-name">Nome</label><input class="form-input" id="subject-name" required minlength="2" maxlength="255"></div>
    <div class="form-group"><label class="form-label" for="subject-description">Descrição</label><textarea class="form-input" id="subject-description"></textarea></div>
    <div class="form-group"><label class="form-label" for="subject-course">Curso</label><select class="form-input" id="subject-course" required></select></div>
    <div class="form-group"><label class="form-label" for="subject-hours">Carga horária</label><input class="form-input" id="subject-hours" type="number" min="1" value="60" required></div>
    <div class="form-group"><label class="form-label" for="subject-credits">Créditos</label><input class="form-input" id="subject-credits" type="number" min="1" value="4" required></div>
    <div class="workspace-form-actions">
      <button class="btn btn-primary" id="subject-submit" type="submit">Cadastrar matéria</button>
      <button class="btn btn-secondary" id="subject-cancel" type="button" hidden>Cancelar edição</button>
    </div>
  `;
  const subjectMessage = document.createElement('p');
  subjectMessage.setAttribute('role', 'status');
  const subjectTable = document.createElement('div');
  subjectTable.className = 'workspace-table-wrap';
  subjectSection.append(subjectTitle, subjectForm, subjectMessage, subjectTable);
  container.replaceChildren(section, subjectSection);

  let courses = [];
  let subjects = [];
  let editingSubjectId = null;
  const courseSelect = subjectForm.querySelector('#subject-course');

  const refresh = async () => {
    const [courseResult, subjectResult] = await Promise.all([
      api.request('/academic/courses?page=1&page_size=100&active_only=false'),
      api.request('/academic/subjects?page=1&page_size=100'),
    ]);
    courses = normalizeRows(courseResult);
    subjects = normalizeRows(subjectResult);
    courseSelect.replaceChildren(new Option('Selecione o curso...', ''));
    courses.filter(course => course.is_active).forEach(course => {
      courseSelect.add(new Option(`${course.code} — ${course.name}`, course.id));
    });
    renderCourses();
    renderSubjects();
  };

  function renderCourses() {
    const table = document.createElement('table');
    const body = document.createElement('tbody');
    const header = document.createElement('tr');
    ['Código', 'Curso', 'Duração', 'Status', 'Ações'].forEach(text => {
      const cell = document.createElement('th');
      cell.textContent = text;
      header.append(cell);
    });
    table.append(header);
    courses.forEach(course => {
      const row = document.createElement('tr');
      [course.code, course.name, `${course.duration_semesters} semestres`, course.is_active ? 'Ativo' : 'Inativo']
        .forEach(text => {
          const cell = document.createElement('td');
          cell.textContent = text;
          row.append(cell);
        });
      const action = document.createElement('td');
      const toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'btn btn-secondary btn-sm';
      toggle.textContent = course.is_active ? 'Desativar' : 'Ativar';
      toggle.addEventListener('click', () => updateAcademicStatus('courses', course, !course.is_active));
      action.append(toggle);
      row.append(action);
      body.append(row);
    });
    table.append(body);
    courseTable.replaceChildren(table);
  }

  function renderSubjects() {
    const courseNames = new Map(courses.map(course => [course.id, course.name]));
    const table = document.createElement('table');
    const body = document.createElement('tbody');
    const header = document.createElement('tr');
    ['Código', 'Matéria', 'Curso', 'Carga horária', 'Status', 'Ações'].forEach(text => {
      const cell = document.createElement('th');
      cell.textContent = text;
      header.append(cell);
    });
    table.append(header);
    subjects.forEach(subject => {
      const row = document.createElement('tr');
      [
        subject.code,
        subject.name,
        courseNames.get(subject.course_id) || subject.course_id,
        `${subject.workload_hours} h`,
        subject.is_active ? 'Ativa' : 'Inativa',
      ].forEach(text => {
        const cell = document.createElement('td');
        cell.textContent = text;
        row.append(cell);
      });
      const actions = document.createElement('td');
      const edit = document.createElement('button');
      edit.type = 'button';
      edit.className = 'btn btn-secondary btn-sm';
      edit.textContent = 'Editar';
      edit.addEventListener('click', () => {
        editingSubjectId = subject.id;
        subjectForm.querySelector('#subject-code').value = subject.code;
        subjectForm.querySelector('#subject-name').value = subject.name;
        subjectForm.querySelector('#subject-description').value = subject.description || '';
        subjectForm.querySelector('#subject-course').value = subject.course_id;
        courseSelect.disabled = true;
        subjectForm.querySelector('#subject-hours').value = subject.workload_hours;
        subjectForm.querySelector('#subject-credits').value = subject.credits;
        subjectForm.querySelector('#subject-submit').textContent = 'Salvar alterações';
        subjectForm.querySelector('#subject-cancel').hidden = false;
      });
      const toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'btn btn-ghost btn-sm';
      toggle.textContent = subject.is_active ? 'Desativar' : 'Ativar';
      toggle.addEventListener('click', () => updateAcademicStatus('subjects', subject, !subject.is_active));
      actions.append(edit, toggle);
      row.append(actions);
      body.append(row);
    });
    table.append(body);
    subjectTable.replaceChildren(table);
  }

  async function updateAcademicStatus(resource, record, isActive) {
    try {
      await api.request(`/academic/${resource}/${record.id}`, {
        method: 'PATCH',
        body: { is_active: isActive },
      });
      await refresh();
    } catch (error) {
      subjectMessage.textContent = error.message || 'Não foi possível alterar o status.';
      subjectMessage.classList.add('workspace-error');
    }
  }

  subjectForm.querySelector('#subject-cancel').addEventListener('click', () => {
    editingSubjectId = null;
    subjectForm.reset();
    courseSelect.disabled = false;
    subjectForm.querySelector('#subject-hours').value = '60';
    subjectForm.querySelector('#subject-credits').value = '4';
    subjectForm.querySelector('#subject-submit').textContent = 'Cadastrar matéria';
    subjectForm.querySelector('#subject-cancel').hidden = true;
  });
  courseForm.addEventListener('submit', async event => {
    event.preventDefault();
    try {
      await api.request('/academic/courses', {
        method: 'POST',
        body: {
          code: courseForm.querySelector('#course-code').value,
          name: courseForm.querySelector('#course-name').value,
          description: courseForm.querySelector('#course-description').value || null,
          duration_semesters: Number(courseForm.querySelector('#course-duration').value),
        },
      });
      courseForm.reset();
      courseForm.querySelector('#course-duration').value = '8';
      courseMessage.textContent = 'Curso cadastrado.';
      await refresh();
    } catch (error) {
      courseMessage.textContent = error.message || 'Não foi possível cadastrar o curso.';
      courseMessage.classList.add('workspace-error');
    }
  });
  subjectForm.addEventListener('submit', async event => {
    event.preventDefault();
    const payload = {
      code: subjectForm.querySelector('#subject-code').value,
      name: subjectForm.querySelector('#subject-name').value,
      description: subjectForm.querySelector('#subject-description').value || null,
      course_id: courseSelect.value,
      workload_hours: Number(subjectForm.querySelector('#subject-hours').value),
      credits: Number(subjectForm.querySelector('#subject-credits').value),
    };
    try {
      if (editingSubjectId) {
        await api.request(`/academic/subjects/${editingSubjectId}`, { method: 'PATCH', body: payload });
      } else {
        await api.request('/academic/subjects', { method: 'POST', body: payload });
      }
      subjectMessage.textContent = editingSubjectId ? 'Matéria atualizada.' : 'Matéria cadastrada.';
      subjectMessage.classList.remove('workspace-error');
      subjectForm.reset();
      courseSelect.disabled = false;
      editingSubjectId = null;
      subjectForm.querySelector('#subject-hours').value = '60';
      subjectForm.querySelector('#subject-credits').value = '4';
      subjectForm.querySelector('#subject-submit').textContent = 'Cadastrar matéria';
      subjectForm.querySelector('#subject-cancel').hidden = true;
      await refresh();
    } catch (error) {
      subjectMessage.textContent = error.message || 'Não foi possível salvar a matéria.';
      subjectMessage.classList.add('workspace-error');
    }
  });

  await refresh();
  await loadTeacherSubjectAdmin(container);
}

async function loadClassManagementScreen(container) {
  const [courseResult, subjectResult, periodResult] = await Promise.all([
    api.request('/academic/courses?page=1&page_size=100'),
    api.request('/academic/subjects?page=1&page_size=100'),
    api.request('/academic/periods?page=1&page_size=100'),
  ]);
  const courses = normalizeRows(courseResult);
  const subjects = normalizeRows(subjectResult);
  const periods = normalizeRows(periodResult);
  let classes = [];
  let students = [];
  let enrollments = [];
  let editingClassId = null;
  const classSection = document.createElement('section');
  classSection.className = 'card';
  const classTitle = document.createElement('h2');
  classTitle.className = 'card-title';
  classTitle.textContent = 'Cadastrar turma';
  const classForm = document.createElement('form');
  classForm.className = 'workspace-form';
  classForm.innerHTML = `
    <div class="form-group"><label class="form-label" for="class-code">Código</label><input class="form-input" id="class-code" required maxlength="20"></div>
    <div class="form-group"><label class="form-label" for="class-name">Nome</label><input class="form-input" id="class-name" required maxlength="255"></div>
    <div class="form-group" data-context-field><label class="form-label" for="class-course">Curso</label><select class="form-input" id="class-course" required></select></div>
    <div class="form-group" data-context-field><label class="form-label" for="class-subject">Matéria</label><select class="form-input" id="class-subject" required></select></div>
    <div class="form-group" data-context-field><label class="form-label" for="class-period">Período letivo</label><select class="form-input" id="class-period" required></select></div>
    <div class="form-group" data-context-field><label class="form-label" for="class-semester">Semestre</label><input class="form-input" id="class-semester" type="number" min="1" max="20" value="1" required></div>
    <div class="form-group" data-context-field><label class="form-label" for="class-year">Ano</label><input class="form-input" id="class-year" type="number" min="2000" max="2100" value="${new Date().getFullYear()}" required></div>
    <div class="form-group"><label class="form-label" for="class-schedule">Horário</label><input class="form-input" id="class-schedule" maxlength="500"></div>
    <div class="form-group"><label class="form-label" for="classroom">Sala</label><input class="form-input" id="classroom" maxlength="100"></div>
    <div class="form-group"><label class="form-label" for="class-capacity">Limite de alunos</label><input class="form-input" id="class-capacity" type="number" min="1" max="200" value="50" required></div>
    <div class="workspace-form-actions">
      <button class="btn btn-primary" type="submit" id="class-submit">Cadastrar turma</button>
      <button class="btn btn-secondary" type="button" id="class-cancel" hidden>Cancelar edição</button>
    </div>
  `;
  const classMessage = document.createElement('p');
  classMessage.setAttribute('role', 'status');
  const classTable = document.createElement('div');
  classTable.className = 'workspace-table-wrap';
  classSection.append(classTitle, classForm, classMessage, classTable);

  const enrollmentSection = document.createElement('section');
  enrollmentSection.className = 'card';
  const enrollmentTitle = document.createElement('h2');
  enrollmentTitle.className = 'card-title';
  enrollmentTitle.textContent = 'Matrículas de alunos';
  const enrollmentForm = document.createElement('form');
  enrollmentForm.className = 'workspace-form';
  enrollmentForm.innerHTML = `
    <div class="form-group"><label class="form-label" for="enrollment-student">Aluno</label><select class="form-input" id="enrollment-student" required></select></div>
    <div class="form-group"><label class="form-label" for="enrollment-class">Turma e matéria</label><select class="form-input" id="enrollment-class" required></select></div>
    <button class="btn btn-primary" type="submit">Matricular aluno</button>
  `;
  const enrollmentMessage = document.createElement('p');
  enrollmentMessage.setAttribute('role', 'status');
  const enrollmentTable = document.createElement('div');
  enrollmentTable.className = 'workspace-table-wrap';
  enrollmentSection.append(enrollmentTitle, enrollmentForm, enrollmentMessage, enrollmentTable);
  container.replaceChildren(classSection, enrollmentSection);

  const addOptions = (select, rows, label) => {
    select.replaceChildren(new Option('Selecione...', ''));
    rows.forEach(row => select.add(new Option(label(row), row.id)));
  };
  const courseSelect = classForm.querySelector('#class-course');
  const subjectSelect = classForm.querySelector('#class-subject');
  const periodSelect = classForm.querySelector('#class-period');
  addOptions(courseSelect, courses, row => `${row.code} — ${row.name}`);
  addOptions(periodSelect, periods, row => `${row.name} (${row.code})`);
  const updateSubjects = () => addOptions(
    subjectSelect,
    subjects.filter(subject => subject.course_id === courseSelect.value),
    row => `${row.code} — ${row.name}`,
  );
  courseSelect.addEventListener('change', updateSubjects);
  updateSubjects();

  const resetClassForm = () => {
    editingClassId = null;
    classForm.reset();
    classForm.querySelectorAll('[data-context-field]').forEach(field => { field.hidden = false; });
    classTitle.textContent = 'Cadastrar turma';
    classForm.querySelector('#class-submit').textContent = 'Cadastrar turma';
    classForm.querySelector('#class-cancel').hidden = true;
    courseSelect.disabled = false;
    subjectSelect.disabled = false;
    periodSelect.disabled = false;
    updateSubjects();
  };
  classForm.querySelector('#class-cancel').addEventListener('click', resetClassForm);

  const refresh = async () => {
    const [classResult, studentResult, enrollmentResult] = await Promise.all([
      api.request('/academic/classes?page=1&page_size=100'),
      api.request('/users/students?page=1&page_size=100'),
      api.request('/academic/enrollments?page=1&page_size=100'),
    ]);
    classes = normalizeRows(classResult);
    students = normalizeRows(studentResult);
    enrollments = normalizeRows(enrollmentResult);
    addOptions(
      enrollmentForm.querySelector('#enrollment-student'),
      students,
      student => `${student.user?.full_name || student.ra} — RA ${student.ra}`,
    );
    addOptions(
      enrollmentForm.querySelector('#enrollment-class'),
      classes,
      classRecord => `${classRecord.code} — ${classRecord.name}`,
    );
    renderClasses();
    renderEnrollments();
  };

  function renderClasses() {
    const table = document.createElement('table');
    const body = document.createElement('tbody');
    const header = document.createElement('tr');
    ['Turma', 'Matéria', 'Período', 'Alunos ativos', 'Ações'].forEach(text => {
      const cell = document.createElement('th');
      cell.textContent = text;
      header.append(cell);
    });
    table.append(header);
    classes.forEach(classRecord => {
      const row = document.createElement('tr');
      [
        `${classRecord.code} — ${classRecord.name}`,
        classRecord.subject?.name || classRecord.subject_id,
        classRecord.academic_period?.name || classRecord.academic_period_id,
        String(classRecord.enrollments_count ?? 0),
      ].forEach(text => {
        const cell = document.createElement('td');
        cell.textContent = text;
        row.append(cell);
      });
      const actions = document.createElement('td');
      const edit = document.createElement('button');
      edit.type = 'button';
      edit.className = 'btn btn-secondary btn-sm';
      edit.textContent = 'Editar turma';
      edit.addEventListener('click', () => {
        editingClassId = classRecord.id;
        classTitle.textContent = 'Editar turma';
        classForm.querySelector('#class-submit').textContent = 'Salvar alterações';
        classForm.querySelector('#class-cancel').hidden = false;
        classForm.querySelector('#class-code').value = classRecord.code;
        classForm.querySelector('#class-name').value = classRecord.name;
        classForm.querySelector('#class-schedule').value = classRecord.schedule || '';
        classForm.querySelector('#classroom').value = classRecord.classroom || '';
        classForm.querySelector('#class-capacity').value = classRecord.max_students;
        classForm.querySelectorAll('[data-context-field]').forEach(field => { field.hidden = true; });
      });
      actions.append(edit);
      row.append(actions);
      body.append(row);
    });
    table.append(body);
    classTable.replaceChildren(table);
  }

  function renderEnrollments() {
    const studentById = new Map(students.map(student => [student.id, student]));
    const classById = new Map(classes.map(classRecord => [classRecord.id, classRecord]));
    const table = document.createElement('table');
    const body = document.createElement('tbody');
    const header = document.createElement('tr');
    ['Aluno', 'Turma', 'Período', 'Status', 'Ações'].forEach(text => {
      const cell = document.createElement('th');
      cell.textContent = text;
      header.append(cell);
    });
    table.append(header);
    enrollments.forEach(enrollment => {
      const student = studentById.get(enrollment.student_id);
      const classRecord = classById.get(enrollment.class_id);
      const row = document.createElement('tr');
      [
        `${student?.user?.full_name || student?.ra || enrollment.student_id} (RA ${student?.ra || '—'})`,
        classRecord?.name || enrollment.class_id,
        enrollment.academic_period?.name || enrollment.academic_period_id,
        enrollment.status,
      ].forEach(text => {
        const cell = document.createElement('td');
        cell.textContent = text;
        row.append(cell);
      });
      const actionCell = document.createElement('td');
      const toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'btn btn-secondary btn-sm';
      toggle.textContent = enrollment.status === 'active' ? 'Desativar matrícula' : 'Reativar matrícula';
      toggle.addEventListener('click', async () => {
        try {
          await api.request(`/academic/enrollments/${enrollment.id}`, {
            method: 'PATCH',
            body: { status: enrollment.status === 'active' ? 'inactive' : 'active' },
          });
          await refresh();
        } catch (error) {
          enrollmentMessage.textContent = error.message || 'Não foi possível alterar a matrícula.';
          enrollmentMessage.classList.add('workspace-error');
        }
      });
      actionCell.append(toggle);
      row.append(actionCell);
      body.append(row);
    });
    table.append(body);
    enrollmentTable.replaceChildren(table);
  }

  classForm.addEventListener('submit', async event => {
    event.preventDefault();
    const payload = {
      code: classForm.querySelector('#class-code').value,
      name: classForm.querySelector('#class-name').value,
      schedule: classForm.querySelector('#class-schedule').value || null,
      classroom: classForm.querySelector('#classroom').value || null,
      max_students: Number(classForm.querySelector('#class-capacity').value),
    };
    try {
      if (editingClassId) {
        await api.request(`/academic/classes/${editingClassId}`, { method: 'PATCH', body: payload });
      } else {
        Object.assign(payload, {
          course_id: courseSelect.value,
          subject_id: subjectSelect.value,
          academic_period_id: periodSelect.value,
          semester: Number(classForm.querySelector('#class-semester').value),
          year: Number(classForm.querySelector('#class-year').value),
        });
        await api.request('/academic/classes', { method: 'POST', body: payload });
      }
      classMessage.textContent = editingClassId ? 'Turma atualizada.' : 'Turma cadastrada.';
      classMessage.classList.remove('workspace-error');
      resetClassForm();
      await refresh();
    } catch (error) {
      classMessage.textContent = error.message || 'Não foi possível salvar a turma.';
      classMessage.classList.add('workspace-error');
    }
  });

  enrollmentForm.addEventListener('submit', async event => {
    event.preventDefault();
    const classRecord = classes.find(
      item => item.id === enrollmentForm.querySelector('#enrollment-class').value,
    );
    if (!classRecord) return;
    try {
      await api.request('/academic/enrollments', {
        method: 'POST',
        body: {
          student_id: enrollmentForm.querySelector('#enrollment-student').value,
          class_id: classRecord.id,
          academic_period_id: classRecord.academic_period_id,
        },
      });
      enrollmentMessage.textContent = 'Matrícula criada.';
      enrollmentMessage.classList.remove('workspace-error');
      enrollmentForm.reset();
      await refresh();
    } catch (error) {
      enrollmentMessage.textContent = error.message || 'Não foi possível matricular o aluno.';
      enrollmentMessage.classList.add('workspace-error');
    }
  });

  await refresh();
}

async function loadTeacherSubjectAdmin(container) {
  const section = document.createElement('section');
  section.className = 'card';
  const heading = document.createElement('h2');
  heading.className = 'card-title';
  heading.textContent = 'Vínculos de professores e disciplinas';
  section.appendChild(heading);

  const [teacherData, subjectData, periodData, associationData] = await Promise.all([
    api.request('/users/teachers?page=1&page_size=100'),
    api.request('/academic/subjects?page=1&page_size=100'),
    api.request('/academic/periods?page=1&page_size=100'),
    api.request('/academic/teacher-subjects?page=1&page_size=100'),
  ]);
  const teachers = normalizeRows(teacherData);
  const subjects = normalizeRows(subjectData);
  const periods = normalizeRows(periodData);
  let associations = normalizeRows(associationData);

  const form = document.createElement('form');
  form.className = 'workspace-form';
  const fields = [
    {
      label: 'Professor',
      rows: teachers,
      getValue: row => row.id,
      getLabel: row => row.user?.full_name || row.user?.email || row.id,
      placeholder: 'Selecione o professor',
    },
    {
      label: 'Disciplina',
      rows: subjects,
      getValue: row => row.id,
      getLabel: row => `${row.code} — ${row.name}`,
      placeholder: 'Selecione a disciplina',
    },
    {
      label: 'Período letivo',
      rows: periods,
      getValue: row => row.id,
      getLabel: row => row.name || `${row.year || ''} ${row.semester || ''}`.trim() || row.id,
      placeholder: 'Sem período específico',
    },
  ];
  const selects = [];
  fields.forEach((field, index) => {
    const group = document.createElement('div');
    group.className = 'form-group';
    const label = document.createElement('label');
    label.className = 'form-label';
    label.textContent = field.label;
    const select = document.createElement('select');
    select.className = 'form-input';
    select.required = index < 2;
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = field.placeholder;
    select.appendChild(placeholder);
    field.rows.forEach(row => {
      const option = document.createElement('option');
      option.value = field.getValue(row);
      option.textContent = field.getLabel(row);
      select.appendChild(option);
    });
    label.appendChild(select);
    group.appendChild(label);
    form.appendChild(group);
    selects.push(select);
  });
  const submit = document.createElement('button');
  submit.type = 'submit';
  submit.className = 'btn btn-primary';
  submit.textContent = 'Vincular disciplina';
  form.appendChild(submit);
  section.appendChild(form);

  const tableContainer = document.createElement('div');
  tableContainer.className = 'workspace-table-wrap';
  section.appendChild(tableContainer);

  const teacherById = new Map(teachers.map(teacher => [
    teacher.id,
    teacher.user?.full_name || teacher.user?.email || teacher.id,
  ]));
  const subjectById = new Map(subjects.map(subject => [subject.id, subject.name]));
  const periodById = new Map(periods.map(period => [
    period.id,
    period.name || `${period.year || ''} ${period.semester || ''}`.trim() || period.id,
  ]));

  function renderAssociations() {
    if (associations.length === 0) {
      tableContainer.textContent = 'Nenhum vínculo cadastrado.';
      return;
    }
    const table = document.createElement('table');
    const body = document.createElement('tbody');
    const header = document.createElement('tr');
    ['Professor', 'Disciplina', 'Período', 'Coordenação', 'Ações'].forEach(text => {
      const cell = document.createElement('th');
      cell.textContent = text;
      header.appendChild(cell);
    });
    table.appendChild(header);
    associations.forEach(association => {
      const row = document.createElement('tr');
      [
        teacherById.get(association.teacher_id) || association.teacher_id,
        subjectById.get(association.subject_id) || association.subject_id,
        association.academic_period_id
          ? periodById.get(association.academic_period_id) || association.academic_period_id
          : 'Todos os períodos',
        association.is_coordinator ? 'Sim' : 'Não',
      ].forEach(text => {
        const cell = document.createElement('td');
        cell.textContent = text;
        row.appendChild(cell);
      });
      const actions = document.createElement('td');
      const coordinator = document.createElement('button');
      coordinator.type = 'button';
      coordinator.className = 'btn btn-secondary btn-sm';
      coordinator.textContent = association.is_coordinator ? 'Remover coordenação' : 'Definir coordenação';
      coordinator.addEventListener('click', async () => {
        try {
          await api.request(
            `/academic/teacher-subjects/${encodeURIComponent(association.id)}?is_coordinator=${!association.is_coordinator}`,
            { method: 'PATCH' },
          );
          await refreshAssociations();
          showWorkspaceMessage('Vínculo atualizado.');
        } catch (error) {
          showWorkspaceMessage(error.message || 'Não foi possível atualizar o vínculo.', true);
        }
      });
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'btn btn-danger btn-sm';
      remove.textContent = 'Remover';
      remove.addEventListener('click', async () => {
        try {
          await api.request(`/academic/teacher-subjects/${encodeURIComponent(association.id)}`, {
            method: 'DELETE',
          });
          await refreshAssociations();
          showWorkspaceMessage('Vínculo removido.');
        } catch (error) {
          showWorkspaceMessage(error.message || 'Não foi possível remover o vínculo.', true);
        }
      });
      actions.append(coordinator, remove);
      row.appendChild(actions);
      body.appendChild(row);
    });
    table.appendChild(body);
    tableContainer.replaceChildren(table);
  }

  async function refreshAssociations() {
    const response = await api.request('/academic/teacher-subjects?page=1&page_size=100');
    associations = normalizeRows(response);
    renderAssociations();
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    submit.disabled = true;
    try {
      await api.request('/academic/teacher-subjects', {
        method: 'POST',
        body: {
          teacher_id: selects[0].value,
          subject_id: selects[1].value,
          academic_period_id: selects[2].value || null,
          is_coordinator: false,
        },
      });
      form.reset();
      await refreshAssociations();
      showWorkspaceMessage('Disciplina vinculada ao professor.');
    } catch (error) {
      showWorkspaceMessage(error.message || 'Não foi possível vincular a disciplina.', true);
    } finally {
      submit.disabled = false;
    }
  });
  renderAssociations();
  container.appendChild(section);
}

async function loadWorkspaceScreen() {
  const screen = WORKSPACE_SCREENS[window.location.pathname];
  const title = document.getElementById('workspace-title');
  const description = document.getElementById('workspace-description');
  const content = document.getElementById('workspace-content');

  if (!screen) {
    title.textContent = 'Tela não encontrada';
    description.textContent = 'Não há uma tela cadastrada para este endereço.';
    showWorkspaceMessage('Volte ao painel e escolha uma opção disponível.', true);
    content.replaceChildren();
    return;
  }

  document.title = `${screen.title} - EduGrade`;
  title.textContent = screen.title;
  description.textContent = screen.description;
  document.getElementById('workspace-logout').addEventListener('click', () => Auth.logout());

  const authenticated = await Auth.init();
  if (!authenticated) {
    window.location.replace('/login.html');
    return;
  }
  if (screen.roles && !State.hasRole(...screen.roles)) {
    window.location.replace(Auth.dashboardPath());
    return;
  }
  document.getElementById('workspace-home').href = Auth.dashboardPath();

  // Retoma operações em andamento (ex.: página recarregada durante a correção).
  if (typeof ProgressManager !== 'undefined') ProgressManager.resumeActive();

  if (screen.message) showWorkspaceMessage(screen.message);

  if (window.location.pathname === '/admin/users.html') {
    try {
      await loadAdminUsersScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar os usuários.', true);
    }
    return;
  }

  if (screen.accessRequests) {
    try {
      await loadAdminAccessRequestsScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar os chamados.', true);
    }
    return;
  }

  if (screen.classManagement) {
    try {
      await loadClassManagementScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar turmas e matrículas.', true);
    }
    return;
  }

  if (screen.gradeManagement) {
    try {
      await loadTeacherGradesScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar as notas.', true);
    }
    return;
  }

  if (screen.teacherStudents) {
    try {
      await loadTeacherStudentsScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar os alunos.', true);
    }
    return;
  }

  if (screen.subjectManagement) {
    try {
      await loadAcademicManagementScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar cursos e matérias.', true);
    }
    return;
  }

  if (screen.quality) {
    try {
      await loadQualityScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar os dados de qualidade.', true);
    }
    return;
  }

  if (screen.createExam) {
    await loadCreateExamScreen(content);
    return;
  }

  if (screen.editExam) {
    const examId = new URLSearchParams(window.location.search).get('id');
    if (!examId) {
      showWorkspaceMessage('Selecione uma prova para editar.', true);
      content.replaceChildren();
      return;
    }
    await loadCreateExamScreen(content, examId);
    return;
  }

  if (screen.printExams) {
    await loadPrintExamsScreen(content);
    return;
  }

  if (screen.uploadExams) {
    await loadUploadExamsScreen(content);
    return;
  }

  if (screen.myAttendance) {
    try {
      await loadStudentAttendanceScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar a frequência.', true);
    }
    return;
  }

  if (screen.mySchedule) {
    try {
      await loadStudentScheduleScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar a grade horária.', true);
    }
    return;
  }

  if (screen.storageUsage) {
    try {
      await loadStorageUsageScreen(content);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível carregar o armazenamento.', true);
    }
    return;
  }

  if (screen.importKind) {
    try {
      await loadImportScreen(content, screen.importKind);
    } catch (error) {
      content.replaceChildren();
      showWorkspaceMessage(error.message || 'Não foi possível importar os dados.', true);
    }
    return;
  }

  const classId = screen.classDetail && new URLSearchParams(window.location.search).get('id');
  const examId = screen.examDetail && new URLSearchParams(window.location.search).get('id');
  let endpoint = screen.endpoint;
  if (classId) endpoint = `/academic/classes/${encodeURIComponent(classId)}`;
  if (examId && screen.examDetail) endpoint = `/exams/${encodeURIComponent(examId)}`;
  const sections = screen.endpoints || (endpoint ? [{ title: screen.title, endpoint }] : []);
  if (sections.length === 0) {
    content.replaceChildren();
    return;
  }

  content.textContent = 'Carregando dados...';
  try {
    const results = await Promise.all(sections.map(async section => ({
      title: section.title,
      data: await api.request(section.endpoint),
    })));
    content.replaceChildren();

    for (const result of results) {
      if (results.length > 1) {
        const heading = document.createElement('h2');
        heading.className = 'card-title';
        heading.textContent = result.title;
        content.appendChild(heading);
      }
      const sectionContent = document.createElement('div');
      sectionContent.className = 'workspace-table-wrap';
      if (screen.examList) {
        renderExamList(sectionContent, normalizeRows(result.data));
      } else {
        renderWorkspaceTable(sectionContent, normalizeRows(result.data));
      }
      content.appendChild(sectionContent);
    }
    if (screen.teacherSubjects) await loadTeacherSubjectAdmin(content);
  } catch (error) {
    content.replaceChildren();
    showWorkspaceMessage(error.message || 'Não foi possível carregar os dados desta tela.', true);
  }
}

async function loadTeacherGradesScreen(container) {
  const section = document.createElement('section');
  section.className = 'workspace-grade-management';
  section.innerHTML = `
    <form class="workspace-form" id="teacher-grade-form">
      <div class="form-group">
        <label class="form-label" for="teacher-grade-class">Turma</label>
        <select class="form-input" id="teacher-grade-class" required></select>
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-grade-enrollment">Aluno matriculado</label>
        <select class="form-input" id="teacher-grade-enrollment" required></select>
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-grade-assessment">Avaliação</label>
        <select class="form-input" id="teacher-grade-assessment" required></select>
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-grade-score">Nota</label>
        <input class="form-input" id="teacher-grade-score" type="number" min="0" step="0.01" required>
      </div>
      <div class="workspace-form-actions">
        <button class="btn btn-primary" type="submit">Salvar nota</button>
      </div>
    </form>
    <h2>Notas da turma</h2>
    <div class="workspace-table-wrap">
      <table>
        <thead><tr><th>Aluno</th><th>Avaliação</th><th>Nota</th><th>Situação</th><th>Ações</th></tr></thead>
        <tbody id="teacher-grades-body"></tbody>
      </table>
    </div>
  `;
  container.replaceChildren(section);

  const classSelect = section.querySelector('#teacher-grade-class');
  const enrollmentSelect = section.querySelector('#teacher-grade-enrollment');
  const assessmentSelect = section.querySelector('#teacher-grade-assessment');
  const scoreInput = section.querySelector('#teacher-grade-score');
  const gradeForm = section.querySelector('#teacher-grade-form');
  const gradeBody = section.querySelector('#teacher-grades-body');
  let selectedClassData = null;
  let isSaving = false;

  const addOption = (select, label, value = '') => {
    select.add(new Option(label, value));
  };

  const setStatus = (message, isError = false) => {
    showWorkspaceMessage(message, isError);
  };

  const displayName = student => {
    const name = student?.user?.full_name || student?.ra || 'Aluno';
    const identifiers = [
      student?.ra ? `RA ${student.ra}` : null,
      student?.registration_number ? `Matrícula ${student.registration_number}` : null,
    ].filter(Boolean);
    return identifiers.length ? `${name} — ${identifiers.join(' · ')}` : name;
  };

  const setSelectOptions = (select, placeholder, options, labelFor) => {
    select.replaceChildren();
    addOption(select, placeholder);
    options.forEach(item => addOption(select, labelFor(item), item.id));
  };

  const updateScoreLimit = () => {
    const assessment = selectedClassData?.assessments.find(
      item => item.id === assessmentSelect.value,
    );
    scoreInput.max = assessment?.max_score ?? '';
  };

  const loadClassData = async (classId, successMessage) => {
    if (!classId) {
      selectedClassData = null;
      setSelectOptions(enrollmentSelect, 'Selecione um aluno...', [], () => '');
      setSelectOptions(assessmentSelect, 'Selecione uma avaliação...', [], () => '');
      gradeBody.replaceChildren();
      setStatus('Selecione uma turma.');
      return;
    }

    setStatus('Carregando matrículas, avaliações e notas...');
    try {
      const query = `class_id=${encodeURIComponent(classId)}&page=1&page_size=100`;
      const [enrollmentResponse, studentResponse, assessmentResponse, gradeResponse] = await Promise.all([
        api.request(`/academic/enrollments?${query}`),
        api.request(`/students?${query}`),
        api.request(`/academic/assessments?${query}`),
        api.request(`/academic/grades?${query}`),
      ]);
      const enrollments = normalizeRows(enrollmentResponse).filter(item => item.status === 'active');
      const students = new Map(
        normalizeRows(studentResponse).map(student => [student.id, student]),
      );
      selectedClassData = {
        enrollments,
        students,
        assessments: normalizeRows(assessmentResponse),
        grades: normalizeRows(gradeResponse),
      };

      setSelectOptions(
        enrollmentSelect,
        'Selecione um aluno...',
        enrollments,
        enrollment => displayName(students.get(enrollment.student_id)),
      );
      setSelectOptions(
        assessmentSelect,
        'Selecione uma avaliação...',
        selectedClassData.assessments,
        assessment => assessment.title,
      );
      renderGrades();
      updateScoreLimit();
      setStatus(successMessage || `${selectedClassData.grades.length} nota(s) carregada(s).`);
    } catch (error) {
      selectedClassData = null;
      gradeBody.replaceChildren();
      setStatus(error.message || 'Não foi possível carregar os dados da turma.', true);
    }
  };

  const renderGrades = () => {
    gradeBody.replaceChildren();
    if (!selectedClassData || selectedClassData.grades.length === 0) {
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 5;
      cell.textContent = 'Nenhuma nota cadastrada para esta turma.';
      row.appendChild(cell);
      gradeBody.appendChild(row);
      return;
    }

    selectedClassData.grades.forEach(grade => {
      const enrollment = selectedClassData.enrollments.find(
        item => item.id === grade.enrollment_id,
      );
      const student = enrollment && selectedClassData.students.get(enrollment.student_id);
      const assessment = selectedClassData.assessments.find(
        item => item.id === grade.assessment_id,
      );
      const row = document.createElement('tr');
      const values = [
        displayName(student),
        assessment?.title || 'Avaliação indisponível',
      ];
      values.forEach(value => {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.appendChild(cell);
      });

      const scoreCell = document.createElement('td');
      const gradeInput = document.createElement('input');
      gradeInput.type = 'number';
      gradeInput.min = '0';
      gradeInput.step = '0.01';
      gradeInput.max = assessment?.max_score ?? '';
      gradeInput.value = String(grade.score);
      gradeInput.setAttribute('aria-label', `Nota de ${displayName(student)}`);
      scoreCell.appendChild(gradeInput);
      if (assessment?.max_score !== undefined) {
        const maximum = document.createElement('span');
        maximum.textContent = ` / ${assessment.max_score}`;
        scoreCell.appendChild(maximum);
      }
      row.appendChild(scoreCell);

      const statusCell = document.createElement('td');
      statusCell.textContent = grade.is_official ? 'Publicada' : 'Rascunho';
      row.appendChild(statusCell);

      const actionsCell = document.createElement('td');
      const saveButton = document.createElement('button');
      saveButton.className = 'btn btn-secondary btn-sm';
      saveButton.type = 'button';
      saveButton.textContent = 'Salvar';
      saveButton.addEventListener('click', () => saveExistingGrade(grade, gradeInput, saveButton));
      actionsCell.appendChild(saveButton);
      if (!grade.is_official) {
        const publishButton = document.createElement('button');
        publishButton.className = 'btn btn-primary btn-sm';
        publishButton.type = 'button';
        publishButton.textContent = 'Publicar';
        publishButton.addEventListener('click', () => publishGrade(grade.id, publishButton));
        actionsCell.appendChild(publishButton);
      }
      row.appendChild(actionsCell);
      gradeBody.appendChild(row);
    });
  };

  const saveExistingGrade = async (grade, input, button) => {
    const score = Number(input.value);
    if (!Number.isFinite(score) || score < 0 || (input.max && score > Number(input.max))) {
      setStatus('Informe uma nota válida dentro do limite da avaliação.', true);
      input.focus();
      return;
    }
    button.disabled = true;
    try {
      await api.request(`/academic/grades/${encodeURIComponent(grade.id)}`, {
        method: 'PATCH',
        body: { score },
      });
      await loadClassData(classSelect.value, 'Nota atualizada com sucesso.');
    } catch (error) {
      setStatus(error.message || 'Não foi possível atualizar a nota.', true);
    } finally {
      button.disabled = false;
    }
  };

  const publishGrade = async (gradeId, button) => {
    button.disabled = true;
    try {
      await api.request(`/academic/grades/${encodeURIComponent(gradeId)}/publish`, {
        method: 'POST',
      });
      await loadClassData(classSelect.value, 'Nota publicada com sucesso.');
    } catch (error) {
      setStatus(error.message || 'Não foi possível publicar a nota.', true);
    } finally {
      button.disabled = false;
    }
  };

  classSelect.addEventListener('change', () => loadClassData(classSelect.value));
  assessmentSelect.addEventListener('change', updateScoreLimit);
  gradeForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (isSaving) return;
    const assessment = selectedClassData?.assessments.find(
      item => item.id === assessmentSelect.value,
    );
    const score = Number(scoreInput.value);
    if (!classSelect.value || !enrollmentSelect.value || !assessment || !Number.isFinite(score)) {
      setStatus('Selecione turma, aluno e avaliação e informe uma nota válida.', true);
      return;
    }
    if (score < 0 || score > Number(assessment.max_score)) {
      setStatus(`A nota deve estar entre 0 e ${assessment.max_score}.`, true);
      scoreInput.focus();
      return;
    }

    isSaving = true;
    const submitButton = gradeForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    try {
      await api.request('/academic/grades', {
        method: 'POST',
        body: {
          enrollment_id: enrollmentSelect.value,
          assessment_id: assessment.id,
          score,
        },
      });
      const currentClassId = classSelect.value;
      gradeForm.reset();
      classSelect.value = currentClassId;
      await loadClassData(currentClassId, 'Nota registrada com sucesso.');
    } catch (error) {
      setStatus(error.message || 'Não foi possível registrar a nota.', true);
    } finally {
      isSaving = false;
      submitButton.disabled = false;
    }
  });

  setStatus('Carregando turmas autorizadas...');
  try {
    const response = await api.request('/academic/classes/my?page=1&page_size=100');
    const classes = normalizeRows(response);
    setSelectOptions(
      classSelect,
      'Selecione uma turma...',
      classes,
      classRecord => `${classRecord.code} — ${classRecord.name}`,
    );
    if (classes.length === 0) {
      setStatus('Não há turmas ativas atribuídas a esta conta.');
      setSelectOptions(enrollmentSelect, 'Selecione um aluno...', [], () => '');
      setSelectOptions(assessmentSelect, 'Selecione uma avaliação...', [], () => '');
      gradeBody.replaceChildren();
      return;
    }
    await loadClassData(classes[0].id);
    classSelect.value = classes[0].id;
  } catch (error) {
    setStatus(error.message || 'Não foi possível carregar as turmas autorizadas.', true);
    throw error;
  }
}

async function loadTeacherStudentsScreen(container) {
  const section = document.createElement('section');
  section.innerHTML = `
    <h2>Cadastrar aluno em uma turma autorizada</h2>
    <form class="workspace-form" id="teacher-create-student-form">
      <div class="form-group">
        <label class="form-label" for="teacher-new-student-class">Turma</label>
        <select class="form-input" id="teacher-new-student-class" required></select>
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-new-student-name">Nome completo</label>
        <input class="form-input" id="teacher-new-student-name" required minlength="2" maxlength="255">
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-new-student-username">Login</label>
        <input class="form-input" id="teacher-new-student-username" required minlength="3" maxlength="100" autocomplete="off">
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-new-student-email">E-mail</label>
        <input class="form-input" id="teacher-new-student-email" type="email" required>
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-new-student-password">Senha inicial</label>
        <input class="form-input" id="teacher-new-student-password" type="password" required minlength="8" maxlength="100" autocomplete="new-password">
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-new-student-ra">RA</label>
        <input class="form-input" id="teacher-new-student-ra" required maxlength="50">
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-new-student-registration">Matrícula institucional</label>
        <input class="form-input" id="teacher-new-student-registration" required maxlength="50">
      </div>
      <div class="workspace-form-actions">
        <button class="btn btn-primary" type="submit">Cadastrar aluno</button>
      </div>
    </form>
    <h2>Alunos matriculados</h2>
    <div class="workspace-table-wrap">
      <table>
        <thead><tr><th>Nome</th><th>RA</th><th>Matrícula</th><th>E-mail</th><th>Situação</th><th>Ações</th></tr></thead>
        <tbody id="teacher-students-body"></tbody>
      </table>
    </div>
    <form class="workspace-form" id="teacher-edit-student-form" hidden>
      <h2>Editar dados do aluno</h2>
      <div class="form-group">
        <label class="form-label" for="teacher-edit-student-name">Nome completo</label>
        <input class="form-input" id="teacher-edit-student-name" required minlength="2" maxlength="255">
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-edit-student-username">Login</label>
        <input class="form-input" id="teacher-edit-student-username" required minlength="3" maxlength="100">
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-edit-student-email">E-mail</label>
        <input class="form-input" id="teacher-edit-student-email" type="email" required>
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-edit-student-ra">RA</label>
        <input class="form-input" id="teacher-edit-student-ra" required maxlength="50">
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-edit-student-registration">Matrícula institucional</label>
        <input class="form-input" id="teacher-edit-student-registration" required maxlength="50">
      </div>
      <div class="form-group">
        <label class="form-label" for="teacher-edit-student-status">Situação acadêmica</label>
        <input class="form-input" id="teacher-edit-student-status" required maxlength="50">
      </div>
      <div class="workspace-form-actions">
        <button class="btn btn-primary" type="submit">Salvar alterações</button>
        <button class="btn btn-secondary" id="teacher-edit-student-cancel" type="button">Cancelar</button>
      </div>
    </form>
  `;
  container.replaceChildren(section);

  const classSelect = section.querySelector('#teacher-new-student-class');
  const createForm = section.querySelector('#teacher-create-student-form');
  const editForm = section.querySelector('#teacher-edit-student-form');
  const studentsBody = section.querySelector('#teacher-students-body');
  const editFields = {
    name: editForm.querySelector('#teacher-edit-student-name'),
    username: editForm.querySelector('#teacher-edit-student-username'),
    email: editForm.querySelector('#teacher-edit-student-email'),
    ra: editForm.querySelector('#teacher-edit-student-ra'),
    registration: editForm.querySelector('#teacher-edit-student-registration'),
    status: editForm.querySelector('#teacher-edit-student-status'),
  };
  let students = [];
  let selectedStudent = null;
  let isSaving = false;

  const setStatus = (message, isError = false) => showWorkspaceMessage(message, isError);
  const selectedClassId = () => classSelect.value;

  const loadStudents = async successMessage => {
    const classId = selectedClassId();
    if (!classId) {
      studentsBody.replaceChildren();
      setStatus('Selecione uma turma.');
      return;
    }
    studentsBody.textContent = 'Carregando alunos...';
    try {
      const response = await api.request(
        `/students?class_id=${encodeURIComponent(classId)}&page=1&page_size=100`,
      );
      students = normalizeRows(response);
      studentsBody.replaceChildren();
      if (students.length === 0) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 6;
        cell.textContent = 'Nenhum aluno matriculado nesta turma.';
        row.appendChild(cell);
        studentsBody.appendChild(row);
      }
      students.forEach(student => {
        const row = document.createElement('tr');
        [
          student.user?.full_name || '—',
          student.ra || '—',
          student.registration_number || '—',
          student.user?.email || '—',
          student.status || '—',
        ].forEach(value => {
          const cell = document.createElement('td');
          cell.textContent = value;
          row.appendChild(cell);
        });
        const actions = document.createElement('td');
        const editButton = document.createElement('button');
        editButton.className = 'btn btn-secondary btn-sm';
        editButton.type = 'button';
        editButton.textContent = 'Editar';
        editButton.addEventListener('click', () => openEditForm(student));
        actions.appendChild(editButton);
        row.appendChild(actions);
        studentsBody.appendChild(row);
      });
      setStatus(successMessage || `${students.length} aluno(s) carregado(s).`);
    } catch (error) {
      students = [];
      studentsBody.replaceChildren();
      setStatus(error.message || 'Não foi possível carregar os alunos desta turma.', true);
    }
  };

  const openEditForm = student => {
    selectedStudent = student;
    editFields.name.value = student.user?.full_name || '';
    editFields.username.value = student.user?.username || '';
    editFields.email.value = student.user?.email || '';
    editFields.ra.value = student.ra || '';
    editFields.registration.value = student.registration_number || '';
    editFields.status.value = student.status || 'active';
    editForm.hidden = false;
    editForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  classSelect.addEventListener('change', () => {
    editForm.hidden = true;
    selectedStudent = null;
    loadStudents();
  });
  createForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (isSaving) return;
    const submitButton = createForm.querySelector('button[type="submit"]');
    isSaving = true;
    submitButton.disabled = true;
    try {
      await api.create('/users/provision', {
        user: {
          full_name: section.querySelector('#teacher-new-student-name').value.trim(),
          username: section.querySelector('#teacher-new-student-username').value.trim(),
          email: section.querySelector('#teacher-new-student-email').value.trim(),
          password: section.querySelector('#teacher-new-student-password').value,
          role: 'student',
        },
        student_ra: section.querySelector('#teacher-new-student-ra').value.trim(),
        student_registration_number: section.querySelector(
          '#teacher-new-student-registration',
        ).value.trim(),
        student_class_id: selectedClassId(),
      });
      const currentClassId = selectedClassId();
      createForm.reset();
      classSelect.value = currentClassId;
      await loadStudents('Aluno cadastrado e vinculado à turma.');
    } catch (error) {
      setStatus(error.message || 'Não foi possível cadastrar o aluno.', true);
    } finally {
      isSaving = false;
      submitButton.disabled = false;
    }
  });
  editForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (!selectedStudent || isSaving) return;
    const submitButton = editForm.querySelector('button[type="submit"]');
    isSaving = true;
    submitButton.disabled = true;
    try {
      await api.request(`/users/${encodeURIComponent(selectedStudent.user_id)}/academic-profile`, {
        method: 'PATCH',
        body: {
          user: {
            full_name: editFields.name.value.trim(),
            username: editFields.username.value.trim(),
            email: editFields.email.value.trim(),
          },
          student: {
            ra: editFields.ra.value.trim(),
            registration_number: editFields.registration.value.trim(),
            status: editFields.status.value.trim(),
          },
        },
      });
      editForm.hidden = true;
      selectedStudent = null;
      await loadStudents('Dados do aluno atualizados com sucesso.');
    } catch (error) {
      setStatus(error.message || 'Não foi possível atualizar o aluno.', true);
    } finally {
      isSaving = false;
      submitButton.disabled = false;
    }
  });
  editForm.querySelector('#teacher-edit-student-cancel').addEventListener('click', () => {
    selectedStudent = null;
    editForm.hidden = true;
  });

  setStatus('Carregando turmas autorizadas...');
  try {
    const response = await api.request('/academic/classes/my?page=1&page_size=100');
    const classes = normalizeRows(response);
    classSelect.replaceChildren(new Option('Selecione uma turma...', ''));
    classes.forEach(classRecord => {
      classSelect.add(new Option(`${classRecord.code} — ${classRecord.name}`, classRecord.id));
    });
    if (classes.length === 0) {
      setStatus('Não há turmas ativas atribuídas a esta conta.');
      createForm.hidden = true;
      return;
    }
    classSelect.value = classes[0].id;
    await loadStudents();
  } catch (error) {
    setStatus(error.message || 'Não foi possível carregar as turmas autorizadas.', true);
    throw error;
  }
}

document.addEventListener('DOMContentLoaded', loadWorkspaceScreen);

/* ==================== Importação de alunos e notas ==================== */

const IMPORT_HELP = {
  students: {
    columns: 'nome; email; usuario; senha; ra; matricula',
    example: 'Maria Souza;maria.souza@escola.edu.br;maria.souza;SenhaForte123;RA2026001;20261001',
    template: 'modelo_alunos.csv',
    next: 'Depois de importar, os alunos já aparecem na turma e podem acessar o portal.',
  },
  grades: {
    columns: 'ra; avaliacao; nota',
    example: 'RA123456;A1 — Validação;8,5',
    template: 'modelo_notas.csv',
    next: 'As notas entram como rascunho; publique-as na tela "Lançar notas".',
  },
};

function renderImportSummary(container, job, kind) {
  const summary = job.result || {};
  container.replaceChildren();

  const grid = createSummaryGrid([
    { label: 'Registros no arquivo', value: String(summary.total_rows ?? summary.processed ?? 0) },
    { label: 'Importados', value: String(summary.imported ?? 0) },
    { label: 'Duplicados', value: String(summary.duplicated ?? 0) },
    { label: 'Ignorados', value: String(summary.skipped ?? 0) },
    { label: 'Com erro', value: String(summary.failed ?? 0) },
  ]);
  container.appendChild(grid);

  const message = document.createElement('p');
  message.className = 'workspace-import-message';
  message.textContent = job.message || 'Importação concluída.';
  container.appendChild(message);

  const errors = Array.isArray(summary.errors) ? summary.errors : [];
  if (errors.length > 0) {
    const heading = document.createElement('h3');
    heading.textContent = `Registros que precisam de atenção (${errors.length})`;
    container.appendChild(heading);

    const wrap = document.createElement('div');
    wrap.className = 'workspace-table-wrap';
    const table = document.createElement('table');
    table.innerHTML = '<thead><tr><th>Linha</th><th>Motivo</th><th>Situação</th></tr></thead>';
    const body = document.createElement('tbody');
    for (const error of errors) {
      const row = document.createElement('tr');
      const line = document.createElement('td');
      line.textContent = String(error.row ?? '—');
      const reason = document.createElement('td');
      reason.textContent = error.message || 'Erro não detalhado';
      const kindCell = document.createElement('td');
      kindCell.textContent = {
        duplicated: 'Duplicado',
        skipped: 'Ignorado',
        error: 'Erro',
      }[error.kind] || 'Erro';
      row.append(line, reason, kindCell);
      body.appendChild(row);
    }
    table.appendChild(body);
    wrap.appendChild(table);
    container.appendChild(wrap);
  }

  const tips = document.createElement('p');
  tips.className = 'workspace-empty-state';
  tips.textContent = IMPORT_HELP[kind].next;
  container.appendChild(tips);
}

async function loadImportScreen(container, kind) {
  const help = IMPORT_HELP[kind];
  if (!help) throw new Error('Tipo de importação desconhecido.');

  const section = document.createElement('section');
  section.innerHTML = `
    <div class="workspace-import-help">
      <p><strong>Colunas do CSV:</strong> <code>${help.columns}</code></p>
      <p><strong>Exemplo:</strong> <code>${help.example}</code></p>
      <p>Use <code>;</code> ou <code>,</code> como separador e salve em UTF-8. O cabeçalho é obrigatório.</p>
    </div>
    <form class="workspace-form" id="import-form">
      <div class="form-group">
        <label class="form-label" for="import-class">Turma</label>
        <select class="form-input" id="import-class" required></select>
      </div>
      <div class="form-group">
        <label class="form-label" for="import-file">Arquivo CSV</label>
        <input class="form-input" id="import-file" name="file" type="file" accept=".csv,text/csv" required>
      </div>
      <div class="workspace-form-actions">
        <button class="btn btn-primary" type="submit">Importar</button>
        <button class="btn btn-secondary" type="button" id="import-template">Baixar modelo CSV</button>
      </div>
    </form>
    <div id="import-result" aria-live="polite"></div>
  `;
  const oldContent = container;
  oldContent.replaceChildren(section);
  const form = section.querySelector('#import-form');
  const classSelect = section.querySelector('#import-class');
  const resultContainer = section.querySelector('#import-result');
  const submitButton = form.querySelector('button[type="submit"]');

  section.querySelector('#import-template').addEventListener('click', async () => {
    try {
      await api.download(`/imports/templates/${kind}.csv`, help.template);
    } catch (error) {
      showWorkspaceMessage(error.message || 'Não foi possível baixar o modelo.', true);
    }
  });

  const isTeacher = State.hasRole('teacher') && !State.hasRole('admin');
  const endpoint = isTeacher
    ? '/academic/classes/my?page=1&page_size=100'
    : '/academic/classes?page=1&page_size=100';
  const classes = normalizeRows(await api.request(endpoint));
  classSelect.replaceChildren(new Option('Selecione uma turma...', ''));
  for (const classRecord of classes) {
    classSelect.add(
      new Option(
        `${classRecord.code} — ${classRecord.name} (${classRecord.subject?.name || 'sem disciplina'})`,
        classRecord.id,
      ),
    );
  }
  if (classes.length === 0) {
    submitButton.disabled = true;
    showWorkspaceMessage('Nenhuma turma autorizada para importar.', true);
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const file = form.querySelector('#import-file').files[0];
    const classId = classSelect.value;
    if (!file || !classId) {
      showWorkspaceMessage('Selecione a turma e o arquivo CSV.', true);
      return;
    }

    submitButton.disabled = true;
    resultContainer.replaceChildren();
    const operation = ProgressManager.start({
      title: kind === 'students' ? 'Importação de alunos' : 'Importação de notas',
      subtitle: file.name,
    });
    try {
      const body = new FormData();
      body.append('file', file);
      body.append('class_id', classId);
      const created = await api.uploadForm(`/imports/${kind}`, body, {
        onProgress: ({ loaded, total, percent }) =>
          operation.setUpload({ loaded, total, percent }),
      });
      operation.setStep('Arquivo recebido. Processando registros...');
      const job = await operation.followJob(created.job_id);
      renderImportSummary(resultContainer, job, kind);
      showWorkspaceMessage(job.message || 'Importação concluída.');
      form.querySelector('#import-file').value = '';
    } catch (error) {
      operation.fail(error.message || 'Não foi possível concluir a importação.');
      const failure = document.createElement('p');
      failure.className = 'workspace-import-message is-error';
      failure.textContent = error.message || 'Não foi possível concluir a importação.';
      resultContainer.replaceChildren(failure);
      showWorkspaceMessage(error.message || 'Não foi possível importar os dados.', true);
    } finally {
      submitButton.disabled = false;
    }
  });
}

/* ==================== Consultas do aluno ==================== */

const WEEK_DAYS = [
  { label: 'Segunda-feira', tokens: ['seg', 'segunda'] },
  { label: 'Terça-feira', tokens: ['ter', 'terca', 'terça'] },
  { label: 'Quarta-feira', tokens: ['qua', 'quarta'] },
  { label: 'Quinta-feira', tokens: ['qui', 'quinta'] },
  { label: 'Sexta-feira', tokens: ['sex', 'sexta'] },
  { label: 'Sábado', tokens: ['sab', 'sáb', 'sabado', 'sábado'] },
  { label: 'Domingo', tokens: ['dom', 'domingo'] },
];

function formatFileSize(bytes) {
  const value = Number(bytes) || 0;
  if (value < 1024) return `${value} B`;
  const units = ['KB', 'MB', 'GB', 'TB'];
  let size = value;
  let unit = 'B';
  for (const candidate of units) {
    if (size < 1024) break;
    size /= 1024;
    unit = candidate;
  }
  return `${size.toFixed(size >= 10 ? 0 : 1)} ${unit}`;
}

function parseSchedule(schedule) {
  const text = String(schedule || '').trim();
  if (!text) return { days: [], time: '' };
  const match = text.match(/^(?<days>[^0-9]+?)\s*(?<time>\d{1,2}:\d{2}.*)$/);
  if (!match?.groups) return { days: [], time: text };
  const days = match.groups.days
    .split(/[\/,;|-]+/)
    .map(token => token.trim().toLowerCase())
    .filter(Boolean)
    .map(token => {
      const found = WEEK_DAYS.find(day => day.tokens.includes(token));
      return found ? found.label : token;
    });
  return { days, time: match.groups.time.trim() };
}

function formatPercentage(value) {
  const number = Number.parseFloat(value);
  return Number.isFinite(number) ? `${number.toFixed(1)}%` : '—';
}

function createSummaryGrid(items) {
  const grid = document.createElement('div');
  grid.className = 'workspace-summary-grid';
  for (const item of items) {
    const card = document.createElement('article');
    card.className = 'workspace-summary-card';
    const value = document.createElement('strong');
    value.textContent = item.value;
    const label = document.createElement('span');
    label.textContent = item.label;
    card.append(value, label);
    grid.appendChild(card);
  }
  return grid;
}

function createEmptyState(message) {
  const paragraph = document.createElement('p');
  paragraph.className = 'workspace-empty-state';
  paragraph.textContent = message;
  return paragraph;
}

async function loadStudentAttendanceScreen(container) {
  const summaries = await api.request('/academic/attendance/my');
  const list = Array.isArray(summaries) ? summaries : [];
  container.replaceChildren();
  if (list.length === 0) {
    container.appendChild(
      createEmptyState('Você não possui matrículas ativas para exibir a frequência.'),
    );
    showWorkspaceMessage('Nenhuma matrícula ativa encontrada.');
    return;
  }

  const totals = list.reduce(
    (accumulator, item) => ({
      classes: accumulator.classes + Number(item.total_classes || 0),
      present: accumulator.present + Number(item.present_count || 0),
      absent: accumulator.absent + Number(item.absent_count || 0),
      justified: accumulator.justified + Number(item.justified_count || 0),
    }),
    { classes: 0, present: 0, absent: 0, justified: 0 },
  );
  const overall = totals.classes > 0 ? (totals.present / totals.classes) * 100 : 0;

  container.appendChild(
    createSummaryGrid([
      { label: 'Frequência geral', value: formatPercentage(overall) },
      { label: 'Aulas registradas', value: String(totals.classes) },
      { label: 'Presenças', value: String(totals.present) },
      { label: 'Faltas', value: String(totals.absent) },
      { label: 'Faltas justificadas', value: String(totals.justified) },
    ]),
  );

  for (const summary of list) {
    const section = document.createElement('section');
    section.className = 'workspace-attendance-card';

    const header = document.createElement('div');
    header.className = 'workspace-exam-card-header';
    const title = document.createElement('div');
    const heading = document.createElement('h2');
    heading.className = 'workspace-exam-title';
    heading.textContent = summary.subject_name || summary.class_name;
    const context = document.createElement('p');
    context.className = 'workspace-exam-context';
    context.textContent = `${summary.class_code} — ${summary.class_name}`;
    title.append(heading, context);
    const badge = document.createElement('span');
    badge.className = 'workspace-exam-status';
    badge.textContent = formatPercentage(summary.percentage);
    header.append(title, badge);
    section.appendChild(header);

    const details = document.createElement('dl');
    details.className = 'workspace-exam-details';
    const detailValues = [
      ['Aulas', String(summary.total_classes ?? 0)],
      ['Presenças', String(summary.present_count ?? 0)],
      ['Faltas', String(summary.absent_count ?? 0)],
      ['Justificadas', String(summary.justified_count ?? 0)],
    ];
    for (const [term, value] of detailValues) {
      const wrapper = document.createElement('div');
      const dt = document.createElement('dt');
      dt.textContent = term;
      const dd = document.createElement('dd');
      dd.textContent = value;
      wrapper.append(dt, dd);
      details.appendChild(wrapper);
    }
    section.appendChild(details);

    const records = Array.isArray(summary.records) ? summary.records : [];
    if (records.length === 0) {
      section.appendChild(
        createEmptyState('Ainda não há chamadas registradas para esta turma.'),
      );
    } else {
      const wrap = document.createElement('div');
      wrap.className = 'workspace-table-wrap';
      const table = document.createElement('table');
      table.innerHTML = `
        <thead>
          <tr><th>Data</th><th>Situação</th><th>Justificativa</th></tr>
        </thead>
      `;
      const body = document.createElement('tbody');
      for (const record of [...records].reverse()) {
        const row = document.createElement('tr');
        const dateCell = document.createElement('td');
        dateCell.textContent = record.date || '—';
        const statusCell = document.createElement('td');
        if (record.is_present) {
          statusCell.textContent = 'Presente';
        } else if (record.justified) {
          statusCell.textContent = 'Falta justificada';
        } else {
          statusCell.textContent = 'Falta';
        }
        const justificationCell = document.createElement('td');
        justificationCell.textContent = record.justification || '—';
        row.append(dateCell, statusCell, justificationCell);
        body.appendChild(row);
      }
      table.appendChild(body);
      wrap.appendChild(table);
      section.appendChild(wrap);
    }

    container.appendChild(section);
  }

  showWorkspaceMessage(
    `Frequência de ${list.length} matrícula(s) ativa(s): ${formatPercentage(overall)} de presença.`,
  );
}

async function loadStudentScheduleScreen(container) {
  const items = await api.request('/academic/schedule/my');
  const schedule = Array.isArray(items) ? items : [];
  container.replaceChildren();
  if (schedule.length === 0) {
    container.appendChild(createEmptyState('Nenhuma turma ativa vinculada ao seu perfil.'));
    showWorkspaceMessage('Nenhuma turma encontrada.');
    return;
  }

  const weekly = new Map(WEEK_DAYS.map(day => [day.label, []]));
  for (const item of schedule) {
    const parsed = parseSchedule(item.schedule);
    for (const day of parsed.days) {
      if (!weekly.has(day)) weekly.set(day, []);
      weekly.get(day).push({ item, time: parsed.time });
    }
  }

  const weekSection = document.createElement('section');
  const weekTitle = document.createElement('h2');
  weekTitle.textContent = 'Grade semanal';
  weekSection.appendChild(weekTitle);
  const weekGrid = document.createElement('div');
  weekGrid.className = 'workspace-week-grid';
  for (const [day, entries] of weekly) {
    const column = document.createElement('article');
    column.className = 'workspace-week-day';
    const heading = document.createElement('h3');
    heading.textContent = day;
    column.appendChild(heading);
    if (entries.length === 0) {
      const empty = document.createElement('p');
      empty.className = 'workspace-empty-state';
      empty.textContent = 'Sem aulas';
      column.appendChild(empty);
    }
    for (const entry of entries) {
      const slot = document.createElement('div');
      slot.className = 'workspace-week-slot';
      const time = document.createElement('strong');
      time.textContent = entry.time || 'Horário não informado';
      const subject = document.createElement('span');
      subject.textContent = entry.item.subject_name || entry.item.class_name;
      const room = document.createElement('span');
      room.textContent = [entry.item.classroom, entry.item.teacher_name]
        .filter(Boolean)
        .join(' · ');
      slot.append(time, subject, room);
      column.appendChild(slot);
    }
    weekGrid.appendChild(column);
  }
  weekSection.appendChild(weekGrid);
  container.appendChild(weekSection);

  const detailSection = document.createElement('section');
  const detailTitle = document.createElement('h2');
  detailTitle.textContent = 'Detalhes das turmas';
  detailSection.appendChild(detailTitle);
  const wrap = document.createElement('div');
  wrap.className = 'workspace-table-wrap';
  const table = document.createElement('table');
  table.innerHTML = `
    <thead>
      <tr>
        <th>Disciplina</th><th>Turma</th><th>Horário</th>
        <th>Professor</th><th>Sala</th><th>Período</th>
      </tr>
    </thead>
  `;
  const body = document.createElement('tbody');
  for (const item of schedule) {
    const row = document.createElement('tr');
    const values = [
      item.subject_name || '—',
      `${item.class_code} — ${item.class_name}`,
      item.schedule || 'A definir',
      item.teacher_name || '—',
      item.classroom || '—',
      item.period_name || `${item.semester}º semestre de ${item.year}`,
    ];
    for (const value of values) {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.appendChild(cell);
    }
    body.appendChild(row);
  }
  table.appendChild(body);
  wrap.appendChild(table);
  detailSection.appendChild(wrap);
  container.appendChild(detailSection);

  showWorkspaceMessage(`${schedule.length} turma(s) na sua grade horária.`);
}

/* ==================== Administração ==================== */

async function loadStorageUsageScreen(container) {
  const usage = await api.request('/admin/settings/storage');
  const folders = Array.isArray(usage.folders) ? usage.folders : [];
  container.replaceChildren();

  container.appendChild(
    createSummaryGrid([
      { label: 'Total utilizado', value: formatFileSize(usage.total_bytes) },
      {
        label: 'Banco de dados',
        value: formatFileSize(usage.database_bytes),
      },
      {
        label: 'Espaço livre em disco',
        value: usage.free_bytes === null ? '—' : formatFileSize(usage.free_bytes),
      },
      { label: 'Pastas monitoradas', value: String(folders.length) },
    ]),
  );

  const wrap = document.createElement('div');
  wrap.className = 'workspace-table-wrap';
  const table = document.createElement('table');
  table.innerHTML = `
    <thead>
      <tr><th>Pasta</th><th>Arquivos</th><th>Tamanho</th><th>Caminho</th></tr>
    </thead>
  `;
  const body = document.createElement('tbody');
  for (const folder of folders) {
    const row = document.createElement('tr');
    const labelCell = document.createElement('td');
    labelCell.textContent = folder.label;
    const countCell = document.createElement('td');
    countCell.textContent = folder.exists ? String(folder.file_count) : 'Pasta ausente';
    const sizeCell = document.createElement('td');
    sizeCell.textContent = formatFileSize(folder.total_bytes);
    const pathCell = document.createElement('td');
    pathCell.className = 'workspace-path-cell';
    pathCell.textContent = folder.path;
    row.append(labelCell, countCell, sizeCell, pathCell);
    body.appendChild(row);
  }
  if (usage.database_path) {
    const row = document.createElement('tr');
    const labelCell = document.createElement('td');
    labelCell.textContent = 'Banco de dados (SQLite)';
    const countCell = document.createElement('td');
    countCell.textContent = '1';
    const sizeCell = document.createElement('td');
    sizeCell.textContent = formatFileSize(usage.database_bytes);
    const pathCell = document.createElement('td');
    pathCell.className = 'workspace-path-cell';
    pathCell.textContent = usage.database_path;
    row.append(labelCell, countCell, sizeCell, pathCell);
    body.appendChild(row);
  }
  table.appendChild(body);
  wrap.appendChild(table);
  container.appendChild(wrap);

  showWorkspaceMessage(
    `Uso total de ${formatFileSize(usage.total_bytes)} em ${folders.length} pasta(s).`,
  );
}

