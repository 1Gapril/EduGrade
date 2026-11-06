/**
 * EduGrade - Main JavaScript Application
 * Common utilities, API client, and shared components
 */

// ============================================================
// Configuration
// ============================================================
const CONFIG = {
  API_BASE: '/api/v1',
  TOKEN_KEY: 'edugrade_token',
  REFRESH_KEY: 'edugrade_refresh',
  USER_KEY: 'edugrade_user',
};

// ============================================================
// API Client
// ============================================================
class APIClient {
  constructor() {
    this.baseURL = CONFIG.API_BASE;
    this.accessToken = localStorage.getItem(CONFIG.TOKEN_KEY);
    this.refreshToken = localStorage.getItem(CONFIG.REFRESH_KEY);
  }

  setTokens(access, refresh) {
    this.accessToken = access;
    this.refreshToken = refresh;
    if (access) localStorage.setItem(CONFIG.TOKEN_KEY, access);
    if (refresh) localStorage.setItem(CONFIG.REFRESH_KEY, refresh);
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.REFRESH_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };
    const isFormData = typeof FormData !== 'undefined' && config.body instanceof FormData;

    if (isFormData) {
      delete config.headers['Content-Type'];
    } else if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      let response = await fetch(url, config);

      // Handle token refresh on 401
      if (response.status === 401 && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          config.headers = this.getHeaders();
          if (isFormData) delete config.headers['Content-Type'];
          response = await fetch(url, config);
        } else {
          this.clearTokens();
          window.location.href = '/login.html';
          return;
        }
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
        const detail = Array.isArray(error.detail)
          ? error.detail.map(item => item.msg || 'Confira os dados enviados.').join('; ')
          : error.detail;
        throw new APIError(response.status, detail || error.message || 'Erro na requisição');
      }

      if (response.status === 204) return null;
      return await response.json();
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError(0, error.message || 'Erro de conexão');
    }
  }

  async download(endpoint, filename, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const requestOptions = { ...options };
    const headers = { ...(requestOptions.headers || {}) };
    if (this.accessToken) headers.Authorization = 'Bearer ' + this.accessToken;
    if (
      requestOptions.body
      && typeof requestOptions.body === 'object'
      && !(requestOptions.body instanceof FormData)
    ) {
      headers['Content-Type'] = 'application/json';
      requestOptions.body = JSON.stringify(requestOptions.body);
    }

    try {
      let response = await fetch(url, { ...requestOptions, headers });
      if (response.status === 401 && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          headers.Authorization = 'Bearer ' + this.accessToken;
          response = await fetch(url, { ...requestOptions, headers });
        } else {
          this.clearTokens();
          window.location.href = '/login.html';
          return;
        }
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Não foi possível baixar o arquivo.' }));
        const detail = Array.isArray(error.detail)
          ? error.detail.map(item => item.msg || 'Confira os dados enviados.').join('; ')
          : error.detail;
        throw new APIError(response.status, detail || error.message || 'Erro no download');
      }

      const objectUrl = URL.createObjectURL(await response.blob());
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = filename || 'material';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError(0, error.message || 'Erro de conexão ao baixar o material');
    }
  }

  async refreshAccessToken() {
    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        this.setTokens(data.access_token, data.refresh_token);
        return true;
      }
    } catch (e) {
      // Ignore
    }
    return false;
  }

  // Auth
  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Credenciais inválidas' }));
      throw new APIError(response.status, error.message || error.detail || 'Credenciais inválidas');
    }

    const data = await response.json();
    this.setTokens(data.access_token, data.refresh_token);
    return data;
  }

  async getProfile() {
    return this.request('/auth/me');
  }

  async logout() {
    await this.request('/auth/logout', { method: 'POST' }).catch(() => {});
    this.clearTokens();
  }

  // Generic CRUD
  async list(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`${endpoint}?${query}`);
  }

  async get(endpoint, id) {
    return this.request(`${endpoint}/${id}`);
  }

  async create(endpoint, data) {
    return this.request(endpoint, { method: 'POST', body: data });
  }

  async update(endpoint, id, data) {
    return this.request(`${endpoint}/${id}`, { method: 'PUT', body: data });
  }

  async patch(endpoint, id, data) {
    return this.request(`${endpoint}/${id}`, { method: 'PATCH', body: data });
  }

  async delete(endpoint, id) {
    return this.request(`${endpoint}/${id}`, { method: 'DELETE' });
  }

  // File upload
  async upload(endpoint, file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${this.baseURL}${endpoint}`);
      if (this.accessToken) {
        xhr.setRequestHeader('Authorization', `Bearer ${this.accessToken}`);
      }

      xhr.upload.onprogress = (e) => {
        if (onProgress && e.lengthComputable) {
          onProgress((e.loaded / e.total) * 100);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new APIError(xhr.status, JSON.parse(xhr.responseText)?.detail || 'Erro no upload'));
        }
      };

      xhr.onerror = () => reject(new APIError(0, 'Erro de conexão'));
      xhr.send(formData);
    });
  }

  /**
   * Envia um FormData com progresso real de transferência (XHR).
   * Usado pelo ProgressManager nas operações de upload do EduGrade.
   */
  uploadForm(endpoint, formData, { method = 'POST', onProgress } = {}) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open(method, `${this.baseURL}${endpoint}`);
      if (this.accessToken) {
        xhr.setRequestHeader('Authorization', `Bearer ${this.accessToken}`);
      }
      xhr.upload.onprogress = event => {
        if (onProgress && event.lengthComputable) {
          onProgress({
            loaded: event.loaded,
            total: event.total,
            percent: (event.loaded / event.total) * 100,
          });
        }
      };
      xhr.onload = () => {
        let body = null;
        try {
          body = JSON.parse(xhr.responseText);
        } catch {
          body = null;
        }
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(body);
          return;
        }
        const detail = Array.isArray(body?.detail)
          ? body.detail.map(item => item.msg || 'Confira os dados enviados.').join('; ')
          : body?.detail || body?.message || `Falha no envio (HTTP ${xhr.status})`;
        reject(new APIError(xhr.status, detail));
      };
      xhr.onerror = () => reject(new APIError(0, 'Falha de conexão durante o envio'));
      xhr.ontimeout = () => reject(new APIError(0, 'Tempo esgotado durante o envio'));
      xhr.send(formData);
    });
  }
}

class APIError extends Error {
  constructor(status, message) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

// Singleton instance
const api = new APIClient();

// ============================================================
// State Management
// ============================================================
const State = {
  user: null,
  sidebarOpen: false,
  sidebarCollapsed: false,

  init() {
    const stored = localStorage.getItem(CONFIG.USER_KEY);
    if (stored) {
      try {
        this.user = JSON.parse(stored);
      } catch {
        this.clearUser();
      }
    }
    this.sidebarCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
    this.applySidebarState();
  },

  setUser(user) {
    this.user = user;
    localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
  },

  clearUser() {
    this.user = null;
    localStorage.removeItem(CONFIG.USER_KEY);
  },

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
    document.body.classList.toggle('sidebar-open', this.sidebarOpen);
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) overlay.classList.toggle('active', this.sidebarOpen);
  },

  closeSidebar() {
    this.sidebarOpen = false;
    document.body.classList.remove('sidebar-open');
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) overlay.classList.remove('active');
  },

  toggleSidebarCollapse() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
    localStorage.setItem('sidebar_collapsed', this.sidebarCollapsed);
    this.applySidebarState();
  },

  applySidebarState() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.toggle('collapsed', this.sidebarCollapsed);
    }
  },

  hasRole(...roles) {
    return this.user && roles.includes(this.user.role);
  },

  isAuthenticated() {
    return !!this.user && !!api.accessToken;
  },
};

// ============================================================
// UI Components
// ============================================================
const UI = {
  // Toast notifications
  toasts: [],

  showToast(message, type = 'info', duration = 5000) {
    const container = this.getToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <i class="toast-icon ${this.getToastIcon(type)}"></i>
        <span class="toast-message">${this.escapeHtml(message)}</span>
      </div>
      <button class="toast-close" aria-label="Fechar">&times;</button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => this.removeToast(toast));
    container.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => toast.classList.add('show'));

    // Auto remove
    setTimeout(() => this.removeToast(toast), duration);
  },

  showError(message) {
    this.showToast(message, 'error');
  },

  showSuccess(message) {
    this.showToast(message, 'success');
  },

  getToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    return container;
  },

  removeToast(toast) {
    toast.classList.remove('show');
    toast.addEventListener('transitionend', () => toast.remove());
  },

  getToastIcon(type) {
    const icons = {
      success: 'check-circle',
      error: 'x-circle',
      warning: 'alert-triangle',
      info: 'info-circle',
    };
    return icons[type] || 'info-circle';
  },

  // Modals
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
      // Focus first focusable element
      const focusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      if (focusable) focusable.focus();
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  closeAllModals() {
    document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
    document.body.style.overflow = '';
  },

  // Loading states
  setLoading(element, loading) {
    if (loading) {
      element.classList.add('loading');
      element.disabled = true;
      const spinner = document.createElement('span');
      spinner.className = 'spinner';
      element.prepend(spinner);
    } else {
      element.classList.remove('loading');
      element.disabled = false;
      const spinner = element.querySelector('.spinner');
      if (spinner) spinner.remove();
    }
  },

  // Form handling
  serializeForm(form) {
    const data = {};
    new FormData(form).forEach((value, key) => {
      if (data[key]) {
        if (!Array.isArray(data[key])) data[key] = [data[key]];
        data[key].push(value);
      } else {
        data[key] = value;
      }
    });
    return data;
  },

  fillForm(form, data) {
    Object.entries(data).forEach(([key, value]) => {
      const input = form.querySelector(`[name="${key}"]`);
      if (input) {
        if (input.type === 'checkbox') {
          input.checked = value;
        } else if (input.type === 'radio') {
          const radio = form.querySelector(`[name="${key}"][value="${value}"]`);
          if (radio) radio.checked = true;
        } else {
          input.value = value;
        }
      }
    });
  },

  showFormErrors(form, errors) {
    this.clearFormErrors(form);
    Object.entries(errors).forEach(([field, messages]) => {
      const input = form.querySelector(`[name="${field}"]`);
      if (input) {
        input.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = Array.isArray(messages) ? messages[0] : messages;
        input.parentNode.appendChild(errorDiv);
      }
    });
  },

  clearFormErrors(form) {
    form.querySelectorAll('.form-error').forEach(e => e.remove());
    form.querySelectorAll('.form-input.error').forEach(e => e.classList.remove('error'));
  },

  // Table utilities
  renderTable(container, { columns, data, actions, emptyMessage = 'Nenhum registro encontrado' }) {
    if (!data || data.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path><line x1="9" y1="12" x2="9" y2="12"></line></svg>
          <h3 class="empty-state-title">Sem dados</h3>
          <p class="empty-state-message">${this.escapeHtml(emptyMessage)}</p>
        </div>
      `;
      return;
    }

    const table = document.createElement('div');
    table.className = 'table-container';
    table.innerHTML = `
      <table class="table">
        <thead>
          <tr>
            ${columns.map(c => `<th${c.width ? ` style="width: ${c.width}"` : ''}>${this.escapeHtml(c.title)}</th>`).join('')}
            ${actions ? '<th style="width: 120px;">Ações</th>' : ''}
          </tr>
        </thead>
        <tbody>
          ${data.map(row => `
            <tr>
              ${columns.map(c => `<td>${this.renderCell(row, c)}</td>`).join('')}
              ${actions ? `<td>${this.renderActions(row, actions)}</td>` : ''}
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    container.innerHTML = '';
    container.appendChild(table);
  },

  renderCell(row, column) {
    const value = column.key ? this.getNestedValue(row, column.key) : '';
    if (column.render) return column.render(value, row);
    if (column.type === 'badge') return this.renderBadge(value, column.badgeMap);
    if (column.type === 'date') return value ? new Date(value).toLocaleDateString('pt-BR') : '-';
    if (column.type === 'datetime') return value ? new Date(value).toLocaleString('pt-BR') : '-';
    return this.escapeHtml(value ?? '-');
  },

  renderBadge(value, badgeMap = {}) {
    const config = badgeMap[value] || { class: 'gray', label: value };
    return `<span class="badge-status ${config.class}">${this.escapeHtml(config.label)}</span>`;
  },

  renderActions(row, actions) {
    return actions.map(action => {
      const show = !action.condition || action.condition(row);
      if (!show) return '';
      const onclick = action.onclick ? `onclick="${action.onclick}('${row.id}')"` : '';
      return `<button class="btn btn-ghost btn-sm" ${onclick} title="${this.escapeHtml(action.title)}"><i class="${action.icon}"></i></button>`;
    }).join(' ');
  },

  getNestedValue(obj, path) {
    return path.split('.').reduce((o, k) => o?.[k], obj);
  },

  // Progress bar
  renderProgress(percentage, label = '', variant = 'primary') {
    return `
      <div class="progress-wrapper">
        ${label ? `<div class="progress-label">${this.escapeHtml(label)}</div>` : ''}
        <div class="progress">
          <div class="progress-bar ${variant !== 'primary' ? variant : ''}" style="width: ${percentage}%"></div>
        </div>
        <div class="progress-text">${percentage}%</div>
      </div>
    `;
  },

  // Utility
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  formatDate(dateStr, options = {}) {
    if (!dateStr) return '-';
    const defaultOptions = { day: '2-digit', month: '2-digit', year: 'numeric', ...options };
    return new Date(dateStr).toLocaleDateString('pt-BR', defaultOptions);
  },

  formatDateTime(dateStr) {
    return this.formatDate(dateStr, { hour: '2-digit', minute: '2-digit' });
  },

  formatNumber(num, decimals = 0) {
    if (num === null || num === undefined) return '-';
    return Number(num).toLocaleString('pt-BR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  },

  truncate(text, length = 50) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
  },
};

