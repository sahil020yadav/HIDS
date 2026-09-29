function badge(value) {
  return `<span class="badge-status badge-${value}">${value}</span>`;
}

async function init() {
  const body = renderLayout('Prediction History', 'All past predictions made with the trained model');
  body.innerHTML = `<div class="text-secondary py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading history…</div>`;

  try {
    const rows = await getPredictions(200);

    const rowsHtml = rows.length
      ? rows
          .map(
            (p, i) => `
      <tr>
        <td class="text-secondary">${new Date(p.created_at).toLocaleString()}</td>
        <td>${badge(p.label)}</td>
        <td class="text-secondary">${p.attack_type || '—'}</td>
        <td>${(p.confidence * 100).toFixed(1)}%</td>
        <td>${badge(p.risk_level)}</td>
        <td>
          <button class="btn btn-sm btn-link text-accent p-0" data-bs-toggle="collapse" data-bs-target="#row-${i}">
            View input
          </button>
        </td>
      </tr>
      <tr class="collapse" id="row-${i}">
        <td colspan="6"><pre class="input-json">${JSON.stringify(JSON.parse(p.input_data), null, 2)}</pre></td>
      </tr>`
          )
          .join('')
      : `<tr><td colspan="6" class="text-center text-secondary py-4">No predictions yet.</td></tr>`;

    body.innerHTML = `
      <div class="panel-card p-0">
        <div class="table-responsive">
          <table class="table table-hids mb-0">
            <thead>
              <tr><th>Date / Time</th><th>Prediction</th><th>Attack Type</th><th>Confidence</th><th>Risk</th><th></th></tr>
            </thead>
            <tbody>${rowsHtml}</tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    body.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', init);