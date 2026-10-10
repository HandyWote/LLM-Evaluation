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
  var ALIGN_ORDER = ['EXCEEDS', 'PARTIAL', 'ALIGNED', 'UNCLEAR'];
  var PROCESS_FIELDS = [
    'Provisional_Alignment', 'Codex_Alignment', 'Agreement_Status',
    'Rationale', 'Final_Rationale', 'Final_Decision_Type', 'Human_Review_Flag'
  ];
  var VALUE_PRIORITY = { yes: 0, no: 1, 'n/a': 2 };

  var DOWNLOADS = [
    { href: 'downloads/final-table.csv', title: 'Paper-level coding table',
      desc: '52 papers \u00d7 38 coded fields, groups G1\u2013G6.', size: '137 KB' },
    { href: 'downloads/theory_eval_refined_coding_refined.csv', title: 'Refined theory coding',
      desc: 'Theory grounding, operationalization and instrument types.', size: '57 KB' },
    { href: 'downloads/claim_level_FINAL_analysis_ready.csv', title: 'Claim\u2013evidence alignment',
      desc: 'The 72 claim\u2013evidence slots coded in G7.', size: '119 KB' },
    { href: 'downloads/09_appendices.tex', title: 'Codebook appendix (LaTeX)',
      desc: 'The 7 coding groups and their field definitions.', size: '49 KB' }
  ];

  var state = {
    q: '',
    textOpen: {},
    claimOpen: {},
    pop: { field: null, pinned: false },
    claim: { align: 'ALL', slot: 'ALL', review: 'ALL' }
  };

  var paperRowsByGroup = {};
  var claimRows = [];

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

  var PALETTE = ['#0f766e', '#0d9488', '#0e7490', '#4f46e5', '#7c3aed', '#b45309', '#be123c', '#15803d', '#c2410c', '#1d4ed8'];
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
  function gateFlag(paper, name) {
    var gate = gateOf(name);
    if (!gate || gateMet(paper, gate)) return null;
    return isYes(paper.values[name]) ? gate : null;
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
  function gateFlagTitle(paper, name) {
    var gate = gateFlag(paper, name);
    if (!gate) return '';
    var counts = gateCounts(name);
    return 'Coded "' + clean(paper.values[name]) + '", but ' + gate.gate_field + ' = ' +
      gate.gate_value + ' is not met for this paper, so it is excluded from the conditional count' +
      (counts ? ' (' + counts.n + ' of ' + counts.denominator + ')' : '') + '.';
  }

  var GATE_MARK = '<span class="gate-mark" aria-hidden="true">\u2020</span>';

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
      if (gateFlag(paper, name)) {
        return cellTd(name, 'bool flagged', gateFlagTitle(paper, name) + ' ' + defTitle(f),
          '<span class="bmark yes">&#10003;</span>' + GATE_MARK, ' data-gate-flag="1"');
      }
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

  function searchTextPaper(p) {
    var hay = [p.Title, p.Citation_Key, p.Paper_ID];
    Object.keys(p.values).forEach(function (k) { hay.push(p.values[k]); });
    return clean(hay.join(' ')).toLowerCase();
  }

  function paperSectionHTML(group, index) {
    var sid = group.id.toLowerCase();
    var fields = group.fields;
    var head = '<div class="sec-head"><span class="sec-num">' + esc(group.id) + '</span>' +
      '<h2>' + esc(group.name) + ' <span class="gcount">' + fields.length + ' fields</span></h2></div>';
    var lead = '<p class="lead">' + esc(clean(group.description)) + '</p>';
    var thead = '<thead><tr><th scope="col" class="col-idx">#</th>' +
      '<th scope="col" class="col-paper">Paper</th>' +
      fields.map(function (f) {
        return '<th scope="col" class="col-cell">' +
          '<button type="button" class="col-btn" data-field="' + esc(f.name) + '"' +
          ' aria-expanded="false" title="' + esc(defTitle(f)) + '">' + esc(f.name) + '</button></th>';
      }).join('') + '</tr></thead>';
    var tbody = '<tbody>' + PAPERS.slice().sort(byPaperId).map(function (p) {
      return '<tr class="row" data-paper="' + esc(p.Paper_ID) + '" data-search="' + esc(searchTextPaper(p)) + '">' +
        '<td class="col-idx idx">' + esc(p.Paper_ID) + '</td>' +
        '<td class="col-paper paper"><span class="paper-title">' + esc(clean(p.Title)) + '</span>' +
          '<span class="citation-key">' + esc(p.Citation_Key) + '</span></td>' +
        fields.map(function (f) { return cellHTML(p, f); }).join('') + '</tr>';
    }).join('') + '</tbody>';
    var tfoot = '<tfoot><tr><td class="col-idx"></td>' +
      '<td class="col-paper"><span class="tfoot-label">Tally \u00b7 all ' + N + ' papers</span></td>' +
      fields.map(function (f) { return tallyCellHTML(f.name); }).join('') + '</tr></tfoot>';

    return '<section class="group-section" id="' + sid + '" aria-labelledby="' + sid + '-h">' +
      head + lead +
      '<div class="tablewrap"><table class="sheet-table" id="table-' + sid + '">' +
      thead + tbody + tfoot + '</table></div>' +
      '<p class="caption" data-caption="' + esc(group.id) + '">' + captionHTML(group, fields.length) + '</p>' +
      '<p class="section-empty" hidden>No paper matches the current search.</p>' +
      '</section>';
  }

  function captionHTML(group, fieldCount) {
    var base = 'Tallies in the footer cover all ' + N + ' coded papers, and every paper is shown, ' +
      'so no row is omitted.';
    if (group.id === 'G4') {
      return '<strong>' + esc(group.name) + '.</strong> Extended dialogue, dynamic user state and ' +
        'longitudinal evaluation are three <em>independent</em> coded fields, not a nested funnel: ' +
        'paper 34 is longitudinal without extended dialogue, and papers 65 and 111 model a dynamic user ' +
        'state without extended dialogue. ' + base;
    }
    if (group.id === 'G5') {
      return '<strong>Reliability_Reported</strong> is coded for all ' + N + ' papers (N/A means no human ' +
        'evaluation was used). The 13 of 45 figure is a derived intersection between Has_Rubric and ' +
        'Reliability_Reported, not a field gate. ' + base;
    }
    if (group.id === 'G6') {
      return '<strong>LLM_Judge_Validated</strong> is conditional on Eval_LLM_Judge = Yes: 23 of the 30 ' +
        'eligible papers validate the judge against humans. The grid still shows the released codes ' +
        '(24 Yes, one of them flagged \u2020 because the governing question does not apply). ' + base;
    }
    return '<strong>' + esc(group.id) + ' \u00b7 ' + esc(group.name) + '</strong> \u2014 ' + fieldCount +
      ' of 38 coded fields. ' + base;
  }

  /* --------------------------------------------------------- claim table -- */

  function searchTextClaim(s) {
    return clean([
      s.Title, s.Citation_Key, s.Paper_ID, s.Claim_Slot, s.Claim_Quote, s.Claim_Section,
      s.Evidence_Quote, s.Evidence_Section, s.Evidence_Location_Detail, s.Final_Alignment,
      s.Final_Decision_Type, s.Human_Review_Flag
    ].join(' ')).toLowerCase();
  }

  function claimOrder(a, b) {
    var ra = ALIGN_ORDER.indexOf(clean(a.Final_Alignment));
    var rb = ALIGN_ORDER.indexOf(clean(b.Final_Alignment));
    if (ra < 0) ra = 99;
    if (rb < 0) rb = 99;
    if (ra !== rb) return ra - rb;
    if (byPaperId(a, b) !== 0) return byPaperId(a, b);
    return clean(a.Claim_Slot).localeCompare(clean(b.Claim_Slot));
  }

  function claimQuoteCell(s, which) {
    var quote = which === 'claim' ? s.Claim_Quote : s.Evidence_Quote;
    var page = which === 'claim' ? s.Claim_Page : s.Evidence_Page;
    var section = which === 'claim' ? s.Claim_Section : s.Evidence_Section;
    var detail = which === 'claim' ? '' : clean(s.Evidence_Location_Detail);
    var key = s.Paper_ID + '|' + s.Claim_Slot + '|' + which;
    var open = !!state.textOpen[key];
    var body = '<button type="button" class="txt-btn quote-btn' + (open ? ' open' : '') + '"' +
      ' data-text-key="' + esc(key) + '" aria-expanded="' + (open ? 'true' : 'false') + '"' +
      ' title="' + esc(clean(quote)) + '">' + esc(clean(quote)) + '</button>';
    var meta = 'p. ' + esc(clean(page)) + ' \u00b7 ' + esc(clean(section)) +
      (detail ? ' \u00b7 ' + esc(detail) : '');
    return '<td class="quote-cell">' + body + '<p class="meta">' + meta + '</p></td>';
  }

  function claimDetailHTML(s, key) {
    var items = PROCESS_FIELDS.map(function (name) {
      var v = clean(s[name]);
      if (!v) return '';
      return '<li class="rec-item"><span class="rec-label">' + esc(name) + '</span>' +
        '<span class="rec-value">' + esc(v) + '</span></li>';
    }).join('');
    var links = [];
    if (s.Paper_URL) links.push('Paper: <a class="page-link" href="' + esc(s.Paper_URL) + '" target="_blank" rel="noopener">' + esc(s.Citation_Key) + '</a>');
    if (s.Claim_URL) links.push('Claim: <a class="page-link" href="' + esc(s.Claim_URL) + '" target="_blank" rel="noopener">PDF p. ' + esc(clean(s.Claim_Page)) + '</a>');
    if (s.Evidence_URL) links.push('Evidence: <a class="page-link" href="' + esc(s.Evidence_URL) + '" target="_blank" rel="noopener">PDF p. ' + esc(clean(s.Evidence_Page)) + '</a>');
    return '<tr class="claim-detail-row" id="cd-' + esc(key) + '" hidden><td colspan="7"><div class="claim-detail">' +
      '<h4>Coding process for ' + esc(s.Citation_Key) + ' \u00b7 ' + esc(s.Claim_Slot) + '</h4>' +
      (items ? '<ul class="rec">' + items + '</ul>'
             : '<p class="note">No coding-process columns are bundled for this claim.</p>') +
      (links.length ? '<div class="claim-links">' + links.join('') + '</div>' : '') +
      '</div></td></tr>';
  }

  function claimSectionHTML() {
    var rows = SLOTS.slice().sort(claimOrder).map(function (s) {
      var key = s.Paper_ID + '|' + s.Claim_Slot;
      var align = clean(s.Final_Alignment);
      var review = clean(s.Human_Review_Flag);
      return '<tr class="claim-row" data-key="' + esc(key) + '" id="cr-' + esc(key) + '"' +
        ' data-paper="' + esc(s.Paper_ID) + '" data-align="' + esc(align) + '"' +
        ' data-slot="' + esc(s.Claim_Slot) + '" data-review="' + esc(review) + '"' +
        ' data-search="' + esc(searchTextClaim(s)) + '">' +
        '<td class="col-idx idx">' + esc(s.Paper_ID) + '</td>' +
        '<td class="col-paper paper"><button type="button" class="claim-toggle" aria-expanded="false"' +
          ' aria-controls="cd-' + esc(key) + '">' +
          '<span class="chev" aria-hidden="true">\u25b8</span>' +
          '<span class="pt"><span class="paper-title">' + esc(clean(s.Title)) + '</span>' +
          '<span class="citation-key">' + esc(s.Citation_Key) + '</span></span></button></td>' +
        '<td><span class="chip slot">' + esc(s.Claim_Slot) + '</span></td>' +
        claimQuoteCell(s, 'claim') +
        claimQuoteCell(s, 'evidence') +
        '<td>' + (align ? chipHTML('Final_Alignment', align) : '<span class="dash">&mdash;</span>') + '</td>' +
        '<td>' + (review ? chipHTML('Human_Review_Flag', review) : '<span class="dash">&mdash;</span>') + '</td>' +
        '</tr>' + claimDetailHTML(s, key);
    }).join('');

    var filters = '<div class="filters" id="claim-filters">' +
      selectHTML('cf-align', 'Alignment', 'align', distinct('Final_Alignment')) +
      selectHTML('cf-slot', 'Slot', 'slot', distinct('Claim_Slot')) +
      selectHTML('cf-review', 'Review flag', 'review', distinct('Human_Review_Flag')) +
      '</div>';

    return '<section class="group-section" id="g7" aria-labelledby="g7-h">' +
      '<div class="sec-head"><span class="sec-num">G7</span>' +
      '<h2>Claim&ndash;Evidence Alignment <span class="gcount">' + SLOTS.length + ' claim rows</span></h2></div>' +
      '<p class="lead">One row per claim&ndash;evidence slot (72 rows across ' + N + ' papers), ordered ' +
      'Exceeds first, then Partial, Aligned and Unclear. Click a row to reveal its coding-process columns ' +
      'and the page-level links.</p>' +
      filters +
      '<div class="tablewrap"><table class="sheet-table" id="table-g7"><thead><tr>' +
      '<th scope="col" class="col-idx">#</th>' +
      '<th scope="col" class="col-paper">Paper</th>' +
      '<th scope="col">Slot</th>' +
      '<th scope="col">Claim quote \u00b7 page \u00b7 section</th>' +
      '<th scope="col">Evidence quote \u00b7 page \u00b7 section \u00b7 location</th>' +
      '<th scope="col">Alignment</th>' +
      '<th scope="col">Review flag</th>' +
      '</tr></thead><tbody>' + rows + '</tbody></table></div>' +
      '<p class="caption" data-caption="G7"><strong>G7 &middot; Claim&ndash;evidence alignment.</strong> ' +
      'All ' + SLOTS.length + ' slots are shown; the alignment, slot and review filters only narrow the ' +
      'view and never remove a paper from the corpus.</p>' +
      '<p class="section-empty" hidden>No claim&ndash;evidence slot matches the current search or filters.</p>' +
      '</section>';
  }

  function distinct(field) {
    var seen = {};
    SLOTS.forEach(function (s) { var v = clean(s[field]); if (v) seen[v] = true; });
    return Object.keys(seen).sort();
  }
  function selectHTML(id, label, key, values) {
    return '<label class="tool-field">' + esc(label) +
      '<select id="' + id + '" data-claim="' + esc(key) + '">' +
      '<option value="ALL">All</option>' +
      values.map(function (v) {
        return '<option value="' + esc(v) + '"' + (state.claim[key] === v ? ' selected' : '') + '>' +
          esc(v) + '</option>';
      }).join('') + '</select></label>';
  }

  /* ------------------------------------------------------------ jump bar -- */

  function jumpLinksHTML() {
    return GROUPS.map(function (g) {
      var count = g.fields.length;
      return '<a class="jump-link" href="#' + g.id.toLowerCase() + '" data-target="' + esc(g.id) + '">' +
        esc(g.id + ' ' + (SHORT[g.id] || g.name) + ' (' + count + ')') + '</a>';
    }).join('') +
      '<a class="jump-link" href="#g7" data-target="G7">G7 Claim\u2013Evidence (' + SLOTS.length + ')</a>';
  }

  function renderDownloads() {
    $id('dl-list').innerHTML = DOWNLOADS.map(function (d) {
      return '<a class="dl-item" href="' + esc(d.href) + '">' +
        '<span class="dl-title">' + esc(d.title) + '</span>' +
        '<span class="dl-desc">' + esc(d.desc) + '</span>' +
        '<span class="dl-meta"><code>' + esc(d.href) + '</code> \u00b7 ' + esc(d.size) + '</span></a>';
    }).join('');
  }

  /* -------------------------------------------------------- key figures --- */

  function yesCount(field) {
    return PAPERS.filter(function (p) { return isYes(p.values[field]); }).length;
  }
  function bvCount(id) {
    var bv = STATS.behavioral_validity;
    var hit = bv && bv.criteria && bv.criteria.filter(function (c) { return c.id === id; })[0];
    if (hit && hit.n != null) return hit.n;
    if (id === 'extended_dialogue') {
      return PAPERS.filter(function (p) {
        return clean(p.values.Interaction_Level).toLowerCase() === 'extended dialogue';
      }).length;
    }
    return yesCount(id === 'dynamic_state' ? 'Uses_Dynamic_State' : 'Has_Longitudinal_Eval');
  }

  function renderKeyFigures() {
    var rubric = STATS.rubric || {};
    var judge = STATS.llm_judge || {};
    var rubricN = rubric.has != null ? rubric.has : yesCount('Has_Rubric');
    var relN = rubric.reported_reliability != null ? rubric.reported_reliability : 13;
    var judgeN = judge.used != null ? judge.used : yesCount('Eval_LLM_Judge');
    var validN = judge.validated != null ? judge.validated : 23;
    $id('keyline').innerHTML =
      '<strong>' + N + ' papers</strong> &middot; ' +
      '<strong>' + rubricN + '</strong> use a rubric &rarr; <strong>' + relN + '</strong> report inter-rater reliability &middot; ' +
      '<strong>' + judgeN + '</strong> use an LLM judge &rarr; <strong>' + validN + '</strong> validate against humans &middot; ' +
      '<strong>' + bvCount('extended_dialogue') + '</strong> evaluate extended dialogues / ' +
      '<strong>' + bvCount('dynamic_state') + '</strong> model a dynamic user state / ' +
      '<strong>' + bvCount('longitudinal') + '</strong> include longitudinal evaluation';
    $id('keyline-note').textContent = 'Extended dialogue, dynamic user state and longitudinal evaluation are ' +
      'three independent coded fields (of ' + N + ' papers each), not a nested funnel.';
  }

  /* ----------------------------------------------------------- filtering -- */

  function paperMatches(tr, q) {
    return !q || tr.getAttribute('data-search').indexOf(q) >= 0;
  }
  function claimMatches(tr, q) {
    var c = state.claim;
    if (c.align !== 'ALL' && tr.getAttribute('data-align') !== c.align) return false;
    if (c.slot !== 'ALL' && tr.getAttribute('data-slot') !== c.slot) return false;
    if (c.review !== 'ALL' && tr.getAttribute('data-review') !== c.review) return false;
    return !q || tr.getAttribute('data-search').indexOf(q) >= 0;
  }

  function syncClaimDetail(tr, visible) {
    var det = tr.nextElementSibling;
    if (!det || !det.classList.contains('claim-detail-row')) return;
    var open = !!state.claimOpen[tr.getAttribute('data-key')];
    det.hidden = !(visible && open);
    var btn = tr.querySelector('.claim-toggle');
    var chev = tr.querySelector('.chev');
    if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (chev) chev.textContent = open ? '\u25be' : '\u25b8';
    tr.classList.toggle('open', open && visible);
  }

  function applyFilters() {
    var q = clean(state.q).toLowerCase();
    var paperHits = 0, claimHits = 0;

    SECTION_IDS.forEach(function (gid) {
      var sec = $id(gid.toLowerCase());
      if (!sec) return;
      var rows = paperRowsByGroup[gid] || [];
      var visible = 0;
      rows.forEach(function (tr) {
        var ok = paperMatches(tr, q);
        tr.classList.toggle('row-hidden', !ok);
        if (ok) visible++;
      });
      if (gid === 'G1') paperHits = visible;
      var empty = sec.querySelector('.section-empty');
      if (empty) empty.hidden = visible > 0 || !rows.length;
    });

    claimRows.forEach(function (tr) {
      var ok = claimMatches(tr, q);
      tr.classList.toggle('row-hidden', !ok);
      if (ok) claimHits++;
      syncClaimDetail(tr, ok);
    });
    var claimEmpty = $id('g7') && $id('g7').querySelector('.section-empty');
    if (claimEmpty) claimEmpty.hidden = claimHits > 0;

    var mc = $id('match-count');
    if (mc) {
      mc.innerHTML = q
        ? '<b>' + paperHits + '</b> of ' + N + ' papers match \u00b7 <b>' + claimHits + '</b> of ' + SLOTS.length + ' claims match'
        : '';
    }
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

  function toggleClaimRow(tr) {
    var key = tr.getAttribute('data-key');
    var open = !state.claimOpen[key];
    if (open) state.claimOpen[key] = true; else delete state.claimOpen[key];
    syncClaimDetail(tr, !tr.classList.contains('row-hidden'));
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
    var html = GROUPS.map(function (g, i) { return paperSectionHTML(g, i); }).join('');
    html += claimSectionHTML();
    $id('groups').innerHTML = html;

    paperRowsByGroup = {};
    GROUPS.forEach(function (g) {
      paperRowsByGroup[g.id] = Array.prototype.slice.call(
        document.querySelectorAll('#table-' + g.id.toLowerCase() + ' tbody tr.row'));
    });
    claimRows = Array.prototype.slice.call(document.querySelectorAll('.claim-row'));
  }

  /* --------------------------------------------------------------- events -- */

  function bind() {
    $id('jump-links').innerHTML = jumpLinksHTML();
    renderDownloads();
    renderKeyFigures();

    $id('search').addEventListener('input', function () {
      state.q = this.value;
      applyFilters();
    });

    $id('claim-filters').addEventListener('change', function (e) {
      var sel = e.target.closest('[data-claim]');
      if (!sel) return;
      state.claim[sel.getAttribute('data-claim')] = sel.value;
      applyFilters();
    });

    $id('groups').addEventListener('click', function (e) {
      var colBtn = e.target.closest('.col-btn');
      if (colBtn) { openPopover(colBtn.getAttribute('data-field'), colBtn); return; }
      var txt = e.target.closest('.txt-btn');
      if (txt) { toggleText(txt.getAttribute('data-text-key'), txt); return; }
      var toggle = e.target.closest('.claim-toggle');
      if (toggle) { toggleClaimRow(toggle.closest('tr.claim-row')); return; }
      var row = e.target.closest('tr.claim-row');
      if (row) { toggleClaimRow(row); return; }
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
  applyFilters();
  syncJumpbarHeight();
  spy();
  setTimeout(function () { syncJumpbarHeight(); spy(); }, 0);
})();
