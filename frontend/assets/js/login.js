// If already logged in, skip straight to the dashboard.
if (getToken()) {
  location.href = 'dashboard.html';
}

const form = document.getElementById('login-form');
const errorBox = document.getElementById('form-error');
const submitBtn = document.getElementById('submit-btn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorBox.classList.add('d-none');

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  if (!email || !password) {
    form.classList.add('was-validated');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Signing in…';

  try {
    const data = await loginUser({ email, password });
    localStorage.setItem('hids_token', data.access_token);
    localStorage.setItem('hids_user', JSON.stringify(data.user));
    showToast('Logged in successfully', 'success');
    setTimeout(() => (location.href = 'dashboard.html'), 300);
  } catch (err) {
    errorBox.textContent = err.message || 'Login failed. Check the backend is running.';
    errorBox.classList.remove('d-none');
    showToast(err.message || 'Login failed', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Sign in';
  }
});