// ============================================================
// Authentication
// ============================================================
const Auth = {
  dashboardPath(user = State.user) {
    const dashboardPaths = {
      admin: '/admin/dashboard.html',
      teacher: '/professor/dashboard.html',
      student: '/aluno/dashboard.html',
    };
    return dashboardPaths[user?.role] || '/dashboard.html';
  },

  async init() {
    if (!api.accessToken) return false;

    try {
      const user = await api.getProfile();
      State.setUser(user);
      return true;
    } catch {
      api.clearTokens();
      State.clearUser();
      return false;
    }
  },

  async login(username, password) {
    const data = await api.login(username, password);
    const user = await api.getProfile();
    State.setUser(user);
    return user;
  },

  async logout() {
    await api.logout();
    State.clearUser();
    window.location.href = '/login.html';
  },

  requireAuth() {
    if (!State.isAuthenticated()) {
      window.location.href = '/login.html';
      return false;
    }
    return true;
  },

  requireRole(...roles) {
    if (!this.requireAuth()) return false;
    if (!State.hasRole(...roles)) {
      UI.showToast('Acesso negado', 'error');
      window.location.href = '/dashboard.html';
      return false;
    }
    return true;
  },
};

// ============================================================
// Sidebar Navigation
// ============================================================
const Sidebar = {
  init() {
    this.bindEvents();
    this.setActiveLink();
    State.applySidebarState();
  },

  bindEvents() {
    // Toggle sidebar on mobile
    const toggle = document.getElementById('sidebar-toggle');
    if (toggle) {
      toggle.addEventListener('click', () => State.toggleSidebar());
    }

    // Sidebar overlay
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => State.closeSidebar());
    }

    // Collapse sidebar
    const collapseBtn = document.getElementById('sidebar-collapse');
    if (collapseBtn) {
      collapseBtn.addEventListener('click', () => State.toggleSidebarCollapse());
    }

    // Nav items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        if (item.dataset.href) {
          // Allow normal navigation
          return;
        }
        e.preventDefault();
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });

    // User dropdown
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');
    if (userMenuBtn && userDropdown) {
      userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('active');
      });
      document.addEventListener('click', () => userDropdown.classList.remove('active'));
    }

    // Logout
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => Auth.logout());
    }
  },

  setActiveLink() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item[data-href]').forEach(item => {
      if (item.dataset.href === path) {
        item.classList.add('active');
      }
    });
  },

  renderUserInfo() {
    if (!State.user) return;

    const nameEl = document.getElementById('user-name');
    const roleEl = document.getElementById('user-role');
    const avatarEl = document.getElementById('user-avatar');

    if (nameEl) nameEl.textContent = State.user.name || State.user.username;
    if (roleEl) roleEl.textContent = State.user.role;
    if (avatarEl) avatarEl.textContent = (State.user.name || State.user.username)[0].toUpperCase();
  },
};

