// Include this script FIRST (in <head>, before any other JS) on every
// protected page. It redirects to login.html immediately if there's no
// token, so protected content never flashes on screen for a logged-out user.
(function () {
  const token = localStorage.getItem('hids_token');
  if (!token) {
    window.location.href = 'login.html';
  }
})();