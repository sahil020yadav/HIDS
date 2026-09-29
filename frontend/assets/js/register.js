if (getToken()) {
  location.href = 'dashboard.html';
}

const form = document.getElementById('register-form');
const errorBox = document.getElementById('form-error');
const submitBtn = document.getElementById('submit-btn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorBox.classList.add('d-none');

  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirm_password = document.getElementById('confirm_password').value;

  if (!name || !email || !password) {
    errorBox.textContent = 'Please fill in all fields.';
    errorBox.classList.remove('d-none');
    return;
  }
  if (password.length < 8) {
    errorBox.textContent = 'Password must be at least 8 characters.';
    errorBox.classList.remove('d-none');
    return;
  }
  if (password !== confirm_password) {
    errorBox.textContent = 'Passwords do not match.';
    errorBox.classList.remove('d-none');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Creating account…';

  try {
    await registerUser({ name, email, password, confirm_password });
    showToast('Account created — please sign in', 'success');
    setTimeout(() => (location.href = 'login.html'), 400);
  } catch (err) {
    errorBox.textContent = err.message || 'Registration failed';
    errorBox.classList.remove('d-none');
    showToast(err.message || 'Registration failed', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Register';
  }
});