// ============================================================
// Page Base Class
// ============================================================
class Page {
  constructor(options = {}) {
    this.requiresAuth = options.requiresAuth !== false;
    this.requiredRoles = options.roles || [];
  }

  async init() {
    if (this.requiresAuth && !Auth.requireAuth()) return;
    if (this.requiredRoles.length && !Auth.requireRole(...this.requiredRoles)) return;

    Sidebar.init();
    Sidebar.renderUserInfo();
    await this.onInit();
  }

  async onInit() {
    // Override in subclasses
  }

  showError(message) {
    UI.showToast(message, 'error');
  }

  showSuccess(message) {
    UI.showToast(message, 'success');
  }
}

// ============================================================
// Initialize on DOM ready
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  // Add toast styles if not present
  if (!document.getElementById('toast-styles')) {
    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
      .toast-container { position: fixed; top: 1rem; right: 1rem; z-index: 2000; display: flex; flex-direction: column; gap: 0.5rem; }
      .toast { background: var(--color-white); border: 1px solid var(--color-gray-200); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); box-shadow: var(--shadow-lg); min-width: 300px; max-width: 450px; transform: translateX(120%); opacity: 0; transition: all var(--transition-fast); }
      .toast.show { transform: translateX(0); opacity: 1; }
      .toast-success { border-left: 4px solid var(--color-success); }
      .toast-error { border-left: 4px solid var(--color-danger); }
      .toast-warning { border-left: 4px solid var(--color-warning); }
      .toast-info { border-left: 4px solid var(--color-info); }
      .toast-content { display: flex; align-items: center; gap: var(--space-2); flex: 1; }
      .toast-icon { width: 20px; height: 20px; flex-shrink: 0; }
      .toast-success .toast-icon { color: var(--color-success); }
      .toast-error .toast-icon { color: var(--color-danger); }
      .toast-warning .toast-icon { color: var(--color-warning); }
      .toast-info .toast-icon { color: var(--color-info); }
      .toast-close { background: none; border: none; font-size: 1.25rem; color: var(--color-gray-400); cursor: pointer; padding: 0; line-height: 1; }
      .toast-close:hover { color: var(--color-gray-700); }
      .progress-wrapper { display: flex; align-items: center; gap: var(--space-2); }
      .progress-label { min-width: 120px; font-size: 0.875rem; }
      .progress-text { min-width: 45px; text-align: right; font-size: 0.75rem; color: var(--color-gray-500); }
      .btn.loading { position: relative; color: transparent; pointer-events: none; }
      .btn.loading .spinner { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }
    `;
    document.head.appendChild(style);
  }

  // Feather icons replacement (simple SVG icons)
  window.feather = {
    icons: {
      'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>',
      'x': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>',
      'chevron-left': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>',
      'chevron-right': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>',
      'home': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>',
      'users': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
      'book-open': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>',
      'file-text': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
      'check-circle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
      'x-circle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
      'alert-triangle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
      'info-circle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
      'bell': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>',
      'user': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
      'log-out': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>',
      'settings': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
      'upload': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',
      'download': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',
      'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
      'filter': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>',
      'plus': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>',
      'edit': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>',
      'trash': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>',
      'eye': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>',
      'check': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>',
      'arrow-left': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>',
      'arrow-right': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>',
      'refresh-cw': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>',
      'activity': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
      'database': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
      'graduation-cap': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 21l-6-6-6 6"></path><path d="M21 21l-6-6-6 6"></path></svg>',
    },
    replace() {
      document.querySelectorAll('[data-feather]').forEach(el => {
        const icon = el.dataset.feather;
        if (this.icons[icon]) {
          el.innerHTML = this.icons[icon];
        }
      });
    },
  };
  feather.replace();
});

// Export for modules
window.api = api;
window.State = State;
window.UI = UI;
window.Auth = Auth;
window.Sidebar = Sidebar;
window.Page = Page;
window.CONFIG = CONFIG;