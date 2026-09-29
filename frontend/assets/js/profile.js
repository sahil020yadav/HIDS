function init() {
  const body = renderLayout('Profile', 'Your account details');
  const user = getUser() || {};

  const rows = [
    { label: 'Name', value: user.name || '—', icon: 'bi-person' },
    { label: 'Email', value: user.email || '—', icon: 'bi-envelope' },
    { label: 'Role', value: user.role || '—', icon: 'bi-shield' },
    { label: 'Account Created', value: user.created_at ? new Date(user.created_at).toLocaleString() : '—', icon: 'bi-calendar3' },
  ];

  body.innerHTML = `
    <div class="panel-card p-4" style="max-width:32rem;">
      <div class="d-flex align-items-center gap-3 mb-4">
        <div class="rounded-circle d-flex align-items-center justify-content-center text-accent fw-bold fs-4"
             style="width:56px;height:56px;background:rgba(34,211,238,0.15);">
          ${(user.name || 'U')[0].toUpperCase()}
        </div>
        <div>
          <div class="fs-5 fw-semibold">${user.name || ''}</div>
          <div class="text-secondary small">${user.email || ''}</div>
        </div>
      </div>
      <div class="d-flex flex-column gap-2">
        ${rows
          .map(
            (r) => `
          <div class="d-flex align-items-center gap-3 bg-panel2 rounded-3 px-3 py-2">
            <i class="bi ${r.icon} text-accent"></i>
            <div>
              <div class="stat-label mb-0">${r.label}</div>
              <div class="small">${r.value}</div>
            </div>
          </div>`
          )
          .join('')}
      </div>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', init);