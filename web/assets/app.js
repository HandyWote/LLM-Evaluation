/* ==========================================================================
   From Surface Realism to Behavioral Validity — front-end renderer
   Reads window.SURVEY_DATA (bundled by web/data/data.js). No fetch, no deps,
   so the page renders when opened directly from file://.
   ========================================================================== */
(function () {
  'use strict';

  var DATA = window.SURVEY_DATA;
  var main = document.getElementById('main');

  if (!DATA) {
    var msg = document.createElement('p');
    msg.className = 'fatal';
    msg.textContent = 'Data bundle not found. Expected web/data/data.js to define window.SURVEY_DATA.';
    (main || document.body).insertBefore(msg, (main || document.body).firstChild);
    return;
  }

  var codebook = DATA.codebook || [];
  var papersObj = DATA.papers || { papers: [], fields: [], n: 0 };
  var papers = papersObj.papers || [];
  var paperFields = papersObj.fields || [];
  var claims = DATA.claims || { slots: [], summary: {} };
  var claimSlots = claims.slots || [];
  var summary = claims.summary || {};
  var stats = DATA.stats || {};
  var N = stats.n || papersObj.n || papers.length;

  /* ---------------------------------------------------------- helpers ---- */

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function clean(value) {
    return String(value == null ? '' : value).replace(/\s+/g, ' ').trim();
  }
  // Drop leading LaTeX label artifacts (e.g. "app:claim-coding ") from parsed prose.
  function cleanProse(value) {
    return clean(value).replace(/^[a-z]+:[A-Za-z0-9_-]+\s+/, '');
  }
  function pct(n, total) {
    if (!total) return 0;
    return Math.round((n / total) * 1000) / 10;
  }
  function isYes(value) { return /^yes$/i.test(clean(value)); }
  function $(id) { return document.getElementById(id); }

  var BOOL_FIELDS = {};
  codebook.forEach(function (g) {
    g.fields.forEach(function (f) {
      if (f.type === 'boolean' || /^yes\s*\/\s*no$/i.test(clean(f.values))) BOOL_FIELDS[f.name] = true;
    });
  });

  var FIELD_DEF = {};
  codebook.forEach(function (g) {
    g.fields.forEach(function (f) { FIELD_DEF[f.name] = f.definition || ''; });
  });

  // Optional gate metadata published by the build: a field is only meaningful
  // for the subset of papers where gate_field === gate_value.
  var FIELD_GATE = {};
  codebook.forEach(function (g) {
    g.fields.forEach(function (f) {
      if (f.gate && f.gate.gate_field) FIELD_GATE[f.name] = f.gate;
    });
  });

  function yesCount(field) {
    return papers.filter(function (p) { return isYes(p.values ? p.values[field] : ''); }).length;
  }

  /* ----------------------------------------------------------- palette --- */

  var SCALE = ['#134e4a', '#0f766e', '#0d9488', '#14b8a6', '#2dd4bf', '#5eead4', '#99f6e4', '#ccfbf1'];
  var NAMED = {
    'Yes': '#0d9488', 'No': '#fda4af',
    'ALIGNED': '#0f766e', 'PARTIAL': '#d97706', 'EXCEEDS': '#e11d48', 'UNCLEAR': '#64748b',
    'Strong': '#134e4a', 'Mentioned': '#99f6e4',
    'Full Disclosure': '#0f766e', 'Full': '#0f766e', 'Partial Disclosure': '#99f6e4',
    'No Disclosure': '#fda4af',
    'Static': '#99f6e4', 'Pattern-level': '#5eead4', 'Dynamic': '#0d9488', 'None': '#e2e8f0'
  };
  function colorFor(label, index) {
    if (NAMED[label]) return NAMED[label];
    return SCALE[index % SCALE.length];
  }
  var ALIGN_ORDER = ['ALIGNED', 'PARTIAL', 'EXCEEDS', 'UNCLEAR'];
  var ALIGN_LABEL = { ALIGNED: 'Aligned', PARTIAL: 'Partial', EXCEEDS: 'Exceeds', UNCLEAR: 'Unclear' };

  /* -------------------------------------------------- value aggregation -- */

  // Frequency of a coded field across the corpus. opts.multi splits on ";".
  function valueCounts(field, opts) {
    opts = opts || {};
    var map = {};
    papers.forEach(function (p) {
      var raw = p.values ? p.values[field] : '';
      if (raw == null || clean(raw) === '') return;
      var parts = opts.multi ? String(raw).split(';') : [String(raw)];
      parts.forEach(function (part) {
        var key = clean(part);
        if (!key) return;
        map[key] = (map[key] || 0) + 1;
      });
    });
    var arr = Object.keys(map).map(function (k) { return { name: k, n: map[k] }; });
    if (opts.order) {
      arr.sort(function (a, b) {
        var ia = opts.order.indexOf(a.name); var ib = opts.order.indexOf(b.name);
        if (ia < 0) ia = opts.order.length; if (ib < 0) ib = opts.order.length;
        return ia - ib;
      });
    } else {
      arr.sort(function (a, b) { return b.n - a.n; });
    }
    return opts.limit ? arr.slice(0, opts.limit) : arr;
  }

  function statItems(list) {
    return (list || []).map(function (x) { return { name: x.name, n: x.n }; });
  }
  function distItems(obj, order) {
    var arr = Object.keys(obj || {}).map(function (k) { return { name: k, n: obj[k] }; });
    if (order) {
      arr.sort(function (a, b) {
        var ia = order.indexOf(a.name); var ib = order.indexOf(b.name);
        if (ia < 0) ia = order.length; if (ib < 0) ib = order.length;
        return ia - ib;
      });
    } else {
      arr.sort(function (a, b) { return b.n - a.n; });
    }
    return arr;
  }

  /* ------------------------------------------------------- chart pieces -- */

  function barsHTML(items, spec) {
    spec = spec || {};
    var total = spec.total || 0;
    if (!total) {
      total = 1;
      items.forEach(function (i) { if (i.n > total) total = i.n; });
    }
    if (!items.length) return '<p class="note">No coded values available.</p>';
    return '<div class="bars">' + items.map(function (item, i) {
      var c = spec.colorMap && spec.colorMap[item.name]
        ? spec.colorMap[item.name]
        : colorFor(item.name, i);
      var w = Math.max(2, Math.min(100, pct(item.n, total)));
      return '<div class="bar-row">' +
        '<span class="bar-label" title="' + esc(item.name) + '">' + esc(item.name) + '</span>' +
        '<span class="bar-track"><span class="bar-fill" style="width:' + w + '%;background:' + c + '"></span></span>' +
        '<span class="bar-value">' + item.n +
          (spec.showPct === false ? '' : ' <span class="bar-pct">' + w + '%</span>') +
        '</span>' +
      '</div>';
    }).join('') + '</div>';
  }

  // Stacked distribution bar for one field/summary.
  function stackHTML(row, total) {
    var dist = row.dist || {};
    var keys = row.order || ALIGN_ORDER;
    var sum = row.n || keys.reduce(function (acc, k) { return acc + (dist[k] || 0); }, 0);
    var segs = keys.map(function (k) {
      var n = dist[k] || 0;
      if (!n || !sum) return '';
      var w = pct(n, sum);
      var label = row.labelMap && row.labelMap[k] ? row.labelMap[k] : k;
      return '<span class="stack-seg" style="width:' + w + '%;background:' +
        colorFor(k, keys.indexOf(k)) + '" title="' + esc(label + ': ' + n) + '">' +
        (w >= 8 ? esc(label) + ' ' + n : '') + '</span>';
    }).join('');
    var legend = keys.map(function (k) {
      var n = dist[k] || 0;
      var label = row.labelMap && row.labelMap[k] ? row.labelMap[k] : k;
      return '<span><span class="swatch" style="background:' + colorFor(k, keys.indexOf(k)) + '"></span>' +
        esc(label) + ' (' + n + ')</span>';
    }).join('');
    return '<div class="stack">' +
      '<div class="stack-head"><span class="t">' + esc(row.label) + '</span>' +
        '<span class="g">n = ' + sum + '</span></div>' +
      '<div class="stack-track">' + (segs || '<span class="stack-seg" style="width:100%;background:#e2e8f0"></span>') + '</div>' +
      '<div class="stack-legend">' + legend + '</div>' +
    '</div>';
  }

  /* ------------------------- behavioral validity (non-nested criteria) -- */

  // The three criteria are measured by independent fields. They are NOT a
  // funnel: a paper can satisfy any subset, so each keeps its own denominator.
  var BVE_SPEC = [
    { id: 'extended_dialogue', label: 'evaluate extended dialogues', field: 'Interaction_Level',
      rule: 'Interaction_Level = \u2018Extended Dialogue\u2019',
      test: function (v) { return clean(v).toLowerCase() === 'extended dialogue'; } },
    { id: 'dynamic_state', label: 'model a dynamic user state', field: 'Uses_Dynamic_State',
      rule: 'Uses_Dynamic_State = Yes', test: isYes },
    { id: 'longitudinal', label: 'include longitudinal evaluation', field: 'Has_Longitudinal_Eval',
      rule: 'Has_Longitudinal_Eval = Yes', test: isYes }
  ];

  function bveIds(match) {
    return papers.filter(function (p) { return match(p.values || {}); })
      .map(function (p) { return String(p.Paper_ID); });
  }

  // Fallback if stats.behavioral_validity has not landed yet: recompute from
  // the per-paper coding so the card always shows real numbers.
  function bveFallback() {
    var criteria = BVE_SPEC.map(function (c) {
      return { id: c.id, label: c.label, field: c.field, rule: c.rule,
        n: bveIds(function (v) { return c.test(v[c.field]); }).length,
        definition: FIELD_DEF[c.field] || '' };
    });
    var combos = [];
    for (var m = 7; m >= 0; m--) {
      var flags = [!!(m & 4), !!(m & 2), !!(m & 1)];
      var ids = bveIds(function (v) {
        return BVE_SPEC.every(function (c, k) { return c.test(v[c.field]) === flags[k]; });
      });
      combos.push({ extended_dialogue: flags[0], dynamic_state: flags[1], longitudinal: flags[2],
        n: ids.length, paper_ids: ids });
    }
    return { n: N, nested: false, criteria: criteria, combinations: combos, caveats: [] };
  }

  function bveData() {
    var bv = stats.behavioral_validity;
    if (bv && bv.criteria && bv.criteria.length && bv.combinations && bv.combinations.length) return bv;
    return bveFallback();
  }

  function idList(ids) {
    if (!ids || !ids.length) return '';
    return 'Paper' + (ids.length > 1 ? 's ' : ' ') + ids.join(', ');
  }

  function bveCaveats(bv) {
    if (bv.caveats && bv.caveats.length) return bv.caveats;
    var dyn = 0, lon = 0;
    (bv.criteria || []).forEach(function (c) {
      if (c.id === 'dynamic_state') dyn = c.n;
      if (c.id === 'longitudinal') lon = c.n;
    });
    function pick(fn) {
      return (bv.combinations || []).filter(fn).reduce(function (acc, c) {
        return acc.concat(c.paper_ids || []);
      }, []);
    }
    var dynNotExt = pick(function (c) { return c.dynamic_state && !c.extended_dialogue; });
    var lonNotExt = pick(function (c) { return c.longitudinal && !c.extended_dialogue; });
    var out = ['The three criteria are independent, not nested: a study can evaluate long dialogues, ' +
      'model a dynamic user state, or run a longitudinal evaluation in any combination.'];
    if (dynNotExt.length) out.push(dynNotExt.length + ' of the ' + dyn + ' dynamic-state papers (' +
      idList(dynNotExt) + ') do not evaluate extended dialogues.');
    if (lonNotExt.length) out.push(lonNotExt.length + ' of the ' + lon + ' longitudinal papers (' +
      idList(lonNotExt) + ') do not evaluate extended dialogues.');
    out.push('A longer dialogue does not by itself provide trajectory-level evidence (paper Sec. 4.2).');
    return out;
  }

  function bveInd(v) {
    return '<td class="bve-ind ' + (v ? 'yes' : 'no') + '" title="' + (v ? 'Yes' : 'No') + '">' +
      (v ? '\u25cf' : '\u25cb') + '</td>';
  }

  function bveHTML(bv) {
    bv = bv || bveData();
    if (!bv || !bv.criteria || !bv.criteria.length) {
      return '<p class="note">Behavioral-validity breakdown is not available in this data bundle.</p>';
    }
    var total = bv.n || N || 0;
    var bars = bv.criteria.map(function (c, i) {
      var w = total ? Math.max(2, Math.min(100, pct(c.n, total))) : 0;
      return '<div class="bve-bar">' +
        '<div class="bve-bar-head"><span class="bve-bar-count">' + c.n + ' / ' + total + '</span>' +
          '<span class="bve-bar-label">' + esc(c.label) + '</span></div>' +
        '<span class="bve-bar-track"><span class="bve-bar-fill" style="width:' + w + '%;background:' +
          colorFor(c.id, i) + '"></span></span>' +
        '<div class="bve-bar-meta"><code>' + esc(c.rule || c.field) + '</code>' +
          (c.definition ? ' \u00b7 ' + esc(c.definition) : '') + '</div>' +
      '</div>';
    }).join('');
    var combos = (bv.combinations || []).slice().sort(function (a, b) {
      if (b.n !== a.n) return b.n - a.n;
      return (b.extended_dialogue - a.extended_dialogue) || (b.dynamic_state - a.dynamic_state) ||
        (b.longitudinal - a.longitudinal);
    });
    var rows = combos.map(function (c) {
      var ids = (c.paper_ids || []).map(String);
      return '<tr' + (c.n ? '' : ' class="zero"') + '>' +
        bveInd(c.extended_dialogue) + bveInd(c.dynamic_state) + bveInd(c.longitudinal) +
        '<td class="bve-n">' + c.n + '</td>' +
        '<td class="bve-ids">' + (ids.length ? esc(ids.join(', ')) : '\u2014') + '</td></tr>';
    }).join('');
    return '<div class="bve">' +
      '<div class="bve-bars">' + bars + '</div>' +
      '<div class="bve-matrix-wrap"><table class="bve-matrix">' +
        '<caption>All 8 Yes/No combinations of the three criteria across ' + total + ' papers. ' +
          'Rows are intersections, not stages; each criterion keeps its own denominator.</caption>' +
        '<thead><tr><th>Extended<br>dialogue</th><th>Dynamic<br>state</th><th>Longitudinal</th>' +
          '<th>Papers</th><th>Paper IDs</th></tr></thead><tbody>' + rows + '</tbody></table></div>' +
      '<p class="bve-caveat"><strong>Caution.</strong> ' + bveCaveats(bv).map(esc).join(' ') + '</p>' +
    '</div>';
  }

  /* ------------------------------------------------------- gated stats -- */

  function gatedFallback() {
    return [
      { id: 'llm_judge_validation', field: 'LLM_Judge_Validated', gate_field: 'Eval_LLM_Judge',
        gate_value: 'Yes', label: 'Validate the LLM judge against human judgments',
        n: stats.llm_judge ? stats.llm_judge.validated : yesCount('LLM_Judge_Validated'),
        denominator: stats.llm_judge ? stats.llm_judge.used : yesCount('Eval_LLM_Judge') },
      { id: 'rubric_reliability', field: 'Reliability_Reported', gate_field: 'Has_Rubric',
        gate_value: 'Yes', label: 'Report inter-rater reliability',
        n: stats.rubric ? stats.rubric.reported_reliability : yesCount('Reliability_Reported'),
        denominator: stats.rubric ? stats.rubric.has : yesCount('Has_Rubric') }
    ].filter(function (g) { return g.denominator; });
  }

  function gatedData() {
    if (stats.gated && stats.gated.length) return stats.gated;
    return gatedFallback();
  }

  // Conditional counts only. The unconditional numerator is deliberately never
  // printed on its own: 23/30 and 13/45 are the counts the paper reports.
  function gatedHTML(items) {
    items = items || gatedData();
    if (!items || !items.length) return '<p class="note">No gated statistics available.</p>';
    return '<div class="gated">' + items.map(function (g) {
      var gate = FIELD_GATE[g.field] || g;
      var n = g.n || 0, den = g.denominator || 0;
      var w = den ? Math.max(2, Math.min(100, pct(n, den))) : 0;
      return '<div class="gated-row">' +
        '<div class="gated-head"><span class="gated-count">' + n + ' of ' + den + '</span>' +
          '<span class="gated-label">' + esc(g.label || '') + '</span></div>' +
        '<span class="gated-track"><span class="gated-fill" style="width:' + w + '%"></span></span>' +
        '<div class="gated-caption">Conditional on <code>' +
          esc(gate.gate_field || g.gate_field || '') + ' = ' + esc(gate.gate_value || g.gate_value || '') +
          '</code> \u2014 ' + n + ' of ' + den + ' eligible papers.</div>' +
      '</div>';
    }).join('') + '</div>';
  }

  /* ---------------------------------------------------- clinical theory -- */

  function clinicalHTML(ct) {
    if (!ct || !ct.families) {
      var raw = valueCounts('Clinical_Theory', { multi: true });
      var missing = papers.filter(function (p) {
        return clean(p.values ? p.values.Clinical_Theory : '') === '';
      }).length;
      ct = { denominator: N, multi_label: true, families: raw,
        unclassified: { n: 0, paper_ids: [] },
        not_specified: { n: missing, paper_ids: [] }, raw: raw,
        mapping_note: 'Family grouping is produced by the data build step; until it is available ' +
          'the entries below are the coded strings exactly as reported.' };
    }
    var den = ct.denominator || N || 0;
    var fams = (ct.families || []).filter(function (f) { return f && f.n; })
      .slice().sort(function (a, b) { return b.n - a.n; });
    var bars = fams.length
      ? barsHTML(fams.map(function (f) { return { name: f.name, n: f.n }; }), { total: den })
      : '';
    var extras = [];
    if (ct.unclassified && ct.unclassified.n) {
      extras.push({ label: 'Other / unclassified', n: ct.unclassified.n, color: '#5eead4' });
    }
    if (ct.not_specified && ct.not_specified.n) {
      extras.push({ label: 'Not specified', n: ct.not_specified.n, color: '#e2e8f0', muted: true });
    }
    var extraHTML = extras.map(function (e) {
      var w = den ? Math.max(2, Math.min(100, pct(e.n, den))) : 0;
      return '<div class="bar-row' + (e.muted ? ' is-empty' : '') + '">' +
        '<span class="bar-label">' + esc(e.label) + '</span>' +
        '<span class="bar-track"><span class="bar-fill" style="width:' + w + '%;background:' +
          e.color + '"></span></span>' +
        '<span class="bar-value">' + e.n + ' <span class="bar-pct">' + w + '%</span></span></div>';
    }).join('');
    var rawList = (ct.raw || []).filter(function (r) { return r && clean(r.value); });
    var rawHTML = rawList.length
      ? '<details class="ct-raw"><summary>Raw reported strings (' + rawList.length + ')</summary><ul>' +
        rawList.map(function (r) {
          return '<li><span class="ct-raw-val">' + esc(r.value) + '</span>' +
            '<span class="ct-raw-n">' + r.n + '</span></li>';
        }).join('') + '</ul></details>'
      : '';
    return '<div class="ct">' +
      '<div class="ct-denom">Denominator: <strong>' + den + '</strong> papers' +
        (ct.multi_label ? ' \u00b7 multi-label (a paper can name several frameworks, so families may sum above ' +
          den + ')' : '') + '.</div>' +
      '<div class="ct-bars">' + bars + extraHTML + '</div>' +
      (ct.mapping_note ? '<p class="ct-mapping">' + esc(ct.mapping_note) + '</p>' : '') +
      rawHTML +
    '</div>';
  }

  function reliabilityItems() {
    var rr = stats.reliability_reporting;
    if (rr && rr.value_counts) return distItems(rr.value_counts, ['Yes', 'No', 'N/A']);
    return valueCounts('Reliability_Reported', { order: ['Yes', 'No', 'N/A'] });
  }

  function chainHTML(steps) {
    return steps.map(function (s, i) {
      var node = '<span class="chain-step ' + s.tone + '">' +
        '<span class="n">' + s.n + '</span><span class="l">' + esc(s.label) + '</span></span>';
      if (i === 0) return node;
      var prev = steps[i - 1];
      return '<span class="chain-arrow">\u2192 <span class="chain-gap">\u2212' + (prev.n - s.n) + '</span></span>' + node;
    }).join('');
  }

  function chartBodyHTML(spec) {
    if (spec.type === 'stack') {
      return spec.rows.map(function (r) { return stackHTML(r); }).join('');
    }
    if (spec.type === 'chain') {
      return '<div class="chain">' + chainHTML(spec.steps) + '</div>';
    }
    if (spec.type === 'bve') {
      return bveHTML(spec.data);
    }
    if (spec.type === 'gated') {
      return gatedHTML(spec.data);
    }
    if (spec.type === 'clinical') {
      return clinicalHTML(spec.data || stats.clinical_theory);
    }
    return barsHTML(spec.items, spec);
  }

  function chartCardHTML(spec, wide) {
    return '<div class="chart-card' + (wide ? ' wide' : '') + '">' +
      '<div class="chart-title">' + esc(spec.title) + '</div>' +
      (spec.sub ? '<div class="chart-sub">' + esc(spec.sub) + '</div>' : '') +
      chartBodyHTML(spec) +
      (spec.note ? '<p class="chart-note">' + spec.note + '</p>' : '') +
    '</div>';
  }

  function miniChartHTML(spec) {
    return '<div class="mini-chart' + (spec.wide ? ' wide' : '') + '">' +
      '<div class="chart-title">' + esc(spec.title) + '</div>' +
      (spec.sub ? '<div class="chart-sub">' + esc(spec.sub) + '</div>' : '') +
      chartBodyHTML(spec) +
      (spec.note ? '<p class="chart-note">' + spec.note + '</p>' : '') +
    '</div>';
  }

  /* ------------------------------------------------------------ header --- */

  function renderHeader() {
    var host = $('hero-badges');
    if (!host) return;
    var totalFields = codebook.reduce(function (acc, g) { return acc + g.fields.length; }, 0);
    host.innerHTML =
      '<span class="badge">' + N + ' papers \u00b7 ' + totalFields + ' coded fields</span>' +
      '<span class="badge">' + codebook.length + ' coding groups</span>' +
      '<span class="badge">' + (claimSlots.length || 0) + ' claim\u2013evidence slots</span>' +
      '<span class="badge">Evidence-linked coding</span>';
  }

  /* ---------------------------------------------------------- overview --- */

  function renderOverview() {
    var totalFields = codebook.reduce(function (acc, g) { return acc + g.fields.length; }, 0);
    var extDepth = distItems(stats.behavior_depth_extended);
    var extTotal = extDepth.reduce(function (acc, i) { return acc + i.n; }, 0);
    var kpis = [
      { n: N, l: 'Papers reviewed', s: '2019\u20132026' },
      { n: totalFields, l: 'Coded fields', s: codebook.length + ' groups' },
      { n: stats.dims_ge1 || 0, l: 'Assess \u2265 1 local-quality dimension', s: 'of ' + N },
      { n: (summary.all && summary.all.ALIGNED) || 0, l: 'Claim slots aligned', s: 'of ' + (claimSlots.length || 0) + ' slots' },
      { n: stats.rubric ? stats.rubric.has : 0, l: 'Use a scoring rubric', s: 'of ' + N },
      { n: stats.rubric ? stats.rubric.reported_reliability : 0, l: 'Report rubric reliability',
        s: 'of ' + (stats.rubric ? stats.rubric.has : yesCount('Has_Rubric')) + ' rubric papers' }
    ];
    $('overview-kpis').innerHTML = kpis.map(function (k) {
      return '<div class="kpi"><div class="kpi-n">' + k.n + '</div>' +
        '<div class="kpi-l">' + esc(k.l) + '</div>' +
        '<div class="kpi-s">' + esc(k.s) + '</div></div>';
    }).join('');

    var specs = [];

    specs.push({
      title: 'Who evaluates?',
      sub: 'Evaluator types are not mutually exclusive',
      items: statItems(stats.evaluators),
      total: N,
      colorMap: { 'Human experts': '#0d9488', 'LLM judges': '#d97706', 'Automatic metrics': '#4f46e5', 'All three': '#134e4a' }
    });

    specs.push({
      title: 'Evaluation dimensions assessed',
      sub: 'Papers coding each dimension as evaluated',
      items: statItems(stats.dimensions),
      total: N
    });

    specs.push({
      title: 'Behavioral validity: independent criteria, not a nested funnel',
      sub: 'Three separately coded criteria, each with its own denominator; intersections below',
      type: 'bve',
      wide: true
    });

    specs.push({
      title: 'Rubric \u2192 reported reliability',
      sub: 'Practice vs. reported evidence',
      type: 'chain',
      steps: [
        { n: stats.rubric ? stats.rubric.has : 0, label: 'papers use a scoring rubric', tone: 'a' },
        { n: stats.rubric ? stats.rubric.reported_reliability : 0, label: 'report inter-rater reliability', tone: 'b' }
      ]
    });

    specs.push({
      title: 'LLM judge \u2192 human validation',
      sub: 'Are automated scores checked against human judgments?',
      type: 'chain',
      steps: [
        { n: stats.llm_judge ? stats.llm_judge.used : 0, label: 'papers use an LLM judge', tone: 'a' },
        { n: stats.llm_judge ? stats.llm_judge.validated : 0, label: 'validate the judge against humans', tone: 'b' }
      ]
    });

    specs.push({
      title: 'Theory grounding',
      sub: 'How far evaluation ties to recognized clinical theory',
      items: distItems(stats.theory_grounding),
      total: N,
      colorMap: { Strong: '#134e4a', Partial: '#14b8a6', Mentioned: '#99f6e4' }
    });

    specs.push({
      title: 'Theory operationalized',
      sub: 'Whether theory becomes measurable evaluation criteria',
      items: distItems(stats.theory_operationalized),
      total: N,
      colorMap: { Strong: '#134e4a', Partial: '#14b8a6', None: '#fda4af' }
    });

    specs.push({
      title: 'Prompt disclosure',
      sub: 'Whether prompts needed for reproduction are reported',
      items: distItems(stats.prompt_disclosure, ['Full Disclosure', 'Partial Disclosure', 'No Disclosure']),
      total: N,
      colorMap: { 'Full Disclosure': '#0f766e', 'Partial Disclosure': '#99f6e4', 'No Disclosure': '#fda4af' }
    });

    specs.push({
      title: 'Behavioral depth in extended dialogues',
      sub: 'Deepest behavior level among the ' + extTotal + ' papers with 6+ turns',
      items: extDepth,
      total: extTotal,
      colorMap: { Dynamic: '#0d9488', 'Pattern-level': '#5eead4', Static: '#ccfbf1', None: '#e2e8f0' }
    });

    specs.push({
      title: 'Theory-linked evaluation instruments',
      sub: 'Papers using each instrument type (multi-label)',
      items: distItems(stats.theory_eval_types),
      total: N,
      wide: true
    });

    $('overview-charts').innerHTML = specs.map(function (s) { return chartCardHTML(s, s.wide); }).join('');
  }

  /* ------------------------------------------------------------ groups --- */

  function groupChartSpecs(g) {
    var yesno = ['Yes', 'No'];
    var rubricDen = stats.rubric ? stats.rubric.has : yesCount('Has_Rubric');
    var rubricN = stats.rubric ? stats.rubric.reported_reliability : yesCount('Reliability_Reported');
    switch (g.id) {
      case 'G1':
        return [
          { title: 'Simulation target', sub: 'Papers by simulated role', items: valueCounts('Simulation_Target'), total: N },
          { title: 'Persona / client model depth', sub: 'Papers by model depth', items: valueCounts('Persona_Model_Depth'), total: N },
          { title: 'Tracks a dynamic user state', sub: 'Uses_Dynamic_State', items: valueCounts('Uses_Dynamic_State', { order: yesno }), total: N }
        ];
      case 'G2':
        return [
          { title: 'Evaluator types', sub: 'Papers using each evaluator (multi-label)', items: statItems(stats.evaluators), total: N,
            colorMap: { 'Human experts': '#0d9488', 'LLM judges': '#d97706', 'Automatic metrics': '#4f46e5', 'All three': '#134e4a' } },
          { title: 'Interactive user studies', sub: 'Eval_User_Study', items: valueCounts('Eval_User_Study', { order: yesno }), total: N },
          { title: 'Lay-user participants', sub: 'Eval_Lay_Users', items: valueCounts('Eval_Lay_Users', { order: yesno }), total: N }
        ];
      case 'G3':
        return [
          { title: 'Evaluation dimensions', sub: 'Papers assessing each dimension', items: statItems(stats.dimensions), total: N },
          { title: 'Breadth of dimension coverage', sub: 'Number of local-quality dimensions assessed', total: N,
            items: [
              { name: '\u2265 1 dimension', n: stats.dims_ge1 || 0 },
              { name: '\u2265 3 dimensions', n: stats.dims_ge3 || 0 }
            ],
            colorMap: { '\u2265 1 dimension': '#0d9488', '\u2265 3 dimensions': '#134e4a' } }
        ];
      case 'G4':
        return [
          { title: 'Behavioral validity: independent criteria, not a nested funnel',
            sub: 'Each criterion has its own denominator and is coded independently of the others',
            type: 'bve', wide: true },
          { title: 'Interaction level in evaluation', sub: 'Interaction_Level', items: valueCounts('Interaction_Level'), total: N },
          { title: 'Behavioral evaluation depth', sub: 'Behavior_Eval_Depth (all papers)', items: valueCounts('Behavior_Eval_Depth', { order: ['Dynamic', 'Pattern-level', 'Static', 'None'] }), total: N },
          { title: 'Intervention sensitivity tested', sub: 'Intervention_Sensitivity', items: valueCounts('Intervention_Sensitivity', { order: yesno }), total: N }
        ];
      case 'G5':
        return [
          { title: 'Theory grounding', sub: 'Strength of theoretical grounding', items: distItems(stats.theory_grounding), total: N,
            colorMap: { Strong: '#134e4a', Partial: '#14b8a6', Mentioned: '#99f6e4' } },
          { title: 'Theory operationalized', sub: 'Theory translated into evaluation criteria', items: distItems(stats.theory_operationalized), total: N,
            colorMap: { Strong: '#134e4a', Partial: '#14b8a6', None: '#fda4af' } },
          { title: 'Prompt disclosure', sub: 'Reproducibility of system and evaluation prompts', items: distItems(stats.prompt_disclosure, ['Full Disclosure', 'Partial Disclosure', 'No Disclosure']), total: N,
            colorMap: { 'Full Disclosure': '#0f766e', 'Partial Disclosure': '#99f6e4', 'No Disclosure': '#fda4af' } },
          { title: 'Reliability reporting', sub: 'Reliability_Reported across all ' + N + ' papers',
            items: reliabilityItems(), total: N,
            note: 'Denominator: ' + N + ' reviewed papers (unconditional). The conditional count \u2014 ' +
              rubricN + ' of ' + rubricDen + ' papers that use a rubric \u2014 is reported under G6.' },
          { title: 'Theory-linked evaluation instruments', sub: 'Papers using each instrument type (multi-label)', items: distItems(stats.theory_eval_types), total: N },
          { title: 'Clinical theories referenced', sub: 'Canonical therapy families (multi-label)', type: 'clinical', wide: true }
        ];
      case 'G6':
        return [
          { title: 'Gated statistics: conditional counts',
            sub: 'Each count is shown only against its eligible denominator',
            type: 'gated', wide: true },
          { title: 'Rubric \u2192 reliability reported', sub: 'Reported evidence for scoring criteria', type: 'chain',
            steps: [
              { n: stats.rubric ? stats.rubric.has : 0, label: 'papers use a scoring rubric', tone: 'a' },
              { n: stats.rubric ? stats.rubric.reported_reliability : 0, label: 'report inter-rater reliability', tone: 'b' }
            ] },
          { title: 'LLM judge \u2192 human validation', sub: 'LLM-judge scores checked against human judgments', type: 'chain',
            steps: [
              { n: stats.llm_judge ? stats.llm_judge.used : 0, label: 'papers use an LLM judge', tone: 'a' },
              { n: stats.llm_judge ? stats.llm_judge.validated : 0, label: 'validate it against humans', tone: 'b' }
            ] },
          { title: 'Additional transparency and robustness checks', sub: 'Papers coding each field as Yes', total: N, wide: true,
            items: ['Has_Rubric', 'Uses_Standard_Metrics', 'Metric_Interpretable',
              'Comparable_To_Prior_Work', 'Has_Longitudinal_Eval', 'Has_Robustness_Testing', 'Has_Failure_Analysis',
              'Sim_Behavior_Realistic', 'Dataset_Available']
              .map(function (f) { return { name: f, n: yesCount(f) }; }) }
        ];
      case 'G7':
        return [
          { title: 'Claim\u2013evidence alignment (all 72 slots)', sub: 'Final aligned coding', type: 'stack',
            rows: [{ label: 'All slots', n: summary.all ? summary.all.n : claimSlots.length, dist: (summary.all || {}) }] },
          { title: 'By claim slot', sub: 'C1 = primary claim; C2 = explicit inferential extension', type: 'stack',
            rows: [
              { label: 'C1', n: summary.c1 ? summary.c1.n : 0, dist: (summary.c1 || {}) },
              { label: 'C2', n: summary.c2 ? summary.c2.n : 0, dist: (summary.c2 || {}) }
            ] }
        ];
      default:
        return [];
    }
  }

  function fieldTableHTML(g) {
    var rows = g.fields.map(function (f) {
      var gate = f.gate;
      return '<tr>' +
        '<td class="field-name-cell"><span class="field-name">' + esc(f.name) + '</span>' +
          '<span class="type-chip">' + esc(f.type || 'other') + '</span>' +
          (gate ? '<span class="gate-chip">conditional on ' + esc(gate.gate_field) + ' = ' +
            esc(gate.gate_value) + '</span>' : '') + '</td>' +
        '<td class="field-values">' + esc(f.values) + '</td>' +
        '<td class="field-def">' + esc(f.definition) + '</td>' +
      '</tr>';
    }).join('');
    return '<table class="field-table">' +
      '<thead><tr><th>Field</th><th>Values</th><th>Definition</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table>';
  }

  function renderGroups() {
    var host = $('group-sections');
    if (!host) return;
    codebook.forEach(function (g, i) {
      var section = document.createElement('section');
      section.className = 'group';
      section.id = 'g' + (i + 1);
      var specs = groupChartSpecs(g);
      var isG7 = g.id === 'G7';
      var charts = specs.length
        ? '<div class="group-charts">' + specs.map(miniChartHTML).join('') + '</div>'
        : '';
      section.innerHTML =
        '<div class="group-head"><span class="group-id">' + esc(g.id) + '</span>' +
          '<h3>' + esc(g.name) + '</h3>' +
          '<span class="group-count">' + g.fields.length + ' fields</span></div>' +
        '<p class="group-desc">' + esc(cleanProse(g.description)) + '</p>' +
        charts +
        fieldTableHTML(g) +
        (isG7 ? claimsExplorerHTML() : '');
      host.appendChild(section);
    });
    initClaims();
  }

  /* ------------------------------------------------------------ claims --- */

  function claimsExplorerHTML() {
    return '<div class="claim-controls">' +
      '<label>Alignment <select id="claim-align">' +
        '<option value="ALL">All</option>' +
        ALIGN_ORDER.map(function (a) { return '<option value="' + a + '">' + esc(ALIGN_LABEL[a]) + '</option>'; }).join('') +
      '</select></label>' +
      '<label>Slot <select id="claim-slot"><option value="ALL">All</option><option value="C1">C1</option><option value="C2">C2</option></select></label>' +
      '<label>Review flag <select id="claim-review">' +
        '<option value="ALL">All</option><option value="YES">Flagged</option><option value="NO">Not flagged</option>' +
      '</select></label>' +
      '<label class="search-field"><input type="search" id="claim-search" placeholder="Search paper or quote\u2026"></label>' +
      '<span class="claim-count" id="claim-count"></span>' +
    '</div>' +
    '<div class="claim-list" id="claim-list"></div>';
  }

  function alignChip(align) {
    var key = clean(align).toUpperCase();
    var cls = ALIGN_ORDER.indexOf(key) >= 0 ? key.toLowerCase() : 'unclear';
    return '<span class="chip ' + cls + '">' + esc(ALIGN_LABEL[key] || key || 'Unknown') + '</span>';
  }

  function pageLinkHTML(page, url) {
    var label = page ? 'Page ' + page : 'Open in paper';
    if (!url) return esc(label);
    return '<a class="page-link" href="' + esc(url) + '" target="_blank" rel="noopener">' +
      esc(label) + ' \u2192 open in paper</a>';
  }

  function quoteBlock(label, text, page, section, detail, url) {
    var meta = [];
    if (page) meta.push(pageLinkHTML(page, url));
    else if (url) meta.push(pageLinkHTML('', url));
    if (section) meta.push(esc(section));
    if (detail) meta.push(esc(detail));
    return '<div class="quote-block' + (label === 'Evidence' ? ' evidence' : '') + '">' +
      '<div class="quote-label">' + esc(label) + '</div>' +
      '<div class="quote-text">\u201c' + esc(clean(text) || 'Not reported') + '\u201d</div>' +
      (meta.length ? '<div class="quote-meta">' + meta.join(' \u00b7 ') + '</div>' : '') +
    '</div>';
  }

  function claimCardHTML(s) {
    var review = isYes(s.Human_Review_Flag);
    var paperName = esc(s.Citation_Key || '');
    if (s.Paper_URL) {
      paperName = '<a class="paper-link" href="' + esc(s.Paper_URL) +
        '" target="_blank" rel="noopener">' + paperName + '</a>';
    }
    return '<details class="claim-card">' +
      '<summary>' +
        '<span class="chip slot">' + esc(s.Claim_Slot || 'C') + '</span>' +
        alignChip(s.Final_Alignment) +
        '<span class="claim-paper">' + paperName +
          ' <span class="cid">#' + esc(s.Paper_ID || '') + '</span></span>' +
        '<span class="chip ' + (review ? 'review-yes' : 'review-no') + '">human review: ' +
          (review ? 'YES' : 'NO') + '</span>' +
        '<span class="claim-preview">' + esc(clean(s.Claim_Quote)) + '</span>' +
      '</summary>' +
      '<div class="claim-body">' +
        '<div class="claim-paper-title">' + esc(clean(s.Title)) + '</div>' +
        quoteBlock('Claim', s.Claim_Quote, s.Claim_Page, s.Claim_Section, '', s.Claim_URL) +
        '<div class="claim-arrow">\u25bc supporting evidence</div>' +
        quoteBlock('Evidence', s.Evidence_Quote, s.Evidence_Page, s.Evidence_Section, s.Evidence_Location_Detail, s.Evidence_URL) +
        '<div class="claim-foot">' +
          '<span>Alignment: <strong>' + esc(ALIGN_LABEL[clean(s.Final_Alignment).toUpperCase()] || s.Final_Alignment) + '</strong></span>' +
          '<span>Decision: ' + esc(s.Final_Decision_Type || 'n/a') + '</span>' +
          '<span>Review flag: ' + (review ? 'yes' : 'no') + '</span>' +
          (s.Paper_URL ? '<span><a class="page-link" href="' + esc(s.Paper_URL) +
            '" target="_blank" rel="noopener">Open paper \u2192</a></span>' : '') +
        '</div>' +
      '</div>' +
    '</details>';
  }

  function initClaims() {
    var list = $('claim-list');
    var countEl = $('claim-count');
    if (!list) return;
    var alignSel = $('claim-align');
    var slotSel = $('claim-slot');
    var reviewSel = $('claim-review');
    var search = $('claim-search');

    function render() {
      var align = alignSel ? alignSel.value : 'ALL';
      var slot = slotSel ? slotSel.value : 'ALL';
      var review = reviewSel ? reviewSel.value : 'ALL';
      var q = search ? clean(search.value).toLowerCase() : '';
      var kept = claimSlots.filter(function (s) {
        if (align !== 'ALL' && clean(s.Final_Alignment).toUpperCase() !== align) return false;
        if (slot !== 'ALL' && clean(s.Claim_Slot) !== slot) return false;
        if (review !== 'ALL' && (isYes(s.Human_Review_Flag) ? 'YES' : 'NO') !== review) return false;
        if (q) {
          var hay = clean(s.Citation_Key) + ' ' + clean(s.Title) + ' ' +
            clean(s.Claim_Quote) + ' ' + clean(s.Evidence_Quote);
          if (hay.toLowerCase().indexOf(q) < 0) return false;
        }
        return true;
      });
      list.innerHTML = kept.length
        ? kept.map(claimCardHTML).join('')
        : '<p class="no-results">No claim slots match these filters.</p>';
      if (countEl) countEl.textContent = 'Showing ' + kept.length + ' of ' + claimSlots.length + ' slots';
    }

    [alignSel, slotSel, reviewSel].forEach(function (el) { if (el) el.addEventListener('change', render); });
    if (search) search.addEventListener('input', render);
    render();
  }

  /* --------------------------------------------------------- downloads --- */

  var DOWNLOADS = [
    { href: 'downloads/final-table.csv', title: 'Paper-level coding table',
      desc: '52 papers \u00d7 38 coded fields, G1\u2013G6.', path: 'web/downloads/final-table.csv' },
    { href: 'downloads/theory_eval_refined_coding_refined.csv', title: 'Refined theory coding',
      desc: 'Theory grounding, operationalization, and evaluation instruments.',
      path: 'web/downloads/theory_eval_refined_coding_refined.csv' },
    { href: 'downloads/claim_level_FINAL_analysis_ready.csv', title: 'Claim\u2013evidence alignment',
      desc: '72 claim slots with quotes, pages, and final alignment decisions.',
      path: 'web/downloads/claim_level_FINAL_analysis_ready.csv' },
    { href: 'downloads/09_appendices.tex', title: 'Codebook appendix (LaTeX)',
      desc: 'The 7 groups and 40 field definitions used for coding.', path: 'web/downloads/09_appendices.tex' }
  ];

  function renderDownloads() {
    var host = $('download-grid');
    if (!host) return;
    host.innerHTML = DOWNLOADS.map(function (d) {
      return '<a class="download-card" href="' + esc(d.href) + '">' +
        '<div class="dl-title">' + esc(d.title) + '</div>' +
        '<div class="dl-desc">' + esc(d.desc) + '</div>' +
        '<div class="dl-path">' + esc(d.path) + '</div></a>';
    }).join('');
  }

  /* ----------------------------------------------------------- explorer -- */

  var paperById = {};
  papers.forEach(function (p) { paperById[String(p.Paper_ID)] = p; });

  function cellHTML(field, value) {
    var title = FIELD_DEF[field] ? ' title="' + esc(FIELD_DEF[field]) + '"' : '';
    var raw = value == null ? '' : String(value);
    if (BOOL_FIELDS[field]) {
      var yes = isYes(raw);
      return '<td class="cell bool"' + title + ' data-field="' + esc(field) + '">' +
        '<span class="dot ' + (yes ? 'yes' : 'no') + '"></span>' + (yes ? 'Yes' : 'No') + '</td>';
    }
    if (clean(raw) === '') return '<td class="cell empty"' + title + ' data-field="' + esc(field) + '">\u2014</td>';
    return '<td class="cell"' + title + ' data-field="' + esc(field) + '">' + esc(raw) + '</td>';
  }

  function rowHTML(p) {
    var cells = paperFields.map(function (f) {
      return cellHTML(f, p.values ? p.values[f] : '');
    }).join('');
    return '<tr data-pid="' + esc(p.Paper_ID) + '">' +
      '<td class="sticky-col"><span class="paper-title">' + esc(clean(p.Title)) + '</span><br>' +
        '<span class="citation-key">' + esc(p.Citation_Key) + '</span></td>' +
      '<td class="idx">' + esc(p.Year) + '</td>' +
      '<td>' + esc(p.Venue) + '</td>' +
      cells + '</tr>';
  }

  function renderExplorer() {
    var head = $('corpus-head');
    var body = $('corpus-body');
    if (!head || !body) return;
    $('corpus-n').textContent = N;
    $('corpus-f').textContent = paperFields.length;

    head.innerHTML = '<tr>' +
      '<th class="sticky-col">Paper</th><th>Year</th><th>Venue</th>' +
      paperFields.map(function (f) {
        return '<th title="' + esc(FIELD_DEF[f] || '') + '">' + esc(f) + '</th>';
      }).join('') +
    '</tr>';
    body.innerHTML = papers.map(rowHTML).join('');

    var search = $('corpus-search');
    var searchValues = $('corpus-search-values');
    var count = $('corpus-count');

    function applyFilter() {
      var q = search ? clean(search.value).toLowerCase() : '';
      var inValues = searchValues && searchValues.checked;
      var shown = 0;
      Array.prototype.forEach.call(body.rows, function (row) {
        var paper = paperById[row.getAttribute('data-pid')];
        var hay;
        if (inValues) {
          hay = clean(paper.Title) + ' ' + clean(paper.Citation_Key) + ' ' + paperFields.map(function (f) {
            return clean(paper.values ? paper.values[f] : '');
          }).join(' ');
        } else {
          hay = clean(paper.Title) + ' ' + clean(paper.Citation_Key) + ' ' + paper.Paper_ID;
        }
        var match = !q || hay.toLowerCase().indexOf(q) >= 0;
        row.classList.toggle('no-match', !match);
        if (match) shown += 1;
      });
      if (count) count.textContent = 'Showing ' + shown + ' of ' + papers.length + ' papers';
    }

    if (search) search.addEventListener('input', applyFilter);
    if (searchValues) searchValues.addEventListener('change', applyFilter);
    applyFilter();

    body.addEventListener('click', function (ev) {
      var row = ev.target.closest ? ev.target.closest('tr[data-pid]') : null;
      if (!row) return;
      var paper = paperById[row.getAttribute('data-pid')];
      if (!paper) return;
      var cell = ev.target.closest ? ev.target.closest('td.cell') : null;
      openPaperModal(paper, cell ? cell.getAttribute('data-field') : null);
    });
  }

  /* -------------------------------------------------------------- modal -- */

  var modal, modalTitle, modalSub, modalBody, lastFocus;

  function modalGroupHTML(g, paper, focusField) {
    var rows = g.fields.filter(function (f) {
      return paper.values && Object.prototype.hasOwnProperty.call(paper.values, f.name);
    }).map(function (f) {
      var val = clean(paper.values[f.name]);
      var focus = f.name === focusField ? ' focus' : '';
      var display = BOOL_FIELDS[f.name] && val ? '<span class="dot ' + (isYes(val) ? 'yes' : 'no') + '"></span>' + val
        : esc(val || '\u2014');
      return '<div class="modal-field' + focus + '" data-field="' + esc(f.name) + '">' +
        '<span class="mf-name">' + esc(f.name) + '</span>' +
        '<span class="mf-val' + (val ? '' : ' empty') + '">' + display + '</span></div>';
    }).join('');
    if (!rows) return '';
    return '<div class="modal-group"><h4>' + esc(g.id + ' \u00b7 ' + g.name) + '</h4>' + rows + '</div>';
  }

  function openPaperModal(paper, focusField) {
    if (!modal) return;
    var pid = String(paper.Paper_ID);
    var paperClaims = claimSlots.filter(function (s) { return String(s.Paper_ID) === pid; });
    var claimsHTML = paperClaims.length
      ? '<div class="modal-group"><h4>G7 \u00b7 Claim\u2013evidence alignment</h4>' + paperClaims.map(function (s) {
          return '<div class="modal-claim-row">' + alignChip(s.Final_Alignment) +
            '<span class="chip slot">' + esc(s.Claim_Slot) + '</span>' +
            '<span class="q">' + esc(clean(s.Claim_Quote)) + '</span></div>';
        }).join('') + '</div>'
      : '';
    modalTitle.textContent = clean(paper.Title);
    modalSub.textContent = paper.Citation_Key + ' \u00b7 ' + clean(paper.Year) + ' \u00b7 ' + clean(paper.Venue) +
      ' \u00b7 Paper #' + pid;
    modalBody.innerHTML = codebook.map(function (g) { return modalGroupHTML(g, paper, focusField); }).join('') +
      claimsHTML;

    lastFocus = document.activeElement;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    var focusEl = focusField ? modalBody.querySelector('.modal-field.focus') : null;
    if (focusEl && focusEl.scrollIntoView) focusEl.scrollIntoView({ block: 'center' });
    var closeBtn = $('modal-close');
    if (closeBtn) closeBtn.focus();
  }

  function closeModal() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function initModal() {
    modal = $('modal');
    if (!modal) return;
    modalTitle = $('modal-title');
    modalSub = $('modal-sub');
    modalBody = $('modal-body');
    var closeBtn = $('modal-close');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', function (ev) { if (ev.target === modal) closeModal(); });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') closeModal();
    });
  }

  /* ---------------------------------------------------------------- nav -- */

  function initNavHighlight() {
    var links = Array.prototype.slice.call(document.querySelectorAll('.nav-link')).filter(function (l) {
      return (l.getAttribute('href') || '').charAt(0) === '#';
    });
    if (!links.length || !('IntersectionObserver' in window)) return;
    var byId = {};
    links.forEach(function (l) {
      var id = decodeURIComponent(l.getAttribute('href').slice(1));
      byId[id] = l;
    });
    var sections = Object.keys(byId).map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (l) { l.classList.remove('active'); });
        var link = byId[entry.target.id];
        if (link) link.classList.add('active');
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
    sections.forEach(function (s) { observer.observe(s); });
  }

  /* --------------------------------------------------------------- init -- */

  function init() {
    try {
      initModal();
      renderHeader();
      renderOverview();
      renderGroups();
      renderExplorer();
      renderDownloads();
      initNavHighlight();
    } catch (err) {
      var fail = document.createElement('p');
      fail.className = 'fatal';
      fail.textContent = 'Failed to render page: ' + (err && err.message ? err.message : err);
      if (main) main.insertBefore(fail, main.firstChild);
      if (window.console && console.error) console.error(err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
