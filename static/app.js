/* Troca de abas sem recarregar a página (progressive enhancement: sem JS, os links funcionam normalmente). */
(function () {
  var T = function (x, v) { var o = (window.NEXUS_I18N && window.NEXUS_I18N[x]) || x; if (v) Object.keys(v).forEach(function (k) { o = o.split('{' + k + '}').join(String(v[k])); }); return o; };
  var view = document.getElementById('view'), toast = document.getElementById('toast'), tid;
  function say(t) { toast.textContent = t; toast.classList.add('on'); clearTimeout(tid); tid = setTimeout(function () { toast.classList.remove('on'); }, 1800); }
  function copy(t) {
    var ok = function () { say(T('Copiado: ') + t); };
    var fb = function () {
      var a = document.createElement('textarea'); a.value = t; document.body.appendChild(a); a.select();
      try { document.execCommand('copy'); ok(); } catch (e) { say(t); } a.remove();
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, fb); else fb();
  }
  function schedule() {
    var s = document.getElementById('sched'); if (!s) return;
    var start = +s.dataset.start, off = {}; s.dataset.off.split(',').forEach(function (x) { if (x !== '') off[+x] = 1; });
    var parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Sao_Paulo', weekday: 'short', hour: 'numeric', hour12: false }).formatToParts(new Date()), m = {};
    parts.forEach(function (x) { m[x.type] = x.value; });
    var d = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 }[m.weekday], h = (+m.hour) % 24;
    var names = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado'].map(function (n) { return T(n); });
    document.querySelectorAll('.day').forEach(function (e) { e.classList.toggle('today', +e.dataset.d === d); });
    var nx = document.getElementById('nx'), sub = document.getElementById('nxs');
    if (!off[d] && h < start) { nx.textContent = T('Hoje às {h}h', { h: start }); sub.textContent = T('Previsão para hoje ({day})', { day: names[d] }); return; }
    if (!off[d]) { nx.textContent = T('Hoje, a partir das {h}h', { h: start }); sub.textContent = T('Confira na Twitch se está no ar'); return; }
    var k = (d + 1) % 7, t = 1; while (off[k]) { k = (k + 1) % 7; t++; }
    var dayName = names[k][0].toUpperCase() + names[k].slice(1);
    nx.textContent = t === 1 ? T('Amanhã') + ' ' + T('{day} às {h}h', { day: '', h: start }).trim() : T('{day} às {h}h', { day: dayName, h: start });
    sub.textContent = T('{day}, horário de Brasília', { day: dayName });
  }
  function go(url, push) {
    fetch(url, { headers: { 'X-Requested-With': 'fetch' } }).then(function (r) { if (!r.ok) throw 0; return r.text(); }).then(function (t) {
      var d = new DOMParser().parseFromString(t, 'text/html'), nv = d.getElementById('view'); if (!nv) throw 0;
      view.innerHTML = nv.innerHTML; document.title = d.title;
      var md = document.querySelector('meta[name=description]'), nd = d.querySelector('meta[name=description]'); if (md && nd) md.content = nd.content;
      var path = new URL(url, location.href).pathname.replace(/\/$/, '') || '/';
      document.querySelectorAll('nav.tabs a').forEach(function (a) {
        var p = new URL(a.href).pathname.replace(/\/$/, '') || '/';
        if (p === path) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
      });
      if (push) history.pushState({}, '', url);
      view.classList.remove('in'); void view.offsetWidth; view.classList.add('in');
      window.scrollTo(0, 0); schedule();
    }).catch(function () { location.href = url; });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-copy]'); if (b) { copy(b.dataset.copy); return; }
    var a = e.target.closest('nav.tabs a');
    if (a && !e.defaultPrevented && e.button === 0 && !(e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) && a.origin === location.origin) { e.preventDefault(); go(a.href, true); }
  });
  window.addEventListener('popstate', function () { go(location.href, false); });
  schedule();
})();
