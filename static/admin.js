/* Editor do painel /admin. Sem dependências: monta os formulários a partir do JSON do servidor. */
(function () {
  var H = { 'X-Requested-With': 'fetch', 'Content-Type': 'application/json' };
  var data, glyphs = [], tab = 'geral', dirty = false;
  var panel = document.getElementById('panel'), status = document.getElementById('status'), tabsEl = document.getElementById('tabs');
  var TABS = [['geral', 'Geral'], ['sobre', 'Sobre'], ['setup', 'Setup'], ['horarios', 'Horários'], ['contatos', 'Contatos'], ['etc', 'ETC.'], ['json', 'Avançado']];
  var DIAS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
  var HTML_HINT = 'Aceita HTML simples: <b>negrito</b>, <br> para quebra de linha, &nbsp; para espaço sem quebra.';

  function add(e, c) {
    if (c == null) return;
    if (Array.isArray(c)) { c.forEach(function (x) { add(e, x); }); return; }
    e.append(c.nodeType ? c : document.createTextNode(c));
  }
  function el(tag, attrs) {
    var e = document.createElement(tag);
    for (var k in (attrs || {})) {
      if (k === 'class') e.className = attrs[k];
      else if (k.slice(0, 2) === 'on') e.addEventListener(k.slice(2), attrs[k]);
      else if (k === 'value') e.value = attrs[k];
      else if (k === 'checked') e.checked = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    for (var i = 2; i < arguments.length; i++) {
      add(e, arguments[i]);
    }
    return e;
  }
  function at(path) { return path.reduce(function (o, k) { return o[k]; }, data); }
  function put(path, v) { at(path.slice(0, -1))[path[path.length - 1]] = v; touch(); }
  function touch() { dirty = true; setStatus('Alterações não salvas', ''); }
  function setStatus(t, cls) { status.textContent = t; status.className = cls || ''; }

  function field(label, path, o) {
    o = o || {};
    var v = at(path), inp;
    if (o.type === 'select') {
      inp = el('select', { onchange: function () { put(path, inp.value); } }, o.options.map(function (x) { return el('option', { value: x }, x); }));
      inp.value = v;
    } else if (o.type === 'area') {
      inp = el('textarea', { rows: o.rows || 2, oninput: function () { put(path, inp.value); } }); inp.value = v;
    } else if (o.type === 'number') {
      inp = el('input', { type: 'number', min: o.min, max: o.max, oninput: function () { put(path, inp.value === '' ? 0 : parseInt(inp.value, 10)); } }); inp.value = v;
    } else {
      inp = el('input', { type: o.type || 'text', oninput: function () { put(path, inp.value); } }); inp.value = v;
    }
    return el('label', { class: 'f' }, el('span', {}, label), inp, o.hint ? el('small', {}, o.hint) : null);
  }

  /* lista editável: cols = [{ph, area}] (1 coluna = lista de textos; 2 = pares) */
  function list(label, path, cols, hint) {
    var arr = at(path), wrap = el('div', { class: 'rows' });
    function move(i, d) { var j = i + d; if (j < 0 || j >= arr.length) return; var t = arr[i]; arr[i] = arr[j]; arr[j] = t; touch(); render(); }
    arr.forEach(function (item, i) {
      var cells = el('div', { class: 'cells' });
      cols.forEach(function (c, ci) {
        var val = cols.length === 1 ? item : item[ci];
        var inp = el(c.area ? 'textarea' : 'input', { placeholder: c.ph, 'aria-label': c.ph, rows: 2, oninput: function () { if (cols.length === 1) arr[i] = inp.value; else arr[i][ci] = inp.value; touch(); } });
        inp.value = val; cells.append(inp);
      });
      wrap.append(el('div', { class: 'row' + (cols.length === 2 ? ' two' : '') }, cells,
        el('div', { class: 'ctl' },
          el('button', { class: 'abtn sm', type: 'button', title: 'Subir', onclick: function () { move(i, -1); } }, '↑'),
          el('button', { class: 'abtn sm', type: 'button', title: 'Descer', onclick: function () { move(i, 1); } }, '↓'),
          el('button', { class: 'abtn sm', type: 'button', title: 'Remover', onclick: function () { arr.splice(i, 1); touch(); render(); } }, '✕'))));
    });
    wrap.append(el('div', {}, el('button', { class: 'abtn sm', type: 'button', onclick: function () { arr.push(cols.length === 1 ? '' : cols.map(function () { return ''; })); touch(); render(); } }, '+ Adicionar')));
    return el('div', { class: 'f' }, el('span', {}, label), wrap, hint ? el('small', {}, hint) : null);
  }

  function card(title) { return el('section', { class: 'card' }, el('h2', {}, title), [].slice.call(arguments, 1)); }

  function common(k) {
    return [
      field('Título da página', ['pages', k, 'title']),
      field('Etiqueta (acima do título)', ['pages', k, 'tag']),
      field('Ícone', ['pages', k, 'glyph'], { type: 'select', options: glyphs }),
      field('Frase de apoio', ['pages', k, 'lede'], { type: 'area' }),
      field('Descrição para buscadores e redes sociais', ['pages', k, 'desc'], { type: 'area', hint: 'Aparece na prévia do link no Discord, WhatsApp e Google.' })
    ];
  }

  var VIEWS = {
    geral: function () {
      return [
        card('Links', ['twitch', 'github', 'discord', 'nexus', 'tracker'].map(function (k) {
          return field({ twitch: 'Twitch', github: 'GitHub', discord: 'Convite do Discord', nexus: 'Site do Nexus', tracker: 'TwitchTracker' }[k], ['links', k], { type: 'url' });
        })),
        card('Contato', field('E-mail', ['email'], { type: 'email' }), field('Usuário do Discord', ['discord_user'])),
        card('Site', field('Nome', ['site', 'name']), field('Domínio', ['site', 'domain']), field('Site principal', ['site', 'main_site'], { type: 'url' }))
      ];
    },
    sobre: function () {
      return [card('Cabeçalho', common('sobre')), card('Quem sou', list('Tópicos', ['pages', 'sobre', 'bullets'], [{ ph: 'Texto do tópico', area: true }], HTML_HINT))];
    },
    setup: function () {
      return [card('Cabeçalho', common('setup')), card('Especificações', list('Peças', ['pages', 'setup', 'specs'], [{ ph: 'Peça (ex.: Processador)' }, { ph: 'Modelo e detalhes', area: true }], HTML_HINT))];
    },
    horarios: function () {
      var off = at(['pages', 'horarios', 'off_days']);
      var checks = el('div', { class: 'checks' }, DIAS.map(function (n, d) {
        var cb = el('input', { type: 'checkbox', checked: off.indexOf(d) >= 0, onchange: function () {
          var a = at(['pages', 'horarios', 'off_days']), i = a.indexOf(d);
          if (cb.checked && i < 0) a.push(d); if (!cb.checked && i >= 0) a.splice(i, 1); a.sort(); touch();
        } });
        return el('label', {}, cb, n);
      }));
      return [card('Cabeçalho', common('horarios')),
        card('Agenda', field('Hora de início (horário de Brasília)', ['pages', 'horarios', 'start_hour'], { type: 'number', min: 0, max: 23, hint: 'A frase de apoio é texto livre: se mudar a hora ou os dias, ajuste ela também.' }),
          el('div', { class: 'f' }, el('span', {}, 'Dias de folga'), checks, el('small', {}, 'Marcados = sem live. O cálculo de "próxima live" usa isso.')))];
    },
    contatos: function () { return [card('Cabeçalho', common('contatos'))]; },
    etc: function () { return [card('Cabeçalho', common('etc'))]; },
    json: function () {
      var ta = el('textarea', { class: 'json', spellcheck: 'false', oninput: function () { dirty = true; setStatus('Alterações não salvas (JSON)', ''); } });
      ta.value = JSON.stringify(data, null, 2); ta.id = 'rawjson';
      return [card('JSON completo', el('p', { class: 'note' }, 'Para quem prefere editar tudo de uma vez. O servidor valida antes de salvar.'), ta)];
    }
  };

  function render() {
    var y = window.scrollY;
    tabsEl.replaceChildren.apply(tabsEl, TABS.map(function (t) {
      return el('button', { type: 'button', 'aria-current': t[0] === tab ? 'true' : 'false', onclick: function () { if (tab === 'json') applyRaw(); tab = t[0]; render(); } }, t[1]);
    }));
    panel.replaceChildren.apply(panel, [].concat.apply([], VIEWS[tab]()));
    window.scrollTo(0, y);
  }

  function applyRaw() {
    var ta = document.getElementById('rawjson'); if (!ta) return true;
    try { data = JSON.parse(ta.value); return true; } catch (e) { setStatus('JSON inválido: ' + e.message, 'bad'); return false; }
  }

  function api(url, body) {
    return fetch(url, { method: 'POST', headers: H, body: body === undefined ? undefined : JSON.stringify(body), credentials: 'same-origin' })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (r.status === 401) { location.reload(); } return { ok: r.ok, j: j }; }); });
  }

  function save() {
    if (tab === 'json' && !applyRaw()) return;
    var btn = document.getElementById('save'); btn.disabled = true; setStatus('Salvando…', '');
    api('/admin/save', data).then(function (r) {
      btn.disabled = false;
      if (!r.ok) { setStatus(r.j.error || 'Erro ao salvar', 'bad'); return; }
      data = r.j.data; dirty = false; render();
      var d = new Date(); setStatus('Salvo às ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) + ' · já está no ar', 'ok');
    }, function () { btn.disabled = false; setStatus('Sem conexão com o servidor', 'bad'); });
  }

  document.getElementById('save').addEventListener('click', save);
  document.getElementById('logout').addEventListener('click', function () { api('/admin/logout').then(function () { location.href = '/admin/'; }); });
  document.getElementById('reset').addEventListener('click', function () {
    if (!confirm('Voltar todos os textos e links ao padrão do código? Suas edições serão apagadas (faça o Backup antes se quiser guardá-las).')) return;
    api('/admin/reset').then(function (r) { if (r.ok) { data = r.j.data; dirty = false; render(); setStatus('Padrão restaurado', 'ok'); } });
  });
  window.addEventListener('beforeunload', function (e) { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
  document.addEventListener('keydown', function (e) { if ((e.ctrlKey || e.metaKey) && e.key === 's') { e.preventDefault(); save(); } });

  fetch('/admin/data', { credentials: 'same-origin' }).then(function (r) {
    if (r.status === 401) { location.reload(); throw 0; } return r.json();
  }).then(function (j) {
    data = j.data; glyphs = j.glyphs;
    var w = document.getElementById('warn');
    if (!j.persistent) {
      w.hidden = false;
      w.textContent = 'Atenção: o servidor não tem um volume persistente. Suas edições funcionam, mas somem no próximo deploy ou reinício. Crie um volume no Railway com mount path /data e defina DATA_DIR=/data.';
    }
    setStatus('Pronto', ''); render();
  }).catch(function () { setStatus('Não consegui carregar o conteúdo', 'bad'); });
})();
