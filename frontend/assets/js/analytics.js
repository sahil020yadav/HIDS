async function init() {
  const body = renderLayout('Analytics', 'Deeper insight into prediction confidence and dataset structure');
  body.innerHTML = `<div class="text-secondary py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading analytics…</div>`;

  try {
    const data = await getAnalytics();
    const entries = Object.entries(data.confidence_distribution);

    body.innerHTML = `
      <div class="panel-card p-4 mb-4">
        <h3 class="h6 text-secondary mb-3">Confidence Distribution (${data.total_analyzed} predictions)</h3>
        <canvas id="confidenceChart" height="100"></canvas>
      </div>

      <div class="panel-card p-4">
        <h3 class="h6 text-secondary mb-2">Dataset Feature Analysis</h3>
        <p class="text-secondary small mb-3">
          Upload a CSV (e.g. a raw IoT traffic capture) to get row/column counts and per-column numeric
          averages. Processed in streamed chunks server-side, so large files never load fully into memory.
        </p>
        <label class="btn btn-outline-light btn-sm">
          <i class="bi bi-upload"></i> <span id="upload-label">Upload CSV</span>
          <input type="file" id="csv-input" accept=".csv" class="d-none" />
        </label>
        <div id="summary-box" class="row g-2 mt-3"></div>
      </div>
    `;

    new Chart(document.getElementById('confidenceChart'), {
      type: 'bar',
      data: {
        labels: entries.map(([name]) => name),
        datasets: [{ data: entries.map(([, v]) => v), backgroundColor: '#22d3ee' }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#64748b' }, grid: { display: false } },
          y: { ticks: { color: '#64748b', precision: 0 }, grid: { color: '#22304d' } },
        },
      },
    });

    const csvInput = document.getElementById('csv-input');
    const uploadLabel = document.getElementById('upload-label');
    const summaryBox = document.getElementById('summary-box');

    csvInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      uploadLabel.textContent = 'Analyzing…';
      try {
        const result = await uploadDatasetSummary(file);
        summaryBox.innerHTML = `
          <div class="col-6 col-md-3">
            <div class="bg-panel2 rounded-3 p-3">
              <div class="stat-label mb-1">Rows</div>
              <div class="fs-5 fw-semibold">${result.row_count.toLocaleString()}</div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="bg-panel2 rounded-3 p-3">
              <div class="stat-label mb-1">Columns</div>
              <div class="fs-5 fw-semibold">${result.column_count}</div>
            </div>
          </div>
          <div class="col-12 col-md-6">
            <div class="bg-panel2 rounded-3 p-3">
              <div class="stat-label mb-1">File</div>
              <div class="small text-truncate">${result.filename}</div>
            </div>
          </div>
        `;
        showToast(`Analyzed ${result.row_count.toLocaleString()} rows`, 'success');
      } catch (err) {
        showToast(err.message || 'Failed to analyze CSV', 'error');
      } finally {
        uploadLabel.textContent = 'Upload CSV';
        csvInput.value = '';
      }
    });
  } catch (err) {
    body.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', init);