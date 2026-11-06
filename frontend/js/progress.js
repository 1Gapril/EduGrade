/**
 * EduGrade — ProgressManager
 * Painel global e reutilizável de acompanhamento de operações.
 *
 * Regras:
 * - O percentual exibido vem sempre de uma medida real: bytes transferidos no
 *   upload (XHR) ou contadores/etapas informados pelo backend em /jobs/{id}.
 * - Quando não existe medida confiável, a barra fica indeterminada e mostra a
 *   etapa atual — nunca um percentual inventado.
 */
const ProgressManager = (() => {
  const POLL_INTERVAL_MS = 700;
  const MAX_NETWORK_ERRORS = 3;
  const TERMINAL = ['succeeded', 'succeeded_with_warnings', 'failed', 'cancelled'];

  const STATUS_LABELS = {
    pending: 'Aguardando',
    running: 'Em andamento',
    succeeded: 'Concluído',
    succeeded_with_warnings: 'Concluído com avisos',
    failed: 'Erro',
    cancelled: 'Cancelado',
  };

  let stack = null;

  function ensureStack() {
    if (stack && document.body.contains(stack)) return stack;
    stack = document.createElement('div');
    stack.className = 'progress-stack';
    stack.setAttribute('aria-live', 'polite');
    document.body.appendChild(stack);
    return stack;
  }

  function formatBytes(bytes) {
    const value = Number(bytes) || 0;
    if (value < 1024) return `${value} B`;
    const units = ['KB', 'MB', 'GB'];
    let size = value;
    let unit = 'B';
    for (const candidate of units) {
      if (size < 1024) break;
      size /= 1024;
      unit = candidate;
    }
    return `${size.toFixed(size >= 10 ? 0 : 1)} ${unit}`;
  }

  function formatElapsed(seconds) {
    const total = Math.max(0, Math.round(Number(seconds) || 0));
    const minutes = Math.floor(total / 60);
    const rest = total % 60;
    return minutes > 0 ? `${minutes}m ${String(rest).padStart(2, '0')}s` : `${rest}s`;
  }

  class Operation {
    constructor({ title, subtitle = '', total = 0, cancelable = true }) {
      this.title = title;
      this.status = 'running';
      this.stepLabel = 'Preparando...';
      this.progress = null;
      this.processed = 0;
      this.total = total;
      this.succeeded = 0;
      this.failed = 0;
      this.skipped = 0;
      this.jobId = null;
      this.cancelable = cancelable;
      this.startedAt = Date.now();
      this.timer = null;
      this.pollTimer = null;
      this.networkErrors = 0;
      this.onDone = null;
      this.files = new Map();
      this._build(subtitle);
    }

    _build(subtitle) {
      const panel = document.createElement('section');
      panel.className = 'progress-panel is-running';
      panel.innerHTML = `
        <header class="progress-panel-header">
          <div>
            <h2 class="progress-panel-title"></h2>
            <p class="progress-panel-subtitle"></p>
          </div>
          <div class="progress-panel-actions">
            <button type="button" class="progress-panel-btn" data-action="minimize" title="Minimizar">–</button>
            <button type="button" class="progress-panel-btn" data-action="close" title="Fechar" hidden>×</button>
          </div>
        </header>
        <div class="progress-panel-body">
          <p class="progress-step"></p>
          <div class="progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100">
            <div class="progress-bar-fill"></div>
          </div>
          <div class="progress-meta">
            <span data-role="percent"></span>
            <span data-role="counters"></span>
            <span data-role="elapsed"></span>
          </div>
          <ul class="progress-files" hidden></ul>
          <div class="progress-result" hidden></div>
        </div>
        <footer class="progress-panel-footer">
          <button type="button" class="btn btn-ghost btn-sm" data-action="cancel">Cancelar</button>
        </footer>
      `;
      this.panel = panel;
      this.titleEl = panel.querySelector('.progress-panel-title');
      this.subtitleEl = panel.querySelector('.progress-panel-subtitle');
      this.stepEl = panel.querySelector('.progress-step');
      this.barEl = panel.querySelector('.progress-bar');
      this.fillEl = panel.querySelector('.progress-bar-fill');
      this.percentEl = panel.querySelector('[data-role="percent"]');
      this.countersEl = panel.querySelector('[data-role="counters"]');
      this.elapsedEl = panel.querySelector('[data-role="elapsed"]');
      this.filesEl = panel.querySelector('.progress-files');
      this.resultEl = panel.querySelector('.progress-result');
      this.cancelBtn = panel.querySelector('[data-action="cancel"]');
      this.closeBtn = panel.querySelector('[data-action="close"]');

      this.titleEl.textContent = this.title;
      this.subtitleEl.textContent = subtitle;
      this.subtitleEl.hidden = !subtitle;

      panel.querySelector('[data-action="minimize"]').addEventListener('click', () => {
        panel.classList.toggle('is-minimized');
      });
      this.closeBtn.addEventListener('click', () => this.close());
      this.cancelBtn.addEventListener('click', () => this.cancel());

      ensureStack().appendChild(panel);
      this._render();
      this.timer = window.setInterval(() => this._renderElapsed(), 1000);
    }

    // ------------------------------------------------------------- atualizações
    setTitle(title) {
      this.title = title;
      this.titleEl.textContent = title;
    }

    setStep(label, progress = null) {
      this.stepLabel = label;
      this.progress = progress === null || progress === undefined ? null : Number(progress);
      this._render();
    }

    setUpload({ loaded, total, percent }) {
      const value = Number(percent);
      this.progress = Number.isFinite(value) ? Math.min(100, Math.max(0, value)) : null;
      this.processed = Number(loaded) || 0;
      this.total = Number(total) || 0;
      this.uploadBytes = { loaded: this.processed, total: this.total };
      this.stepLabel = 'Enviando arquivo';
      this._render();
    }

    setCounters({ processed, total, succeeded, failed, skipped }) {
      if (processed !== undefined) this.processed = Number(processed) || 0;
      if (total !== undefined) this.total = Number(total) || 0;
      if (succeeded !== undefined) this.succeeded = Number(succeeded) || 0;
      if (failed !== undefined) this.failed = Number(failed) || 0;
      if (skipped !== undefined) this.skipped = Number(skipped) || 0;
      this._render();
    }

    applySnapshot(job) {
      this.jobId = job.id;
      this.status = job.status;
      if (job.step_label) this.stepLabel = job.step_label;
      this.progress = job.progress === null || job.progress === undefined ? null : Number(job.progress);
      this.processed = job.processed ?? this.processed;
      this.total = job.total ?? this.total;
      this.succeeded = job.succeeded ?? this.succeeded;
      this.failed = job.failed ?? this.failed;
      this.skipped = job.skipped ?? this.skipped;
      this.elapsedFromServer = job.elapsed_seconds;
      this.snapshotAt = Date.now();
      this.canCancel = job.can_cancel;
      this._render();
      if (TERMINAL.includes(job.status)) this._finish(job);
    }

    // ------------------------------------------------------------------- arquivos
    trackFile(id, { name, size }) {
      const item = document.createElement('li');
      item.className = 'progress-file is-pending';
      item.dataset.fileId = id;
      item.innerHTML = `
        <span class="progress-file-name"></span>
        <span class="progress-file-state">Aguardando</span>
      `;
      item.querySelector('.progress-file-name').textContent = name;
      this.filesEl.appendChild(item);
      this.filesEl.hidden = false;
      this.files.set(id, { el: item, name, size, state: 'pending', percent: 0 });
      this._renderFiles();
    }

    setFileState(id, state, percent = null, detail = '') {
      const entry = this.files.get(id);
      if (!entry) return;
      entry.state = state;
      if (percent !== null) entry.percent = Math.min(100, Math.max(0, Number(percent)));
      entry.detail = detail;
      this._renderFiles();
    }

    fileSummary() {
      const entries = [...this.files.values()];
      return {
        total: entries.length,
        sent: entries.filter(entry => entry.state === 'done').length,
        pending: entries.filter(entry => entry.state === 'pending').length,
        uploading: entries.filter(entry => entry.state === 'uploading').length,
        failed: entries.filter(entry => entry.state === 'failed').length,
      };
    }

    _renderFiles() {
      for (const entry of this.files.values()) {
        const labels = {
          pending: 'Aguardando',
          uploading: `Enviando ${entry.percent.toFixed(0)}%`,
          done: 'Enviada',
          failed: `Erro${entry.detail ? `: ${entry.detail}` : ''}`,
        };
        entry.el.classList.remove('is-pending', 'is-uploading', 'is-done', 'is-failed');
        entry.el.classList.add(`is-${entry.state}`);
        entry.el.querySelector('.progress-file-state').textContent = labels[entry.state] || entry.state;
      }
    }

    // -------------------------------------------------------------------- follow
    followJob(jobId, { onDone } = {}) {
      this.jobId = jobId;
      this.onDone = onDone || null;
      this.stepLabel = 'Acompanhando processamento...';
      this._render();
      return new Promise((resolve, reject) => {
        const poll = async () => {
          try {
            const job = await api.request(`/jobs/${encodeURIComponent(jobId)}`);
            this.networkErrors = 0;
            this.applySnapshot(job);
            if (TERMINAL.includes(job.status)) {
              window.clearTimeout(this.pollTimer);
              this.pollTimer = null;
              if (this.onDone) this.onDone(job);
              if (job.status === 'failed') {
                reject(new Error(job.message || job.error || 'A operação falhou.'));
              } else if (job.status === 'cancelled') {
                const error = new Error('Operação cancelada.');
                error.cancelled = true;
                reject(error);
              } else {
                resolve(job);
              }
              return;
            }
          } catch (error) {
            this.networkErrors += 1;
            if (error.status === 404) {
              this.fail('Operação não encontrada. O servidor pode ter sido reiniciado.');
              reject(error);
              return;
            }
            if (this.networkErrors >= MAX_NETWORK_ERRORS) {
              this.stepLabel = 'Sem conexão com o servidor — tentando novamente...';
              this._render();
            }
          }
          this.pollTimer = window.setTimeout(poll, POLL_INTERVAL_MS);
        };
        poll();
      });
    }

    // -------------------------------------------------------------------- estado
    succeed(message, { autoClose = false } = {}) {
      this.status = 'succeeded';
      this.progress = 100;
      this._setMessage(message || 'Operação concluída.');
      this._setTerminalClasses();
      if (autoClose) window.setTimeout(() => this.close(), 4000);
    }

    warn(message) {
      this.status = 'succeeded_with_warnings';
      this._setMessage(message || 'Operação concluída com avisos.');
      this._setTerminalClasses();
    }

    fail(message) {
      this.status = 'failed';
      this.progress = null;
      this._setMessage(message || 'A operação falhou.');
      this.stepLabel = 'Não foi possível concluir';
      this._setTerminalClasses();
    }

    cancel() {
      if (this.status !== 'running') {
        // Operação já terminou: o botão apenas fecha o painel.
        this.close();
        return;
      }
      if (this.jobId) {
        api.request(`/jobs/${encodeURIComponent(this.jobId)}/cancel`, { method: 'POST' }).catch(() => {});
      }
      this.status = 'cancelled';
      this.cancelBtn.hidden = true;
      this._setMessage(
        this.jobId
          ? 'Cancelamento solicitado ao servidor.'
          : 'Operação interrompida nesta tela.',
      );
      this._setTerminalClasses();
    }

    close() {
      window.clearInterval(this.timer);
      window.clearTimeout(this.pollTimer);
      this.panel.remove();
    }

    _finish(job) {
      if (job.status === 'succeeded') {
        this.succeed(job.message || 'Operação concluída.');
      } else if (job.status === 'succeeded_with_warnings') {
        this.warn(job.message || 'Operação concluída com avisos.');
      } else if (job.status === 'cancelled') {
        this.status = 'cancelled';
        this._setMessage(job.message || 'Operação cancelada.');
      } else {
        this.fail(job.message || job.error || 'A operação falhou.');
      }
    }

    _setMessage(message) {
      this.resultEl.hidden = false;
      this.resultEl.className = `progress-result is-${this.status}`;
      this.resultEl.textContent = message;
      this.panel.classList.remove('is-running');
      this.panel.classList.add(`is-${this.status}`);
      this.stepEl.textContent = STATUS_LABELS[this.status] || this.status;
      this.cancelBtn.hidden = true;
      this.closeBtn.hidden = false;
      // Para o relógio e a animação: o estado final não pode parecer "carregando".
      window.clearInterval(this.timer);
      this.timer = null;
      window.clearTimeout(this.pollTimer);
      this.pollTimer = null;
      this.barEl.classList.remove('is-indeterminate');
      if (this.status === 'succeeded' || this.status === 'succeeded_with_warnings') {
        this.fillEl.style.width = '100%';
        this.percentEl.textContent = '100%';
      } else {
        this.fillEl.style.width = '';
        this.percentEl.textContent = STATUS_LABELS[this.status] || '';
      }
    }

    _setTerminalClasses() {
      this.panel.classList.remove('is-running');
      this.panel.classList.add(`is-${this.status}`);
      this.cancelBtn.hidden = true;
      this.closeBtn.hidden = false;
    }

    _render() {
      if (this.status !== 'running') {
        // Estado final: o conteúdo já foi definido por _setMessage.
        this.cancelBtn.hidden = true;
        return;
      }
      this.stepEl.textContent = this.stepLabel;
      const indeterminate = this.progress === null || Number.isNaN(this.progress);
      this.barEl.classList.toggle('is-indeterminate', indeterminate);
      const value = indeterminate ? 0 : Math.min(100, Math.max(0, this.progress));
      this.fillEl.style.width = indeterminate ? '' : `${value}%`;
      if (indeterminate) {
        this.barEl.removeAttribute('aria-valuenow');
      } else {
        this.barEl.setAttribute('aria-valuenow', String(Math.round(value)));
      }
      this.percentEl.textContent = indeterminate ? 'Processando...' : `${value.toFixed(0)}%`;

      const parts = [];
      if (this.uploadBytes && this.uploadBytes.total > 0) {
        parts.push(`${formatBytes(this.uploadBytes.loaded)} de ${formatBytes(this.uploadBytes.total)}`);
      }
      if (this.total > 0) {
        parts.push(`${this.processed} de ${this.total} registro(s)`);
      } else if (this.processed > 0) {
        parts.push(`${this.processed} processado(s)`);
      }
      if (this.succeeded > 0) parts.push(`${this.succeeded} ok`);
      if (this.failed > 0) parts.push(`${this.failed} com erro`);
      if (this.skipped > 0) parts.push(`${this.skipped} ignorado(s)`);
      this.countersEl.textContent = parts.join(' · ');
      this._renderElapsed();
    }

    _renderElapsed() {
      if (this.status !== 'running') return;
      const base = this.elapsedFromServer || 0;
      const extra = this.snapshotAt ? (Date.now() - this.snapshotAt) / 1000 : 0;
      const seconds = base + extra || (Date.now() - this.startedAt) / 1000;
      this.elapsedEl.textContent = formatElapsed(seconds);
    }
  }

  return {
    start(options) {
      return new Operation(options || {});
    },

    /** Retoma operações em andamento após recarregar a página. */
    async resumeActive() {
      if (!api.accessToken) return;
      try {
        const response = await api.request('/jobs?limit=5');
        const jobs = Array.isArray(response?.items) ? response.items : [];
        for (const job of jobs) {
          if (TERMINAL.includes(job.status)) continue;
          const operation = new Operation({ title: job.title, subtitle: 'Retomada automática' });
          operation.applySnapshot(job);
          operation.followJob(job.id).catch(() => {});
        }
      } catch (error) {
        // Sem operações recuperáveis: nada a exibir.
      }
    },

    formatBytes,
    isTerminal: status => TERMINAL.includes(status),
  };
})();
