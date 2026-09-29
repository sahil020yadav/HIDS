let modelInfo = null;

function resultCard(result) {
  const isAttack = result.label === 'Attack';
  return `
    <h3 class="h6 text-secondary mb-3">Prediction Result</h3>
    <div class="p-4 rounded-3 text-center mb-3" style="background:${isAttack ? 'rgba(244,63,94,0.1)' : 'rgba(34,197,94,0.1)'};border:1px solid ${isAttack ? 'rgba(244,63,94,0.3)' : 'rgba(34,197,94,0.3)'};">
      <div class="stat-label mb-1">Classification</div>
      <div class="fs-3 fw-bold ${isAttack ? 'text-danger-custom' : 'text-safe'}">${result.label}</div>
    </div>
    <div class="row g-2 mb-3">
      <div class="col-6">
        <div class="bg-panel2 rounded-3 p-3">
          <div class="stat-label mb-1">Confidence</div>
          <div class="fs-5 fw-semibold">${(result.confidence * 100).toFixed(1)}%</div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-panel2 rounded-3 p-3">
          <div class="stat-label mb-1">Risk Level</div>
          <span class="badge-status badge-${result.risk_level}">${result.risk_level}</span>
        </div>
      </div>
    </div>
    <div class="bg-panel2 rounded-3 p-3 mb-3">
      <div class="stat-label mb-1">Attack Type</div>
      <div class="small">${result.attack_type || 'N/A — classified as Normal traffic'}</div>
    </div>
    <div class="bg-panel2 rounded-3 p-3">
      <div class="stat-label mb-1">Timestamp</div>
      <div class="small">${new Date(result.created_at).toLocaleString()}</div>
    </div>
  `;
}

async function init() {
  const body = renderLayout('Prediction', 'Enter host/flow parameters and run intrusion detection');
  body.innerHTML = `
    <div class="row g-4">
      <div class="col-lg-7">
        <div class="panel-card p-4" id="form-panel">
          <div class="text-secondary py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading model schema…</div>
        </div>
      </div>
      <div class="col-lg-5">
        <div class="panel-card p-4" id="result-panel" style="position:sticky; top:6rem;">
          <h3 class="h6 text-secondary mb-3">Prediction Result</h3>
          <p class="text-secondary small">Run a prediction to see results here.</p>
        </div>
      </div>
    </div>
  `;

  const formPanel = document.getElementById('form-panel');
  const resultPanel = document.getElementById('result-panel');

  try {
    modelInfo = await getModelInfo();

    const fieldsHtml = modelInfo.features
      .map(
        (f) => `
      <div class="col-sm-6">
        <label class="form-label">${f}</label>
        <input type="number" step="any" class="form-control feature-input" data-feature="${f}" required />
      </div>`
      )
      .join('');

    formPanel.innerHTML = `
      <p class="text-secondary small mb-3">
        Model: <span class="text-light fw-medium">${modelInfo.model_type}</span>
        ${modelInfo.is_pipeline ? '<span class="text-secondary">(sklearn Pipeline)</span>' : ''}
        · ${modelInfo.n_features} input features
      </p>
      <form id="predict-form">
        <div class="row g-3">${fieldsHtml}</div>
        <button type="submit" id="predict-btn" class="btn btn-accent w-100 py-2 mt-4">
          <i class="bi bi-lightning-charge"></i> Detect Intrusion
        </button>
      </form>
    `;

    document.getElementById('predict-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('predict-btn');
      const values = {};
      let missing = false;
      document.querySelectorAll('.feature-input').forEach((input) => {
        if (input.value === '') missing = true;
        values[input.dataset.feature] = parseFloat(input.value);
      });
      if (missing) {
        showToast('Please fill in all feature fields', 'error');
        return;
      }

      btn.disabled = true;
      btn.innerHTML = 'Analyzing…';
      try {
        const result = await predict(values);
        resultPanel.innerHTML = resultCard(result);
        showToast(`Prediction complete: ${result.label}`, result.label === 'Attack' ? 'error' : 'success');
      } catch (err) {
        showToast(err.message || 'Prediction failed', 'error');
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-lightning-charge"></i> Detect Intrusion';
      }
    });
  } catch (err) {
    formPanel.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', init);