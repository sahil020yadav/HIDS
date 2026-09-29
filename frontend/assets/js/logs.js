async function init() {
  const body = renderLayout('Security Logs', 'Login attempts, model events, and prediction alerts');
  body.innerHTML = `<div class="text-secondary py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading logs…</div>`;

  try {
    const logs = await getLogs(300);

    const logsHtml = logs.length
      ? logs
          .map(
            (log) => `
      <div class="d-flex gap-3 py-2 border-bottom" style="border-color: rgba(34,48,77,0.4) !important; font-family: monospace; font-size: 0.8rem;">
        <span class="text-secondary flex-shrink-0">${new Date(log.created_at).toLocaleString()}</span>
        <span class="fw-semibold flex-shrink-0 badge-${log.severity}">[${log.severity}]</span>
        <span class="text-secondary flex-shrink-0">${log.event_type}</span>
        <span>${log.message}</span>
      </div>`
          )
          .join('')
      : `<p class="text-secondary">No log entries yet.</p>`;

    body.innerHTML = `<div class="panel-card p-4" style="max-height:70vh; overflow-y:auto;">${logsHtml}</div>`;
  } catch (err) {
    body.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', init);