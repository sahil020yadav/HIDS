const RISK_COLORS = { Low: '#22c55e', Medium: '#f59e0b', High: '#fb923c', Critical: '#f43f5e' };

function statCard(label, value, colorClass, icon) {
  return `
    <div class="col-6 col-md-3">
      <div class="panel-card stat-card p-4">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="stat-label">${label}</span>
          <i class="bi ${icon} ${colorClass}"></i>
        </div>
        <div class="stat-value ${colorClass}">${value}</div>
      </div>
    </div>`;
}

function badge(value) {
  return `<span class="badge-status badge-${value}">${value}</span>`;
}

async function init() {
  const body = renderLayout('Dashboard', 'Live overview of host-based intrusion detection activity');
  body.innerHTML = `<div class="text-secondary py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading dashboard…</div>`;

  try {
    const stats = await getDashboardStats();

    const riskEntries = Object.entries(stats.risk_distribution);

    body.innerHTML = `
      <div class="row g-3 mb-4">
        ${statCard('Total Predictions', stats.total_predictions, 'text-accent', 'bi-shield-check')}
        ${statCard('Normal Activities', stats.normal_count, 'text-safe', 'bi-check-circle')}
        ${statCard('Detected Attacks', stats.attack_count, 'text-danger-custom', 'bi-exclamation-triangle')}
        ${statCard('Attack Percentage', stats.attack_percentage + '%', 'text-warn', 'bi-percent')}
      </div>

      <div class="row g-3 mb-4">
        <div class="col-lg-8">
          <div class="panel-card p-4 h-100">
            <h3 class="h6 text-secondary mb-3">Prediction Trend</h3>
            <canvas id="trendChart" height="110"></canvas>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="panel-card p-4 h-100">
            <h3 class="h6 text-secondary mb-3">Risk Distribution</h3>
            ${riskEntries.length ? '<canvas id="riskChart" height="180"></canvas>' : '<p class="text-secondary text-center py-5">No data yet</p>'}
          </div>
        </div>
      </div>

      <div class="panel-card p-4 mb-4">
        <h3 class="h6 text-secondary mb-3">Normal vs Attack Volume</h3>
        <canvas id="volumeChart" height="90"></canvas>
      </div>

      <div class="panel-card p-4">
        <h3 class="h6 text-secondary mb-3">Latest Predictions</h3>
        <div class="table-responsive">
          <table class="table table-hids mb-0">
            <thead><tr><th>Time</th><th>Result</th><th>Confidence</th><th>Risk</th></tr></thead>
            <tbody>
              ${
                stats.latest_predictions.length
                  ? stats.latest_predictions
                      .map(
                        (p) => `
                <tr>
                  <td class="text-secondary">${new Date(p.created_at).toLocaleString()}</td>
                  <td>${badge(p.label)}</td>
                  <td>${(p.confidence * 100).toFixed(1)}%</td>
                  <td>${badge(p.risk_level)}</td>
                </tr>`
                      )
                      .join('')
                  : `<tr><td colspan="4" class="text-center text-secondary py-4">No predictions yet — try the Prediction page.</td></tr>`
              }
            </tbody>
          </table>
        </div>
      </div>
    `;

    new Chart(document.getElementById('trendChart'), {
      type: 'line',
      data: {
        labels: stats.trend.map((t) => t.day),
        datasets: [
          { label: 'Normal', data: stats.trend.map((t) => t.normal_count), borderColor: '#22c55e', tension: 0.3 },
          { label: 'Attack', data: stats.trend.map((t) => t.attack_count), borderColor: '#f43f5e', tension: 0.3 },
        ],
      },
      options: {
        plugins: { legend: { labels: { color: '#cbd5e1' } } },
        scales: {
          x: { ticks: { color: '#64748b' }, grid: { color: '#22304d' } },
          y: { ticks: { color: '#64748b', precision: 0 }, grid: { color: '#22304d' } },
        },
      },
    });

    if (riskEntries.length) {
      new Chart(document.getElementById('riskChart'), {
        type: 'doughnut',
        data: {
          labels: riskEntries.map(([name]) => name),
          datasets: [{ data: riskEntries.map(([, v]) => v), backgroundColor: riskEntries.map(([name]) => RISK_COLORS[name] || '#64748b') }],
        },
        options: { plugins: { legend: { labels: { color: '#cbd5e1' } } } },
      });
    }

    new Chart(document.getElementById('volumeChart'), {
      type: 'bar',
      data: {
        labels: ['Normal', 'Attack'],
        datasets: [{ data: [stats.normal_count, stats.attack_count], backgroundColor: ['#22c55e', '#f43f5e'] }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#64748b' }, grid: { display: false } },
          y: { ticks: { color: '#64748b', precision: 0 }, grid: { color: '#22304d' } },
        },
      },
    });
  } catch (err) {
    body.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', init);