const NAV_LINKS = [
  { href: 'dashboard.html', label: 'Dashboard', icon: 'bi-grid-1x2' },
  { href: 'predict.html', label: 'Prediction', icon: 'bi-lightning-charge' },
  { href: 'history.html', label: 'Prediction History', icon: 'bi-clock-history' },
  { href: 'analytics.html', label: 'Analytics', icon: 'bi-bar-chart-line' },
  { href: 'logs.html', label: 'Security Logs', icon: 'bi-file-earmark-text' },
  { href: 'profile.html', label: 'Profile', icon: 'bi-person-circle' },
];

function renderLayout(pageTitle, pageSubtitle) {
  const user = getUser() || {};
  const currentPage = location.pathname.split('/').pop();

  const navHtml = NAV_LINKS.map(
    (link) => `
      <a href="${link.href}" class="nav-link ${link.href === currentPage ? 'active' : ''}">
        <i class="bi ${link.icon}"></i> ${link.label}
      </a>`
  ).join('');

  const shell = document.createElement('div');
  shell.className = 'app-shell';
  shell.innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="icon-box"><i class="bi bi-shield-exclamation"></i></div>
        <div>
          <div class="fw-semibold">HIDS-IoT</div>
          <div class="text-secondary" style="font-size:0.75rem;">Intrusion Detection</div>
        </div>
      </div>
      <nav class="sidebar-nav">${navHtml}</nav>
      <div class="sidebar-footer">
        <div class="d-flex align-items-center gap-2 bg-panel2 rounded p-2 mb-2">
          <div class="rounded-circle d-flex align-items-center justify-content-center text-accent fw-bold"
               style="width:36px;height:36px;background:rgba(34,211,238,0.15);">
            ${(user.name || 'U')[0].toUpperCase()}
          </div>
          <div class="text-truncate">
            <div class="text-truncate" style="font-size:0.85rem;">${user.name || 'User'}</div>
            <div class="text-secondary text-truncate" style="font-size:0.72rem;">${user.email || ''}</div>
          </div>
        </div>
        <button id="logout-btn" class="btn btn-outline-secondary btn-sm w-100">
          <i class="bi bi-box-arrow-right"></i> Log out
        </button>
      </div>
    </aside>
    <main class="main-content">
      <header class="topbar">
        <h1 class="h5 mb-0">${pageTitle}</h1>
        ${pageSubtitle ? `<p class="text-secondary small mb-0 mt-1">${pageSubtitle}</p>` : ''}
      </header>
      <div class="page-body" id="page-body"></div>
    </main>
  `;

  document.body.prepend(shell);

  document.getElementById('logout-btn').addEventListener('click', () => {
    clearSession();
    location.href = 'login.html';
  });

  return document.getElementById('page-body');
}