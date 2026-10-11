/* ==========================================================================
   From Surface Realism to Behavioral Validity — linear coded-corpus page
   Reads window.SURVEY_DATA (bundled by web/data/data.js). No fetch, no deps,
   so the page renders when opened directly from file://.

   One long document: the seven coding-group tables stacked in paper order
   behind a sticky jump bar. G1-G6 are 52-row paper tables (all rows always
   present) with a tally row computed over all 52 papers; G7 is the 72-row
   claim-evidence table. No tabs, no pagination, no row collapsing.
   ========================================================================== */
(function () {
  'use strict';

  var DATA = window.SURVEY_DATA;
  if (!DATA) {
    var msg = document.createElement('p');
    msg.className = 'fatal';
    msg.textContent = 'Data bundle not found. Expected web/data/data.js to define window.SURVEY_DATA.';
    var main = document.getElementById('main') || document.body;
    main.insertBefore(msg, main.firstChild);
    return;
  }

  var CODEBOOK = DATA.codebook || [];
  var GROUPS = CODEBOOK.filter(function (g) { return g.id !== 'G7'; });
  var META = {};
  GROUPS.forEach(function (g) {
    g.fields.forEach(function (f) { META[f.name] = { group: g, field: f }; });
  });

  var PAPERS = (DATA.papers && DATA.papers.papers) || [];
  var SLOTS = (DATA.claims && DATA.claims.slots) || [];
  var STATS = DATA.stats || {};
  var N = STATS.n || PAPERS.length;

  var SHORT = {
    G1: 'System & Simulation',
    G2: 'Evaluation Methods',
    G3: 'Evaluation Dimensions',
    G4: 'Interaction & Behavior',
    G5: 'Theory & Reliability',
    G6: 'Additional Characteristics'
  };
  var SECTION_IDS = GROUPS.map(function (g) { return g.id; }).concat(['G7']);
  var ALIGN_ORDER = ['ALIGNED', 'PARTIAL', 'EXCEEDS', 'UNCLEAR'];
  var ALIGN_COLORS = { ALIGNED: '#16a34a', PARTIAL: '#d97706', EXCEEDS: '#dc2626', UNCLEAR: '#64748b' };
  var ALIGN_CLASS = { ALIGNED: 'aligned', PARTIAL: 'partial', EXCEEDS: 'exceeds', UNCLEAR: 'unclear' };
  var VALUE_PRIORITY = { yes: 0, no: 1, 'n/a': 2 };

  var state = {
    textOpen: {},
    pop: { field: null, pinned: false }
  };

  /* --------------------------------------------------------------- utils -- */

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function clean(value) { return String(value == null ? '' : value).replace(/\s+/g, ' ').trim(); }
  function isYes(value) { return /^yes$/i.test(clean(value)); }
  function isNA(value) { return clean(value).toUpperCase() === 'N/A'; }
  function $id(id) { return document.getElementById(id); }
  function isBool(f) { return f.type === 'boolean'; }
  function defTitle(f) {
    return f.name + ' \u2014 ' + clean(f.definition) + '  |  Values: ' + clean(f.values || 'Free text');
  }
  function byPaperId(a, b) { return (parseInt(a.Paper_ID, 10) || 0) - (parseInt(b.Paper_ID, 10) || 0); }

  /* --------------------------------------------------------- chip colours -- */

  var PALETTE = ['#3f5f91', '#2f6f6b', '#7a5a2e', '#5b4b8a', '#8a4b3f', '#2e6b4f', '#8a5a1e', '#3a6e8f', '#6b4a7a', '#5a6b2e'];
  function chipColor(field, value) {
    var s = field + '|' + value, h = 0;
    for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
    return PALETTE[Math.abs(h) % PALETTE.length];
  }
  function chipHTML(field, value) {
    var c = chipColor(field, value);
    return '<span class="chip" style="color:' + c + ';background:' + c + '1f;border-color:' + c + '55">' +
      esc(value) + '</span>';
  }
  function chipsHTML(field, raw) {
    return String(raw).split(';').map(clean).filter(Boolean)
      .map(function (v) { return chipHTML(field, v); }).join(' ');
  }
  // Focus_Type is free text: split on '/', ',', U+FF0C and U+3001, show at most
  // two chips plus a '+N' chip. The raw coded string is never rewritten: it is
  // trimmed only for the visible fragments and kept intact in the tooltip.
  function focusChipsHTML(raw) {
    var parts = String(raw).split(/[\/,\uFF0C\u3001]/).map(clean).filter(Boolean);
    if (!parts.length) return '<span class="dash">&mdash;</span>';
    var shown = parts.slice(0, 2);
    var html = shown.map(function (v) { return chipHTML('Focus_Type', v); }).join(' ');
    var extra = parts.length - shown.length;
    if (extra > 0) html += ' <span class="chip chip-more" title="' + esc(raw) + '">+' + extra + '</span>';
    return html;
  }

  /* ------------------------------------------------------- gate handling -- */

  function gateOf(name) {
    var m = META[name];
    return m && m.field.gate && m.field.gate.gate_field ? m.field.gate : null;
  }
  function gateMet(paper, gate) {
    return clean(paper.values[gate.gate_field]).toLowerCase() === clean(gate.gate_value).toLowerCase();
  }
  function gateCounts(name) {
    var published = (STATS.gated || []).filter(function (g) { return g.field === name; })[0];
    if (published && published.n != null && published.denominator != null) {
      return { n: published.n, denominator: published.denominator };
    }
    var gate = gateOf(name);
    if (!gate) return null;
    var denom = 0, n = 0;
    PAPERS.forEach(function (p) {
      if (!gateMet(p, gate)) return;
      denom++;
      if (isYes(p.values[name])) n++;
    });
    return { n: n, denominator: denom };
  }
  function gateNote(name) {
    var gate = gateOf(name), counts = gateCounts(name);
    if (!gate || !counts) return '';
    return 'Conditional on ' + gate.gate_field + ' = ' + gate.gate_value + ': ' +
      counts.n + ' of ' + counts.denominator + '.';
  }
  /* -------------------------------------------------------- cell renders -- */

  function cellTd(name, cls, title, body, extraAttr) {
    return '<td class="cell ' + cls + '" data-field="' + esc(name) + '"' +
      (extraAttr || '') + ' title="' + esc(title) + '">' + body + '</td>';
  }

  function cellHTML(paper, f) {
    var name = f.name;
    var raw = clean(paper.values[name]);
    if (!raw) {
      return cellTd(name, 'empty', 'Not reported. ' + defTitle(f), '<span class="dash">&mdash;</span>');
    }
    if (name === 'Focus_Type') {
      return cellTd(name, 'focus', raw, focusChipsHTML(raw));
    }
    if (isBool(f)) {
      if (isNA(raw)) return cellTd(name, 'na', defTitle(f), 'N/A');
      return isYes(raw)
        ? cellTd(name, 'bool', 'Yes. ' + defTitle(f), '<span class="bmark yes" title="Yes">&#10003;</span>')
        : cellTd(name, 'bool', 'No. ' + defTitle(f), '<span class="bmark no" title="No">&#10007;</span>');
    }
    if (isNA(raw)) return cellTd(name, 'na', defTitle(f), 'N/A');
    if (f.type === 'multi-label') return cellTd(name, 'multi', defTitle(f), chipsHTML(name, raw));
    if (f.type === 'single-choice') return cellTd(name, 'choice', defTitle(f), chipHTML(name, raw));
    var key = String(paper.Paper_ID) + '|' + name;
    var open = !!state.textOpen[key];
    return cellTd(name, 'text' + (open ? ' open' : ''), defTitle(f),
      '<button type="button" class="txt-btn' + (open ? ' open' : '') + '" data-text-key="' + esc(key) + '"' +
      ' aria-expanded="' + (open ? 'true' : 'false') + '" title="' + esc(raw) + '">' + esc(raw) + '</button>');
  }

  /* ------------------------------------------------------------ tallies --- */

  function tallyCellHTML(name) {
    var f = META[name].field;
    var counts = {};
    PAPERS.forEach(function (p) {
      var v = clean(p.values[name]);
      if (v) counts[v] = (counts[v] || 0) + 1;
    });
    var parts = [];
    if (isBool(f)) {
      var y = 0, n = 0, na = 0, other = [];
      Object.keys(counts).forEach(function (k) {
        if (isYes(k)) y += counts[k];
        else if (/^no$/i.test(k)) n += counts[k];
        else if (isNA(k)) na += counts[k];
        else other.push(k + ' ' + counts[k]);
      });
      parts.push('Yes ' + y, 'No ' + n);
      if (na) parts.push('N/A ' + na);
      parts = parts.concat(other);
    } else if (f.type === 'single-choice') {
      Object.keys(counts).sort(function (a, b) {
        var pa = VALUE_PRIORITY[clean(a).toLowerCase()];
        var pb = VALUE_PRIORITY[clean(b).toLowerCase()];
        pa = pa == null ? 9 : pa; pb = pb == null ? 9 : pb;
        return pa - pb || counts[b] - counts[a] || a.localeCompare(b);
      }).forEach(function (k) { parts.push(esc(k) + ' ' + counts[k]); });
    } else {
      var filled = Object.keys(counts).reduce(function (s, k) { return s + counts[k]; }, 0);
      parts.push(filled + (filled === 1 ? ' with a value' : ' with a value'));
    }
    var g = (STATS.gated || []).filter(function (x) { return x.field === name; })[0];
    var note = (g && g.n != null && g.denominator != null)
      ? 'conditional ' + g.n + ' of ' + g.denominator : '';
    return '<td data-tally="' + esc(name) + '" title="Tally computed over all ' + N + ' coded papers">' +
      '<span class="tally">' + parts.join(' \u00b7 ') + '</span>' +
      (note ? '<span class="tally-note">' + esc(note) + '</span>' : '') + '</td>';
  }

  /* -------------------------------------------------------- paper tables -- */

  function paperSectionHTML(group) {
    var sid = group.id.toLowerCase();
    var fields = group.fields;
    var head = '<div class="sec-head"><span class="sec-num">' + esc(group.id) + '</span>' +
      '<h2 id="' + sid + '-h">' + esc(group.name) + ' <span class="gcount">' + fields.length + ' fields</span></h2></div>';
    var lead = '<p class="lead">' + esc(clean(group.description)) + '</p>';
    var thead = '<thead><tr><th scope="col" class="col-idx">#</th>' +
      '<th scope="col" class="col-paper">Paper</th>' +
      fields.map(function (f) {
        return '<th scope="col" class="col-cell">' +
          '<button type="button" class="col-btn" data-field="' + esc(f.name) + '"' +
          ' aria-expanded="false" title="' + esc(defTitle(f)) + '">' + esc(f.name) + '</button></th>';
      }).join('') + '</tr></thead>';
    var tbody = '<tbody>' + PAPERS.slice().sort(byPaperId).map(function (p, i) {
      return '<tr class="row">' +
        '<td class="col-idx idx">' + (i + 1) + '</td>' +
        '<td class="col-paper paper"><span class="paper-title">' + esc(clean(p.Title)) + '</span>' +
          '<span class="citation-key">' + esc(clean(p.Author_Year || p.Citation_Key)) + '</span></td>' +
        fields.map(function (f) { return cellHTML(p, f); }).join('') + '</tr>';
    }).join('') + '</tbody>';
    var tfoot = '<tfoot><tr><td class="col-idx"></td>' +
      '<td class="col-paper"><span class="tfoot-label">Tally \u00b7 all ' + N + ' papers</span></td>' +
      fields.map(function (f) { return tallyCellHTML(f.name); }).join('') + '</tr></tfoot>';

    return '<section class="group-section" id="' + sid + '" aria-labelledby="' + sid + '-h">' +
      head + lead +
      '<div class="tablewrap"><table class="sheet-table" id="table-' + sid + '">' +
      thead + tbody + tfoot + '</table></div>' +
      '</section>';
  }

  /* --------------------------------------------------------- claim table -- */

  var SLOT_BY = {};
  SLOTS.forEach(function (s) { SLOT_BY[clean(s.Paper_ID) + '|' + clean(s.Claim_Slot).toUpperCase()] = s; });

  function slotOf(paperId, slot) { return SLOT_BY[clean(paperId) + '|' + slot]; }
  function alignValue(s) { return s ? clean(s.Final_Alignment) : ''; }

  function alignChipHTML(value) {
    var key = clean(value).toUpperCase();
    if (!key || !ALIGN_CLASS[key]) return '<span class="dash">&mdash;</span>';
    return '<span class="chip align ' + ALIGN_CLASS[key] + '" title="' + esc(key) + '">' + esc(key) + '</span>';
  }

  // The full claim sentence is always present in the DOM: it is clamped to two
  // lines by CSS and expanded on click, so nothing is hidden from find-in-page.
  function claimTextHTML(s) {
    var txt = s ? clean(s.Claim_Quote) : '';
    if (!txt) return '<span class="dash">&mdash;</span>';
    return '<span class="claim-text clamp2" role="button" tabindex="0" aria-expanded="false"' +
      ' title="Click to show the full claim">' + esc(txt) + '</span>';
  }

  function alignCountsHTML(slots) {
    var counts = {};
    slots.forEach(function (s) {
      var v = clean(s.Final_Alignment).toUpperCase();
      if (v) counts[v] = (counts[v] || 0) + 1;
    });
    var keys = ALIGN_ORDER.filter(function (k) { return counts[k]; });
    return keys.length ? keys.map(function (k) { return k + ' ' + counts[k]; }).join(' \u00b7 ') : '\u2014';
  }

  function claimSectionHTML() {
    var ordered = PAPERS.slice().sort(byPaperId);

    var rows = ordered.map(function (p, i) {
      var c1 = slotOf(p.Paper_ID, 'C1');
      var c2 = slotOf(p.Paper_ID, 'C2');
      return '<tr class="claim-row">' +
        '<td class="col-idx idx">' + (i + 1) + '</td>' +
        '<td class="col-paper paper"><span class="paper-title">' + esc(clean(p.Title)) + '</span>' +
          '<span class="citation-key">' + esc(clean(p.Author_Year || p.Citation_Key)) + '</span></td>' +
        '<td class="claim-cell">' + claimTextHTML(c1) + '</td>' +
        '<td class="value-cell">' + alignChipHTML(alignValue(c1)) + '</td>' +
        '<td class="claim-cell">' + claimTextHTML(c2) + '</td>' +
        '<td class="value-cell">' + alignChipHTML(alignValue(c2)) + '</td>' +
        '</tr>';
    }).join('');

    var c1Slots = SLOTS.filter(function (s) { return clean(s.Claim_Slot).toUpperCase() === 'C1'; });
    var c2Slots = SLOTS.filter(function (s) { return clean(s.Claim_Slot).toUpperCase() === 'C2'; });
    var tfoot = '<tfoot><tr><td class="col-idx"></td>' +
      '<td class="col-paper"><span class="tfoot-label">Tally \u00b7 all ' + SLOTS.length + ' claim rows</span></td>' +
      '<td class="claim-cell"><span class="tally">' + c1Slots.length + ' slots</span></td>' +
      '<td class="value-cell"><span class="tally">' + alignCountsHTML(c1Slots) + '</span></td>' +
      '<td class="claim-cell"><span class="tally">' + c2Slots.length + ' slots</span></td>' +
      '<td class="value-cell"><span class="tally">' + alignCountsHTML(c2Slots) + '</span></td>' +
      '</tr></tfoot>';

    return '<section class="group-section" id="g7" aria-labelledby="g7-h">' +
      '<div class="sec-head"><span class="sec-num">G7</span>' +
      '<h2 id="g7-h">Claim&ndash;Evidence Alignment <span class="gcount">' + SLOTS.length + ' claim slots</span></h2></div>' +
      '<p class="lead">One row per paper. C1 is the paper\u2019s primary claim; C2 is an explicit extension ' +
      'beyond it, shown where the paper makes one. The value columns give the claim\u2013evidence alignment coding.</p>' +
      '<div class="tablewrap"><table class="sheet-table claim-table" id="table-g7"><thead><tr>' +
      '<th scope="col" class="col-idx">#</th>' +
      '<th scope="col" class="col-paper">Paper</th>' +
      '<th scope="col" class="col-claim">C1</th>' +
      '<th scope="col" class="col-value">C1 value</th>' +
      '<th scope="col" class="col-claim">C2</th>' +
      '<th scope="col" class="col-value">C2 value</th>' +
      '</tr></thead><tbody>' + rows + '</tbody>' + tfoot + '</table></div>' +
      '</section>';
  }

  /* ------------------------------------------------------------ jump bar -- */

  function jumpLinksHTML() {
    return GROUPS.map(function (g) {
      return '<a class="jump-link" href="#' + g.id.toLowerCase() + '" data-target="' + esc(g.id) + '">' +
        esc(g.id + ' ' + (SHORT[g.id] || g.name)) + '</a>';
    }).join('') +
      '<a class="jump-link" href="#g7" data-target="G7">G7 Claim\u2013Evidence</a>';
  }

  /* ---------------------------------------------------------- definition -- */

  function renderPopover(fieldName) {
    var pop = $id('field-pop');
    var f = META[fieldName].field;
    var gate = gateOf(fieldName);
    var note = gateNote(fieldName);
    var fieldNote = clean(f.note);
    pop.dataset.field = fieldName;
    pop.classList.toggle('pinned', !!state.pop.pinned);
    pop.innerHTML =
      '<div class="fp-head"><code>' + esc(f.name) + '</code>' +
      '<span class="fp-actions">' +
      '<button type="button" class="fp-pin" aria-pressed="' + (state.pop.pinned ? 'true' : 'false') + '">' +
      (state.pop.pinned ? 'Unpin' : 'Pin') + '</button>' +
      '<button type="button" class="fp-close" aria-label="Close definition">Close</button></span></div>' +
      '<p class="fp-values"><strong>Values:</strong> ' + esc(clean(f.values || 'Free text')) + '</p>' +
      '<p class="fp-def">' + esc(clean(f.definition)) + '</p>' +
      (note ? '<p class="fp-gate">' + esc(note) + '</p>' : '') +
      (gate && gate.gate_note && !note ? '<p class="fp-gate">' + esc(clean(gate.gate_note)) + '</p>' : '') +
      (fieldNote ? '<p class="fp-def">' + esc(fieldNote) + '</p>' : '');
    pop.hidden = false;
  }

  function openPopover(fieldName, btn) {
    if (state.pop.pinned) {
      state.pop.field = fieldName;
      renderPopover(fieldName);
      highlightHeader(fieldName);
      return;
    }
    state.pop.field = fieldName;
    renderPopover(fieldName);
    positionPopover(btn);
    highlightHeader(fieldName);
  }

  function highlightHeader(fieldName) {
    var btns = document.querySelectorAll('.col-btn');
    for (var i = 0; i < btns.length; i++) {
      var on = state.pop.field === fieldName && btns[i].getAttribute('data-field') === fieldName;
      btns[i].setAttribute('aria-expanded', on ? 'true' : 'false');
    }
  }

  function positionPopover(btn) {
    var pop = $id('field-pop');
    if (!btn) return;
    var rect = btn.getBoundingClientRect();
    var top = rect.bottom + 6;
    var left = Math.max(8, Math.min(rect.left, window.innerWidth - pop.offsetWidth - 16));
    if (top + pop.offsetHeight > window.innerHeight - 8) top = Math.max(8, rect.top - pop.offsetHeight - 6);
    pop.style.top = top + 'px';
    pop.style.left = left + 'px';
  }

  function closePopover(force) {
    if (state.pop.pinned && !force) return;
    state.pop.pinned = false;
    state.pop.field = null;
    var pop = $id('field-pop');
    pop.hidden = true;
    pop.classList.remove('pinned');
    highlightHeader(null);
  }

  function togglePin() {
    state.pop.pinned = !state.pop.pinned;
    renderPopover(state.pop.field);
    if (state.pop.pinned) {
      document.getElementById('field-pop').style.top = '';
      document.getElementById('field-pop').style.left = '';
    }
  }

  /* ------------------------------------------------------------- widgets -- */

  function toggleText(key, btn) {
    var open = !state.textOpen[key];
    if (open) state.textOpen[key] = true; else delete state.textOpen[key];
    btn.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    var td = btn.closest('td');
    if (td) td.classList.toggle('open', open);
  }

  function toggleClaimText(el) {
    var open = !el.classList.contains('expanded');
    el.classList.toggle('expanded', open);
    el.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  /* --------------------------------------------------------- scroll-spy --- */

  function jumpbarHeight() {
    var v = getComputedStyle(document.documentElement).getPropertyValue('--jumpbar-h');
    var n = parseInt(v, 10);
    return isNaN(n) ? 0 : n;
  }
  function syncJumpbarHeight() {
    var bar = $id('jumpbar');
    if (bar) document.documentElement.style.setProperty('--jumpbar-h', bar.offsetHeight + 'px');
  }
  function spy() {
    var threshold = jumpbarHeight() + 18;
    var active = SECTION_IDS[0];
    SECTION_IDS.forEach(function (gid) {
      var el = $id(gid.toLowerCase());
      if (!el) return;
      if (el.getBoundingClientRect().top - threshold <= 4) active = gid;
    });
    // The last section can never reach the threshold once the page is scrolled
    // to its end, so pin it as active at the bottom of the document.
    var doc = document.documentElement;
    if (window.innerHeight + window.scrollY >= doc.scrollHeight - 4) {
      active = SECTION_IDS[SECTION_IDS.length - 1];
    }
    var links = document.querySelectorAll('.jump-link');
    for (var i = 0; i < links.length; i++) {
      if (links[i].getAttribute('data-target') === active) links[i].setAttribute('aria-current', 'true');
      else links[i].removeAttribute('aria-current');
    }
  }

  /* ---------------------------------------------------------------- build -- */

  function build() {
    var html = GROUPS.map(function (g) { return paperSectionHTML(g); }).join('');
    html += claimSectionHTML();
    $id('groups').innerHTML = html;
  }

  /* --------------------------------------------------------------- events -- */

  function bind() {
    $id('jump-links').innerHTML = jumpLinksHTML();

    $id('groups').addEventListener('click', function (e) {
      var colBtn = e.target.closest('.col-btn');
      if (colBtn) { openPopover(colBtn.getAttribute('data-field'), colBtn); return; }
      var txt = e.target.closest('.txt-btn');
      if (txt) { toggleText(txt.getAttribute('data-text-key'), txt); return; }
      var claim = e.target.closest('.claim-text');
      if (claim) toggleClaimText(claim);
    });

    $id('groups').addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;
      var claim = e.target.closest('.claim-text');
      if (!claim) return;
      e.preventDefault();
      toggleClaimText(claim);
    });

    document.addEventListener('click', function (e) {
      if (e.target.closest('#field-pop')) return;
      if (e.target.closest('.col-btn')) return;
      closePopover(false);
    });

    $id('field-pop').addEventListener('click', function (e) {
      if (e.target.closest('.fp-close')) { closePopover(true); return; }
      if (e.target.closest('.fp-pin')) { togglePin(); return; }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closePopover(true);
    });

    window.addEventListener('scroll', spy, { passive: true });
    window.addEventListener('resize', function () { syncJumpbarHeight(); spy(); });
    window.addEventListener('hashchange', function () { setTimeout(spy, 30); });
    window.addEventListener('load', function () { syncJumpbarHeight(); spy(); });
  }

  /* ---------------------------------------------------------------- start -- */

  syncJumpbarHeight();
  build();
  bind();
  syncJumpbarHeight();
  spy();
  setTimeout(function () { syncJumpbarHeight(); spy(); }, 0);
})();
