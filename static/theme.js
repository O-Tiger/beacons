// Light/dark theme: applied before first paint (loaded in <head>); the button in the corner toggles and remembers it.
(function () {
  'use strict';
  var KEY = 'nx-theme';
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { console.warn('[theme] storage unavailable', e); }
  root.setAttribute('data-theme', saved === 'light' ? 'light' : 'dark');

  function label() {
    var b = document.getElementById('theme-btn');
    if (b) b.textContent = root.getAttribute('data-theme') === 'light' ? '☾' : '☀';
  }

  document.addEventListener('DOMContentLoaded', function () {
    label();
    var b = document.getElementById('theme-btn');
    if (!b) return;
    b.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) { console.warn('[theme] cannot save theme', e); }
      label();
    });
  });
})();
