/* ==========================================================================
   Behavior-Grounded Evaluation — framework page renderer
   Reads window.SURVEY_DATA (bundled by web/data/data.js). No fetch, no deps,
   so the page renders when opened directly from file://.
   ========================================================================== */
(function () {
  'use strict';

  var DATA = window.SURVEY_DATA;
  var main = document.getElementById('main');

  function fatal(message) {
    var msg = document.createElement('p');
    msg.className = 'fatal';
    msg.textContent = message;
    if (main) main.insertBefore(msg, main.firstChild);
    else document.body.insertBefore(msg, document.body.firstChild);
  }

  if (!DATA) {
    fatal('Data bundle not found. Expected web/data/data.js to define window.SURVEY_DATA.');
    return;
  }

  var papersObj = DATA.papers || { papers: [] };
  var papers = papersObj.papers || [];
  var claims = DATA.claims || { slots: [] };
  var claimSlots = claims.slots || [];

  /* ---------------------------------------------------------- helpers ---- */

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function clean(value) {
    return String(value == null ? '' : value).replace(/\s+/g, ' ').trim();
  }
  function isYes(value) { return /^yes$/i.test(clean(value)); }
  function num(value) {
    var n = parseFloat(value);
    return isNaN(n) ? 0 : n;
  }
  function $(id) { return document.getElementById(id); }
  function valueOf(paper, field) {
    return paper && paper.values ? clean(paper.values[field]) : '';
  }

  var paperByKey = {};
  var paperById = {};
  papers.forEach(function (p) {
    paperById[String(p.Paper_ID)] = p;
    paperByKey[clean(p.Citation_Key)] = p;
  });

  var slotsByPaper = {};
  claimSlots.forEach(function (s) {
    var id = String(s.Paper_ID);
    (slotsByPaper[id] = slotsByPaper[id] || []).push(s);
  });

  function slotsFor(paper) {
    return paper ? (slotsByPaper[String(paper.Paper_ID)] || []) : [];
  }
  function firstSlotFor(citationKey) {
    var paper = paperByKey[citationKey];
    return paper ? (slotsFor(paper)[0] || null) : null;
  }

  /* ------------------------------------------- page-level evidence links -- */

  // Fallback PDF bases, taken from the released BibTeX (docs/citations.bib), for
  // the corpus examples named on this page. When the T1 data layer provides
  // Paper_URL / Claim_URL / Evidence_URL on a claim slot, those win.
  var FALLBACK_PDF = {
    'Louie2024Roleplay-doh': 'https://aclanthology.org/2024.emnlp-main.591.pdf',
    'Feng2025Reframe': 'https://aclanthology.org/2025.emnlp-main.1245.pdf',
    'Qiu2025EmoAgent': 'https://aclanthology.org/2025.emnlp-main.594.pdf'
  };

  function pdfBase(slot) {
    var provided = clean(slot && slot.Paper_URL);
    if (provided) return provided;
    return FALLBACK_PDF[clean(slot && slot.Citation_Key)] || '';
  }

  // Prefer the slot's pre-built URL field; otherwise append a #page= anchor.
  function pageHref(slot, page, urlKey) {
    var direct = clean(slot && slot[urlKey]);
    if (direct) return direct;
    var base = pdfBase(slot);
    if (!base) return '';
    var p = clean(page);
    return p ? base + '#page=' + encodeURIComponent(p) : base;
  }

  function claimHref(slot) { return pageHref(slot, slot && slot.Claim_Page, 'Claim_URL'); }
  function evidenceHref(slot) { return pageHref(slot, slot && slot.Evidence_Page, 'Evidence_URL'); }

  function externalLink(href, label, className) {
    if (!href) return '<span class="' + (className || '') + '">' + label + '</span>';
    return '<a class="' + (className || '') + '" href="' + esc(href) + '" target="_blank" rel="noopener">' +
      label + '</a>';
  }

  /* -------------------------------------------- BGE component content ----- */

  var COMPONENTS = [
    {
      id: 'claim',
      name: 'Claim',
      question: 'Q1',
      anchor: 'Paper \u00a75, p.\u00a05',
      quote: 'Evaluation begins by stating the behavioral claim to be evaluated.',
      summary: 'A behavioral claim states what the system is asserted to do. It is the entry point of ' +
        'the chain: every later component exists to test this claim, so it has to be stated explicitly ' +
        'rather than left implicit in a performance result.'
    },
    {
      id: 'construct',
      name: 'Construct',
      question: 'Q1',
      anchor: 'Paper \u00a75.1, pp.\u00a05\u20136',
      quote: 'A behavioral claim should be translated into a construct that identifies what property of ' +
        'behavior must be present for the claim to hold.',
      summary: 'For example, a claim that a simulated client exhibits resistance requires specifying what ' +
        'counts as resistance in the interaction, rather than treating any negative or disagreeing ' +
        'response as evidence for it.'
    },
    {
      id: 'markers',
      name: 'Behavioral Markers',
      question: 'Q1',
      anchor: 'Paper \u00a75.1, pp.\u00a05\u20136',
      quote: 'These markers should specify not only behaviors that count as evidence for the construct, ' +
        'but also nearby behaviors from which the construct must be distinguished.',
      summary: 'For resistance, markers might include limited disclosure, reluctance to accept ' +
        'suggestions, or sustained disagreement under particular interactional conditions \u2014 while ' +
        'general negativity or disengagement should not automatically receive the same interpretation. ' +
        'Defining these markers carefully matters because evaluator agreement does not guarantee construct ' +
        'validity.',
      corpusExamples: true
    },
    {
      id: 'trajectory',
      name: 'Trajectory',
      question: 'Q2',
      anchor: 'Paper \u00a75.2, p.\u00a06',
      quote: 'A trajectory is an ordered expectation about persistence or change, not simply a sequence of ' +
        'individually acceptable responses.',
      summary: 'Researchers should specify the relevant interaction window, the markers to be tracked, and ' +
        'whether those markers are expected to persist, increase, decrease, or change following particular ' +
        'interaction events. This can reveal behavioral drift that aggregate frequency or whole-dialogue ' +
        'ratings conceal.',
      corpusExamples: true
    },
    {
      id: 'intervention',
      name: 'Intervention',
      question: 'Q2',
      anchor: 'Paper \u00a75.2, p.\u00a06',
      quote: 'Holding the patient profile and scenario constant while varying a meaningful counselor ' +
        'action allows the expected behavioral consequence to be specified in advance.',
      summary: 'The unit of evaluation becomes the relation between an interaction event and the behavior ' +
        'that follows, rather than only the quality of the immediate response. Intervention-sensitive ' +
        'evaluation distinguishes genuine interactional adaptation from generic consistency.'
    },
    {
      id: 'evaluator',
      name: 'Evaluator',
      question: 'Q1',
      anchor: 'Paper \u00a75.1, p.\u00a06',
      quote: 'Experts, human coders, LLM judges, and automatic metrics provide different forms of evidence ' +
        'and should be validated for the judgments they are asked to make.',
      summary: 'Evaluator reliability concerns whether judgments can be reproduced, whereas construct ' +
        'validity concerns whether those judgments capture the behavior required by the claim. Reliable ' +
        'scoring therefore does not by itself establish valid measurement.'
    },
    {
      id: 'evidence-boundary',
      name: 'Evidence Boundary',
      question: 'Q3',
      anchor: 'Paper \u00a75.3, p.\u00a06',
      quote: 'The final component is the evidence boundary: the strongest conclusion warranted by the ' +
        'evaluation that has actually been conducted.',
      summary: 'The boundary should be stated in three elements \u2014 what the current evaluation ' +
        'supports, what stronger claim it does not yet support, and what additional evidence would be ' +
        'required. Simulated or model-based evidence stays informative; it simply does not, by itself, ' +
        'establish effects on the people who use the system.'
    }
  ];

  var QUESTION_LABEL = {
    Q1: 'What behavior is being measured? \u00b7 \u00a75.1',
    Q2: 'How should the behavior develop across interaction? \u00b7 \u00a75.2',
    Q3: 'What conclusions can the evidence support? \u00b7 \u00a75.3'
  };

  function corpusExamplesHTML() {
    function example(citationKey, display) {
      var paper = paperByKey[citationKey];
      if (!paper) {
        return '<li class="cx missing">' + esc(display) +
          ' <span class="cx-meta">no matching coded corpus row</span></li>';
      }
      var slot = slotsFor(paper)[0] || null;
      var href = slot ? evidenceHref(slot) : '';
      var page = slot ? clean(slot.Evidence_Page) : '';
      var label = esc(display) + ' <span class="cx-meta">paper #' + esc(paper.Paper_ID) +
        (page ? ' \u00b7 evidence p.\u00a0' + esc(page) : '') + '</span>';
      if (href) {
        return '<li class="cx"><a href="' + esc(href) + '" target="_blank" rel="noopener">' +
          label + ' \u2197</a></li>';
      }
      return '<li class="cx">' + label + '</li>';
    }
    return '<div class="cx-block">' +
      '<div class="cx-title">Corpus examples (review \u00a74.2, p.\u00a05)</div>' +
      '<ul class="cx-list">' +
        example('Feng2025Reframe', 'Interactive Narrative Therapist') +
        '<li class="cx missing">MusPsy (Wang et al., 2025a) ' +
          '<span class="cx-meta">cited in the review; not in the coded corpus</span></li>' +
        example('Qiu2025EmoAgent', 'EmoAgent') +
      '</ul></div>';
  }

  function renderChain() {
    var host = $('bge-chain');
    if (!host) return;
    var html = COMPONENTS.map(function (c, i) {
      var node = '<span class="chain-step a">' +
        '<span class="n">' + (i + 1) + '</span>' +
        '<span class="l">' + esc(c.name) + '</span></span>';
      if (i === 0) return node;
      return '<span class="chain-arrow">\u2192</span>' + node;
    }).join('');
    host.innerHTML = '<div class="chain">' + html + '</div>' +
      '<p class="note">Read left to right: each component constrains the next. The order follows the ' +
      'paper\u2019s chain (Sec.&nbsp;5).</p>';
  }

  function renderComponents() {
    var host = $('bge-components');
    if (!host) return;
    host.innerHTML = COMPONENTS.map(function (c, i) {
      var qLabel = QUESTION_LABEL[c.question] || c.question;
      return '<article class="comp-card" id="comp-' + esc(c.id) + '">' +
        '<div class="comp-head">' +
          '<span class="comp-num">' + (i + 1) + '</span>' +
          '<h3>' + esc(c.name) + '</h3>' +
        '</div>' +
        '<p class="comp-q"><span class="q-pill">' + esc(c.question) + '</span> ' + esc(qLabel) + '</p>' +
        '<p class="comp-quote">\u201c' + esc(c.quote) + '\u201d</p>' +
        '<p class="comp-sum">' + esc(c.summary) + '</p>' +
        (c.corpusExamples ? corpusExamplesHTML() : '') +
        '<p class="comp-anchor"><a href="#comp-' + esc(c.id) + '" class="anchor-tag">' +
          esc(c.anchor) + '</a></p>' +
      '</article>';
    }).join('');
  }

  /* -------------------------------------- Roleplay-doh corpus record ------ */

  function recordItem(label, value, extraClass) {
    var v = clean(value);
    return '<div class="record-item' + (extraClass ? ' ' + extraClass : '') + '">' +
      '<div class="record-label">' + esc(label) + '</div>' +
      '<div class="record-value">' + (v ? esc(v) : '\u2014') + '</div></div>';
  }

  function quoteBlockHTML(label, text, page, section, href) {
    var meta = [];
    if (page) meta.push('Page ' + esc(page));
    if (section) meta.push(esc(section));
    var link = href
      ? ' <a class="page-link" href="' + esc(href) + '" target="_blank" rel="noopener">open p.\u00a0' +
        esc(page) + ' \u2197</a>'
      : '';
    return '<div class="quote-block' + (label === 'Evidence' ? ' evidence' : '') + '">' +
      '<div class="quote-label">' + esc(label) + '</div>' +
      '<div class="quote-text">\u201c' + esc(clean(text) || 'Not reported') + '\u201d</div>' +
      '<div class="quote-meta">' + meta.join(' \u00b7 ') + link + '</div></div>';
  }

  function renderRoleplayRecord() {
    var host = $('roleplay-record');
    if (!host) return;
    var paper = paperById['80'] || paperByKey['Louie2024Roleplay-doh'];
    if (!paper) {
      host.innerHTML = '<p class="note">The Roleplay-doh corpus record is unavailable in this data ' +
        'bundle.</p>';
      return;
    }
    var slot = slotsFor(paper)[0] || null;
    var record = '<div class="record-grid">' +
      recordItem('Interaction level', valueOf(paper, 'Interaction_Level')) +
      recordItem('Behavioral evaluation depth', valueOf(paper, 'Behavior_Eval_Depth')) +
      recordItem('Theory grounding', valueOf(paper, 'Theory_Grounding')) +
      recordItem('Scoring rubric', valueOf(paper, 'Has_Rubric')) +
      recordItem('LLM-judge validation', valueOf(paper, 'LLM_Judge_Validated')) +
      recordItem('Reliability reported', valueOf(paper, 'Reliability_Reported')) +
    '</div>';

    var slotHTML;
    if (slot) {
      slotHTML =
        quoteBlockHTML('Claim', slot.Claim_Quote, slot.Claim_Page, slot.Claim_Section, claimHref(slot)) +
        '<div class="claim-arrow">\u25bc supporting evidence</div>' +
        quoteBlockHTML('Evidence', slot.Evidence_Quote, slot.Evidence_Page, slot.Evidence_Section,
          evidenceHref(slot)) +
        '<div class="claim-foot">' +
          '<span>Slot: <strong>' + esc(slot.Claim_Slot || 'C1') + '</strong></span>' +
          '<span>Final alignment: <strong>' + esc(slot.Final_Alignment || '\u2014') + '</strong></span>' +
          '<span>Decision: ' + esc(slot.Final_Decision_Type || 'n/a') + '</span>' +
        '</div>';
    } else {
      slotHTML = '<p class="note">No claim\u2013evidence slot is available for this paper in the ' +
        'current bundle.</p>';
    }

    host.innerHTML =
      '<div class="record-head">' +
        '<div>' +
          '<h3>Corpus record \u2014 Roleplay-doh (paper #80)</h3>' +
          '<p class="record-intro">Roleplay-doh (Louie et al., 2024) is paper #80 in the coded corpus ' +
            'and the subject of the case study. Its coded record and first claim\u2013evidence slot are ' +
            'shown below.</p>' +
        '</div>' +
        '<a class="record-link" href="index.html#corpus">Full record in the Corpus Explorer \u2192</a>' +
      '</div>' +
      record +
      '<h4 class="record-sub">C1 claim\u2013evidence slot</h4>' +
      '<div class="claim-foot-slot">' + slotHTML + '</div>';
  }

  /* --------------------------------------- Corpus construction / funnel --- */

  var FUNNEL = [
    { label: 'Records identified', n: 900, note: 'ACL Anthology, ACM Digital Library, IJHCS, IJHCI, and Google Scholar' },
    { label: 'Screened by title and abstract', n: 112, excluded: 'excluded: 788' },
    { label: 'Sought for retrieval', n: 112, excluded: 'not retrieved: 0' },
    { label: 'Full-text assessed for eligibility', n: 112, excluded: 'excluded: 60' },
    { label: 'Included in final synthesis', n: 52, included: true }
  ];

  var SOURCES = [
    { name: 'ACL Anthology', n: 440 },
    { name: 'ACM Digital Library', n: 198 },
    { name: 'IJHCI', n: 110 },
    { name: 'IJHCS', n: 100 },
    { name: 'Google Scholar (Others)', n: 52 }
  ];

  var FUNNEL_COLORS = ['#134e4a', '#0f766e', '#14b8a6', '#5eead4', '#0d9488'];

  function renderFunnel() {
    var host = $('corpus-funnel');
    if (!host) return;
    var top = FUNNEL[0].n;
    host.innerHTML = FUNNEL.map(function (stage, i) {
      var width = Math.max(12, Math.round((stage.n / top) * 1000) / 10);
      var extra = stage.excluded
        ? ' <span class="funnel-drop">(' + esc(stage.excluded) + ')</span>'
        : (stage.included ? ' <span class="funnel-keep">included</span>' : '');
      return '<div class="funnel-row">' +
        '<span class="funnel-label">' + esc(stage.label) + '</span>' +
        '<span class="funnel-bar" style="width:' + width + '%;background:' +
          FUNNEL_COLORS[i % FUNNEL_COLORS.length] + '">' + stage.n + '</span>' +
        '<span class="funnel-meta"><b>' + Math.round((stage.n / top) * 1000) / 10 + '%</b> of identified' +
          extra + '</span>' +
      '</div>';
    }).join('');
  }

  function renderSources() {
    var host = $('corpus-sources');
    if (!host) return;
    var total = SOURCES.reduce(function (acc, s) { return acc + s.n; }, 0);
    host.innerHTML = '<div class="bars">' + SOURCES.map(function (s, i) {
      var w = Math.max(2, Math.round((s.n / total) * 1000) / 10);
      return '<div class="bar-row">' +
        '<span class="bar-label">' + esc(s.name) + '</span>' +
        '<span class="bar-track"><span class="bar-fill" style="width:' + w + '%;background:' +
          FUNNEL_COLORS[i % FUNNEL_COLORS.length] + '"></span></span>' +
        '<span class="bar-value">' + s.n + ' <span class="bar-pct">' + w + '%</span></span>' +
      '</div>';
    }).join('') + '</div>' +
    '<p class="note">Total: ' + total + ' identified records (n&nbsp;=&nbsp;900 in Figure&nbsp;1).</p>';
  }

  /* ---------------------------------------------------------------- nav --- */

  function initNavHighlight() {
    var links = Array.prototype.slice.call(document.querySelectorAll('.nav-link'));
    var sections = links.map(function (l) {
      var href = l.getAttribute('href') || '';
      if (href.charAt(0) !== '#') return null;
      return document.getElementById(href.slice(1));
    }).filter(Boolean);
    if (!sections.length || !('IntersectionObserver' in window)) return;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (l) { l.classList.remove('active'); });
        links.forEach(function (l) {
          if (l.getAttribute('href') === '#' + entry.target.id) l.classList.add('active');
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
    sections.forEach(function (s) { observer.observe(s); });
  }

  /* --------------------------------------------------------------- init -- */

  function init() {
    try {
      renderChain();
      renderComponents();
      renderRoleplayRecord();
      renderFunnel();
      renderSources();
      initNavHighlight();
    } catch (err) {
      fatal('Failed to render page: ' + (err && err.message ? err.message : err));
      if (window.console && console.error) console.error(err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
