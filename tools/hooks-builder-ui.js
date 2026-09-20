/*
 * Hooks builder — page wiring. Renders the form from HooksBuilder.HOOK_EVENTS,
 * regenerates the output on every change, and handles copy.
 * Language comes from <html lang>. All generation logic lives in hooks-builder.js.
 */
(function () {
  'use strict';
  var HB = window.HooksBuilder;
  var LANG = document.documentElement.lang === 'ja' ? 'ja' : 'en';

  var T = {
    en: {
      matcher: 'matcher',
      copy: 'Copy JSON',
      copied: 'Copied to clipboard',
      copyFailed: 'Copy failed — select the text and copy it manually',
      selected: function (n) { return n + ' selected'; },
      none: 'none',
      errors: {
        no_events: 'select at least one event',
        command_required: 'enter a command',
        statusline_command_required: 'enter the status line command',
        timeout_invalid: 'timeout must be a whole number of seconds, 1 or more'
      }
    },
    ja: {
      matcher: 'matcher',
      copy: 'JSON をコピー',
      copied: 'コピーしました',
      copyFailed: 'コピーできませんでした。テキストを選択して手動でコピーしてください',
      selected: function (n) { return n + ' 件選択'; },
      none: '未選択',
      errors: {
        no_events: 'イベントを 1 つ以上選んでください',
        command_required: 'コマンドを入力してください',
        statusline_command_required: 'ステータス行のコマンドを入力してください',
        timeout_invalid: 'タイムアウトは 1 以上の整数（秒）にしてください'
      }
    }
  }[LANG];

  var $ = function (id) { return document.getElementById(id); };
  var els = {
    presets: $('presets'),
    targets: $('targets'),
    events: $('events'),
    command: $('command'),
    timeout: $('timeout'),
    statusLineOn: $('statusline-on'),
    statusLineRow: $('statusline-row'),
    statusLineCmd: $('statusline-command'),
    out: $('out'),
    outPre: $('out-pre'),
    outPath: $('out-path'),
    copy: $('copy'),
    copyStatus: $('copy-status'),
    howPath: document.querySelectorAll('.how-path')
  };

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') node.textContent = attrs[k];
      else if (k === 'html') node.innerHTML = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { node.appendChild(c); });
    return node;
  }

  // ── Presets ─────────────────────────────────────────────────────
  HB.PRESETS.forEach(function (p) {
    var b = el('button', { type: 'button', 'class': 'preset', 'data-preset': p.id, text: p.label[LANG] });
    b.addEventListener('click', function () { applySpec(p.spec); });
    els.presets.appendChild(b);
  });

  // ── Targets ─────────────────────────────────────────────────────
  HB.TARGETS.forEach(function (t, i) {
    var input = el('input', { type: 'radio', name: 'target', value: t.id });
    if (i === 0) input.checked = true;
    var label = el('label', {}, [
      input,
      el('span', {}, [
        el('code', { text: t.path }),
        el('br'),
        el('span', { 'class': 't-label', text: t.label[LANG] })
      ])
    ]);
    input.addEventListener('change', render);
    els.targets.appendChild(label);
  });

  // ── Events ──────────────────────────────────────────────────────
  var eventInputs = {};   // name -> { check, matcher|null, row|null }
  HB.GROUPS.forEach(function (g, gi) {
    var list = el('div', { 'class': 'e-list' });
    var count = el('span', { 'class': 'count', text: T.none });
    var details = el('details', {}, [
      el('summary', {}, [el('span', { text: g.label[LANG] }), count]),
      list
    ]);
    if (gi < 2) details.open = true;
    details.dataset.group = g.id;

    HB.HOOK_EVENTS.filter(function (e) { return e.group === g.id; }).forEach(function (e) {
      var check = el('input', { type: 'checkbox', value: e.name });
      var label = el('label', {}, [
        check,
        el('span', {}, [
          el('span', { 'class': 'e-name', text: e.name }),
          el('span', { 'class': 'e-desc', text: e.desc[LANG] })
        ])
      ]);
      list.appendChild(label);

      var matcher = null, row = null;
      if (e.matcher) {
        matcher = el('input', { type: 'text', placeholder: e.hint, 'aria-label': e.name + ' matcher', spellcheck: 'false' });
        row = el('div', { 'class': 'e-matcher hidden' }, [
          el('label', {}, [el('span', { text: T.matcher + ' · ' + e.matcher[LANG] }), matcher])
        ]);
        list.appendChild(row);
        matcher.addEventListener('input', render);
      }
      check.addEventListener('change', function () {
        if (row) row.classList.toggle('hidden', !check.checked);
        render();
      });
      eventInputs[e.name] = { check: check, matcher: matcher, row: row, count: count, group: g.id };
    });
    els.events.appendChild(details);
  });

  function updateCounts() {
    HB.GROUPS.forEach(function (g) {
      var n = 0, countEl = null;
      Object.keys(eventInputs).forEach(function (name) {
        var ei = eventInputs[name];
        if (ei.group !== g.id) return;
        countEl = ei.count;
        if (ei.check.checked) n++;
      });
      if (!countEl) return;
      countEl.textContent = n ? T.selected(n) : T.none;
      countEl.classList.toggle('on', n > 0);
    });
  }

  // ── Other inputs ────────────────────────────────────────────────
  els.command.addEventListener('input', render);
  els.timeout.addEventListener('input', render);
  els.statusLineCmd.addEventListener('input', render);
  els.statusLineOn.addEventListener('change', function () {
    els.statusLineRow.classList.toggle('hidden', !els.statusLineOn.checked);
    render();
  });

  function applySpec(spec) {
    Object.keys(eventInputs).forEach(function (name) {
      var ei = eventInputs[name];
      ei.check.checked = false;
      if (ei.matcher) { ei.matcher.value = ''; ei.row.classList.add('hidden'); }
    });
    spec.events.forEach(function (ev) {
      var ei = eventInputs[ev.name];
      if (!ei) throw new Error('preset refers to unknown event: ' + ev.name);
      ei.check.checked = true;
      if (ev.matcher) { ei.matcher.value = ev.matcher; }
      if (ei.row) ei.row.classList.remove('hidden');
      // Open the group so the selection is visible.
      ei.check.closest('details').open = true;
    });
    els.command.value = spec.command || '';
    els.timeout.value = spec.timeout !== undefined ? spec.timeout : '';
    var sl = !!spec.statusLine;
    els.statusLineOn.checked = sl;
    els.statusLineRow.classList.toggle('hidden', !sl);
    els.statusLineCmd.value = sl ? spec.statusLine.command : '';
    render();
  }

  function collectSpec() {
    var spec = { events: [], command: els.command.value };
    Object.keys(eventInputs).forEach(function (name) {
      var ei = eventInputs[name];
      if (!ei.check.checked) return;
      var ev = { name: name };
      if (ei.matcher && ei.matcher.value.trim() !== '') ev.matcher = ei.matcher.value;
      spec.events.push(ev);
    });
    if (els.timeout.value.trim() !== '') spec.timeout = els.timeout.value.trim();
    if (els.statusLineOn.checked) spec.statusLine = { command: els.statusLineCmd.value };
    return spec;
  }

  function currentTargetPath() {
    var checked = els.targets.querySelector('input[name="target"]:checked');
    var t = HB.TARGETS.filter(function (x) { return x.id === checked.value; })[0];
    return t.path;
  }

  var lastJSON = null;
  function render() {
    updateCounts();
    var path = currentTargetPath();
    els.outPath.textContent = path;
    els.howPath.forEach(function (n) { n.textContent = path; });
    els.copyStatus.textContent = '';
    els.copyStatus.className = 'copy-status';
    try {
      lastJSON = HB.toJSON(HB.buildSettings(collectSpec()));
      els.out.textContent = lastJSON;
      els.outPre.classList.remove('is-error');
      els.copy.disabled = false;
    } catch (err) {
      lastJSON = null;
      var message = err.message;
      if (err.code) {
        message = T.errors[err.code];
        // 翻訳漏れはプログラミングエラー。黙って隠さず、そのまま投げる。
        if (message === undefined) throw err;
      }
      els.out.textContent = '// ' + message;
      els.outPre.classList.add('is-error');
      els.copy.disabled = true;
    }
  }

  els.copy.addEventListener('click', function () {
    if (lastJSON === null) return;
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      els.copyStatus.textContent = T.copyFailed;
      els.copyStatus.className = 'copy-status err';
      return;
    }
    navigator.clipboard.writeText(lastJSON).then(function () {
      els.copyStatus.textContent = T.copied;
      els.copyStatus.className = 'copy-status ok';
    }, function () {
      els.copyStatus.textContent = T.copyFailed;
      els.copyStatus.className = 'copy-status err';
    });
  });

  // First paint: the "notify" preset so the page is useful before any click.
  applySpec(HB.PRESETS[0].spec);
}());
