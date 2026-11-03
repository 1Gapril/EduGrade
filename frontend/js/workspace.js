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
    description: 'Informações de armazenamento ainda não são disponibilizadas pela API.',
    roles: ['admin'],
    message: 'A consulta de uso e gerenciamento de arquivos ainda não está implementada.',
  },
  '/exams/list.html': {
    title: 'Banco de provas',
    description: 'Provas cadastradas no sistema.',
    roles: ['admin', 'teacher'],
    endpoint: '/exams?page=1&page_size=100',
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
    description: 'A edição de provas pela interface ainda não está implementada.',
    roles: ['admin', 'teacher'],
    message: 'A API permite atualizar uma prova, mas esta tela ainda não possui formulário de edição.',
    examDetail: true,
  },
  '/professor/exams.html': {
    title: 'Minhas provas',
    description: 'Provas cadastradas no sistema.',
    roles: ['teacher'],
    endpoint: '/exams?page=1&page_size=100',
  },
  '/aluno/exams.html': {
    title: 'Minhas provas',
    description: 'Provas disponíveis no sistema.',
    roles: ['student'],
    endpoint: '/exams?page=1&page_size=100',
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
    message: 'A impressão depende da seleção de uma prova publicada. Selecione uma prova no banco de provas para continuar.',
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
    endpoint: '/academic/classes?page=1&page_size=100',
  },
  '/professor/corrections.html': {
    title: 'Correções pendentes',
    description: 'Correções que aguardam revisão.',
    roles: ['teacher'],
    endpoint: '/ai/reviews/pending',
  },
  '/professor/grades.html': {
    title: 'Lançar notas',
    description: 'A consulta de notas ainda não está disponível pela API.',
    roles: ['teacher'],
    message: 'O lançamento de notas existe na API, mas esta tela ainda não possui formulário para selecionar turma e aluno.',
  },
  '/professor/class-detail.html': {
    title: 'Detalhes da turma',
    description: 'Turmas cadastradas no sistema.',
    roles: ['teacher'],
    endpoint: '/academic/classes?page=1&page_size=100',
    classDetail: true,
  },
  '/aluno/grades.html': {
    title: 'Minhas notas',
    description: 'A consulta de notas do aluno ainda não está disponível pela API.',
    roles: ['student'],
    message: 'O sistema ainda não possui uma operação de consulta de notas para esta tela.',
  },
  '/aluno/attendance.html': {
    title: 'Frequência',
    description: 'A consulta de frequência do aluno ainda não está disponível pela API.',
    roles: ['student'],
    message: 'A API permite consultar a frequência de uma matrícula específica, mas esta tela ainda não carrega a matrícula do aluno.',
  },
  '/aluno/schedule.html': {
    title: 'Grade horária',
    description: 'A consulta de grade horária ainda não está disponível pela API.',
    roles: ['student'],
    message: 'O sistema ainda não possui uma operação de consulta de grade horária para esta tela.',
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

function createUserCell(value) {
  const cell = document.createElement('td');
  cell.textContent = value === null || value === undefined ? '-' : String(value);
  return cell;
}

function renderUsersTable(container, users) {
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
      const button = document.createElement('button');
      button.type = 'button';
      button.className = user.is_active ? 'btn btn-danger btn-sm' : 'btn btn-secondary btn-sm';
      button.dataset.userId = user.id;
      button.dataset.nextActive = String(!user.is_active);
      button.textContent = user.is_active ? 'Desativar' : 'Reativar';
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
    <div class="workspace-form-actions">
      <button class="btn btn-primary" type="submit">Criar usuário</button>
    </div>
  `;

  const message = document.createElement('div');
  message.className = 'workspace-message';
  message.id = 'users-message';
  message.hidden = true;
  const tableContainer = document.createElement('div');
  tableContainer.className = 'workspace-table-wrap';
  container.replaceChildren(form, message, tableContainer);

  const showMessage = (text, isError = false) => {
    message.textContent = text;
    message.hidden = false;
    message.classList.toggle('workspace-error', isError);
  };

  const refreshUsers = async () => {
    tableContainer.textContent = 'Carregando usuários...';
    const response = await api.request('/users?page=1&page_size=100&active_only=false');
    renderUsersTable(tableContainer, response.items || []);
  };

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    UI.setLoading(button, true);
    message.hidden = true;
    try {
      const data = Object.fromEntries(new FormData(form).entries());
      await api.create('/users', data);
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

async function loadCreateExamScreen(container) {
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
    importStatus.textContent = 'Lendo os PDFs e extraindo questões e gabaritos. Aguarde...';
    try {
      const response = await fetch(`${api.baseURL}/exams/analyze-pdfs`, {
        method: 'POST',
        headers: api.accessToken ? { Authorization: 'Bearer ' + api.accessToken } : {},
        body,
      });
      const result = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(result.detail)
          ? result.detail.map(item => item.msg).join('; ')
          : result.detail || result.message;
        const errorMessage = [result.message, detail]
          .filter((message, index, messages) => message && messages.indexOf(message) === index)
          .join(' ');
        throw new Error(errorMessage || 'Não foi possível ler os PDFs.');
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
      importStatus.classList.add('workspace-error');
      importStatus.textContent = error.message || 'Não foi possível ler os PDFs.';
    } finally {
      UI.setLoading(button, false);
    }
  });

  try {
    const [classesResponse, periodsResponse] = await Promise.all([
      api.request('/academic/classes?page=1&page_size=100'),
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

    if (classes.length === 0) {
      showWorkspaceMessage('Cadastre uma turma, disciplina e período letivo antes de criar uma prova.', true);
      classSelect.disabled = true;
      form.querySelector('#save-exam').disabled = true;
      return;
    }
  } catch (error) {
    showWorkspaceMessage(error.message || 'Não foi possível carregar turmas e períodos.', true);
    form.querySelector('#save-exam').disabled = true;
    return;
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

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!savedExam) {
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
          return;
        }
        if (question.type !== 'multiple_choice'
          && !question.expected_answer
          && question.keywords.length === 0
          && question.required_concepts.length === 0) {
          showWorkspaceMessage(`Preencha o gabarito da questão ${index + 1}.`, true);
          return;
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
        form.querySelectorAll('input, select, textarea, button').forEach(element => {
          if (element.id !== 'save-exam') element.disabled = true;
        });
        saveButton.textContent = 'Prova salva. Publicar para correção por IA';
        showWorkspaceMessage(
          `Prova salva com ${questions.length} questão(ões) e gabaritos. Publicando versão para impressão e correção.`,
        );
      } catch (error) {
        showWorkspaceMessage(error.message || 'Não foi possível salvar a prova e os gabaritos.', true);
        UI.setLoading(saveButton, false);
        return;
      }
    }

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
        `/students?class_id=${encodeURIComponent(selectedVersion.class_id)}&page=1&page_size=100`,
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
    let submission = null;
    try {
      showWorkspaceMessage('Preparando a submissão...');
      const copies = await api.create(
        `/exams/versions/${encodeURIComponent(selectedVersion.version_id)}/copies?count=1&student_ids=${encodeURIComponent(selectedStudent.id)}`,
        {},
      );
      if (!Array.isArray(copies) || !copies[0]?.id) {
        throw new Error('Não foi possível criar a cópia vinculada ao aluno.');
      }

      const body = new FormData();
      body.append('copy_id', copies[0].id);
      for (const file of files) body.append('files', file);
      submission = await api.request('/exams/submissions', { method: 'POST', body });

      showWorkspaceMessage('Prova enviada. Iniciando leitura das respostas...');
      const ocrResult = await api.create(`/exams/submissions/${submission.id}/process-ocr`, {});
      if (ocrResult.answers_extracted === 0) {
        throw new Error(
          'A prova foi recebida, mas o OCR não identificou respostas numeradas. Confira a legibilidade e a numeração das questões.',
        );
      }

      showWorkspaceMessage('Respostas identificadas. Comparando com o gabarito publicado...');
      const correction = await api.create('/ai/batch-correct', { submission_id: submission.id });
      if (correction.total_processed === 0 && correction.failed === 0) {
        throw new Error('A prova foi recebida, mas não foram encontradas respostas legíveis para corrigir.');
      }
      showWorkspaceMessage(
        `Correção iniciada para ${selectedStudent.user.full_name}: ${correction.total_processed} questão(ões) processada(s), ${correction.requires_review_count} aguardando conferência, ${correction.skipped} sem resposta reconhecida e ${correction.failed} falha(s).`,
      );
      form.reset();
      studentSelect.disabled = true;
      submitButton.disabled = true;
    } catch (error) {
      const message = error.message || 'Não foi possível enviar e corrigir a prova.';
      if (submission) {
        form.reset();
        studentSelect.disabled = true;
        submitButton.disabled = true;
      }
      showWorkspaceMessage(
        submission
          ? `${message} A submissão ${submission.id} foi salva; confira o status antes de reenviar para evitar duplicidade.`
          : message,
        true,
      );
    } finally {
      UI.setLoading(submitButton, false);
      submitButton.disabled = Boolean(submission) || !versionSelect.value || !studentSelect.value;
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

  if (screen.createExam) {
    await loadCreateExamScreen(content);
    return;
  }

  if (screen.uploadExams) {
    await loadUploadExamsScreen(content);
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
      renderWorkspaceTable(sectionContent, normalizeRows(result.data));
      content.appendChild(sectionContent);
    }
  } catch (error) {
    content.replaceChildren();
    showWorkspaceMessage(error.message || 'Não foi possível carregar os dados desta tela.', true);
  }
}

document.addEventListener('DOMContentLoaded', loadWorkspaceScreen);
