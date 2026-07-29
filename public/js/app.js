document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('theme-toggle');
  if (!toggle) return;

  const applyTheme = (theme) => {
    document.body.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('edusubmit-theme', theme);
    toggle.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
  };

  const savedTheme = localStorage.getItem('edusubmit-theme') || 'light';
  applyTheme(savedTheme);

  toggle.addEventListener('click', () => {
    const nextTheme = document.body.classList.contains('dark') ? 'light' : 'dark';
    applyTheme(nextTheme);
  });
});
