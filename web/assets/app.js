/* ==========================================================================
   From Surface Realism to Behavioral Validity — coded-corpus sheet browser
   Reads window.SURVEY_DATA (bundled by web/data/data.js). No fetch, no deps,
   so the page renders when opened directly from file://.

   The page is the coded Excel sheet: 52 papers folded into the 7 coding groups
   (G1-G6 = 38 coded fields, G7 = the 72-row claim-evidence sheet), unfolded by
   a sheet tab, an expand-all toggle, and a per-row expand.
   ========================================================================== */
(function () {
  'use strict';

  var DATA = window.SURVEY_DATA;
  if (!DATA) {
    var msg = document.createElement('p');
    msg.className = 'fatal';
    msg.textContent = 'Data bundle not found. Expected web/data/data.js to define window.SURVEY_DATA.';
    document.body.insertBefore(msg, document.getElementById('main'));
    return;
  }

  var GROUPS = (DATA.codebook || []).filter(function (g) { return g.id !== 'G7'; });
  var ALL_FIELDS = [];
  var META = {};
  GROUPS.forEach(function (g) {
    g.fields.forEach(function (f) {
      META[f.name] = { group: g, field: f };
      ALL_FIELDS.push(f.name);
    });
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
  function shortName(g) { return SHORT[g.id] || g.name; }

  var SHEETS = GROUPS.map(function (g) {
    return { id: g.id, label: g.id + ' ' + shortName(g) + ' (' + g.fields.length + ')', group: g };
  }).concat([{ id: 'G7', label: 'Claim\u2013evidence (G7, ' + SLOTS.length + ')' }]);

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
    sheet: 'G1',
    page: 1,
    size: 26,
    q: '',
    expandAll: false,
    open: {},
    claim: { q: '', align: 'ALL', slot: 'ALL', review: 'ALL', page: 1 }
  };

  /* ------------------------------------------------------------ helpers -- */

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function clean(value) { return String(value == null ? '' : value).replace(/\s+/g, ' ').trim(); }
  function isYes(value) { return /^yes$/i.test(clean(value)); }
  function isNA(value) { return clean(value).toUpperCase() === 'N/A'; }
  function $id(id) { return document.getElementById(id); }
  function pluck(list, key) {
    var seen = {};
    list.forEach(function (x) { var v = clean(x[key]); if (v) seen[v] = true; });
    return Object.keys(seen).sort();
  }

  // Stable colour for a coded value: the same field+value is always the same
  // colour, and every field's chips are independent of the current view.
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
  function isBool(f) {
    return f.type === 'boolean' || /^yes\s*\/\s*no$/i.test(clean(f.values));
  }
  function defTitle(f) {
    return f.name + ' \u2014 ' + clean(f.definition) + '  |  Values: ' + clean(f.values || 'Free text');
  }

  /* ------------------------------------------------------- gate handling -- */

  // A gated field is only interpretable for the papers where gate_field has
  // gate_value. The released coded value is ALWAYS shown: when a paper is coded
  // Yes although the gate is not met, the cell keeps "Yes" and carries a flag
  // marker explaining that the paper is excluded from the conditional count
  // (e.g. 23 of 30), so the sheet still mirrors the downloadable CSV.
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
  function gateFlagTitle(paper, name) {
    var gate = gateFlag(paper, name);
    if (!gate) return '';
    var counts = gateCounts(name);
    return 'Coded "' + clean(paper.values[name]) + '", but ' + gate.gate_field + ' = ' +
      gate.gate_value + ' is not met for this paper, so it is excluded from the conditional count' +
      (counts ? ' (' + counts.n + ' of ' + counts.denominator + ')' : '') + '.';
  }
  function gateCounts(name) {
    var gate = gateOf(name);
    if (!gate) return null;
    var published = (STATS.gated || []).filter(function (g) { return g.field === name; })[0];
    if (published && published.n != null && published.denominator != null) {
      return { n: published.n, denominator: published.denominator };
    }
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

  /* ----------------------------------------------------- cell rendering -- */

  var GATE_MARK = '<span class="gate-mark" aria-hidden="true">\u2020</span>';

  function cellHTML(paper, name) {
    var f = META[name].field;
    var title = defTitle(f);
    var flag = gateFlag(paper, name);
    var raw = clean(paper.values[name]);
    if (!raw) return '<td class="cell empty" title="Not reported. ' + esc(title) + '">&mdash;</td>';
    if (flag) {
      return '<td class="cell bool flagged" title="' + esc(gateFlagTitle(paper, name) + ' ' + title) + '">' +
        '<span class="bmark yes">&#10003;</span>' + GATE_MARK + '</td>';
    }
    if (isBool(f)) {
      if (isNA(raw)) return '<td class="cell na" title="' + esc(title) + '">N/A</td>';
      return isYes(raw)
        ? '<td class="cell bool" title="Yes. ' + esc(title) + '"><span class="bmark yes" title="Yes">&#10003;</span></td>'
        : '<td class="cell bool" title="No. ' + esc(title) + '"><span class="bmark no" title="No">&#10007;</span></td>';
    }
    if (isNA(raw)) return '<td class="cell na" title="' + esc(title) + '">N/A</td>';
    if (f.type === 'multi-label') return '<td class="cell multi" title="' + esc(title) + '">' + chipsHTML(name, raw) + '</td>';
    if (f.type === 'single-choice') return '<td class="cell choice" title="' + esc(title) + '">' + chipHTML(name, raw) + '</td>';
    return '<td class="cell txt" title="' + esc(title) + '">' +
      '<button type="button" class="txt-btn" title="' + esc(raw) + '">' + esc(raw) + '</button></td>';
  }

  function recordValue(paper, name) {
    var f = META[name].field;
    var flag = gateFlag(paper, name);
    var raw = clean(paper.values[name]);
    var suffix = flag
      ? ' <span class="gate-flag-note">coded ' + esc(raw) + '; excluded from the conditional count' +
        (gateCounts(name) ? ' (' + gateCounts(name).n + ' of ' + gateCounts(name).denominator + ')' : '') +
        '.</span>'
      : '';
    if (!raw) return '<span class="empty">&mdash;</span>';
    if (isBool(f)) {
      if (isNA(raw)) return '<span class="na">N/A</span>';
      return (isYes(raw) ? '<span class="bmark yes">&#10003;</span> Yes' : '<span class="bmark no">&#10007;</span> No') + suffix;
    }
    if (f.type === 'multi-label') return chipsHTML(name, raw) + suffix;
    if (f.type === 'single-choice') return chipHTML(name, raw) + suffix;
    return esc(raw) + suffix;
  }

  /* --------------------------------------------------------- key figures -- */

  function yesCount(field) {
    return PAPERS.filter(function (p) { return isYes(p.values[field]); }).length;
  }
  function crossCount(a, b) {
    return PAPERS.filter(function (p) { return isYes(p.values[a]) && isYes(p.values[b]); }).length;
  }
  function bvCount(id) {
    var bv = STATS.behavioral_validity;
    var hit = bv && bv.criteria && bv.criteria.filter(function (c) { return c.id === id; })[0];
    if (hit && hit.n != null) return hit.n;
    if (id === 'extended_dialogue') {
      return PAPERS.filter(function (p) { return clean(p.values.Interaction_Level).toLowerCase() === 'extended dialogue'; }).length;
    }
    return yesCount(id === 'dynamic_state' ? 'Uses_Dynamic_State' : 'Has_Longitudinal_Eval');
  }

  function renderKeyFigures() {
    var rubric = STATS.rubric || {};
    var judge = STATS.llm_judge || {};
    var rubricN = rubric.has != null ? rubric.has : yesCount('Has_Rubric');
    var relN = rubric.reported_reliability != null ? rubric.reported_reliability : crossCount('Has_Rubric', 'Reliability_Reported');
    var judgeN = judge.used != null ? judge.used : yesCount('Eval_LLM_Judge');
    var validN = judge.validated != null ? judge.validated : crossCount('Eval_LLM_Judge', 'LLM_Judge_Validated');
    var ext = bvCount('extended_dialogue'), dyn = bvCount('dynamic_state'), lon = bvCount('longitudinal');

    $id('keyline').innerHTML =
      '<strong>' + N + ' papers</strong> &middot; ' +
      '<strong>' + rubricN + '</strong> use a rubric &rarr; <strong>' + relN + '</strong> report inter-rater reliability &middot; ' +
      '<strong>' + judgeN + '</strong> use an LLM judge &rarr; <strong>' + validN + '</strong> validate against humans &middot; ' +
      '<strong>' + ext + '</strong> evaluate extended dialogues / <strong>' + dyn + '</strong> model a dynamic user state / ' +
      '<strong>' + lon + '</strong> include longitudinal evaluation';
    $id('keyline-note').textContent = 'Extended dialogue, dynamic user state and longitudinal evaluation are three ' +
      'independent coded fields (of ' + N + ' papers each), not a nested funnel.';
  }

  /* -------------------------------------------------------------- toolbar -- */

  function renderTabs() {
    var host = $id('tabs');
    host.innerHTML = SHEETS.map(function (s) {
      var active = state.sheet === s.id;
      return '<button type="button" role="tab" id="tab-' + s.id + '" data-sheet="' + s.id + '"' +
        ' aria-selected="' + (active ? 'true' : 'false') + '" aria-controls="sheet-table"' +
        ' class="tab' + (active ? ' active' : '') + '">' + esc(s.label) + '</button>';
    }).join('');
  }

  function buildFilters() {
    function select(id, label, key, values) {
      return '<label class="tool-field">' + label +
        '<select id="' + id + '" data-claim="' + key + '"><option value="ALL">All</option>' +
        values.map(function (v) {
          return '<option value="' + esc(v) + '"' + (state.claim[key] === v ? ' selected' : '') + '>' + esc(v) + '</option>';
        }).join('') + '</select></label>';
    }
    $id('claim-filters').innerHTML =
      select('cf-align', 'Alignment', 'align', pluck(SLOTS, 'Final_Alignment')) +
      select('cf-slot', 'Slot', 'slot', pluck(SLOTS, 'Claim_Slot')) +
      select('cf-review', 'Review flag', 'review', pluck(SLOTS, 'Human_Review_Flag'));
  }

  function renderFilters() {
    $id('claim-filters').hidden = state.sheet !== 'G7';
  }

  function renderDownloads() {
    $id('dl-list').innerHTML = DOWNLOADS.map(function (d) {
      return '<a class="dl-item" href="' + esc(d.href) + '">' +
        '<span class="dl-title">' + esc(d.title) + '</span>' +
        '<span class="dl-desc">' + esc(d.desc) + '</span>' +
        '<span class="dl-meta"><code>' + esc(d.href) + '</code> &middot; ' + esc(d.size) + '</span></a>';
    }).join('');
  }

  /* ----------------------------------------------------------- pagination -- */

  function pageSlice(rows, page) {
    var size = state.size > 0 ? state.size : (rows.length || 1);
    var pages = Math.max(1, Math.ceil(rows.length / size));
    if (page > pages) page = pages;
    if (page < 1) page = 1;
    return { rows: rows.slice((page - 1) * size, (page - 1) * size + size), page: page, pages: pages, size: size };
  }

  function footHTML(slice, total, noun) {
    return '<span class="page-info">Page ' + slice.page + ' of ' + slice.pages + '</span>' +
      '<span class="page-count">Showing ' + (slice.rows.length ? ((slice.page - 1) * slice.size + 1) : 0) +
      '&ndash;' + ((slice.page - 1) * slice.size + slice.rows.length) + ' of ' + total + ' ' + noun + '</span>' +
      '<span class="page-btns">' +
      '<button type="button" class="page-btn" data-page="' + (slice.page - 1) + '"' + (slice.page <= 1 ? ' disabled' : '') + '>&larr; Previous</button>' +
      '<button type="button" class="page-btn" data-page="' + (slice.page + 1) + '"' + (slice.page >= slice.pages ? ' disabled' : '') + '>Next &rarr;</button>' +
      '</span>';
  }

  /* -------------------------------------------------------- paper sheets -- */

  function visibleFields() {
    if (state.expandAll) return ALL_FIELDS;
    var g = GROUPS.filter(function (x) { return x.id === state.sheet; })[0];
    return g ? g.fields.map(function (f) { return f.name; }) : [];
  }

  function matchesQuery(paper, q) {
    if (!q) return true;
    var hay = paper.Title + ' ' + paper.Citation_Key + ' ' + paper.Paper_ID;
    Object.keys(paper.values).forEach(function (k) { hay += ' ' + paper.values[k]; });
    return hay.toLowerCase().indexOf(q) >= 0;
  }

  function headerHTML(name) {
    var m = META[name], title = defTitle(m.field);
    return '<th scope="col" class="col-cell" title="' + esc(title) + '">' +
      (state.expandAll ? '<span class="gth">' + esc(m.group.id) + '</span>' : '') +
      '<button type="button" class="col-btn" data-field="' + esc(name) + '" title="' + esc(title) +
      '" aria-expanded="false">' + esc(name) + '</button>' +
      '</th>';
  }

  function detailHTML(paper, colspan) {
    var slots = SLOTS.filter(function (s) { return String(s.Paper_ID) === String(paper.Paper_ID); });
    var record = GROUPS.map(function (g) {
      return '<div class="detail-group">' +
        '<h4><span class="gid">' + esc(g.id) + '</span> ' + esc(g.name) +
        ' <span class="gcount">' + g.fields.length + ' fields</span></h4>' +
        '<ul class="rec">' + g.fields.map(function (f) {
          var note = gateNote(f.name);
          return '<li class="rec-item' + (gateFlag(paper, f.name) ? ' gated' : '') + '">' +
            '<span class="rec-label">' + esc(f.name) + '</span>' +
            '<span class="rec-value">' + recordValue(paper, f.name) + '</span>' +
            (note ? '<span class="rec-note">' + esc(note) + '</span>' : '') +
            '</li>';
        }).join('') + '</ul></div>';
    }).join('');

    var claimsHTML;
    if (!slots.length) {
      claimsHTML = '<p class="note">No claim&ndash;evidence slot is bundled for this paper.</p>';
    } else {
      claimsHTML = slots.map(function (s) {
        var claimLink = s.Claim_URL
          ? ' <a class="page-link" href="' + esc(s.Claim_URL) + '" target="_blank" rel="noopener">PDF p. ' + esc(s.Claim_Page) + '</a>' : '';
        var evLink = s.Evidence_URL
          ? ' <a class="page-link" href="' + esc(s.Evidence_URL) + '" target="_blank" rel="noopener">PDF p. ' + esc(s.Evidence_Page) + '</a>' : '';
        return '<div class="slot">' +
          '<div class="slot-head"><span class="chip slot">' + esc(s.Claim_Slot) + '</span>' +
            chipHTML('Final_Alignment', clean(s.Final_Alignment)) +
            '<span class="chip-quiet">' + esc(clean(s.Final_Decision_Type)) + '</span>' +
            '<span class="chip-quiet">human review: ' + esc(clean(s.Human_Review_Flag)) + '</span></div>' +
          '<div class="quote-block"><span class="quote-label">Claim</span>' +
            '<p class="quote-text">' + esc(clean(s.Claim_Quote)) + '</p>' +
            '<p class="quote-meta">p. ' + esc(clean(s.Claim_Page)) + ' &middot; ' + esc(clean(s.Claim_Section)) + claimLink + '</p></div>' +
          '<div class="claim-arrow">&darr;</div>' +
          '<div class="quote-block evidence"><span class="quote-label">Evidence</span>' +
            '<p class="quote-text">' + esc(clean(s.Evidence_Quote)) + '</p>' +
            '<p class="quote-meta">p. ' + esc(clean(s.Evidence_Page)) + ' &middot; ' + esc(clean(s.Evidence_Section)) +
            ' &middot; ' + esc(clean(s.Evidence_Location_Detail)) + evLink + '</p></div>' +
          '</div>';
      }).join('');
    }

    var links = [];
    if (paper.Paper_URL) links.push('<a class="page-link" href="' + esc(paper.Paper_URL) + '" target="_blank" rel="noopener">Paper</a>');

    return '<tr class="detail-row" id="detail-' + esc(paper.Paper_ID) + '"><td colspan="' + colspan + '">' +
      '<div class="detail">' +
        '<div class="detail-head"><h3>Paper ' + esc(paper.Paper_ID) + ' &middot; ' + esc(clean(paper.Title)) + '</h3>' +
          '<p class="detail-meta">' + esc(paper.Citation_Key) + ' &middot; ' + esc(clean(paper.Year)) +
          ' &middot; ' + esc(clean(paper.Venue)) + (links.length ? ' &middot; ' + links.join(' ') : '') + '</p></div>' +
        record +
        '<div class="detail-group claims"><h4><span class="gid">G7</span> Claim&ndash;evidence alignment ' +
          '<span class="gcount">' + slots.length + ' slot' + (slots.length === 1 ? '' : 's') + ' of 72</span></h4>' +
          claimsHTML + '</div>' +
      '</div></td></tr>';
  }

  function renderPapers(rows) {
    var fields = visibleFields();
    var query = clean(state.q).toLowerCase();
    var matched = rows.filter(function (p) { return matchesQuery(p, query); });
    var slice = pageSlice(matched, state.page);
    state.page = slice.page;
    var colspan = 2 + fields.length;

    $id('sheet-head').innerHTML = '<tr>' +
      '<th scope="col" class="col-idx">#</th>' +
      '<th scope="col" class="col-paper">Paper</th>' +
      fields.map(headerHTML).join('') + '</tr>';

    $id('sheet-body').innerHTML = slice.rows.map(function (p) {
      var id = String(p.Paper_ID);
      var open = !!state.open[id];
      var row = '<tr class="row' + (open ? ' open' : '') + '" data-id="' + esc(id) + '">' +
        '<td class="col-idx idx">' + esc(p.Paper_ID) + '</td>' +
        '<td class="col-paper paper"><button type="button" class="row-toggle" aria-expanded="' + open +
          '" aria-controls="detail-' + esc(id) + '" title="Show or hide the complete record for this paper">' +
          '<span class="chev" aria-hidden="true">' + (open ? '\u25be' : '\u25b8') + '</span>' +
          '<span class="pt"><span class="paper-title">' + esc(clean(p.Title)) + '</span>' +
          '<span class="citation-key">' + esc(p.Citation_Key) + '</span></span></button></td>' +
        fields.map(function (name) { return cellHTML(p, name); }).join('') + '</tr>';
      return open ? row + detailHTML(p, colspan) : row;
    }).join('');

    if (!slice.rows.length) {
      $id('sheet-body').innerHTML = '<tr><td class="no-results" colspan="' + colspan + '">' +
        (query ? 'No paper matches &ldquo;' + esc(query) + '&rdquo;.' : 'No papers are bundled.') + '</td></tr>';
    }

    $id('sheetfoot').innerHTML = footHTML(slice, matched.length, 'papers');
    $id('sheet-caption').innerHTML = captionHTML(fields.length);
  }

  function captionHTML(fieldCount) {
    if (state.expandAll) {
      return 'All 38 coded fields from G1&ndash;G6 in one table; each header carries its group tag. ' +
        'Scroll horizontally for the remaining groups. Click a header for its codebook definition.';
    }
    if (state.sheet === 'G4') {
      return '<strong>Interaction and Behavioral Evaluation.</strong> Extended dialogue, dynamic user state and ' +
        'longitudinal evaluation are three <em>independent</em> coded fields and must not be drawn as a nested funnel. ' +
        'Paper 34 is longitudinal without extended dialogue, and papers 65 and 111 model a dynamic user state ' +
        'without extended dialogue.';
    }
    var g = GROUPS.filter(function (x) { return x.id === state.sheet; })[0];
    if (!g) return '';
    return 'Sheet <strong>' + esc(g.id) + ' &middot; ' + esc(g.name) + '</strong> (' + fieldCount +
      ' of 38 coded fields). Click a row for the complete record.';
  }

  /* -------------------------------------------------------- claim sheet -- */

  function claimMatches(s) {
    var c = state.claim;
    if (c.align !== 'ALL' && clean(s.Final_Alignment) !== c.align) return false;
    if (c.slot !== 'ALL' && clean(s.Claim_Slot) !== c.slot) return false;
    if (c.review !== 'ALL' && clean(s.Human_Review_Flag) !== c.review) return false;
    var q = clean(c.q).toLowerCase();
    if (!q) return true;
    return [s.Title, s.Citation_Key, s.Paper_ID, s.Claim_Slot, s.Claim_Quote, s.Claim_Section,
      s.Evidence_Quote, s.Evidence_Section, s.Evidence_Location_Detail, s.Final_Alignment,
      s.Final_Decision_Type, s.Human_Review_Flag].join(' ').toLowerCase().indexOf(q) >= 0;
  }

  function linkHTML(url, page) {
    if (!url) return '';
    return ' <a class="page-link" href="' + esc(url) + '" target="_blank" rel="noopener">PDF p. ' + esc(clean(page)) + '</a>';
  }

  function renderClaims() {
    var matched = SLOTS.filter(claimMatches);
    var slice = pageSlice(matched, state.claim.page);
    state.claim.page = slice.page;

    $id('sheet-head').innerHTML = '<tr>' +
      '<th scope="col" class="col-idx">#</th>' +
      '<th scope="col" class="col-paper">Paper</th>' +
      '<th scope="col">Slot</th>' +
      '<th scope="col">Claim quote &middot; page &middot; section</th>' +
      '<th scope="col">Evidence quote &middot; page &middot; section &middot; detail</th>' +
      '<th scope="col">Alignment</th>' +
      '<th scope="col">Decision</th>' +
      '<th scope="col">Review flag</th></tr>';

    $id('sheet-body').innerHTML = slice.rows.map(function (s) {
      return '<tr class="claim-row" data-id="' + esc(s.Paper_ID) + '">' +
        '<td class="col-idx idx">' + esc(s.Paper_ID) + '</td>' +
        '<td class="col-paper paper"><span class="paper-title">' + esc(clean(s.Title)) + '</span>' +
          '<span class="citation-key">' + esc(s.Citation_Key) + '</span></td>' +
        '<td><span class="chip slot">' + esc(s.Claim_Slot) + '</span></td>' +
        '<td class="quote-cell"><p class="q">' + esc(clean(s.Claim_Quote)) + '</p>' +
          '<p class="meta">p. ' + esc(clean(s.Claim_Page)) + ' &middot; ' + esc(clean(s.Claim_Section)) +
          linkHTML(s.Claim_URL, s.Claim_Page) + '</p></td>' +
        '<td class="quote-cell"><p class="q">' + esc(clean(s.Evidence_Quote)) + '</p>' +
          '<p class="meta">p. ' + esc(clean(s.Evidence_Page)) + ' &middot; ' + esc(clean(s.Evidence_Section)) +
          ' &middot; ' + esc(clean(s.Evidence_Location_Detail)) + linkHTML(s.Evidence_URL, s.Evidence_Page) + '</p></td>' +
        '<td>' + (s.Final_Alignment ? chipHTML('Final_Alignment', clean(s.Final_Alignment)) : '&mdash;') + '</td>' +
        '<td class="decision">' + (s.Final_Decision_Type ? esc(clean(s.Final_Decision_Type)) : '&mdash;') + '</td>' +
        '<td>' + (s.Human_Review_Flag ? chipHTML('Human_Review_Flag', clean(s.Human_Review_Flag)) : '&mdash;') + '</td>' +
        '</tr>';
    }).join('');

    if (!slice.rows.length) {
      $id('sheet-body').innerHTML = '<tr><td class="no-results" colspan="8">No claim&ndash;evidence slot matches the current filters.</td></tr>';
    }

    $id('sheetfoot').innerHTML = footHTML(slice, matched.length, 'claim\u2013evidence slots');
    $id('sheet-caption').innerHTML = '<strong>G7 &middot; Claim&ndash;evidence alignment.</strong> All ' +
      SLOTS.length + ' slots from the ' + PAPERS.length + ' papers are bundled; 26 are shown per page &mdash; ' +
      'set <em>Rows</em> to <em>All</em> to view them on one page. Filters: alignment, slot and human review flag.';
  }

  /* --------------------------------------------------------------- render -- */

  function render() {
    renderTabs();
    renderFilters();
    $id('expand-all').hidden = state.sheet === 'G7';
    $id('expand-all').setAttribute('aria-pressed', state.expandAll ? 'true' : 'false');
    $id('expand-all').classList.toggle('active', state.expandAll);
    if (state.sheet === 'G7') renderClaims();
    else renderPapers(PAPERS);
  }

  /* -------------------------------------------------------------- events -- */

  function showPopover(btn) {
    var pop = $id('field-pop');
    var f = META[btn.getAttribute('data-field')].field;
    var note = gateNote(f.name);
    pop.innerHTML = '<div class="fp-head"><code>' + esc(f.name) + '</code>' +
      '<button type="button" class="fp-close" aria-label="Close definition">Close</button></div>' +
      '<p class="fp-values"><strong>Values:</strong> ' + esc(clean(f.values || 'Free text')) + '</p>' +
      '<p class="fp-def">' + esc(clean(f.definition)) + '</p>' +
      (note ? '<p class="fp-gate">' + esc(note) + '</p>' : '');
    pop.hidden = false;
    var rect = btn.getBoundingClientRect();
    var top = rect.bottom + 6;
    var left = Math.max(8, Math.min(rect.left, window.innerWidth - 448));
    if (top + pop.offsetHeight > window.innerHeight - 8) top = Math.max(8, rect.top - pop.offsetHeight - 6);
    pop.style.top = top + 'px';
    pop.style.left = left + 'px';
    document.querySelectorAll('.col-btn[aria-expanded="true"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    btn.setAttribute('aria-expanded', 'true');
  }
  function hidePopover() {
    var pop = $id('field-pop');
    pop.hidden = true;
    document.querySelectorAll('.col-btn[aria-expanded="true"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
  }

  function switchSheet(id) {
    state.sheet = id;
    state.expandAll = false;
    state.page = 1;
    state.claim.page = 1;
    $id('search').value = id === 'G7' ? state.claim.q : state.q;
    $id('search').placeholder = id === 'G7'
      ? 'Search quotes, sections, decisions\u2026'
      : 'Search title, key, or coded value\u2026';
    hidePopover();
    render();
    $id('tablewrap').scrollTop = 0;
  }

  $id('tabs').addEventListener('click', function (e) {
    var tab = e.target.closest('[data-sheet]');
    if (tab) switchSheet(tab.getAttribute('data-sheet'));
  });
  $id('tabs').addEventListener('keydown', function (e) {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));
    var i = tabs.indexOf(document.activeElement);
    if (i < 0) return;
    var next = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
    next.focus();
    switchSheet(next.getAttribute('data-sheet'));
    e.preventDefault();
  });

  $id('search').addEventListener('input', function () {
    if (state.sheet === 'G7') { state.claim.q = this.value; state.claim.page = 1; }
    else { state.q = this.value; state.page = 1; }
    render();
  });

  $id('page-size').addEventListener('change', function () {
    state.size = parseInt(this.value, 10) || 0;
    state.page = 1;
    state.claim.page = 1;
    render();
  });

  $id('expand-all').addEventListener('click', function () {
    state.expandAll = !state.expandAll;
    state.page = 1;
    hidePopover();
    render();
  });

  $id('sheetfoot').addEventListener('click', function (e) {
    var btn = e.target.closest('[data-page]');
    if (!btn || btn.disabled) return;
    var page = parseInt(btn.getAttribute('data-page'), 10);
    if (state.sheet === 'G7') state.claim.page = page;
    else state.page = page;
    render();
  });

  $id('claim-filters').addEventListener('change', function (e) {
    var sel = e.target.closest('[data-claim]');
    if (!sel) return;
    state.claim[sel.getAttribute('data-claim')] = sel.value;
    state.claim.page = 1;
    render();
  });

  var wrap = $id('tablewrap');
  wrap.addEventListener('click', function (e) {
    var colBtn = e.target.closest('.col-btn');
    if (colBtn) { showPopover(colBtn); return; }
    if (e.target.closest('.txt-btn')) {
      e.target.closest('.txt-btn').classList.toggle('open');
      e.preventDefault();
      return;
    }
    if (e.target.closest('a')) return;
    var row = e.target.closest('tr.row');
    if (!row) return;
    var id = row.getAttribute('data-id');
    if (state.open[id]) delete state.open[id]; else state.open[id] = true;
    render();
  });
  document.addEventListener('click', function (e) {
    if (e.target.closest('#field-pop') || e.target.closest('.col-btn')) return;
    if (!$id('field-pop').hidden) hidePopover();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') hidePopover();
  });

  /* ---------------------------------------------------------------- start -- */

  renderKeyFigures();
  renderDownloads();
  buildFilters();
  render();
})();
