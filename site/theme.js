// Theme: follows the system preference until the reader picks one with the theme button.
// Loaded in <head> without defer so a stored choice applies before the first paint.
// The choice is stored under "tsc:theme" (never "aicourse:", the other course shares the origin).
(function () {
  var KEY = 'tsc:theme';
  var root = document.documentElement;
  root.classList.add('js'); // lets the CSS tell a page with scripts from one without
  var system = window.matchMedia('(prefers-color-scheme: dark)');
  try {
    var saved = localStorage.getItem(KEY);
    if (saved === 'light' || saved === 'dark') root.dataset.theme = saved;
  } catch (e) { /* storage blocked: follow the system */ }

  function isDark() { return (root.dataset.theme || (system.matches ? 'dark' : 'light')) === 'dark'; }
  function label() {
    var text = isDark() ? 'Switch to light theme' : 'Switch to dark theme';
    document.querySelectorAll('button.theme').forEach(function (b) { b.setAttribute('aria-label', text); b.title = text; });
  }

  document.addEventListener('DOMContentLoaded', function () {
    label();
    document.querySelectorAll('button.theme').forEach(function (b) {
      b.addEventListener('click', function () {
        var next = isDark() ? 'light' : 'dark';
        root.dataset.theme = next;
        try { localStorage.setItem(KEY, next); } catch (e) { /* not stored, still applied */ }
        label();
      });
    });
  });
  system.addEventListener('change', label);
})();
